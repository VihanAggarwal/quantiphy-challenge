"""Run the constant-g lab fits (labfit.py) on the D3 lab gravity events and the stated-speed kill-test clips."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import labfit as L

# event: (clip, dense path index, first frame, last frame, ranges [(capture time, m)])
EVENTS = {
    "0006_toy": ("captured_0006", 0, 25, 31, [(1.0, 1.402), (1.2, 1.065)]),
    "0008_fall": ("captured_0008", 1, 22, 29, [(1.0, 1.401), (1.2, 1.564)]),
    "0008_rebound": ("captured_0008", 0, 32, 41, [(1.52, 1.5225)]),
    "0009_rebound": ("captured_0009", 0, 39, 46, [(1.8, 1.5835), (1.92, 1.5795)]),
    "0016_ball": ("captured_0016", 1, 28, 36, [(1.5, 1.402)]),
    "0020_jar": ("captured_0020", 2, 14, 22, [(0.6, 1.9735)]),
    "0020_toy": ("captured_0020", 1, 14, 22, [(0.6, 2.63)]),
    "0041_kill": ("captured_0041", 0, 34, 38, [(1.5, 2.544), (1.6, 2.074)]),
}

if __name__ == "__main__":
    out = {}
    for name, (v, k, f0, f1, rng) in EVENTS.items():
        path = L.dense_paths(v)[k]
        tau, uv, fr = L.segment(path, f0, f1)
        fg = L.Fit(tau, uv, rng)
        ff = L.Fit(tau, uv, rng, free_g=True)
        G = ff.G()
        print(f"== {name}: frames {fr[0]}-{fr[-1]} (n={len(fr)}), tau {tau[0]:.2f}-{tau[-1]:.2f}")
        print(f"   g fixed: rms {fg.rms_px:.1f} px, range err {np.round(fg.range_err, 3)}, G dir {np.round(fg.G()/9.8, 2)}")
        print(f"   g free : |G| = {np.linalg.norm(G):.2f}, rms {ff.rms_px:.1f} px, range err {np.round(ff.range_err, 3)}")
        out[name] = (fg, ff)
        for t in np.arange(round(tau[0], 2), tau[-1] + 1e-6, 0.04):
            print(f"     t={t:.2f}  fd {fg.speed_fd(t):.3f} / free {ff.speed_fd(t):.3f}   inst {fg.speed_inst(t):.3f}  |P| {np.linalg.norm(fg.pos(np.array([t]))[0]):.3f}")
