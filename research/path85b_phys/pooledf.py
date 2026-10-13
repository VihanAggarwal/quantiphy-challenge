"""Lead C: pooled focal length per exact-camera group of 3D simulation clips (no API, no replay).

Exact-camera groups: clips sharing >= 3-decimal depth_info numbers (scratchpad simcam/camgroups.csv, built from test
inputs only), twins included. For clip c the pooled FOV is the median log tan(fov/2) of the prior-solved FOV of the
OTHER bases in its group (twin of c excluded), using only well-conditioned priors (3d_focal_from_prior, f-sensitivity
>= 0.8). Geometry at the pooled FOV comes from the per-question f sweep (simcam sw_fam3.pkl, run test_v1_high_854),
applied as a ratio to the 3-run log-median geometry: pool = old * t(fov_pool) / t(fov_own).

Outputs (stdout): kill test (held-out prior reproduced at the pooled FOV), then validation and stated-fact scoring of
dmed / old / pool / gm(dmed, pool) / gated variants via research/simfov/evaluate.report.
    .venv/bin/python research/path85b_phys/pooledf.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research/simfov"))
SC = Path("/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/big/simcam")
sys.path.insert(0, str(SC))
from lib import at, lt, fov_from_lt  # noqa: E402
import evaluate as EV  # noqa: E402
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split, load_validation  # noqa: E402

SENS_MIN = 0.8


def main():
    R = pd.read_pickle(SC / "sw_fam3.pkl").set_index("qid")
    cg = pd.read_csv(SC / "camgroups.csv").set_index("vid")
    rp = pd.read_csv(ROOT / "research/simfov/out/replay.csv")
    ok = (rp.method_old == "3d_focal_from_prior") & (rp.sens_old >= SENS_MIN) & rp.fov_old.notna()
    clip_fov = rp[ok].groupby("video_id").fov_old.apply(lambda s: fov_from_lt(np.median([lt(x) for x in s])))
    clip = pd.DataFrame({"cam": cg.cam, "base": cg.base})
    clip["fov_own"] = clip_fov.reindex(clip.index)
    pool = {}
    for v, c in clip.iterrows():
        o = clip[(clip.cam == c.cam) & (clip.base != c.base) & clip.fov_own.notna()]
        if len(o):
            pool[v] = (fov_from_lt(float(np.median([lt(x) for x in o.fov_own]))), len(o),
                       float(np.ptp([lt(x) for x in o.fov_own])) if len(o) > 1 else 0.0)
    clip["fov_pool"] = pd.Series({k: v[0] for k, v in pool.items()})
    clip["n_ref"] = pd.Series({k: v[1] for k, v in pool.items()})
    clip["spread"] = pd.Series({k: v[2] for k, v in pool.items()})
    print("clips with a pooled FOV:", clip.fov_pool.notna().sum())
    print(clip[clip.fov_pool.notna()].round(2).to_string())

    # kill test: the clip's own stated prior reproduced at the pooled FOV (sweep run), well-conditioned priors only
    first = R.reset_index().drop_duplicates("vid").set_index("vid")
    kt = []
    for v, c in clip[clip.fov_pool.notna()].iterrows():
        if v not in first.index:
            continue
        r = first.loc[v]
        if not (r.sens >= SENS_MIN) or r.method != "3d_focal_from_prior":
            continue
        pm = at(r, c.fov_pool, pre="p")
        kt.append(dict(vid=v, pkind=r.pkind, pval=r.pval, pred=pm, err=abs(math.log(pm / r.pval)) if pm > 0 else np.nan,
                       fov_own=c.fov_own, fov_pool=c.fov_pool, n_ref=c.n_ref))
    kt = pd.DataFrame(kt)
    print("\nKILL TEST (held-out prior at pooled FOV; kill if median |log err| >= 0.07):")
    print(kt.round(3).to_string())
    print(f"median |log err| = {kt.err.median():.3f}  (n={len(kt)}, within 7%: {(kt.err < 0.07).mean():.2f})")

    # answers
    t = EV.table(str(ROOT / "research/simfov/out/replay.csv"))
    rows = t.index.intersection(R.index)
    g = pd.Series(np.nan, index=t.index)
    for q in rows:
        v = t.at[q, "video_id"]
        fp = clip.fov_pool.get(v, np.nan)
        if not np.isfinite(fp):
            continue
        r = R.loc[q]
        own = r.fov_own if np.isfinite(r.fov_own) else np.nan
        tp = at(r, fp)
        if np.isfinite(own) and np.isfinite(t.at[q, "old"]):
            to = at(r, own)
            g[q] = t.at[q, "old"] * tp / to if to > 0 else np.nan
        else:
            g[q] = tp
    t["pool"] = g
    t["gm_pool"] = np.sqrt(t.dmed * t.pool)
    t["pool_or_d"] = t.pool.fillna(t.dmed)
    # gate: only where the clip's own prior solve disagrees with the pool by > 1.5x (CSC-like) and pool refs agree
    fo = t.video_id.map(clip.fov_own)
    fpz = t.video_id.map(clip.fov_pool)
    sp = t.video_id.map(clip.spread)
    dis = np.abs(np.log(np.tan(np.radians(fo) / 2) / np.tan(np.radians(fpz) / 2)))
    t["gate15"] = np.where((dis > math.log(1.5)) & (sp <= math.log(1.3)) & t.pool.notna(), t.pool, t.dmed)
    t["gmgate15"] = np.where((dis > math.log(1.5)) & (sp <= math.log(1.3)) & t.pool.notna(), t.gm_pool, t.dmed)
    print(f"\nrows with pooled geometry: {t.pool.notna().sum()} of {len(t)}; gate15 rows: {(t.gate15 != t.dmed).sum()}")
    cols = ["p21", "dmed", "old", "pool_or_d", "gm_pool", "gate15", "gmgate15"]
    sub = t[t.pool.notna()]
    test = load_split("test")
    val = load_validation()
    key = lambda d: list(zip(d.video_id, d.question.map(pp.norm_question)))  # noqa: E731
    vmap = dict(zip(key(val), val.answer))
    lab_v = pd.Series([vmap.get(k, np.nan) for k in key(test)], index=test.qid).dropna()
    EV.report(sub, lab_v, cols, "VALIDATION, rows with a pooled FOV")
    _, log = pp.apply_rules(t.dmed.reindex(test.qid).fillna(1.0), test, rules=("facts",), speed_guard=0)
    f = log[log.applied]
    lab_f = pd.Series(f.new.to_numpy(float), index=f.qid.astype(int))
    EV.report(sub, lab_f[lab_f.index.isin(sub.index)], cols, "STATED FACTS, rows with a pooled FOV", skip_p21=True)
    t.to_csv(ROOT / "research/path85b_phys/pooledf_table.csv")


if __name__ == "__main__":
    main()
