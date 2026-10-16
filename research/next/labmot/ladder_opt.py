"""Per-group optimal factors under the ladder-fitted noise model, and their expected gain over the current base
(trackA_probe_agent_sim2agent = C1 on lab rows), evaluated across the plausible sigma range (robustness).
Usage: ladder_opt.py <samples tag> (e.g. 0.15, 0.25, 0.15_k1.1)."""
import sys, pickle
from pathlib import Path
import numpy as np, pandas as pd
OUT = Path(__file__).resolve().parent / "out"
THR = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])
tag = sys.argv[1] if len(sys.argv) > 1 else "0.15"
SAMP = pickle.load(open(OUT / f"ladder_samples_sA{tag}.pkl", "rb"))
R = pd.read_pickle(OUT / "labmot_rows.pkl")
GRID = np.round(np.arange(0.8, 3.01, 0.01), 2)


def emra(c, Rs):
    rel = np.abs(np.asarray(c)[:, None] - Rs[None]) / Rs[None]
    return (rel[..., None] < 1 - THR).mean(-1).mean(-1)


def grp(r):
    if r.cls == "mid ball":
        return "mid_" + ("speed" if r.kind == "speed" else "disp")
    if r.cls == "small ball":
        return "small_" + {"speed": "speed", "path_length": "path", "displacement": "disp"}[r.kind]
    return "other"


R["grp"] = [grp(r) for r in R.itertuples()]
R = R[R.scored.fillna(False).astype(bool)]
N = {"S3": 538, "D3": 933}
rows = []
for q, r in R.iterrows():
    if q not in SAMP[0.02]:
        continue
    cb = r.best / r.p8
    d = dict(qid=q, cat=r.category, grp=r.grp, cb=cb)
    for s in (0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.05, 0.06):
        e = emra(GRID, SAMP[s][q])
        d[f"opt{s}"] = GRID[int(np.argmax(e))]
        d[f"E{s}"] = e          # expected MRA curve
        d[f"Eb{s}"] = float(emra([cb], SAMP[s][q])[0])
    rows.append(d)
D = pd.DataFrame(rows)


def gain(policy_sig, true_sig, sel):
    """expected item gain (sum) of using opt(policy_sig) vs the base, if the true sigma is true_sig."""
    g = 0.0
    for _, d in D[sel].iterrows():
        c = d[f"opt{policy_sig}"]
        e = d[f"E{true_sig}"][int(np.argmin(np.abs(GRID - c)))]
        g += e - d[f"Eb{true_sig}"]
    return g


pd.set_option("display.width", 220)
for cat in ("S3", "D3"):
    for g in sorted(D[D.cat == cat].grp.unique()):
        sel = (D.cat == cat) & (D.grp == g)
        n = int(sel.sum())
        print(f"\n{cat} {g} (scored modelled rows {n}); base factor median {D[sel].cb.median():.3f}")
        sigs = (0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05)
        print("  policy\\true " + " ".join(f"{s:>7}" for s in sigs) + "   [gain in category points x1000]")
        for ps in sigs:
            print(f"  opt@{ps:<6}  " + " ".join(f"{1000 * gain(ps, ts, sel) / N[cat]:7.2f}" for ts in sigs)
                  + f"   median factor {D[sel][f'opt{ps}'].median():.2f}")
D.drop(columns=[c for c in D.columns if c.startswith("E") and not c.startswith("Eb")]).to_pickle(OUT / f"ladder_opt_{tag}.pkl")
