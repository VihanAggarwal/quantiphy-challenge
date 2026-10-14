"""Evaluate the pre-registered gates (RESULT.md) on held-out rows: validation labels of identical test questions and
exactly-known stated-fact rows on test. Labels are read only for scoring.

    .venv/bin/python research/gates/evaluate.py
Writes research/gates/out/gated.csv (per test row: base, gated value per gate, fire flags)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp import combine  # noqa: E402
from qp.mra import item_scores  # noqa: E402

OUT = ROOT / "research/gates/out"
N_CAT = {"S2": 553, "D2": 1137, "S3": 538, "D3": 933}
INSTAB_FLAGS = {"time_outside_track", "window_extrapolated", "gravity_from_target_track"}


def lrange(df: pd.DataFrame) -> pd.Series:
    L = np.log(df.where(df > 0))
    return L.max(axis=1) - L.min(axis=1)


def lmed(df: pd.DataFrame) -> pd.Series:
    L = np.log(df.where(df > 0))
    return np.exp(L.median(axis=1, skipna=True))


def flagset(s) -> set:
    return set(str(s).split(";")) if isinstance(s, str) and s else set()


def build() -> pd.DataFrame:
    b = pd.read_csv(OUT / "base.csv").set_index("qid")
    f = pd.read_csv(OUT / "features.csv").set_index("qid")
    x = b.join(f.drop(columns=[c for c in f.columns if c in b.columns]))
    runs = "abc"
    # ---------------- G3D: 3D non-lab
    D = x[[f"dir_{k}" for k in runs]]
    Gm = x[[f"geo_old_{k}" for k in runs]]
    x["dmed3"] = lmed(D)
    x["gmed3"] = lmed(Gm)
    x["n_dir"] = (D > 0).sum(axis=1)
    x["n_geo"] = (Gm > 0).sum(axis=1)
    x["R_dir"] = lrange(D)
    x["R_geo"] = lrange(Gm)
    wc = pd.Series(True, index=x.index)
    for k in runs:
        meth = x[f"method_old_{k}"] == "3d_focal_from_prior"
        sens = x[f"sens_old_{k}"] >= 0.3
        noassume = ~x[f"flags_old_{k}"].map(lambda s: bool(flagset(s) & combine.ASSUMED_FLAGS))
        fov = x[f"fov_old_{k}"].between(8, 105)
        wc &= meth & sens & noassume & fov
    x["wellcond3"] = wc
    is3 = x["sub"] == "3Dnl"
    base3 = x.dmed3
    c1 = (x.n_dir == 3) & (x.n_geo == 3)
    x["fire_G3D"] = is3 & c1 & wc & (x.R_geo <= 0.10) & (x.R_dir >= 0.20) & (x.u_geo <= 0.10)
    x["fire_G3D_no4"] = is3 & c1 & wc & (x.R_geo <= 0.10) & (x.u_geo <= 0.10)
    # ---------------- G2D: 2D rows routed to geometry (S2 static, D2 all)
    is2 = (x["sub"] == "2D") & ((x.category == "D2") | ((x.category == "S2") & (x.kind == "static")))
    geo2 = np.where(x.category == "D2", x.geo_ro, x.geo_a)
    x["geo2"] = geo2
    dir2 = x.dir_a
    valid2 = (x.geo2 > 0) & (dir2 > 0)
    # routed value as qp.combine (geometry unless > MAX_DISAGREE off or invalid)
    ratio = np.exp(np.abs(np.log(x.geo2 / dir2)))
    use_geo = valid2 & (ratio <= combine.MAX_DISAGREE)
    x["base2"] = np.where(use_geo, x.geo2, np.where(dir2 > 0, dir2, x.geo2))
    x["gd2"] = np.abs(np.log(x.geo2 / dir2))
    fl = x.geo_ro_flags.map(flagset) if "geo_ro_flags" in x else pd.Series([set()] * len(x), index=x.index)
    flag_hit = fl.map(lambda s: bool(s & INSTAB_FLAGS))
    x["fire_G2D"] = is2 & use_geo & (x.gd2 >= 0.10) & ((x.u_geo >= 0.15) | flag_hit)
    # ---------------- base / gated values per row
    x["base"] = np.where(is3, base3, np.where(is2, x.base2, np.nan))
    x["G3D"] = np.where(x.fire_G3D, np.sqrt(x.dmed3 * x.gmed3), x.base)
    x["G3D_full"] = np.where(x.fire_G3D, x.gmed3, x.base)
    x["G3D_no4"] = np.where(x.fire_G3D_no4, np.sqrt(x.dmed3 * x.gmed3), x.base)
    x["G2D"] = np.where(x.fire_G2D, np.sqrt(x.base2 * dir2), x.base)
    x["G2D_direct"] = np.where(x.fire_G2D, dir2, x.base)
    x["fire_G3D_full"] = x.fire_G3D
    x["fire_G2D_direct"] = x.fire_G2D
    return x


def evaluate(x: pd.DataFrame, gate: str, ev: pd.DataFrame, cand_rows: pd.Series, out: list) -> dict:
    fire = x[f"fire_{gate}"]
    e = ev[ev.qid.isin(x.index[fire])].copy()
    e["cat"] = x.category.reindex(e.qid).values
    e["clip"] = x.video_id.reindex(e.qid).str.replace("_segmented", "", regex=False).values
    e["b"] = item_scores(x.base.reindex(e.qid).to_numpy(float), e.label.to_numpy(float))
    e["g"] = item_scores(x[gate].reindex(e.qid).to_numpy(float), e.label.to_numpy(float))
    e["d"] = e.g - e.b
    n = len(e)
    res = dict(gate=gate, n_fire_test=int(fire.sum()), n_heldout=n)
    if n == 0:
        out.append(res)
        return res
    rng = np.random.default_rng(0)
    clips = e["clip"].unique()
    agg = e.groupby("clip").d.agg(["sum", "size"])
    bs = []
    for _ in range(4000):
        k = rng.choice(len(clips), len(clips))
        a = agg.iloc[k]
        bs.append(a["sum"].sum() / a["size"].sum())
    res.update(mean_base=e.b.mean(), mean_gated=e.g.mean(), delta=e.d.mean(), lo=np.percentile(bs, 5),
               hi=np.percentile(bs, 95), clips=len(clips), n_val=int((e.set == "val").sum()),
               n_facts=int((e.set == "facts").sum()))
    percat = e.groupby("cat").d.agg(["mean", "size"])
    res["per_cat"] = {c: (round(r["mean"], 4), int(r["size"])) for c, r in percat.iterrows()}
    cr = cand_rows & fire
    ncat = x[cr].category.value_counts().to_dict()
    res["cand_rows"] = ncat
    res["exp_overall"] = sum(ncat.get(c, 0) * res["delta"] / (4 * N_CAT[c]) for c in N_CAT)
    res["exp_overall_percat"] = sum(ncat.get(c, 0) * percat["mean"].get(c, 0.0) / (4 * N_CAT[c]) for c in N_CAT)
    res["by_set"] = e.groupby("set").d.agg(["mean", "size"]).round(4).to_dict("index")
    res["by_clip"] = e.groupby("clip").d.agg(["mean", "size"]).round(3).to_dict("index")
    out.append(res)
    return res


def main():
    x = build()
    ev = pd.read_csv(OUT / "evalsets.csv")
    ev = ev.sort_values("set", key=lambda s: s.map({"val": 0, "facts": 1})).drop_duplicates("qid")
    # candidate rows: combo3 still holds the raw routed value; not a validation-overlap (unscored) row
    close = lambda a, b: np.isclose(a, b, rtol=1e-6)  # noqa: E731
    raw3 = (x["sub"] == "3Dnl") & close(x.combo3, x.dmed3)
    raw2 = (x["sub"] == "2D") & (close(x.combo3, x.geo2) | close(x.combo3, x.geo_a) | close(x.combo3, x.geo_ro))
    val_ids = set(ev[ev.set == "val"].qid)
    scored = ~x.index.isin(val_ids)
    cand = (raw3 | raw2) & scored
    x["cand_eligible"] = cand
    out = []
    print("held-out rows:", ev.set.value_counts().to_dict())
    print("rows fired on test (all / eligible-scored):")
    for g in ("G3D", "G3D_no4", "G2D"):
        fire = x[f"fire_{g}"]
        print(f"  {g}: {int(fire.sum())} / {int((fire & cand).sum())}  by cat {x[fire & cand].category.value_counts().to_dict()}")
    for g in ("G3D", "G2D", "G3D_full", "G3D_no4", "G2D_direct"):
        r = evaluate(x, g, ev, cand, out)
        print(f"\n== {g} ==")
        for k, v in r.items():
            if k != "gate":
                print(f"  {k}: {round(v, 4) if isinstance(v, float) else v}")
        if g in ("G3D", "G2D"):
            ok_n = r.get("n_heldout", 0) >= 10
            pc = r.get("per_cat", {})
            no_loss = all(m >= 0 for m, s in pc.values() if s >= 3)
            passed = ok_n and r["delta"] >= 0.01 and r["lo"] > 0 and r["exp_overall"] >= 0.002 and no_loss
            verdict = "INCONCLUSIVE" if not ok_n else ("PASS" if passed else "FAIL")
            print(f"  KILL TEST {g}: {verdict} (n>=10 {ok_n}, delta>=.01 {r.get('delta', 0) >= .01}, "
                  f"CI lo>0 {r.get('lo', -1) > 0}, exp>=.002 {r.get('exp_overall', 0) >= .002}, no cat loss {no_loss})")
    x.to_csv(OUT / "gated.csv")


if __name__ == "__main__":
    main()
