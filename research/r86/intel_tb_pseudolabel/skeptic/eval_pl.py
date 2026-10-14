"""Skeptic check of the Track B pseudo-label routing proposal, with the real family-rule postprocess applied.
Validation labels used only for scoring. Pseudo-labels = Track A combo2 test predictions."""
import itertools, sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
ROOT = Path("/home/user/quantiphy-challenge")
sys.path.insert(0, str(ROOT / "research/trackb_v5")); sys.path.insert(0, str(ROOT))
from harness import Data, V3, CATS, VAL_OFFSET, fmt
from qp.mra import item_scores
RUN = Path("/tmp/claude-0/tb3/x/trackb_v1")
PLD = ROOT / "research/r86/intel_tb_pseudolabel"
D = Data()
rd = lambda p: pd.to_numeric(pd.read_csv(p).set_index("id")["parsed_value"], errors="coerce")
D.add_method("cv_geo_only", rd(RUN / "test/cv/cv_geometry.csv"), rd(RUN / "val/cv/cv_geometry.csv"))
MEM = ["caw", "cv_geo", "cv_geo_only", "cvq_geo", "qwen_geo", "qwen_direct", "qwen35", "gemma4"]

def kind(u):
    u = str(u).lower()
    return "A" if ("s^2" in u or "s2" in u) else ("V" if "/s" in u else "L")
for fr in (D.test, D.val):
    fr["cell"] = fr["category"] + "|" + fr["video_source"].astype(str).str.split("_").str[0] + "|" + fr["target_unit"].map(kind)

def lmed_rows(split, idx_mask, ms):
    L = np.log(np.vstack([D.P[split][m].to_numpy(float) for m in ms]))
    L[~np.isfinite(L)] = np.nan
    return np.exp(np.nanmedian(L, 0))[idx_mask]

def raw_routed(split, cellsets, fallback):
    fr = D.test if split == "test" else D.val
    out = np.full(len(fr), np.nan)
    for c, ms in fallback.items():
        m = (fr.category == c).to_numpy(); out[m] = lmed_rows(split, m, ms)
    for cell, ms in cellsets.items():
        m = (fr.cell == cell).to_numpy()
        if m.any(): out[m] = lmed_rows(split, m, ms)
    return pd.Series(out, index=fr.qid.to_numpy())

def combined_from_raw(rt, rv):
    return pd.concat([rt.reindex(D.test.qid[~D.dup]), pd.Series(rv.to_numpy(), index=D.val.qid.to_numpy() + VAL_OFFSET)])

R = pd.read_csv(PLD / "routing_base8_min25_k2.csv")
CS = {r.cell: r.members.split("+") for r in R.itertuples()}
FB = json.load(open(PLD / "fallback_category_sets.json"))

# v3 + rules
v3raw_t, v3raw_v = D.raw(V3, "test"), D.raw(V3, "val")
v3post, v3log = D.rules(combined_from_raw(v3raw_t, v3raw_v))
plraw_t, plraw_v = raw_routed("test", CS, FB), raw_routed("val", CS, FB)
plpost, pllog = D.rules(combined_from_raw(plraw_t, plraw_v))
print("v3 +rules   val", fmt(D.score(v3post)))
print("PL k2 +rules val", fmt(D.score(plpost)))
print("boot PL vs v3 (rules)", fmt(D.boot(v3post, plpost)))
# raw scores (no rules), for reference
rawv3 = pd.Series(v3raw_v.to_numpy(), index=D.val.qid.to_numpy() + VAL_OFFSET)
rawpl = pd.Series(plraw_v.to_numpy(), index=D.val.qid.to_numpy() + VAL_OFFSET)
print("raw v3 val", fmt(D.score(rawv3)), "| raw PL val", fmt(D.score(rawpl)))
print("boot raw", fmt(D.boot(rawv3, rawpl)))

# changed validation rows per category and their item sum
iv3, ipl = D.items(v3post), D.items(plpost)
ch = ~np.isclose(v3post.reindex(D.lab.index), plpost.reindex(D.lab.index), rtol=1e-6)
print("val rows changed (after rules) by cat:", D.vcat[ch].value_counts().to_dict(),
      "item sum change by cat:", (ipl - iv3)[ch].groupby(D.vcat[ch]).sum().round(3).to_dict())
print("val per-video delta (after rules):")
pv = pd.DataFrame({"d": ipl - iv3, "v": D.vvid, "c": D.vcat})
print(pv.groupby(["c", "v"]).d.sum().round(3)[lambda s: s.abs() > 0.05].to_string())

# test scored rows changed (non-dup test rows) by category
tq = D.test[~D.dup].set_index("qid")
a, b = v3post.reindex(tq.index), plpost.reindex(tq.index)
cht = ~np.isclose(a, b, rtol=1e-6)
print("test scored rows changed by cat:", tq.category[cht].value_counts().to_dict(), "of", tq.category.value_counts().to_dict())
# pseudo-MRA (vs Track A combo2) of the final outputs on scored test rows outside validation videos
pl = rd(ROOT / "submissions/trackA_cand_combo2.csv")
vv = set(D.val.video_id)
fitm = ~tq.video_id.isin(vv)
for name, p in (("v3", a), ("PL", b)):
    s = pd.Series(item_scores(p.to_numpy(float), pl.reindex(tq.index).to_numpy(float)), index=tq.index)
    print(f"pseudo-MRA after rules {name}: fit rows", {c: round(s[fitm & (tq.category == c)].mean(), 3) for c in CATS},
          "macro", round(np.mean([s[fitm & (tq.category == c)].mean() for c in CATS]), 4))
# leaderboard v3 per category for calibration
print("LB v3: S2 .558 D2 .663 S3 .620 D3 .641 = .621")

# stated-fact rows (exact labels from test inputs): raw (pre-rule) answers, v3 vs PL
fl = pd.read_csv(ROOT / "research/trackb_dense/out/fact_labels.csv", index_col=0)
fl = fl[fl.index < VAL_OFFSET]
r0, r1 = v3raw_t.reindex(fl.index), plraw_t.reindex(fl.index)
i0 = pd.Series(item_scores(r0.to_numpy(float), fl.lab.to_numpy(float)), index=fl.index)
i1 = pd.Series(item_scores(r1.to_numpy(float), fl.lab.to_numpy(float)), index=fl.index)
chf = ~np.isclose(r0, r1, rtol=1e-6)
print(f"facts (in-sample for PL fit): n {len(fl)}, changed {int(chf.sum())}, all-row mean {i0.mean():.3f} -> {i1.mean():.3f}; by cat",
      pd.DataFrame({"v3": i0, "pl": i1, "c": fl.cat}).groupby("c").mean().round(3).to_dict())
pd.to_pickle(dict(v3post=v3post, plpost=plpost, v3raw_t=v3raw_t, plraw_t=plraw_t), Path(__file__).parent / "cache.pkl")
