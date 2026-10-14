"""Direct numeric answers from an OpenAI vision model (GPT-6 Astra) on the same frames Claude sees.

One request per video: the Track A v1 frame plan (16 uniform frames + frames at every mentioned time,
max 32, long edge <= --max-side) and every question of the video; the model returns one number per
question in the asked unit (structured output). Resumable (records per video), budget-guarded with its
own ledger (budget/ledger_openai.jsonl, cap --cap-usd): a request is sent only if the money already
spent plus every open request's worst case (input estimate + max_output_tokens at the output price)
stays under the cap.

    python scripts/run_openai_direct.py --split val --name val_astra_high --videos simulation_0089 --dry-run
    python scripts/run_openai_direct.py --split val --name val_astra_high
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qp.claude_annotate import (_question_block, frame_label, frame_plan, read_frames,  # noqa: E402
                                video_fps, video_info)
from qp.data import load_split  # noqa: E402

LEDGER = ROOT / "budget" / "ledger_openai.jsonl"
PRICES = {"gpt-6-astra": (10.0, 1.0, 50.0), "gpt-6.1-sol": (2.0, 0.2, 10.0)}          # $/MTok: input, cached input, output (incl. reasoning)
TOKENS_PER_IMAGE_EST = 1600                          # conservative; calibrated from the first responses

SYSTEM = """You measure physical quantities in short videos. Each question gives a known quantity (the \
prior, exactly true for this video), may give object-to-camera distances (depth info, 3D videos only), and \
asks for another quantity in a stated unit. You see frames with their frame index and time in seconds.

Method: locate the prior object and the target object(s) on the frames, measure them in pixels (sizes as \
the extent of the asked dimension; motion from positions across frames and the frame times), and convert \
with the scale the prior gives (for 3D videos use the depth info: apparent size scales with 1/distance). \
Never answer from world knowledge about typical sizes or speeds: the scenes use arbitrary scales and the \
prior is the only scale. Give every answer as one positive number in the asked unit."""

SCHEMA = {
    "type": "object",
    "properties": {"answers": {"type": "array", "items": {
        "type": "object",
        "properties": {"qid": {"type": "integer"}, "value": {"type": "number"},
                       "unit": {"type": "string"}, "how": {"type": "string"}},
        "required": ["qid", "value", "unit", "how"], "additionalProperties": False}}},
    "required": ["answers"], "additionalProperties": False}

_lock = threading.Lock()


def load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                if v.strip():
                    os.environ.setdefault(k.strip(), v.strip())


def spent() -> float:
    if not LEDGER.exists():
        return 0.0
    return sum(json.loads(l).get("usd", 0.0) for l in LEDGER.read_text().splitlines() if l.strip())


def price(model: str, usage) -> float:
    pin, pcache, pout = PRICES[model]
    cached = getattr(getattr(usage, "input_tokens_details", None), "cached_tokens", 0) or 0
    return ((usage.input_tokens - cached) * pin + cached * pcache + usage.output_tokens * pout) / 1e6


def build_input(rows: pd.DataFrame, max_side: int, n_uniform: int, max_frames: int):
    path = str(rows.iloc[0].video_path)
    n_total, w, h = video_info(path)
    fps, _ = video_fps(rows.iloc[0].fps, path)
    idx, _ = frame_plan(rows, n_total, fps, n_uniform, max_frames, "v1")
    frames, scale = read_frames(path, idx, fps, max_side=max_side)
    content = []
    for f in frames:
        content.append({"type": "input_text", "text": frame_label(f)})
        content.append({"type": "input_image", "image_url": f"data:image/jpeg;base64,{f.jpeg_b64}",
                        "detail": "high"})
    qs = "\n\n".join(_question_block(r) for r in rows.itertuples())
    content.append({"type": "input_text", "text": f"Video {rows.iloc[0].video_id}: {len(frames)} frames "
                    f"({w}x{h} px original, sent at scale {scale:.3f}), {fps:g} fps.\n\nQuestions:\n\n{qs}\n\n"
                    "Answer every qid."})
    return content, len(frames)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["val", "val_hires", "test"], required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--model", default="gpt-6-astra")
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--max-side", type=int, default=854)
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--max-frames", type=int, default=32)
    ap.add_argument("--videos", default="", help="comma-separated video ids (default: all)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--cap-usd", type=float, default=45.0, help="hard cap on this ledger's total spend")
    ap.add_argument("--max-output", type=int, default=0, help="0 = 8000 + 2500 per question (max 40000)")
    ap.add_argument("--service-tier", default="auto", choices=["auto", "default", "flex"],
                    help="flex: half price, slower (billed at 50% only when the response reports tier flex)")
    ap.add_argument("--sources", default="", help="comma-separated video_source values to keep (default: all)")
    ap.add_argument("--skip-segmented", action="store_true", help="skip *_segmented twins (they reuse the original)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    load_env()

    df = load_split(args.split)
    if args.videos:
        df = df[df.video_id.isin(args.videos.split(","))]
    if args.sources:
        df = df[df.video_source.isin(args.sources.split(","))]
    if args.skip_segmented:
        df = df[~df.video_id.str.endswith("_segmented")]
    out = ROOT / "runs" / args.name
    rec_dir = out / args.split / "records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    (out / args.split / "config.json").write_text(json.dumps(vars(args), indent=2))
    groups = {v: g for v, g in df.groupby("video_id")}
    todo = [v for v in groups if not (rec_dir / f"{v}.json").exists()]
    pin, _, pout = PRICES[args.model]
    est = {v: ((len(groups[v]) and 0) + args.max_frames * TOKENS_PER_IMAGE_EST + 1500) for v in todo}
    max_out = {v: args.max_output or min(40000, 8000 + 2500 * len(groups[v])) for v in todo}
    worst = {v: (est[v] * pin + max_out[v] * pout) / 1e6 for v in todo}
    print(f"{len(groups)} videos ({len(df)} questions): {len(groups) - len(todo)} cached, {len(todo)} to run "
          f"with {args.model} effort={args.effort}; worst case per video ~${max(worst.values(), default=0):.2f}, "
          f"ledger ${spent():.2f} of cap ${args.cap_usd:.2f}")
    if args.dry_run or not todo:
        return

    import openai
    client = openai.OpenAI()
    held: dict[str, float] = {}

    def work(v):
        with _lock:
            if spent() + sum(held.values()) + worst[v] > args.cap_usd:
                return v, "skipped: budget cap", 0.0
            held[v] = worst[v]
        try:
            rows = groups[v]
            content, n_frames = build_input(rows, args.max_side, args.frames, args.max_frames)
            t0 = time.time()
            # background mode + polling: long reasoning requests are otherwise dropped by the proxy
            r = client.responses.create(
                model=args.model, reasoning={"effort": args.effort}, max_output_tokens=max_out[v],
                instructions=SYSTEM, input=[{"role": "user", "content": content}], background=True,
                service_tier=args.service_tier,
                text={"format": {"type": "json_schema", "name": "answers", "schema": SCHEMA, "strict": True}})
            while r.status in ("queued", "in_progress"):
                time.sleep(5)
                r = client.responses.retrieve(r.id)
            usd = price(args.model, r.usage) * (0.5 if getattr(r, "service_tier", "") == "flex" else 1.0)
            with _lock:
                with LEDGER.open("a") as fh:
                    fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "run": args.name,
                                         "model": args.model, "video": v, "id": r.id,
                                         "input_tokens": r.usage.input_tokens,
                                         "output_tokens": r.usage.output_tokens, "usd": round(usd, 6)}) + "\n")
            try:
                answers = json.loads(r.output_text)["answers"]
            except Exception:  # noqa: BLE001 - keep the raw text; the question stays without a value
                answers = []
            (rec_dir / f"{v}.json").write_text(json.dumps({
                "video_id": v, "model": args.model, "effort": args.effort, "status": r.status,
                "n_frames": n_frames, "secs": round(time.time() - t0, 1), "usd": usd,
                "usage": {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens},
                "answers": answers, "raw_text": r.output_text}, indent=1))
            return v, f"ok {len(answers)}/{len(rows)} answers, {r.usage.input_tokens} in / "\
                      f"{r.usage.output_tokens} out, ${usd:.3f}", usd
        except Exception as e:  # noqa: BLE001 - report and continue with the other videos
            return v, f"failed: {type(e).__name__}: {str(e)[:300]}", 0.0
        finally:
            with _lock:
                held.pop(v, None)

    with ThreadPoolExecutor(args.workers) as pool:
        for fut in as_completed([pool.submit(work, v) for v in todo]):
            v, msg, _ = fut.result()
            print(f"  {v}: {msg}", flush=True)

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
    print(f"wrote {out / f'{args.split}.csv'}: {int(res.parsed_value.notna().sum())}/{len(res)} answered; "
          f"ledger ${spent():.2f} of cap ${args.cap_usd:.2f}")


if __name__ == "__main__":
    main()
