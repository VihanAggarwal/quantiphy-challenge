"""Verifier: (1) L1 factors do not depend on the Track A noise fit (fit_noise.json) nor on the Table 6 ball sizes
(research/labnoise/common.BALL_D); (2) the S2 routing cells re-derive from Track A pseudo-labels on non-validation
test rows only (selection; no validation label read), with the same open member files."""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.argv = ["x"]
sys.path.insert(0, str(Path(__file__).parent))
import indep_b1 as I  # noqa: E402
import emulate as EM  # noqa: E402
import common as LC  # noqa: E402  research/labnoise/common.py

ROOT = I.ROOT
raw, post, fin, stated, info = I.build(True, True, True, True, True, True)
f0 = I.LN.factors("test", "qwen", post, 0.02, 0.02)
keep = dict(EM.PARAMS)
EM.PARAMS.update(sigma_zb=float("nan"), sigma_zL=float("nan"), sigma_px=EM.PARAMS["sigma_px"])
f1 = I.LN.factors("test", "qwen", post, 0.02, 0.02)
EM.PARAMS.clear(); EM.PARAMS.update(keep)
print("L1: factors with fit_noise sigmas -> NaN identical:", np.array_equal(f0.factor.to_numpy(), f1.factor.to_numpy()),
      "| rows factor!=1:", int((f0.factor != 1).sum()))
bd = dict(LC.BALL_D)
LC.BALL_D.clear()   # no Table 6 sizes: every ball falls to the default class
f2 = I.LN.factors("test", "qwen", post, 0.02, 0.02)
LC.BALL_D.update({k: 0.5 for k in bd})   # every named ball -> large ball class
f3 = I.LN.factors("test", "qwen", post, 0.02, 0.02)
LC.BALL_D.clear(); LC.BALL_D.update(bd)
print("L1: factors with BALL_D emptied identical:", np.array_equal(f0.factor.to_numpy(), f2.factor.to_numpy()),
      "| with all balls -> large class identical:", np.array_equal(f0.factor.to_numpy(), f3.factor.to_numpy()))
print("    sigma_px used:", EM.SIGMA_PX, "SIGMA_A:", EM.SIGMA_A, "(a-priori constants)")

# (2) routing re-derivation (as research/r86/intel_tb_pseudolabel/dump.py, k in (1, 2), cells with >= 25 fit rows)
from qp.data import load_split, load_validation  # noqa: E402
from qp.mra import item_scores  # noqa: E402
TB = Path("/tmp/claude-0/tb3/x/trackb_v1")
MEM = {"caw": "caw/caw.csv", "cv_geo": "cv/geometry.csv", "cv_geo_only": "cv/cv_geometry.csv",
       "cvq_geo": "cvq/geometry.csv", "qwen_geo": "qwen/geometry.csv", "qwen_direct": "qwen/direct.csv",
       "qwen35": "qwen35/direct.csv", "gemma4": "gemma4/direct.csv"}


def rd(p):
    d = pd.read_csv(p)
    return pd.to_numeric(d.set_index("id")["parsed_value"], errors="coerce")


test = load_split("test")
val_vids = set(load_validation().video_id)   # video ids only (no answers used)


def kind(u):
    u = str(u).lower()
    return "A" if ("s^2" in u or "s2" in u or "s²" in u) else ("V" if "/s" in u or "per s" in u else "L")


test["cell"] = test.category + "|" + test.video_source.astype(str).str.split("_").str[0] + "|" + test.target_unit.map(kind)
fit = test[~test.video_id.isin(val_vids)].copy()
fit["pl"] = fit.qid.map(rd(ROOT / "submissions/trackA_cand_combo2.csv"))
Tm = {m: rd(TB / "test" / p) for m, p in MEM.items()}


def lmed(cols):
    a = np.log(np.where(np.isfinite(cols) & (cols > 0), cols, np.nan))
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return np.exp(np.nanmedian(a, axis=1))


def score(f, ms):
    X = np.column_stack([f.qid.map(Tm[m]).to_numpy(float) for m in ms])
    p = lmed(X)
    p = np.where(np.isfinite(p) & (p > 0), p, 1e-9)
    return item_scores(p, f.pl.to_numpy()).mean()


R = pd.read_csv(ROOT / "research/r86/intel_tb_pseudolabel/routing_base8_min25_k2.csv").set_index("cell")
ok = True
for cell, f in fit[fit.category == "S2"].groupby("cell"):
    if len(f) < 25:
        continue
    sc = sorted([(score(f, ms), ms) for k in (1, 2) for ms in itertools.combinations(MEM, k)], reverse=True)
    mine = "+".join(sc[0][1])
    same = cell in R.index and R.members[cell] == mine and R.n_fit[cell] == len(f)
    ok &= same
    print(f"  {cell:20s} n_fit {len(f):4d} best {mine:22s} pl {sc[0][0]:.3f} | table {R.members.get(cell)} -> {'OK' if same else 'DIFF'}")
print("S2 routing cells re-derived from pseudo-labels on non-validation test rows:", ok)
# fallback S2 set = per-category best set of size 1-4 by pseudo-label MRA on all S2 fit rows
f = fit[fit.category == "S2"]
sc = sorted([(score(f, ms), ms) for k in range(1, 5) for ms in itertools.combinations(MEM, k)], reverse=True)
fb = json.load(open(ROOT / "research/r86/intel_tb_pseudolabel/fallback_category_sets.json"))["S2"]
print("S2 fallback set re-derived:", list(sc[0][1]), "| file:", fb, "->", list(sc[0][1]) == fb)
