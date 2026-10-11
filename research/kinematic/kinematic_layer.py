"""Kinematic consistency layer on top of any submission: per (video, object), timed speed answers are pulled toward a
constant-acceleration fit v(t) = v0 + a t (and timed acceleration answers toward its slope), when the group has enough
points and the fit is consistent.

    python research/kinematic/kinematic_layer.py SPLIT RECORDS_DIR IN_CSV OUT_CSV [--w 0.5]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split  # noqa: E402

SPEED = {"speed", "velocity"}


def groups(rec_dir: Path):
    out = {}
    for p in rec_dir.glob("*.json"):
        r = json.loads(p.read_text())
        for q in (r.get("parsed") or {}).get("questions", []):
            s = (q.get("spec") or {}).get("target") or {}
            if s.get("kind") in SPEED | {"acceleration"} and s.get("time") is not None and s.get("objects"):
                out.setdefault((r["video_id"], tuple(s["objects"])), []).append(
                    (int(q["qid"]), "a" if s["kind"] == "acceleration" else "v", float(s["time"])))
    return out


def apply(pred: pd.Series, grp: dict, unit_si: pd.Series, w: float, max_resid: float):
    new, log = pred.copy(), []
    for key, items in grp.items():
        items = [(q, k, t) for q, k, t in items if q in pred.index and np.isfinite(pred[q]) and pred[q] > 0]
        vs = [(q, t, pred[q] * unit_si[q]) for q, k, t in items if k == "v"]
        acs = [(q, t, pred[q] * unit_si[q]) for q, k, t in items if k == "a"]
        if len({t for _, t, _ in vs}) < 2 or len(vs) + len(acs) < 3:
            continue
        T = np.array([t for _, t, _ in vs]); V = np.array([x for _, _, x in vs])
        # constant-acceleration fit; acceleration answers (magnitudes) enter as extra slope observations
        A = np.c_[np.ones_like(T), T]; y = V
        for _, _, a in acs:
            sgn = np.sign(np.polyfit(T, V, 1)[0]) or 1.0
            A = np.r_[A, [[0.0, 1.0]]]; y = np.r_[y, sgn * a]
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        fit_v = coef[0] + coef[1] * T
        if (fit_v <= 0).any():
            continue
        resid = np.abs(np.log(V / fit_v))
        if np.median(resid) > max_resid:           # not one consistent motion (bounce, turn): leave alone
            continue
        for (q, t, x), fv in zip(vs, fit_v):
            new[q] = np.exp((1 - w) * np.log(x) + w * np.log(fv)) / unit_si[q]
            log.append((q, key[0], "v", x, fv))
        for q, t, x in acs:
            fa = abs(coef[1])
            if fa > 0:
                new[q] = np.exp((1 - w) * np.log(x) + w * np.log(fa)) / unit_si[q]
                log.append((q, key[0], "a", x, fa))
    return new, pd.DataFrame(log, columns=["qid", "video_id", "kind", "old_si", "fit_si"])


def unit_factor(u: str) -> float:
    u = str(u).strip().lower()
    return 0.01 if u.startswith("cm") else 0.001 if u.startswith("mm") else 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("split"); ap.add_argument("rec_dir"); ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--w", type=float, default=0.5); ap.add_argument("--max-resid", type=float, default=0.25)
    a = ap.parse_args()
    df = load_split(a.split).set_index("qid")
    d = pd.read_csv(a.inp); d = d.rename(columns={d.columns[0]: "id"}).set_index("id")
    pred = d["parsed_value"].astype(float).reindex(df.index)
    new, log = apply(pred, groups(Path(a.rec_dir)), df.target_unit.map(unit_factor), a.w, a.max_resid)
    pd.DataFrame({"id": new.index, "parsed_value": new.values}).to_csv(a.out, index=False)
    log.to_csv(Path(a.out).with_suffix(".log.csv"), index=False)
    ch = pd.Series(~np.isclose(new, pred, equal_nan=True), index=new.index)
    print(f"changed {int(ch.sum())} rows: {df.loc[ch[ch].index, 'category'].value_counts().to_dict()}; "
          f"median |log change| {np.nanmedian(np.abs(np.log(new[ch] / pred[ch]))):.3f}")


if __name__ == "__main__":
    main()
