"""Per-row label/answer samples R_i(sigma) from the lab label-noise emulator (research/labnoise/emulate.py, unchanged),
for a grid of 'true' ball depth-noise values sigma, on every S3/D3 lab motion row with a target track.
R = L / A where A = the probe-8 answer (the reference all ladder probes were built on) and L = simulated label, with
our own log error SIGMA_A (0.15, as in the emulator) folded in. Writes out/ladder_samples.pkl {sigma: {qid: R}}.
Test inputs only (cached Claude tracks + depth_info); no labels."""
import sys, pickle
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research/labnoise"))
from common import tracks
import emulate as EM
import labmodel as LM

OUT = Path(__file__).resolve().parent / "out"
R = pd.read_pickle(OUT / "labmot_rows.pkl")
d = tracks("test")
_orig = LM.best_factor
CAP = {}


def _bf(L, grid=np.round(np.arange(0.70, 2.51, 0.01), 2)):
    CAP.setdefault("R", np.asarray(L))
    return _orig(L, grid)


EM.LM.best_factor = _bf
sig_grid = [0.0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.05, 0.06, 0.08]
sigA = float(sys.argv[1]) if len(sys.argv) > 1 else 0.15
EM.SIGMA_A = sigA
K = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0   # physical / p8 median (our bias); samples rescaled to L / p8
out = {}
for s in sig_grid:
    params = dict(EM.PARAMS, sigma_zb=s, sigma_zL=0.0)
    out[s] = {}
    for q, r in R.iterrows():
        x = d.get(q)
        if x is None or r.kind == "acceleration":
            continue
        CAP.clear()
        m = EM.row_model(x, r.p8 * K, r.target_unit, params, n=2000)
        if m is not None and "R" in CAP:
            out[s][q] = CAP["R"].copy() * K
    print("sigma", s, "rows modelled", len(out[s]), flush=True)
pickle.dump(out, open(OUT / (f"ladder_samples_sA{sigA}" + (f"_k{K}" if K != 1.0 else "") + ".pkl"), "wb"))
