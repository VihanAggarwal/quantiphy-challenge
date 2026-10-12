"""Test side (label-free): risk flags on every test question, which rows a re-ask could still move,
and stated-fact rows used as exact labels (made by the same procedure) to check flags and ensembles.

    .venv/bin/python research/reask/test_flags.py
writes research/reask/test_rows.csv and prints the tables used in the spend plan.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import add_prior_ratio, run_table  # noqa: E402
from qp import postprocess as pp  # noqa: E402
from qp.data import load_test, load_validation  # noqa: E402
from qp.mra import item_scores  # noqa: E402

t = load_test().set_index("qid")
ft = add_prior_ratio(run_table("runs/test_v1_high_854", "test"), t.target_unit).reindex(t.index)
ft = ft.join(t[["category", "video_source", "question", "prior"]])
ft["video_id"] = t.video_id
ft["src"] = np.where(t.video_type.str[1] == "2", "2D", np.where(t.video_source == "lab", "lab", "3Dnl"))

# validation-overlap rows (no longer scored): same clip and same question text
v = load_validation()
key = lambda vid, q: vid + "||" + pp.norm_question(q)  # noqa: E731
vkeys = {key(a, b) for a, b in zip(v.video_id, v.question)}
ft["val_overlap"] = [key(a, b) in vkeys for a, b in zip(ft.video_id, ft.question)]

# the three runs on 3D non-lab (direct answers) -> spread and median
r = lambda p: pd.read_csv(ROOT / p).set_index("id")["direct_value"].reindex(t.index)  # noqa: E731
D = pd.concat([r("runs/test_v1_high_854/test.csv"), r("runs/test_3dnl_v1_high_b/test.csv"),
               r("runs/test_3dnl_v2_high/test.csv")], axis=1)
L = np.log(D.where(D > 0))
ft["dspread3"] = np.where(ft.src == "3Dnl", L.max(axis=1) - L.min(axis=1), np.nan)
ft["d_med3"] = np.exp(L.median(axis=1))

# p8 and which rows still follow the raw pipeline answer (a re-ask could move them)
p8 = pd.read_csv(ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv",
                 float_precision="round_trip").set_index("id").parsed_value.reindex(t.index)
ft["p8"] = p8
raw = ft.parsed_value.where(ft.src != "3Dnl", ft.parsed_value * ft.d_med3 / ft.direct_value)
ft["follows_raw"] = np.isclose(p8, raw, rtol=0.02) | np.isclose(p8, ft.parsed_value, rtol=0.02)

# stated facts (exact labels by the same procedure) for leave-one-fact-out checks
sf = pp.stated_facts(t.reset_index())
sf = sf[sf.groupby("qid").tier.transform("min") == sf.tier]
sf = sf.assign(vr=np.round(sf.value.astype(float), 9))
nun = sf.groupby("qid").vr.nunique()
fact = sf.groupby("qid").vr.first()[nun == 1]
ft["fact"] = fact.reindex(t.index)
ft["is_fact_row"] = np.isclose(p8, ft.fact, rtol=1e-6)
ft.to_csv(Path(__file__).with_name("test_rows.csv"))

sc = ft[["category", "src"]].copy()
sc["has_fact"] = ft.fact.notna()
for c in ["parsed_value", "direct_value", "geo_value", "d_med3"]:
    sc[c] = item_scores(ft[c], ft.fact)

pd.set_option("display.width", 200)
print("== stated-fact rows as labels (raw pipeline answers, before any family rule) ==")
flags = {"all": pd.Series(True, index=ft.index), "conf<=0.3": ft.conf <= 0.3, "conf<=0.2": ft.conf <= 0.2,
         "gd>0.2": ft.gd > 0.2, "dspread3>0.15": ft.dspread3 > 0.15, "dspread3>0.3": ft.dspread3 > 0.3,
         "prior_ratio_out": (ft.prior_ratio > 10) | (ft.prior_ratio < 0.1), "beyond_end": ft.beyond,
         "cov_gap>0.25": ft.cov_gap > 0.25}
rows = []
for src in ["ALL", "2D", "lab", "3Dnl"]:
    g = sc.has_fact & ((ft.src == src) if src != "ALL" else True)
    for name, f in flags.items():
        m = g & f.fillna(False).astype(bool)
        if m.sum() == 0:
            continue
        s = sc[m]
        rows.append(dict(src=src, flag=name, n=int(m.sum()), parsed=s.parsed_value.mean(),
                         wrong=(s.parsed_value < .5).mean(), direct=s.direct_value.mean(),
                         d_med3=s.d_med3.mean() if src == "3Dnl" else np.nan))
print(pd.DataFrame(rows).round(3).to_string(index=False))

print("\n== scored test rows that still follow the raw answer (re-ask can move them), by category ==")
sc_rows = ~ft.val_overlap
out = []
for cat in ["S2", "D2", "S3", "D3"]:
    for src in ["2D", "lab", "3Dnl"]:
        m = sc_rows & (ft.category == cat) & (ft.src == src)
        if m.sum() == 0:
            continue
        fr = m & ft.follows_raw & ~ft.is_fact_row
        out.append(dict(cat=cat, src=src, scored=int(m.sum()), follows_raw=int(fr.sum()),
                        conf_le_03=int((fr & (ft.conf <= .3)).sum()), gd_gt_02=int((fr & (ft.gd > .2)).sum()),
                        spread_gt_015=int((fr & (ft.dspread3 > .15)).sum()),
                        direct=int((fr & (ft.method == "direct")).sum()),
                        videos=ft[fr].video_id.nunique()))
print(pd.DataFrame(out).to_string(index=False))
print("\nscored N per category:", (ft[sc_rows].category.value_counts()).to_dict())
