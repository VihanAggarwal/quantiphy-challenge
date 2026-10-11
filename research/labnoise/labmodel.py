"""Label-process emulator for QuantiPhy lab motion labels (paper App. D.2): an annotator clicks the object centre
(pixel noise sigma_px, in 1280-px units), reads the depth at that pixel from the ToF map (noise sigma_z, m, by
object class), back-projects with the fixed camera (f = 722 px), and differences consecutive 25 fps frames:
speed = |P_{k+1} - P_k| * 25 (forward difference), path length = sum of such segments, displacement = |P_b - P_a|.
Depth is treated as range (as qp.geometry does); with Z instead the result changes by < 1% at these angles."""
import numpy as np

F = 722.0
FPS = 25.0


def _click(P, sigma_px, sigma_z, rng, n=None):
    """Noisy re-measurement of camera-frame points P (..., 3) -> (n, ..., 3); with n None, P already carries the
    sample axis first (one noise draw per point)."""
    P = np.asarray(P, float)
    if n is not None:
        P = np.broadcast_to(P, (n,) + P.shape)
    r = np.linalg.norm(P, axis=-1)
    uv = P[..., :2] / P[..., 2:3] * F
    uvn = uv + rng.normal(0.0, sigma_px, uv.shape)
    rn = r + rng.normal(0.0, sigma_z, r.shape)
    ray = np.concatenate([uvn / F, np.ones(uvn.shape[:-1] + (1,))], axis=-1)
    return ray / np.linalg.norm(ray, axis=-1, keepdims=True) * rn[..., None]


def speed_labels(p, v, sigma_px, sigma_z, n=4000, seed=0):
    """Forward-difference speed labels for an object at p (m, camera frame) moving with velocity v (m/s)."""
    rng = np.random.default_rng(seed)
    p = np.asarray(p, float); v = np.asarray(v, float)
    P = np.stack([p, p + v / FPS])
    Q = _click(P, sigma_px, sigma_z, rng, n)
    return np.linalg.norm(Q[:, 1] - Q[:, 0], axis=-1) * FPS


def path_labels(Pseq, sigma_px, sigma_z, n=2000, seed=0):
    """Path-length labels: sum of |P_{k+1} - P_k| over clicked 25 fps frames Pseq (m, shape (K, 3))."""
    rng = np.random.default_rng(seed)
    Q = _click(np.asarray(Pseq, float), sigma_px, sigma_z, rng, n)
    return np.linalg.norm(np.diff(Q, axis=1), axis=-1).sum(axis=1)


def speed_labels_s(p, V, sigma_px, sigma_z, seed=0):
    """Per-sample velocities V (n, 3) at position p -> n forward-difference speed labels."""
    rng = np.random.default_rng(seed)
    V = np.asarray(V, float); p = np.broadcast_to(np.asarray(p, float), V.shape)
    Q = _click(np.stack([p, p + V / FPS], axis=1), sigma_px, sigma_z, rng)
    return np.linalg.norm(Q[:, 1] - Q[:, 0], axis=-1) * FPS


def path_labels_s(Pseqs, sigma_px, sigma_z, seed=0):
    """Per-sample paths Pseqs (n, K, 3) -> n path-length labels."""
    rng = np.random.default_rng(seed)
    Q = _click(Pseqs, sigma_px, sigma_z, rng)
    return np.linalg.norm(np.diff(Q, axis=1), axis=-1).sum(axis=1)


def disp_labels(pa, pb, sigma_px, sigma_z, n=4000, seed=0):
    rng = np.random.default_rng(seed)
    Q = _click(np.stack([pa, pb]), sigma_px, sigma_z, rng, n)
    return np.linalg.norm(Q[:, 1] - Q[:, 0], axis=-1)


def geom(speed, sin_psi, depth, x_off=0.0):
    """Synthetic p, v with the given speed (m/s), lateral fraction and range (object at horizontal offset x_off m)."""
    p = np.array([x_off, 0.0, np.sqrt(max(depth ** 2 - x_off ** 2, 1e-6))])
    r = p / np.linalg.norm(p)
    lat = np.cross(r, [0.0, 1.0, 0.0]); lat /= np.linalg.norm(lat)
    c = np.sqrt(max(1 - sin_psi ** 2, 0.0))
    return p, speed * (sin_psi * lat + c * (-r))


THR = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])


def mra(pred, gt):
    rel = np.abs(pred - gt) / gt
    return (rel[..., None] < 1 - THR).mean(-1)


def best_factor(labels_over_ours, grid=np.round(np.arange(0.70, 2.51, 0.01), 2)):
    """MRA-optimal multiplier c for our answer A given samples of label/A (already including our own error)."""
    L = np.asarray(labels_over_ours)
    sc = np.array([mra(c, L).mean() for c in grid])
    i = int(np.argmax(sc))
    return float(grid[i]), float(sc[i]), float(sc[np.argmin(np.abs(grid - 1.0))])
