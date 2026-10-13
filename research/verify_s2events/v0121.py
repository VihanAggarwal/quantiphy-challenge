"""Verifier: independent per-frame check of simulation_0121 (+segmented) left ball around the 0.93 s collision.
Test inputs only. Prints left-ball edge / centre per frame from (a) the segmented twin (white background threshold)
and (b) the original clip (median-background difference), then one-frame backward-difference speeds in m/s at the
pipeline scale."""
import sys
import cv2, numpy as np
ROOT = "/home/user/quantiphy-challenge"
SC = 0.012355324074074069  # pipeline m/px (replay debug)

def frames(v):
    cap = cv2.VideoCapture(f"{ROOT}/data/QuantiPhy/{v}.mp4"); out = []
    while True:
        ok, im = cap.read()
        if not ok: break
        out.append(im)
    return out

def leftmost_profile(masks):
    """per frame: leftmost foreground column within the ball row band, and the column-run of the leftmost blob"""
    res = []
    for m in masks:
        band = m[690:880]  # ball row band (balls at y ~700-880)
        cols = np.nonzero(band.any(axis=0))[0]
        if len(cols) == 0:
            res.append((np.nan, np.nan)); continue
        x0 = cols[0]
        # leftmost contiguous run of columns
        run = [x0]
        for c in cols[1:]:
            if c - run[-1] <= 2: run.append(c)
            else: break
        res.append((x0, run[-1]))
    return np.array(res, float)

for v, mode in (("simulation_0121_segmented", "white"), ("simulation_0121", "bg")):
    fr = frames(v)
    if mode == "white":
        masks = [(f.min(axis=2) < 235) for f in fr]
    else:
        bg = np.median(np.stack(fr[::2]), axis=0).astype(np.int16)
        masks = [(np.abs(f.astype(np.int16) - bg).max(axis=2) > 25) for f in fr]
    p = leftmost_profile(masks)
    print("==", v, "frames", len(fr), "size", fr[0].shape)
    for i in range(18, 40):
        print(f"  f{i:2d} t={i/30:.3f} left_x0={p[i,0]:.0f} run_end={p[i,1]:.0f}")
    x0 = p[:, 0]
    for i in (29, 30, 31):
        print(f"  backward diff of left edge at frame {i}: {(x0[i]-x0[i-1])*30*SC:.3f} m/s;"
              f" 3-frame mean around 30: {np.mean(np.abs(np.diff(x0[28:34])))*30*SC:.3f}")
