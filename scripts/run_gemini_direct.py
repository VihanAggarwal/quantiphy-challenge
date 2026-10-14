"""Direct numeric answers from a Gemini model on QuantiPhy videos (Track A only: closed weights).

One request per video with all of its questions. Two input modes:
  --input frames  the Track A v1 frame plan (16 uniform + frames at mentioned times, max 32), each
                  frame labelled with its index and time, long edge <= --max-side (same frames Claude sees)
  --input video   the whole clip uploaded through the Files API and sampled at --fps (native video)
Resumable (records per video), with retries on rate limits. Budget-guarded with its own ledger
(budget/ledger_gemini.jsonl, cap --cap-usd): a request is sent only if the ledger plus its worst case
(input estimate + max output tokens, thinking included, at the output price) stays under the cap.

    python scripts/run_gemini_direct.py --split val_hires --name val_gem31pro_frames --model gemini-3.1-pro-preview
    python scripts/run_gemini_direct.py --split val_hires --name val_gem31pro_video --input video --fps 12
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qp.claude_annotate import (_question_block, frame_label, frame_plan, read_frames,  # noqa: E402
                                video_fps, video_info)
from qp.data import load_split  # noqa: E402

LEDGER = ROOT / "budget" / "ledger_gemini.jsonl"
# $/MTok (input, output incl. thinking), prompts <= 200k tokens. Flash / Robotics-ER prices are not published
# where we could check: priced as 3.1 Pro (an upper bound) so the cap stays safe.
PRICES = {"gemini-3.1-pro-preview": (2.0, 12.0), "gemini-pro-latest": (2.0, 12.0),
          "gemini-4-argon": (2.0, 10.0)}   # Argon: published $2/$10 (intro, to Nov 30)
DEFAULT_PRICE = (2.0, 12.0)
RES = {"low": "MEDIA_RESOLUTION_LOW", "medium": "MEDIA_RESOLUTION_MEDIUM", "high": "MEDIA_RESOLUTION_HIGH"}


def spent() -> float:
    if not LEDGER.exists():
        return 0.0
    return sum(json.loads(l).get("usd", 0.0) for l in LEDGER.read_text().splitlines() if l.strip())


def cost(model: str, prompt_tokens: int, output_tokens: int) -> float:
    pin, pout = PRICES.get(model, DEFAULT_PRICE)
    return (prompt_tokens * pin + output_tokens * pout) / 1e6

SYSTEM = """You measure physical quantities in short videos. Each question gives a known quantity (the \
prior, exactly true for this video), may give object-to-camera distances (depth info, 3D videos only), and \
asks for another quantity in a stated unit.

Method: locate the prior object and the target object(s), measure them in pixels (sizes as the extent of \
the asked dimension; motion from positions across frames and the frame times), and convert with the scale \
the prior gives (for 3D videos use the depth info: apparent size scales with 1/distance). Never answer from \
world knowledge about typical sizes or speeds: the scenes use arbitrary scales and the prior is the only \
scale. Give every answer as one positive number in the asked unit."""

SCHEMA = {"type": "object", "properties": {"answers": {"type": "array", "items": {
    "type": "object", "properties": {"qid": {"type": "integer"}, "value": {"type": "number"},
                                     "unit": {"type": "string"}, "how": {"type": "string"}},
    "required": ["qid", "value", "unit", "how"]}}}, "required": ["answers"]}


def load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                if v.strip():
                    os.environ.setdefault(k.strip(), v.strip())


def build_parts(client, types, rows: pd.DataFrame, args) -> tuple[list, str]:
    path = str(rows.iloc[0].video_path)
    n_total, w, h = video_info(path)
    fps, _ = video_fps(rows.iloc[0].fps, path)
    qs = "\n\n".join(_question_block(r) for r in rows.itertuples())
    parts = []
    if args.input == "frames":
        idx, _ = frame_plan(rows, n_total, fps, args.frames, args.max_frames, "v1")
        frames, scale = read_frames(path, idx, fps, max_side=args.max_side)
        for f in frames:
            parts.append(types.Part.from_text(text=frame_label(f)))
            parts.append(types.Part.from_bytes(data=base64.b64decode(f.jpeg_b64), mime_type="image/jpeg"))
        head = (f"Video {rows.iloc[0].video_id}: {len(frames)} frames ({w}x{h} px original, sent at scale "
                f"{scale:.3f}), {fps:g} fps, {n_total / fps:.2f} s long.")
    else:
        f = client.files.upload(file=path)
        while f.state and f.state.name == "PROCESSING":
            time.sleep(2)
            f = client.files.get(name=f.name)
        parts.append(types.Part(file_data=types.FileData(file_uri=f.uri, mime_type=f.mime_type),
                                video_metadata=types.VideoMetadata(fps=args.fps)))
        head = (f"Video {rows.iloc[0].video_id}: {w}x{h} px, {n_total} frames at {fps:g} fps "
                f"({n_total / fps:.2f} s); you see it sampled at {args.fps:g} frames per second, and time 0 is "
                "the first frame.")
    parts.append(types.Part.from_text(text=f"{head}\n\nQuestions:\n\n{qs}\n\nAnswer every qid."))
    return parts, head


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["val", "val_hires", "test"], required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--model", default="gemini-3.1-pro-preview")
    ap.add_argument("--input", choices=["frames", "video"], default="frames")
    ap.add_argument("--fps", type=float, default=12.0, help="video mode: sampling rate")
    ap.add_argument("--max-side", type=int, default=854)
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--max-frames", type=int, default=32)
    ap.add_argument("--videos", default="")
    ap.add_argument("--min-interval", type=float, default=2.0, help="seconds between requests")
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--thinking", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--media-resolution", default="high", choices=list(RES))
    ap.add_argument("--max-output", type=int, default=32768, help="output cap per request, thinking included")
    ap.add_argument("--cap-usd", type=float, default=15.0, help="hard cap on this ledger's total spend")
    ap.add_argument("--input-est", type=int, default=60000, help="worst-case prompt tokens per video")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    load_env()

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    df = load_split(args.split)
    if args.videos:
        df = df[df.video_id.isin(args.videos.split(","))]
    out = ROOT / "runs" / args.name
    rec_dir = out / args.split / "records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    (out / args.split / "config.json").write_text(json.dumps(vars(args), indent=2))
    groups = {v: g for v, g in df.groupby("video_id")}
    todo = [v for v in groups if not (rec_dir / f"{v}.json").exists()]
    worst = cost(args.model, args.input_est, args.max_output)
    print(f"{len(groups)} videos ({len(df)} questions): {len(groups) - len(todo)} cached, {len(todo)} to run "
          f"with {args.model} ({args.input}, thinking {args.thinking}, media {args.media_resolution}); worst case "
          f"${worst:.2f}/video, ledger ${spent():.2f} of cap ${args.cap_usd:.2f}", flush=True)
    if args.dry_run:
        return
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM, response_mime_type="application/json", response_schema=SCHEMA,
        max_output_tokens=args.max_output, media_resolution=getattr(types.MediaResolution, RES[args.media_resolution]),
        thinking_config=types.ThinkingConfig(thinking_level=args.thinking))
    last = 0.0
    for v in todo:
        rows = groups[v]
        if spent() + worst > args.cap_usd:
            print(f"budget cap: ledger ${spent():.2f} + worst case ${worst:.2f} > ${args.cap_usd:.2f}; stopping")
            break
        for attempt in range(args.retries):
            wait = args.min_interval - (time.time() - last)
            if wait > 0:
                time.sleep(wait)
            last = time.time()
            try:
                parts, head = build_parts(client, types, rows, args)
                t0 = time.time()
                r = client.models.generate_content(model=args.model,
                                                   contents=[types.Content(role="user", parts=parts)], config=config)
                um = r.usage_metadata
                usage = {"prompt": getattr(um, "prompt_token_count", None) or 0,
                         "output": getattr(um, "candidates_token_count", None) or 0,
                         "thoughts": getattr(um, "thoughts_token_count", None) or 0}
                usd = cost(args.model, usage["prompt"], usage["output"] + usage["thoughts"])
                with LEDGER.open("a") as fh:
                    fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "run": args.name,
                                         "model": args.model, "video": v, **usage, "usd": round(usd, 6)}) + "\n")
                text = r.text or ""
                try:
                    answers = json.loads(text)["answers"]
                except Exception:  # noqa: BLE001
                    answers = []
                rec = {"video_id": v, "model": args.model, "input": args.input, "thinking": args.thinking,
                       "media_resolution": args.media_resolution, "answers": answers, "raw_text": text,
                       "usage": usage, "usd": usd, "secs": round(time.time() - t0, 1)}
                (rec_dir / f"{v}.json").write_text(json.dumps(rec, indent=1))
                print(f"  {v}: {len(answers)}/{len(rows)} answers, tokens {usage}, ${usd:.3f} "
                      f"(ledger ${spent():.2f})", flush=True)
                break
            except Exception as e:  # noqa: BLE001 - rate limits / transient errors: back off and retry
                msg = str(e)[:240]
                print(f"  {v}: attempt {attempt + 1} failed: {type(e).__name__}: {msg}", flush=True)
                if "PerDay" in msg or "per day" in msg.lower():
                    print("daily quota reached: stopping (rerun later; finished videos are cached)")
                    return _write(df, rec_dir, out, args)
                if "402" in msg or "credit" in msg.lower() or "billing" in msg.lower():
                    print("billing error: stopping")
                    return _write(df, rec_dir, out, args)
                time.sleep(min(120, 15 * 2 ** attempt))
    _write(df, rec_dir, out, args)


def _write(df, rec_dir, out, args) -> None:
    vals = {}
    for p in rec_dir.glob("*.json"):
        for a in json.loads(p.read_text()).get("answers", []):
            try:
                x = abs(float(a["value"]))
                vals[int(a["qid"])] = x if math.isfinite(x) and x > 0 else math.nan
            except (KeyError, TypeError, ValueError):
                continue
    res = pd.DataFrame({"id": df.qid, "parsed_value": [vals.get(int(q), math.nan) for q in df.qid]})
    res["direct_value"] = res.parsed_value
    res.to_csv(out / f"{args.split}.csv", index=False)
    print(f"wrote {out / f'{args.split}.csv'}: {int(res.parsed_value.notna().sum())}/{len(res)} answered")


if __name__ == "__main__":
    main()
