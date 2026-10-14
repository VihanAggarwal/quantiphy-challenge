"""Batch-API version of scripts/run_gemini_direct.py (frames mode): same frames, prompt, schema and record format, but
all videos go into one Gemini Batch job (JSONL file upload) at the batch price (half the standard rate) and no
long-lived HTTP connection (the proxy drops long sync requests). Budget-guarded on budget/ledger_gemini.jsonl.

    .venv/bin/python research/newmodels/gemini_batch_direct.py --split val_hires --name val_argon_frames \
        --model gemini-4-argon [--videos a,b] [--dry-run]
    .venv/bin/python research/newmodels/gemini_batch_direct.py ... --fetch batches/<id>    # re-attach to a job
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import run_gemini_direct as G  # noqa: E402
from qp.claude_annotate import _question_block, frame_label, frame_plan, read_frames, video_fps, video_info  # noqa: E402
from qp.data import load_split  # noqa: E402

BATCH_FACTOR = 0.5   # Gemini Batch API: half the standard price


def request_json(rows, args):
    path = str(rows.iloc[0].video_path)
    n_total, w, h = video_info(path)
    fps, _ = video_fps(rows.iloc[0].fps, path)
    idx, _ = frame_plan(rows, n_total, fps, args.frames, args.max_frames, "v1")
    frames, scale = read_frames(path, idx, fps, max_side=args.max_side)
    parts = []
    for f in frames:
        parts.append({"text": frame_label(f)})
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": f.jpeg_b64}})
    head = (f"Video {rows.iloc[0].video_id}: {len(frames)} frames ({w}x{h} px original, sent at scale "
            f"{scale:.3f}), {fps:g} fps, {n_total / fps:.2f} s long.")
    qs = "\n\n".join(_question_block(r) for r in rows.itertuples())
    parts.append({"text": f"{head}\n\nQuestions:\n\n{qs}\n\nAnswer every qid."})
    return {"contents": [{"role": "user", "parts": parts}],
            "system_instruction": {"parts": [{"text": G.SYSTEM}]},
            "generation_config": {"response_mime_type": "application/json", "response_schema": G.SCHEMA,
                                  "max_output_tokens": args.max_output, "media_resolution": G.RES[args.media_resolution],
                                  "thinking_config": {"thinking_level": args.thinking}}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["val", "val_hires", "test"], required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--model", default="gemini-4-argon")
    ap.add_argument("--max-side", type=int, default=854)
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--max-frames", type=int, default=32)
    ap.add_argument("--videos", default="")
    ap.add_argument("--thinking", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--media-resolution", default="high", choices=list(G.RES))
    ap.add_argument("--max-output", type=int, default=32768)
    ap.add_argument("--cap-usd", type=float, default=15.0)
    ap.add_argument("--input-est", type=int, default=45000, help="worst-case prompt tokens per video")
    ap.add_argument("--fetch", default="", help="re-attach to an existing batch job")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    G.load_env()
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    df = load_split(args.split)
    if args.videos:
        df = df[df.video_id.isin(args.videos.split(","))]
    out = ROOT / "runs" / args.name
    rec_dir = out / args.split / "records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    groups = {v: g for v, g in df.groupby("video_id")}
    todo = [v for v in groups if not (rec_dir / f"{v}.json").exists()]
    worst = G.cost(args.model, args.input_est, args.max_output) * BATCH_FACTOR * len(todo)
    print(f"{len(groups)} videos: {len(groups) - len(todo)} cached, {len(todo)} to run with {args.model} (batch, "
          f"thinking {args.thinking}); worst case ${worst:.2f} total, ledger ${G.spent():.2f} of cap ${args.cap_usd:.2f}",
          flush=True)
    if args.dry_run or (not todo and not args.fetch):
        return G._write(df, rec_dir, out, args) if not todo else None
    if args.fetch:
        job = client.batches.get(name=args.fetch)
    else:
        if G.spent() + worst > args.cap_usd:
            raise SystemExit("over the cap: reduce --videos or raise --cap-usd")
        (out / args.split / "config.json").write_text(json.dumps({**vars(args), "mode": "batch"}, indent=2))
        jl = Path(f"/tmp/{args.name}_{args.split}_batch.jsonl")
        with jl.open("w") as fh:
            for v in todo:
                fh.write(json.dumps({"key": v, "request": request_json(groups[v], args)}) + "\n")
        print(f"request file {jl} ({jl.stat().st_size / 1e6:.1f} MB)", flush=True)
        up = client.files.upload(file=str(jl), config={"mime_type": "jsonl", "display_name": jl.name})
        job = client.batches.create(model=args.model, src=up.name, config={"display_name": f"{args.name}_{args.split}"})
        # hold the worst case in the ledger until results arrive (released by the per-video records below)
        print("batch", job.name, flush=True)
    t0 = time.time()
    while True:
        job = client.batches.get(name=job.name)
        st = job.state.name if job.state else ""
        if st in ("JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"):
            break
        time.sleep(30)
    print(f"state {st} after {time.time() - t0:.0f}s", flush=True)
    if st != "JOB_STATE_SUCCEEDED":
        raise SystemExit(f"batch ended {st}: {job.error}")
    raw = client.files.download(file=job.dest.file_name).decode()
    n = 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        v = d.get("key")
        resp = d.get("response") or {}
        um = resp.get("usageMetadata") or resp.get("usage_metadata") or {}
        usage = {"prompt": um.get("promptTokenCount", 0), "output": um.get("candidatesTokenCount", 0),
                 "thoughts": um.get("thoughtsTokenCount", 0)}
        usd = G.cost(args.model, usage["prompt"], usage["output"] + usage["thoughts"]) * BATCH_FACTOR
        with G.LEDGER.open("a") as fh:
            fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "run": args.name, "model": args.model,
                                 "video": v, **usage, "usd": round(usd, 6), "batch": job.name}) + "\n")
        text = ""
        for c in resp.get("candidates") or []:
            for p in (c.get("content") or {}).get("parts") or []:
                if not p.get("thought"):
                    text += p.get("text", "")
        try:
            answers = json.loads(text)["answers"]
        except Exception:  # noqa: BLE001
            answers = []
        rec = {"video_id": v, "model": args.model, "input": "frames", "thinking": args.thinking,
               "media_resolution": args.media_resolution, "answers": answers, "raw_text": text, "usage": usage,
               "usd": usd, "batch": job.name, "error": d.get("error")}
        (rec_dir / f"{v}.json").write_text(json.dumps(rec, indent=1))
        n += 1
        print(f"  {v}: {len(answers)}/{len(groups.get(v, []))} answers, {usage}, ${usd:.3f}", flush=True)
    print(f"{n} records; ledger ${G.spent():.2f}")
    G._write(df, rec_dir, out, args)


if __name__ == "__main__":
    main()
