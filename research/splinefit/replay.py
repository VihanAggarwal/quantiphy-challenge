"""Free replay of a cached Claude run through qp.geometry with the original and the spline derivative estimators.

    ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=<scratch>/ledger.jsonl \
        .venv/bin/python research/splinefit/replay.py --split val_hires --run val_hr_v1_high

Annotations: the submission's 2D setting = qp.refine OFF + dense motion tracks from runs/_dense_cache/<split>
(D2 since probe 4; S2 priors are sizes, which qp.refine never touches, so S2 is the same under either setting).
Only 2D questions (S2, D2) are replayed: 3D non-lab and lab motion are routed to Claude's direct answers, and lab
static answers depend on the motion prior only through the lab camera's f MAP (prior weight ~6%: a 5% change of the
prior's measurement moves them ~0.3%).
Writes research/splinefit/out/<split>_<run>.csv: one row per (qid, mode) with run_claude.build_results' columns.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import run_claude as rc  # noqa: E402
import spline  # noqa: E402
from qp.data import load_split  # noqa: E402

MODES = ("base",) + spline.MODES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--refine", action="store_true", help="qp.refine on (default off = the D2 submission setting)")
    ap.add_argument("--modes", default=",".join(MODES))
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    t0 = time.time()
    df = load_split(a.split)
    df = df[df.category.isin(["S2", "D2"])]
    records = rc.load_records(ROOT / "runs" / a.run / a.split / "records")
    records = {v: r for v, r in records.items() if v in set(df.video_id)}
    df = df[df.video_id.isin(records)]
    anns = rc.annotations(df, records, refine_priors=a.refine, dense="motion",
                          dense_cache=ROOT / "runs" / "_dense_cache" / a.split, dense_workers=a.workers)
    print(f"annotations {len(anns)} ({time.time() - t0:.0f} s)", flush=True)
    out = []
    for mode in a.modes.split(","):
        for k in spline.STATS:
            spline.STATS[k] = 0
        with spline.patched(None if mode == "base" else mode):
            res = rc.build_results(df, records, anns=anns)
        res["mode"] = mode
        out.append(res)
        print(f"{mode}: {dict(spline.STATS)} ({time.time() - t0:.0f} s)", flush=True)
    r = pd.concat(out, ignore_index=True)
    meta = df.set_index("qid")[["video_id", "category", "video_source"]]
    r = r.join(meta, on="id")
    path = HERE / "out" / f"{a.split}_{a.run}{'_refine' if a.refine else ''}.csv"
    r.to_csv(path, index=False)
    print(f"wrote {path}: {len(r)} rows")


if __name__ == "__main__":
    main()
