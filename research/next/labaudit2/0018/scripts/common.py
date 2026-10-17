import numpy as np, cv2
D = '/home/user/quantiphy-challenge/data/QuantiPhy/'
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0018/'
F = 711.0; CX = 640.0; CY = 360.0
_cache = {}
def frames(r=''):
    """All 49 frames of captured_0018{r} (BGR uint8), cached in memory only."""
    if r not in _cache:
        cap = cv2.VideoCapture(D + f'captured_0018{r}.mp4'); fr = []
        while True:
            ok, im = cap.read()
            if not ok: break
            fr.append(im)
        _cache[r] = np.array(fr)
    return _cache[r]
def ray(u, v, f=F):
    return np.array([(u - CX) / f, (v - CY) / f, 1.0])
def bp_range(u, v, rng, f=F):
    d = ray(u, v, f); return rng * d / np.linalg.norm(d)
def bp_z(u, v, z, f=F):
    return z * ray(u, v, f)
def z_from_range(u, v, rng, f=F):
    return rng / np.linalg.norm(ray(u, v, f))
def range_from_z(u, v, z, f=F):
    return z * np.linalg.norm(ray(u, v, f))
