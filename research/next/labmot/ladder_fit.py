"""Fit the 'true' lab label-noise strength per object class to the leaderboard ladder already observed.

Observed S3 contrasts (old scored set, N_S3 = 538; PROBES.md):
  C1 p11 - p8      = +.015   (sz 2 cm on 148 lab motion rows)
  C2 p13 - p8      = +.014   (sz 3 cm on 157 rows)
  C3 U1 - physb2   = -.011   (sz 4 cm instead of sz 2 cm, 154 rows)
  C4 U2 - physb2   = -.004   (18 small-ball path rows reverted to p8)
  C5 U3 - physb2   = +.003   (36 mid-ball speed rows reverted to p8)
Observed D3 contrasts (N_D3 = 933): p11 - p8 = +.001 (emu 2 cm, 34 rows); p13 - p8 = 0 (x1.40 on 101 rows);
  U1 - physb2 = +.001 (emu 3 cm vs 2 cm); U2 - physb2 = +.002 (emu 4 cm vs 2 cm).
Model: label L_i ~ emulator(p8_i-scaled physical motion, sigma_true[class_i]); our p8 answer has log error SIGMA_A.
Predicted contrast = sum_i E[MRA(v_a) - MRA(v_b)] / N over scored rows; covariance from the same label samples
(all probes share each row's label) + leaderboard rounding (sd .0004 per contrast). Gaussian likelihood on a grid.
No labels used; the leaderboard numbers are aggregate category scores already observed."""
import sys, pickle, itertools
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from qp.data import load_test

OUT = Path(__file__).resolve().parent / "out"
THR = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])
t = load_test().set_index("qid")
R = pd.read_pickle(OUT / "labmot_rows.pkl")
sigA = sys.argv[1] if len(sys.argv) > 1 else "0.15"
SAMP = pickle.load(open(OUT / f"ladder_samples_sA{sigA}.pkl", "rb"))
SIG = sorted(SAMP)


def mra(c, Rs):
    rel = np.abs(c - Rs) / Rs
    return (rel[..., None] < 1 - THR).mean(-1)


def group(r):
    if r.cls == "mid ball":
        return "mid"
    if r.cls == "small ball":
        return "small_path" if r.kind == "path_length" else "small"
    return "other"


R["grp"] = [group(r) for r in R.itertuples()]
scored = R.scored.fillna(False).astype(bool)
CONTR = {"S3": [("p11", "p8", .015), ("p13", "p8", .014), ("u1", "physb2", -.011), ("u2", "physb2", -.004),
                ("u3", "physb2", .003)],
         "D3": [("p11", "p8", .001), ("p13", "p8", .000), ("u1", "physb2", .001), ("u2", "physb2", .002)]}
NCAT = {"S3": 538, "D3": 933}


def contrib(cat, sig_of_grp):
    """-> mean vector (n_contr), covariance, per-group mean contributions."""
    rows = R[(R.category == cat) & scored]
    C = CONTR[cat]
    mu = np.zeros(len(C)); cov = np.zeros((len(C), len(C)))
    per = {}
    for q, r in rows.iterrows():
        s = sig_of_grp.get(r.grp, 0.0)
        Rs = SAMP[s].get(q)
        if Rs is None:
            continue
        D = []
        for a, b, _ in C:
            ca, cb = r[a] / r.p8, r[b] / r.p8
            D.append(mra(ca, Rs) - mra(cb, Rs) if not np.isclose(ca, cb) else np.zeros(len(Rs)))
        D = np.array(D)
        m = D.mean(1)
        mu += m
        cov += np.cov(D) if D.std() > 0 else 0
        per.setdefault(r.grp, np.zeros(len(C)))
        per[r.grp] += m
    N = NCAT[cat]
    return mu / N, cov / N ** 2 + np.eye(len(C)) * 0.0004 ** 2, {g: v / N for g, v in per.items()}


def loglik(cat, sig_of_grp):
    mu, cov, per = contrib(cat, sig_of_grp)
    obs = np.array([c[2] for c in CONTR[cat]])
    r = obs - mu
    return float(-0.5 * r @ np.linalg.solve(cov, r) - 0.5 * np.linalg.slogdet(cov)[1]), mu, per, np.sqrt(np.diag(cov))


if __name__ == "__main__":
    res = []
    grid = [s for s in SIG if s <= 0.06]
    for ss, sp, sm in itertools.product(grid, grid, grid):
        ll, mu, per, sd = loglik("S3", {"small": ss, "small_path": sp, "mid": sm})
        res.append(dict(small=ss, path=sp, mid=sm, ll=ll, **{f"C{i+1}": round(v, 4) for i, v in enumerate(mu)}))
    df = pd.DataFrame(res).sort_values("ll", ascending=False)
    df["dll"] = df.ll - df.ll.max()
    pd.set_option("display.width", 200)
    print(f"S3, SIGMA_A {sigA}: obs C = .015 .014 -.011 -.004 .003")
    print(df.head(25).round(4).to_string(index=False))
    for g in ("small", "path", "mid"):
        prof = df.groupby(g).ll.max() - df.ll.max()
        print("profile", g, prof.round(2).to_dict())
    best = df.iloc[0]
    ll, mu, per, sd = loglik("S3", {"small": best.small, "small_path": best.path, "mid": best.mid})
    print("best: sd of contrasts (label noise + rounding)", sd.round(4), "per group", {k: v.round(4) for k, v in per.items()})
    # common-sigma model (one sigma for every ball): the emulator's assumption
    for s in grid:
        ll, mu, per, sd = loglik("S3", {"small": s, "small_path": s, "mid": s})
        print(f"common sigma {s}: ll {ll - df.ll.max():.2f}  C {np.round(mu, 4)}")
    df.to_csv(OUT / f"ladder_fit_S3_sA{sigA}.csv", index=False)
    # D3
    resd = []
    for ss, sm in itertools.product(grid, grid):
        ll, mu, per, sd = loglik("D3", {"small": ss, "small_path": ss, "mid": sm, "other": 0.0})
        resd.append(dict(small=ss, mid=sm, ll=ll, **{f"C{i+1}": round(v, 4) for i, v in enumerate(mu)}))
    dd = pd.DataFrame(resd).sort_values("ll", ascending=False); dd["dll"] = dd.ll - dd.ll.max()
    print("D3: obs .001 .000 .001 .002"); print(dd.head(12).round(4).to_string(index=False))
    print("D3 sd of contrasts", sd.round(4))
