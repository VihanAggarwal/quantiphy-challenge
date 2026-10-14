"""Stage-2 gates (RESULT.md, STAGE 2 PRE-REGISTRATION) + signal diagnostics on held-out rows.

    .venv/bin/python research/gates/evaluate2.py
Writes research/gates/out/gated2.csv."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import INSTAB_FLAGS, N_CAT, OUT, build, evaluate, flagset  # noqa: E402
from qp.mra import item_scores  # noqa: E402


def main():
    x = build()
    ev = pd.read_csv(OUT / "evalsets.csv")
    ev = ev.sort_values("set", key=lambda s: s.map({"val": 0, "facts": 1})).drop_duplicates("qid")
    close = lambda a, b: np.isclose(a, b, rtol=1e-6)  # noqa: E731
    flag_hit = x.geo_ro_flags.map(flagset).map(lambda s: bool(s & INSTAB_FLAGS))
    # ---- G3D-2
    is3 = x["sub"] == "3Dnl"
    c1 = (x.n_dir == 3) & (x.n_geo == 3)
    x["fire_G3D2"] = is3 & c1 & x.wellcond3 & (x.R_geo <= 0.15) & (x.u_geo <= 0.15) & (x.R_dir >= x.R_geo)
    x["G3D2"] = np.where(x.fire_G3D2, np.sqrt(x.dmed3 * x.gmed3), x.base)
    # ---- G2D-2
    is2 = (x["sub"] == "2D") & ((x.category == "D2") | ((x.category == "S2") & (x.kind == "static")))
    use_geo2 = is2 & close(x.base2, x.geo2)
    x["fire_G2D2"] = use_geo2 & (x.gd2 >= 0.10) & ((x.u_geo >= 0.05) | flag_hit)
    x["G2D2"] = np.where(x.fire_G2D2, np.sqrt(x.base2 * x.dir_a), x.base)
    # ---- GLAB-2 (S3 lab static, routed to geometry in run a)
    islab = (x["sub"] == "lab") & (x.category == "S3") & (x.kind == "static")
    geo_routed = x.meth_a.fillna("").str.startswith("geometry") & (x.dir_a > 0) & (x.geo_a > 0)
    x.loc[islab, "base"] = x.par_a[islab]
    gdl = np.abs(np.log(x.geo_a / x.dir_a))
    x["fire_GLAB2"] = islab & geo_routed & (gdl >= 0.10) & ((x.u_geo >= 0.15) | flag_hit)
    x["GLAB2"] = np.where(x.fire_GLAB2, np.sqrt(x.par_a * x.dir_a), x.base)
    # candidate eligibility (raw routed value still in combo3; scored rows only)
    val_ids = set(ev[ev.set == "val"].qid)
    scored = ~x.index.isin(val_ids)
    raw3 = is3 & close(x.combo3, x.dmed3)
    raw2 = is2 & (close(x.combo3, x.geo2) | close(x.combo3, x.geo_a) | close(x.combo3, x.geo_ro))
    rawl = islab & close(x.combo3, x.par_a)
    cand = (raw3 | raw2 | rawl) & scored
    out = []
    for g in ("G3D2", "G2D2", "GLAB2"):
        fire = x[f"fire_{g}"]
        print(f"\n== {g}: fires {int(fire.sum())} test rows, {int((fire & cand).sum())} eligible scored "
              f"{x[fire & cand].category.value_counts().to_dict()}")
        r = evaluate(x, g, ev, cand, out)
        for k, v in r.items():
            if k != "gate":
                print(f"  {k}: {round(v, 4) if isinstance(v, float) else v}")
        ok_n = r.get("n_heldout", 0) >= 10
        pc = r.get("per_cat", {})
        no_loss = all(m >= 0 for m, s in pc.values() if s >= 3)
        passed = ok_n and r["delta"] >= 0.01 and r["lo"] > 0 and r["exp_overall"] >= 0.002 and no_loss
        verdict = "INCONCLUSIVE" if not ok_n else ("PASS" if passed else "FAIL")
        print(f"  KILL TEST {g}: {verdict}")
    x.to_csv(OUT / "gated2.csv")

    # ---------------- diagnostics: does any signal carry routing information?
    e = ev.set_index("qid")
    print("\n================ DIAGNOSTICS (held-out rows; mean item delta vs routed default) ================")
    h3 = x.loc[x.index.intersection(e.index)]
    h3 = h3[(h3["sub"] == "3Dnl") & (h3.n_dir >= 1) & h3.dmed3.notna()].copy()
    lab3 = e.label.reindex(h3.index).to_numpy(float)
    s_d = item_scores(h3.dmed3.to_numpy(float), lab3)
    gm = np.sqrt(h3.dmed3 * h3.gmed3).fillna(h3.dmed3)
    s_gm = item_scores(gm.to_numpy(float), lab3)
    s_g = item_scores(h3.gmed3.fillna(h3.dmed3).to_numpy(float), lab3)
    h3["d_gm"], h3["d_geo"] = s_gm - s_d, s_g - s_d
    h3["gd3"] = np.abs(np.log(h3.gmed3 / h3.dmed3))
    print(f"3D non-lab held-out rows: {len(h3)}  direct {s_d.mean():.3f}  gm {s_gm.mean():.3f}  geometry {s_g.mean():.3f}")
    for sig in ("R_dir", "R_geo", "u_geo", "gd3"):
        q = pd.qcut(h3[sig].rank(method="first"), 3, labels=["low", "mid", "high"])
        t = h3.groupby(q, observed=True).agg(n=("d_gm", "size"), lo=(sig, "min"), hi=(sig, "max"),
                                             d_gm=("d_gm", "mean"), d_geo=("d_geo", "mean"))
        print(f"-- by {sig} tercile\n{t.round(3).to_string()}")
    t = h3.groupby("wellcond3").agg(n=("d_gm", "size"), d_gm=("d_gm", "mean"), d_geo=("d_geo", "mean"))
    print(f"-- by wellcond (all 3 runs)\n{t.round(3).to_string()}")
    h2 = x.loc[x.index.intersection(e.index)]
    h2 = h2[(h2["sub"] == "2D") & (h2.geo2 > 0) & (h2.dir_a > 0)].copy()
    lab2 = e.label.reindex(h2.index).to_numpy(float)
    s_b = item_scores(h2.geo2.to_numpy(float), lab2)
    h2["d_dir"] = item_scores(h2.dir_a.to_numpy(float), lab2) - s_b
    h2["d_gm"] = item_scores(np.sqrt(h2.geo2 * h2.dir_a).to_numpy(float), lab2) - s_b
    print(f"\n2D held-out rows: {len(h2)}  geometry {s_b.mean():.3f}  (all 2D kinds; S2 motion/internet are routed elsewhere in combo3)")
    h2["gdbin"] = pd.cut(h2.gd2, [-1, 0.05, 0.10, 0.25, 99], labels=["<.05", ".05-.10", ".10-.25", ">.25"])
    h2["ubin"] = pd.cut(h2.u_geo, [-1, 0.01, 0.03, 0.05, 99], labels=["<.01", ".01-.03", ".03-.05", ">.05"])
    for by in ("gdbin", "ubin"):
        t = h2.groupby(by, observed=True).agg(n=("d_dir", "size"), d_dir=("d_dir", "mean"), d_gm=("d_gm", "mean"))
        print(f"-- by {by}\n{t.round(3).to_string()}")


if __name__ == "__main__":
    main()
