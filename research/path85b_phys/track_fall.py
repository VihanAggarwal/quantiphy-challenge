"""Pixel tracks of the falling object in the simulation free-fall families (test videos only), by background
subtraction (per-pixel median over the clip), largest moving blob per frame. Fits y(t) = y0 + 0.5*A*(t - t0)^2
(release time t0 = vertex of the parabola) over the frames before impact. Scale-free: t0 does not depend on f or depth.

    .venv/bin/python research/path85b_phys/track_fall.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CLIPS = {  # clip: (last time used for the fit, s) -- before impact (prior says 'before 0.5s' / 'before 0.45s')
    "simulation_0202": 0.42, "simulation_0203": 0.42, "simulation_0204": 0.42, "simulation_0205": 0.42,
    "simulation_0206": 0.40, "simulation_0207": 0.40, "simulation_0208": 0.40, "simulation_0209": 0.40,
    "simulation_0198": 0.25, "simulation_0199": 0.25, "simulation_0200": 0.25, "simulation_0201": 0.25,
}


def frames(v):
    cap = cv2.VideoCapture(str(ROOT / f"data/QuantiPhy/{v}.mp4"))
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32))
    return np.array(out), fps


def track(v, tmax):
    F, fps = frames(v)
    s = 1080.0 / max(F.shape[1:])
    if s < 1:
        F = np.array([cv2.resize(f, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) for f in F])
    else:
        s = 1.0
    bg = np.median(F, axis=0)
    rows = []
    prev = None
    for i, f in enumerate(F):
        t = i / fps
        if t > tmax + 1e-9:
            break
        d = np.abs(f - bg)
        m = (cv2.GaussianBlur(d, (5, 5), 0) > 18).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        if n <= 1:
            rows.append(dict(i=i, t=t, x=np.nan, y=np.nan, area=0))
            continue
        cand = [(st[k, cv2.CC_STAT_AREA], k) for k in range(1, n) if st[k, cv2.CC_STAT_AREA] >= 15]
        if not cand:
            rows.append(dict(i=i, t=t, x=np.nan, y=np.nan, area=0))
            continue
        if prev is not None:   # nearest blob below / near the previous position among the 3 largest
            cand = sorted(cand, reverse=True)[:3]
            k = min(cand, key=lambda c: np.hypot(*(cen[c[1]] - prev)))[1]
        else:
            k = max(cand)[1]
        prev = cen[k]
        rows.append(dict(i=i, t=t, x=cen[k][0] / s, y=cen[k][1] / s, area=int(st[k, cv2.CC_STAT_AREA])))
    return pd.DataFrame(rows), fps


def fit_t0(tr):
    """grid over t0, linear LSQ for (y0, A) of y = y0 + 0.5 A max(t - t0, 0)^2; returns t0, A, rms."""
    tr = tr.dropna()
    t, y = tr.t.to_numpy(), tr.y.to_numpy()
    best = None
    for t0 in np.linspace(-0.15, 0.10, 1001):
        X = np.c_[np.ones_like(t), 0.5 * np.maximum(t - t0, 0) ** 2]
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = np.sqrt(np.mean((X @ c - y) ** 2))
        if best is None or r < best[2]:
            best = (t0, c[1], r)
    return best


def main():
    res = []
    for v, tmax in CLIPS.items():
        tr, fps = track(v, tmax)
        t0, A, rms = fit_t0(tr)
        # also: drop the first frame (object possibly entering at the frame edge)
        t0b, Ab, rmsb = fit_t0(tr.iloc[1:])
        res.append(dict(video_id=v, fps=fps, n=int(tr.y.notna().sum()), t0=t0, A_px=A, rms=rms, t0_drop1=t0b))
        print(v, fps, tr.round(1).to_dict("list")["y"])
    R = pd.DataFrame(res)
    print(R.round(4).to_string())
    R.to_csv(ROOT / "research/path85b_phys/fall_t0.csv", index=False)


if __name__ == "__main__":
    main()
