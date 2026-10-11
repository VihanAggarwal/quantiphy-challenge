"""Candidate = probe 8 with Blender label emulation on the rows that are still raw pipeline geometry.

    .venv/bin/python research/blenderemu/build_candidate.py <replay dir> [--d2-refine-off]

Inputs (from research/blenderemu/emulate.py, no API calls):
  <dir>/test_test_v1_high_854_{off,on}.csv   the test run replayed (qp.refine + dense motion) without / with emulation
  <dir>/test_refoff_{off,on}.csv             probe 4's refine-off D2 annotations replayed (only with --d2-refine-off)
Rule: a row of probe 8 is multiplied by on/off when its clip is a Blender render (simulation_X or
simulation_X_segmented), the pipeline answered it by geometry, and probe 8 still holds that pipeline value
(equal to runs/test_v1_high_854/test.csv; with --d2-refine-off also D2 rows equal to the refine-off replay).
Rows replaced by stated facts, family pools, ensembles or Claude's direct answers are left alone, except a
segmented-twin copy of a changed row (same question and prior, same value in probe 8), which follows it.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split  # noqa: E402

BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
RAW = ROOT / "runs/test_v1_high_854/test.csv"


def read(p: Path, idx) -> pd.DataFrame:
    d = pd.read_csv(p)
    return d.rename(columns={d.columns[0]: "id"}).set_index("id").reindex(idx)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("replay_dir")
    ap.add_argument("--d2-refine-off", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "submissions/trackA_cand_blenderemu_on_p8.csv"))
    a = ap.parse_args()
    d = Path(a.replay_dir)
    test = load_split("test").set_index("qid")
    idx = test.index
    base = read(BASE, idx)["parsed_value"].astype(float)
    raw = read(RAW, idx)["parsed_value"].astype(float)
    off, on = read(d / "test_test_v1_high_854_off.csv", idx), read(d / "test_test_v1_high_854_on.csv", idx)
    blender = test.video_id.str.startswith("simulation")
    same = pd.Series(np.isclose(off.parsed_value, raw, rtol=1e-9, equal_nan=True), index=idx)
    print(f"replay (emulation off) == {RAW.name}: {int(same.sum())} of {len(idx)}; "
          f"Blender rows {int(same[blender].sum())} of {int(blender.sum())} "
          f"(other differences: {test.video_source[~same].value_counts().to_dict()}, combine-rule changes since)")
    if not same[blender].all():
        raise SystemExit("the off replay does not reproduce the cached run on Blender rows; refusing to build")

    geo = off.method.astype(str).str.startswith("geometry")
    ratio = pd.Series(on.parsed_value.to_numpy() / off.parsed_value.to_numpy(), index=idx)
    rule = pd.Series("", index=idx)
    # a row whose emulated geometry makes qp.combine switch to Claude's direct answer is a knife-edge of the
    # disagreement guard, not an emulation effect: left unchanged
    switched = on.method.astype(str).str.split(":").str[0] != off.method.astype(str).str.split(":").str[0]
    elig = (blender & geo & pd.Series(np.isclose(base, raw, rtol=1e-9), index=idx) & np.isfinite(ratio)
            & ~switched)
    rule[elig] = "raw"
    if a.d2_refine_off:
        offB, onB = read(d / "test_refoff_off.csv", idx), read(d / "test_refoff_on.csv", idx)
        rB = pd.Series(onB.parsed_value.to_numpy() / offB.parsed_value.to_numpy(), index=idx)
        swB = onB.method.astype(str).str.split(":").str[0] != offB.method.astype(str).str.split(":").str[0]
        eB = (blender & (test.category == "D2") & offB.method.astype(str).str.startswith("geometry") & ~elig
              & pd.Series(np.isclose(base, offB.parsed_value, rtol=1e-9), index=idx) & np.isfinite(rB) & ~swB)
        switched = switched | swB
        ratio[eB], rule[eB] = rB[eB], "refine_off"
        elig = elig | eB
    # segmented-twin copies of an eligible row follow it
    key = test.video_id.str.replace("_segmented", "", regex=False) + "|" + test.question + "|" + test.prior.astype(str)
    for q in idx[elig & ~np.isclose(ratio, 1.0, rtol=1e-12)]:
        for q2 in idx[(key == key[q]) & (idx != q) & ~elig]:
            if np.isclose(base[q2], base[q], rtol=1e-9):
                ratio[q2], rule[q2] = ratio[q], "twin_copy"
                elig[q2] = True
    new = base.copy()
    new[elig] = base[elig] * ratio[elig]
    ch = elig & ~np.isclose(new, base, rtol=1e-12)
    print(f"eligible {int(elig.sum())} ({rule[elig].value_counts().to_dict()}), changed {int(ch.sum())}; "
          f"left unchanged: geometry->direct switches on Blender rows {int((switched & blender).sum())}")
    kind = np.where(test.question.str.contains("acceleration", case=False), "acc_target", "speed_target")
    for c in ("S2", "D2", "S3", "D3"):
        m = ch & (test.category == c)
        r = ratio[m]
        if m.any():
            print(f"  {c}: changed {int(m.sum())}, median ratio {r.median():.4f}, median |log| "
                  f"{np.abs(np.log(r)).median():.4f}, >5% {int((np.abs(np.log(r)) > 0.05).sum())}, "
                  f"range {r.min():.3f}..{r.max():.3f}")
            for k in ("speed_target", "acc_target"):
                mk = m & (kind == k)
                if mk.any():
                    print(f"      {k}: {int(mk.sum())}, median ratio {ratio[mk].median():.4f}, "
                          f">5% {int((np.abs(np.log(ratio[mk])) > 0.05).sum())}")
        else:
            print(f"  {c}: changed 0")
    log = pd.DataFrame({"qid": idx[ch], "video_id": test.video_id[ch], "category": test.category[ch],
                        "rule": rule[ch], "kind": kind[ch.to_numpy()], "base": base[ch], "new": new[ch], "ratio": ratio[ch]})
    stem = Path(a.out).stem
    log.to_csv(Path(__file__).parent / f"{stem}_changes.csv", index=False)
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": idx, "parsed_value": new.to_numpy()}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, a.out], check=True)


if __name__ == "__main__":
    main()
