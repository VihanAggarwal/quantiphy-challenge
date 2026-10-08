"""Ask a VLM every question of a split; one cached record per question, resumable.

    python scripts/run_vlm.py --split val --provider anthropic --method measure --name opus_measure
    python scripts/run_vlm.py --split val --limit 10 ...          # quick probe

Writes runs/<name>/<split>.jsonl (raw replies) and runs/<name>/<split>.csv
(id + parsed_value, scoreable with scripts/score.py, fillable into the template).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qp import prompts  # noqa: E402
from qp.data import ROOT, load_split  # noqa: E402
from qp.frames import sample_frames, video_duration  # noqa: E402
from qp.parse import parse_answer  # noqa: E402
from qp.providers import Client  # noqa: E402


def load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        import os
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                if v.strip():
                    os.environ.setdefault(k.strip(), v.strip())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["val", "val_hires", "test"], required=True)
    ap.add_argument("--provider", choices=["anthropic", "openai", "gemini"], default="anthropic")
    ap.add_argument("--model")
    ap.add_argument("--method", choices=["direct", "measure"], default="measure")
    ap.add_argument("--name", required=True, help="run name, used as the output folder")
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--grid", type=int, default=0, help="pixel grid spacing to overlay (0 = none)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0, help="only the first N questions")
    args = ap.parse_args()
    load_env()

    df = load_split(args.split)
    if args.limit:
        df = df.head(args.limit)
    missing = df[df.video_path == ""]
    if len(missing):
        raise SystemExit(f"{len(missing)} questions have no local video; run scripts/download_data.py")

    out_dir = ROOT / "runs" / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / f"{args.split}.jsonl"
    done = {}
    if jsonl.exists():
        for line in jsonl.read_text().splitlines():
            rec = json.loads(line)
            done[rec["qid"]] = rec
    (out_dir / "config.json").write_text(json.dumps(vars(args), indent=2))

    client = Client(args.provider, args.model)
    lock = threading.Lock()
    todo = df[~df.qid.isin(done)]
    print(f"{len(done)} cached, {len(todo)} to run with {client.provider}:{client.model}")

    def work(row):
        frames = sample_frames(row.video_path, n=args.frames, fps=row.fps, grid=args.grid)
        system, text = prompts.build(args.method, row, len(frames), video_duration(row.video_path, row.fps))
        reply = client.ask(system, frames, text)
        return {"qid": int(row.qid), "reply": reply, "value": parse_answer(reply, row.target_unit)}

    with ThreadPoolExecutor(args.workers) as pool, jsonl.open("a") as fh:
        futures = {pool.submit(work, r): r.qid for r in todo.itertuples(index=False)}
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                rec = fut.result()
            except Exception as e:  # noqa: BLE001 - keep going; the question stays pending
                print(f"  qid {futures[fut]} failed: {type(e).__name__}: {e}")
                continue
            with lock:
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                done[rec["qid"]] = rec
            if i % 10 == 0 or i == len(futures):
                print(f"  {i}/{len(futures)}")

    vals = [done.get(int(q), {}).get("value", math.nan) for q in df.qid]
    out = pd.DataFrame({"id": df.qid, "parsed_value": vals})
    out.to_csv(out_dir / f"{args.split}.csv", index=False)
    n_bad = int(out.parsed_value.isna().sum())
    print(f"wrote {out_dir / f'{args.split}.csv'} ({n_bad} without a usable number)")


if __name__ == "__main__":
    main()
