"""Context only (no fix rests on it): label distribution for v(1.4) under the repo's lab label-noise model
(click jitter sigma_px, ToF range noise sigma_z per click), noise-free label-style speed 39.8 cm/s, lateral motion
at surface range 0.716 m. Prints the median label and the MRA-optimal constant answer."""
import numpy as np
rng = np.random.default_rng(0); N = 200000; F = 711.0
v = 0.398; r = 0.716; dt = 1 / 25
THR = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])
def mra(c, L): return ((np.abs(c - L) / L)[:, None] < 1 - THR).mean(-1).mean()
for sz in (0.0, 0.01, 0.015, 0.02):
    for spx in (2.0,):
        dx = v * dt + rng.normal(0, spx * r / F * np.sqrt(2), N)
        dy = rng.normal(0, spx * r / F * np.sqrt(2), N)
        dz = rng.normal(0, sz * np.sqrt(2), N) if sz else np.zeros(N)
        L = np.sqrt(dx**2 + dy**2 + dz**2) / dt * 100
        grid = np.arange(35, 80, 0.5); sc = [mra(c, L) for c in grid]
        print(f'sigma_z {sz*100:.1f} cm, px {spx}: median label {np.median(L):.1f} cm/s, mean {L.mean():.1f}; '
              f'MRA-opt answer {grid[int(np.argmax(sc))]:.1f} (score {max(sc):.3f}); score of 39.8 {mra(39.8, L):.3f}, of 60.165 {mra(60.165, L):.3f}')
