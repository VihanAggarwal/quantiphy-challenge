"""Part (2): which rows did the organisers drop when the scored set went from ~3,160 to 3,010 matched rows?

Hypothesis H1: every question of a test clip that belongs to a validation clip's family (the validation clip itself,
its _segmented twin, its lab s/x renders) is now excluded, and the duplicated (video_id, question) pair of
simulation_0263 fails to match.  Count check: 3289 - 277 (val-family rows) - 2 = 3010.

Consistency test on Track B (measurement only): B1 (old set) and B1clamp (new set) differ in 19 rows, so
B1clamp(new) - B1(old) is mostly the set-change effect.  Under H1 the effect per category is
    k * (S_old - mean_removed) / N_new
where mean_removed is estimated on the removed rows that have a validation PROXY label: the label of the validation
question with the same family and the same normalised question (lab renders and segmented twins share the event's
label; R1 premise).  Validation labels are used here only to measure, never to set an answer.

    .venv/bin/python research/next/accounting/scored_set.py
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from load import master, read, ROOT
from qp import postprocess as pp
from qp.data import load_split
from qp.mra import item_scores

OLD = {  # old-set per-category scores of files we can read (PROBES.md)
    "trackB_cand_B1": (.638, .676, .639, .652),
    "trackA_cand_C1_on_combo3": (.831, .868, .773, .814),
    "trackA_combo3_on_combo2": (.831, .863, .770, .813),
}
NEW = {
    "trackB_cand_B1clamp": (.641, .674, .634, .659),
    "trackB_probe_B2route": (.633, .698, .672, .680),
    "trackA_probe_agent_sim2agent": (.863, .875, .813, .832),
    "trackA_cand_agent_full": (.863, .870, .813, .832),
    "trackA_probe_agent_sim2base": (.852, .853, .813, .832),
}
CATS = ["S2", "D2", "S3", "D3"]


def fam(x: str) -> str:
    x = x.replace("_segmented", "")
    m = re.match(r"(captured_\d+[ab]?)([sxSX]*)$", x)
    return m.group(1) if m else x


def main():
    t = master()
    v = load_split("val_hires")
    vf = set(v.video_id.map(fam))
    proxy = {(fam(a), pp.norm_question(q)): float(y) for a, q, y in zip(v.video_id, v.question, v.answer)}
    tf = t.video_id.map(fam)
    infam = tf.isin(vf)
    dup = (t.video_id + "|" + t.question).duplicated(keep=False)
    print(f"rows in validation families: {int(infam.sum())}; + duplicated (video, question): {int(dup.sum())}; "
          f"remaining {len(t) - int((infam | dup).sum())} (leaderboard: 3010)")
    drop = (infam | dup) & t.scored
    N_old = t.scored.groupby(t.category).sum()
    k = drop.groupby(t.category).sum()
    N_new = N_old - k
    tab = pd.DataFrame({"N_old": N_old, "dropped": k, "N_new": N_new}).reindex(CATS)
    tab["drop_lab"] = (drop & t.srcg.eq("lab")).groupby(t.category).sum().reindex(CATS).fillna(0).astype(int)
    tab["drop_sim"] = (drop & t.srcg.eq("sim")).groupby(t.category).sum().reindex(CATS).fillna(0).astype(int)
    tab["drop_inet"] = (drop & t.srcg.eq("internet")).groupby(t.category).sum().reindex(CATS).fillna(0).astype(int)
    print(tab.to_string())
    y = pd.Series([proxy.get((a, pp.norm_question(q)), np.nan) for a, q in zip(tf, t.question)], index=t.index)
    has = drop & y.notna()
    print("dropped scored rows with a validation proxy label:", int(has.sum()), has.groupby(t.category).sum().to_dict())
    rows = []
    for f in list(OLD) + list(NEW):
        x = read(f, t.index)
        s = pd.Series(np.nan, index=t.index)
        s[has] = item_scores(x[has].to_numpy(), y[has].to_numpy())
        for i, c in enumerate(CATS):
            mm = has & t.category.eq(c)
            m_rem = s[mm].mean()
            sc = (OLD.get(f) or NEW.get(f))[i]
            rows.append(dict(file=f.replace("trackA_", "A:").replace("trackB_", "B:"), cat=c, set="old" if f in OLD else "new",
                             score=sc, n_proxy=int(mm.sum()), mean_removed_proxy=m_rem,
                             lab=s[mm & t.srcg.eq("lab")].mean(), nonlab=s[mm & t.srcg.ne("lab")].mean()))
    R = pd.DataFrame(rows)
    # predicted set-change effect for old-set files: k*(S_old - m)/N_new ; implied old score for new-set files:
    # S_old = (S_new*N_new + k*m)/N_old
    R["k"] = R.cat.map(k); R["N_new"] = R.cat.map(N_new); R["N_old"] = R.cat.map(N_old)
    R["pred_shift"] = R.k * (np.where(R.set == "old", R.score, np.nan) - R.mean_removed_proxy) / R.N_new
    R["implied_old"] = np.where(R.set == "new", (R.score * R.N_new + R.k * R.mean_removed_proxy) / R.N_old, np.nan)
    pd.set_option("display.width", 250)
    print(R.round(4).to_string(index=False))
    R.to_csv(__file__.replace("scored_set.py", "scored_set.csv"), index=False)
    # Track B consistency: B1clamp(new) - B1(old) observed vs predicted under H1
    b_old = dict(zip(CATS, OLD["trackB_cand_B1"])); b_new = dict(zip(CATS, NEW["trackB_cand_B1clamp"]))
    for c in CATS:
        r = R[(R.file == "B:cand_B1") & (R.cat == c)].iloc[0]
        print(f"Track B {c}: observed B1clamp(new) - B1(old) {b_new[c] - b_old[c]:+.3f}; predicted by H1 {r.pred_shift:+.4f} "
              f"(removed-row proxy mean {r.mean_removed_proxy:.3f} on {r.n_proxy} rows; category {r.score:.3f})")


if __name__ == "__main__":
    main()
