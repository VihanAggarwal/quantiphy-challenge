"""Replay a cached Claude run with qp.geometry's Blender label emulation off and on (no API calls).

    ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=<scratch ledger> \
        .venv/bin/python research/blenderemu/emulate.py --split test --run test_v1_high_854 --out <dir>

Annotations (qp.refine + dense motion, the run_claude defaults) are built once and reused by both builds.
Emulation is switched on only for clips rendered in Blender: video ids starting with "simulation"
(simulation_X and its segmented twin simulation_X_segmented). internet_X_segmented keeps the internet
labels' convention and lab clips their own, so they are never emulated.
Writes <out>/<split>_<run>[_refoff]_{off,on}.csv (run_claude.build_results columns).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import pandas as pd  # noqa: E402

import qp.geometry as G  # noqa: E402
import run_claude as rc  # noqa: E402
from qp.data import load_split  # noqa: E402


def blender_qids(df: pd.DataFrame) -> set[int]:
    return {int(q) for q, v in zip(df.qid, df.video_id) if str(v).startswith("simulation")}


def build(split: str, run: str, refine: bool = True, dense: str = "motion", anns_pickle: str | None = None):
    df = load_split(split)
    records = rc.load_records(ROOT / "runs" / run / split / "records")
    if anns_pickle:  # annotations already post-processed elsewhere (e.g. probe 4's refine-off dense tracks)
        import pickle
        with open(anns_pickle, "rb") as fh:
            anns = pickle.load(fh)["anns"]
    else:
        anns = rc.annotations(df, records, refine_priors=refine, dense=dense,
                              dense_cache=ROOT / "runs" / "_dense_cache" / split, dense_workers=4)
    sim = blender_qids(df)
    orig = G.solve
    off = rc.build_results(df, records, anns=anns)

    def solve_emu(spec, *a, **kw):
        if int(getattr(spec, "qid", -1)) in sim:
            kw["label_emulation"] = True
        return orig(spec, *a, **kw)

    G.solve = solve_emu
    try:
        on = rc.build_results(df, records, anns=anns)
    finally:
        G.solve = orig
    return df, off, on


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--refine-off", action="store_true")
    ap.add_argument("--dense", default="motion")
    ap.add_argument("--anns-pickle", help="pickle {'anns': ...} of post-processed annotations to use instead")
    ap.add_argument("--tag", help="output tag (default from split, run and options)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    _, off, on = build(a.split, a.run, refine=not a.refine_off, dense=a.dense, anns_pickle=a.anns_pickle)
    tag = a.tag or (f"{a.split}_{a.run}" + ("_refoff" if a.refine_off else "")
                    + ("" if a.dense == "motion" else f"_dense{a.dense}"))
    off.to_csv(out / f"{tag}_off.csv", index=False)
    on.to_csv(out / f"{tag}_on.csv", index=False)
    print(f"wrote {out}/{tag}_{{off,on}}.csv; emulated rows: {int(on["flags"].astype(str).str.contains('label_emulated').sum())}")


if __name__ == "__main__":
    main()
