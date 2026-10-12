"""Replay the cached Claude run on internet clips with the internet label convention for speeds at a time:
a FORWARD one-frame difference v_i = |p_{i+1} - p_i| * fps at i = round(t * fps) (paper App. D.3), evaluated
on the same fitted local polynomial as without emulation (qp.geometry's opt-in emulation hook, here patched
from Blender's backward difference to a forward one). Accelerations at a time keep |a| (central second
difference of positions = the fitted |a|). Applies to targets and timed priors. No API calls.

    ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" .venv/bin/python research/internet/fwd_emulate.py \
        --split test --run test_v1_high_854 --out research/internet/out [--refine-off] [--ahead 1]
Writes <out>/<split>_<run>[_refoff]_fwd{ahead}_{off,on}.csv for internet videos (incl. *_segmented).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import qp.geometry as G  # noqa: E402
import run_claude as rc  # noqa: E402
from qp.data import load_split  # noqa: E402

AHEAD = 1


def _fwd_speeds(fit, t0: float, fps: float, cols: list[int], n: int):
    if n != 1:          # acceleration at a time: keep the fitted |a| (central difference convention)
        return None
    i = int(round(t0 * fps))
    ts = (np.array([i, i + AHEAD]) / fps) - t0
    pts = np.column_stack([np.polyval(fit[7][:, j], ts) for j in cols])
    return [float(np.linalg.norm(pts[1] - pts[0]) * fps / AHEAD)]


def main() -> None:
    global AHEAD
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--refine-off", action="store_true")
    ap.add_argument("--ahead", type=int, default=1)
    a = ap.parse_args()
    AHEAD = a.ahead
    df = load_split(a.split)
    df = df[df.video_id.astype(str).str.startswith("internet")].copy()
    records = rc.load_records(ROOT / "runs" / a.run / a.split / "records")
    records = {k: v for k, v in records.items() if k.startswith("internet")}
    anns = rc.annotations(df, records, refine_priors=not a.refine_off, dense="motion",
                          dense_cache=ROOT / "runs" / "_dense_cache" / a.split, dense_workers=2)
    off = rc.build_results(df, records, anns=anns)
    orig_solve, orig_emu = G.solve, G._emu_speeds

    def solve_emu(spec, *args, **kw):
        kw["label_emulation"] = True
        return orig_solve(spec, *args, **kw)

    G.solve, G._emu_speeds = solve_emu, _fwd_speeds
    try:
        on = rc.build_results(df, records, anns=anns)
    finally:
        G.solve, G._emu_speeds = orig_solve, orig_emu
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tag = f"{a.split}_{a.run}" + ("_refoff" if a.refine_off else "") + f"_fwd{a.ahead}"
    off.to_csv(out / f"{tag}_off.csv", index=False)
    on.to_csv(out / f"{tag}_on.csv", index=False)
    n = int(on["flags"].astype(str).str.contains("label_emulated").sum())
    print(f"wrote {out}/{tag}_{{off,on}}.csv; rows {len(on)}, emulated {n}")


if __name__ == "__main__":
    main()
