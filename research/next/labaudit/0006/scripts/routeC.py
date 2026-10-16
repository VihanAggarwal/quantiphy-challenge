"""Route C: free-fall scale. Image y of the toy centre (yellow-mask centroid, f25-f30) fitted with
Y(t)=Y0+Vy t+g t^2/2 (g=9.8, camera nearly level) and Z(t)=s*Z_model(t), Z_model linear through the
label range at f24 (Z 1.341) and the table landing at f32 (Z 0.889). s=1 means the label ranges match physics."""
import numpy as np
f, cy = 711.0, 360.0
fr = np.array([25, 26, 27, 28, 29, 30]); y = np.array([141.3, 146.9, 161.4, 191.6, 224.9, 278.6])
for fps in (24.0, 25.0):
    t = (fr - 24) / fps
    Zm = 1.341 + (0.889 - 1.341) * (fr - 24) / 8.0
    for k in (6, 5):
        best = None
        for s in np.arange(0.5, 1.5, 0.001):
            A = np.c_[np.ones(k), t[:k]]
            b = (y[:k] - cy) * s * Zm[:k] / f - 4.9 * t[:k] ** 2
            c, *_ = np.linalg.lstsq(A, b, rcond=None)
            pred = cy + f * (A @ c + 4.9 * t[:k] ** 2) / (s * Zm[:k])
            rms = np.sqrt(np.mean((pred - y[:k]) ** 2))
            if best is None or rms < best[0]: best = (rms, s, c)
        rms, s, (Y0, Vy) = best
        print('fps %.0f frames %s: s=%.3f rms %.2f px apex %.3f s after f24  Z(f24)=%.3f Z(f28.8)=%.3f'
              % (fps, fr[:k], s, rms, -Vy / 9.8, s * 1.341, s * (1.341 - 0.452 * 4.8 / 8)))
