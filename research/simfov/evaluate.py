"""Evaluate geometry with a model FOV on the 3D simulation clips (S3/D3) against (1) validation labels (validation
questions matched to the identical test questions; labels read only here, never written to a test answer) and
(2) exactly-known stated-fact rows from scene families on test (qp.postprocess "facts" rule).

    .venv/bin/python research/simfov/evaluate.py research/simfov/out/replay.csv [--fov research/simfov/out/fov_moge.csv]

Columns compared (all on the same rows):
  p21      current best submission (includes family rules; on fact rows it holds the stated value, so it is not
           scored there)
  dmed     Claude direct answer, log-median of the 3 cached runs (the pre-rule base of p21 on 3D non-lab)
  old      geometry, f solved from the prior (log-median of the 3 runs' geometry)
  cam05 / cam15 / fix / snap ...  geometry with the model FOV (see replay.py), log-median over runs
  gm_X     geometric mean of dmed and X (decided a priori)
  gmp_X    geometric mean of p21 and X (validation only)
  gate_X   X where the old solve's f is well conditioned, i.e. the prior is a size with depth or a motion prior
           with f-sensitivity >= 0.3, else dmed  (a priori)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split, load_validation  # noqa: E402
from qp.mra import item_scores  # noqa: E402

P21 = ROOT / "submissions/trackA_best_p21.csv"


def lmed(x: pd.DataFrame) -> pd.Series:
    with np.errstate(all="ignore"):
        L = np.log(x.where(x > 0))
        return np.exp(L.median(axis=1, skipna=True))


def table(replay_csv: str) -> pd.DataFrame:
    r = pd.read_csv(replay_csv)
    geo_cols = [c for c in r.columns if c.startswith("geo_")]
    w = {}
    for c in ["direct"] + geo_cols:
        w[c] = lmed(r.pivot_table(index="qid", columns="run", values=c, aggfunc="first"))
    t = pd.DataFrame(w)
    first = r[r.run == r.run.iloc[0]].set_index("qid")
    for c in ("video_id", "category", "kind", "prior_kind", "fov_model", "fov_old", "sens_old", "method_old",
              "flags_old", "W"):
        t[c] = first[c].reindex(t.index)
    t = t.rename(columns={"direct": "dmed", **{c: c[4:] for c in geo_cols}})
    # well-conditioned prior in the old solve (any run): size prior with depth, or f-sensitive motion prior
    sens = r.pivot_table(index="qid", columns="run", values="sens_old", aggfunc="first").median(axis=1)
    meth = r.groupby("qid").method_old.agg(lambda s: (s == "3d_focal_from_prior").mean() >= 0.5)
    t["wellcond"] = meth.reindex(t.index).fillna(False) & (sens.reindex(t.index) >= 0.3)
    sub = pd.read_csv(P21, float_precision="round_trip").set_index("id").parsed_value
    t["p21"] = sub.reindex(t.index).astype(float)
    return t


def add_combos(t: pd.DataFrame, geo: list[str]) -> list[str]:
    cols = []
    for g in geo:
        t[f"gm_{g}"] = np.sqrt(t.dmed * t[g])
        t[f"gate_{g}"] = np.where(t.wellcond & t[g].notna(), t[g], t.dmed)
        t[f"gmgate_{g}"] = np.where(t.wellcond & t[g].notna(), t[f"gm_{g}"], t.dmed)
        t[f"gmp_{g}"] = np.sqrt(t.p21 * t[g])
        cols += [f"gm_{g}", f"gate_{g}", f"gmgate_{g}", f"gmp_{g}"]
    return cols


def kind_group(k: str) -> str:
    return {"size": "size", "speed": "speed", "acceleration": "accel"}.get(k, "distance")


def report(t: pd.DataFrame, labels: pd.Series, cols: list[str], title: str, skip_p21: bool = False) -> pd.DataFrame:
    x = t.loc[t.index.intersection(labels.index)].copy()
    x["gt"] = labels.reindex(x.index)
    x["kg"] = x.kind.map(kind_group)
    x["fovbin"] = pd.cut(x.fov_model, [0, 20, 60, 180], labels=["<20", "20-60", ">60"])
    use = [c for c in cols if not (skip_p21 and (c == "p21" or c.startswith("gmp_")))]
    S = pd.DataFrame({c: item_scores(x[c].fillna(x.dmed), x.gt) for c in use}, index=x.index)
    S["kg"], S["cat"], S["fovbin"], S["wellcond"] = x.kg, x.category, x.fovbin, x.wellcond
    S["video"] = x.video_id.str.replace("_segmented", "", regex=False)
    print(f"\n== {title}: {len(x)} rows, {S.video.nunique()} clips (geometry missing -> dmed) ==")
    for by in ("kg", "cat", "fovbin", "wellcond"):
        g = S.groupby(by, observed=True)[use].mean()
        g.insert(0, "n", S.groupby(by, observed=True).size())
        print(g.round(3).to_string())
    E = pd.DataFrame({c: np.abs(np.log(x[c].fillna(x.dmed) / x.gt)) for c in use}, index=x.index)
    E["kg"] = x.kg
    print("median |log(pred/gt)| (error budget):")
    print(E.groupby("kg")[use].median().round(3).to_string())
    allrow = S[use].mean()
    print("ALL n=%d  " % len(S) + "  ".join(f"{c} {v:.3f}" for c, v in allrow.items()))
    # clip-clustered spread of (new - dmed): bootstrap over clips
    rng = np.random.default_rng(0)
    vids = S.video.unique()
    for c in [c for c in use if c not in ("dmed", "p21")]:
        d = (S[c] - S.dmed).groupby(S.video).agg(["sum", "size"])
        bs = []
        for _ in range(2000):
            k = rng.choice(len(vids), len(vids))
            dd = d.iloc[k]
            bs.append(dd["sum"].sum() / dd["size"].sum())
        print(f"   {c:16s} - dmed: {allrow[c] - allrow['dmed']:+.3f}  (clip bootstrap 90%: "
              f"{np.percentile(bs, 5):+.3f} .. {np.percentile(bs, 95):+.3f})")
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("replay")
    a = ap.parse_args()
    t = table(a.replay)
    geo = [c for c in ("old", "cam05", "cam15", "fix", "snap05", "camZ05") if c in t.columns]
    cols = ["p21", "dmed"] + geo + add_combos(t, [g for g in geo if g != "old"] + ["old"])
    # (1) validation: identical test questions
    test = load_split("test")
    val = load_validation()
    key = lambda d: list(zip(d.video_id, d.question.map(pp.norm_question)))  # noqa: E731
    vmap = dict(zip(key(val), val.answer))
    lab_v = pd.Series([vmap.get(k, np.nan) for k in key(test)], index=test.qid).dropna()
    report(t, lab_v, cols, "VALIDATION (labels of identical test questions)")
    # (2) stated facts on test (the facts rule's applied rows), scored without the rule
    _, log = pp.apply_rules(t.dmed.reindex(test.qid).fillna(1.0), test, rules=("facts",), speed_guard=0)
    f = log[log.applied]
    lab_f = pd.Series(f.new.to_numpy(float), index=f.qid.astype(int))
    lab_f = lab_f[lab_f.index.isin(t.index)]
    print(f"\nstated facts on 3D sim rows: {len(lab_f)} ({lab_f.index.isin(lab_v.index).sum()} also validation)")
    report(t, lab_f, cols, "STATED FACTS (test, exact)", skip_p21=True)
    t.to_csv(Path(a.replay).with_name("table.csv"))


if __name__ == "__main__":
    main()
