"""Verifier: the B2 routing table (all 23 cells) and the 4 category fallback sets re-derive from the development-time
pseudo-label procedure alone (research/r86/intel_tb_pseudolabel/pseudo_tb.py + dump.py): Track A combo2 test
predictions on test rows of non-validation videos (validation video ids only, no answers), cells with >= 25 fit rows,
1-2 member sets for cells, 1-4 member sets for the category fallback. Track A values are read ONLY here (development-
time method selection, FAQ section 09); nothing here writes or changes an answer.

Diagnostic (development-time information, no answer changed): on the lab cells, pseudo-label agreement of the routed
sets with qwen_geo vs the L2' substitute qwen_fov, and the best set if qwen_fov were a candidate member.
"""
import itertools
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/home/user/quantiphy-challenge")
sys.path.insert(0, str(ROOT))
from qp.data import load_split, load_validation  # noqa: E402
from qp.mra import item_scores  # noqa: E402

TB = Path("/tmp/claude-0/tb3/x/trackb_v1")
MEM = {"caw": "caw/caw.csv", "cv_geo": "cv/geometry.csv", "cv_geo_only": "cv/cv_geometry.csv",
       "cvq_geo": "cvq/geometry.csv", "qwen_geo": "qwen/geometry.csv", "qwen_direct": "qwen/direct.csv",
       "qwen35": "qwen35/direct.csv", "gemma4": "gemma4/direct.csv"}


def rd(p):
    d = pd.read_csv(p)
    return pd.to_numeric(d.set_index("id")["parsed_value"], errors="coerce")


def kind(u):
    u = str(u).lower()
    return "A" if ("s^2" in u or "s2" in u or "s²" in u) else ("V" if "/s" in u or "per s" in u else "L")


test = load_split("test")
val_vids = set(load_validation().video_id)
test["cell"] = test.category + "|" + test.video_source.astype(str).str.split("_").str[0] + "|" + test.target_unit.map(kind)
fit = test[~test.video_id.isin(val_vids)].copy()
fit["pl"] = fit.qid.map(rd(ROOT / "submissions/trackA_cand_combo2.csv"))
Tm = {m: rd(TB / "test" / p) for m, p in MEM.items()}


def lmed(X):
    a = np.log(np.where(np.isfinite(X) & (X > 0), X, np.nan))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return np.exp(np.nanmedian(a, axis=1))


def score(f, ms, src=Tm):
    p = lmed(np.column_stack([f.qid.map(src[m]).to_numpy(float) for m in ms]))
    return item_scores(np.where(np.isfinite(p) & (p > 0), p, 1e-9), f.pl.to_numpy()).mean()


R = pd.read_csv(ROOT / "research/r86/intel_tb_pseudolabel/routing_base8_min25_k2.csv").set_index("cell")
FB = json.load(open(ROOT / "research/r86/intel_tb_pseudolabel/fallback_category_sets.json"))
allok, seen = True, set()
for cell, f in fit.groupby("cell"):
    if len(f) < 25:
        continue
    seen.add(cell)
    sc = sorted([(score(f, ms), ms) for k in (1, 2) for ms in itertools.combinations(MEM, k)], reverse=True)
    mine = "+".join(sc[0][1])
    ok = cell in R.index and R.members[cell] == mine and R.n_fit[cell] == len(f)
    allok &= ok
    print(f"  {cell:20s} n_fit {len(f):4d} best {mine:24s} pl {sc[0][0]:.3f} (runner-up {'+'.join(sc[1][1])} "
          f"{sc[1][0]:.3f}) | table {R.members.get(cell)} -> {'OK' if ok else 'DIFF'}")
print("all table cells re-derived:", allok, "| table cells == re-derived cells:", set(R.index) == seen)
for c in ("S2", "D2", "S3", "D3"):
    f = fit[fit.category == c]
    sc = sorted([(score(f, ms), ms) for k in range(1, 5) for ms in itertools.combinations(MEM, k)], reverse=True)
    print(f"  fallback {c}: re-derived {list(sc[0][1])} pl {sc[0][0]:.3f} | file {FB[c]} -> {list(sc[0][1]) == FB[c]}")

# --- diagnostic: L2' inside routed lab sets (development-time pseudo-label agreement only)
sys.path.insert(0, str(ROOT / "research/trackb_v5"))
sys.path.insert(0, str(ROOT / "research/trackb_dense"))
import io, contextlib  # noqa: E401,E402
with contextlib.redirect_stdout(io.StringIO()):
    from harness import Data  # noqa: E402
    D = Data()
fov = pd.Series(D.P["test"]["qwen_fov"].to_numpy(float), index=D.test.qid.to_numpy())
T2 = dict(Tm, qwen_fov=fov)
print("\nL2' diagnostic on lab cells (pseudo-label MRA on fit rows; development-time information only):")
for cell in ("S3|lab|L", "S3|lab|V", "S3|lab|A", "D3|lab|L", "D3|lab|V", "D3|lab|A"):
    f = fit[fit.cell == cell]
    if not len(f):
        continue
    c = cell.split("|")[0]
    ms = R.members[cell].split("+") if cell in R.index else FB[c]
    msf = [("qwen_fov" if m == "qwen_geo" else m) for m in ms]
    best9 = sorted([(score(f, s, T2), s) for k in (1, 2) for s in itertools.combinations(list(T2), k)], reverse=True)[0]
    print(f"  {cell:10s} n_fit {len(f):3d} set {'+'.join(ms):22s} pl {score(f, ms):.3f} | with qwen_fov {score(f, msf, T2):.3f}"
          f" | best 1-2 set with qwen_fov as a 9th candidate: {'+'.join(best9[1])} {best9[0]:.3f}")
