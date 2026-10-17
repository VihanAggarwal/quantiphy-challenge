"""3D ballistic fit of the toy centre on the 25 fps capture clock (g=9.8 along the camera 'down' with pitch from the table VP).
Centres: yellow-hull centroid for v24-v28 (face patch is inside the ring), background-difference silhouette for v29-v31.
Hypotheses for the capture index of each video frame; fits with gravity only (free scale) and with the stated ranges as soft constraints."""
import numpy as np
from lsq import least_squares
from common import F, CX, CY, ray
th = np.radians(1.17)
dn = np.array([0, np.cos(th), np.sin(th)])
cen = {24: (606.3, 142.5), 25: (601.0, 138.7), 26: (596.1, 144.0), 27: (590.9, 159.1), 28: (584.5, 188.0),
       29: (579.5, 223.9), 30: (570.4, 283.9), 31: (560.3, 368.1)}
stated = {25: 1.402, 30: 1.065}   # capture index -> range
def model(p, t):
    X0, V = p[:3], p[3:6]
    return X0[None] + V[None] * t[:, None] + 0.5 * 9.8 * dn[None] * t[:, None] ** 2
def fit(vids, capmap, use_ranges, sig_px=2.0, sig_R=0.03, verbose=True):
    c = np.array([capmap(v) for v in vids]); t = (c - 30) / 25.0
    uv = np.array([cen[v] for v in vids])
    def res(p):
        X = model(p, t)
        r = np.r_[(CX + F * X[:, 0] / X[:, 2] - uv[:, 0]) / sig_px, (CY + F * X[:, 1] / X[:, 2] - uv[:, 1]) / sig_px]
        if use_ranges:
            for cc, R in stated.items():
                Xc = model(p, np.array([(cc - 30) / 25.0]))[0]
                r = np.r_[r, (np.linalg.norm(Xc) - R) / sig_R]
        return r
    p0 = np.r_[1.0 * ray(*cen[29]) * 1.05, 0, 2, -1.5]
    s = least_squares(res, p0)
    p = s.x
    X = model(p, t)
    pred = np.c_[CX + F * X[:, 0] / X[:, 2], CY + F * X[:, 1] / X[:, 2]]
    rms = np.sqrt(np.mean((pred - uv) ** 2))
    R25 = np.linalg.norm(model(p, np.array([-0.2]))[0]); R30 = np.linalg.norm(model(p, np.array([0.0]))[0])
    V30 = p[3:6]; Vv = V30 @ dn
    tap = -Vv / 9.8
    out = dict(rms=rms, R25=R25, R30=R30, v30=np.linalg.norm(V30), V=V30, tapex=1.2 + tap,
               fd30=np.linalg.norm(model(p, np.array([0.04]))[0] - model(p, np.array([0.0]))[0]) * 25, p=p)
    if verbose:
        print('  frames v%d-v%d ranges=%s: rms %.2f px, R(c25) %.3f R(c30) %.3f, |V|(1.2s) %.2f m/s V=(%.2f,%.2f,%.2f), apex t=%.3f s, FD c30->c31 %.2f'
              % (vids[0], vids[-1], use_ranges, rms, R25, R30, out['v30'], *V30, out['tapex'], out['fd30']))
    return out, s
if __name__ == '__main__':
    maps = {'std (drop before v12, v36)': lambda v: v + 1,
            'drop before v31': lambda v: v + 1 + (v >= 31),
            'drop before v30': lambda v: v + 1 + (v >= 30),
            'drop before v29 (t=1.2 -> v28)': lambda v: v + 1 + (v >= 29),
            'drop before v28': lambda v: v + 1 + (v >= 28),
            'no drop before v31': lambda v: v}
    for name, m in maps.items():
        print(name)
        for vids in (list(range(25, 32)), list(range(26, 32)), list(range(26, 31)), list(range(27, 32))):
            for ur in (False, True):
                fit(vids, m, ur)
