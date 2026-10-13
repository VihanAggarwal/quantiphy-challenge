"""Bird family simulation_0088-0091 (same two birds, four cameras): pixel measurements from sky masks, scale anchored
on the family's STATED speeds (0088: big bird 17.98 m/s; 0090/0091: small bird 11 m/s). Test inputs only; the
validation labels of 0089 are read only in the report at the end (evaluation)."""
from __future__ import annotations
import cv2, numpy as np, pandas as pd, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_test, load_validation
from qp.mra import item_scores

FPS = 24.0
STATED = {"big": 17.98, "small": 11.0}   # family facts: 0088 prior (big), 0090/0091 priors (small)

def comps(vid):
    cap = cv2.VideoCapture(str(ROOT / "data/QuantiPhy" / f"{vid}.mp4")); out = []; i = 0
    while True:
        ok, img = cap.read()
        if not ok: break
        H, W = img.shape[:2]
        m = (img.astype(int).sum(axis=2) < 300).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
        for k in range(1, n):
            if st[k, 4] > 50:
                x, y, w, h, a = st[k]
                out.append(dict(frame=i, cx=cen[k][0], cy=cen[k][1], x0=x, x1=x + w, y0=y, y1=y + h, w=w, h=h, area=a,
                                trunc=bool(x <= 1 or y <= 1 or x + w >= W - 1 or y + h >= H - 1)))
        i += 1
    return pd.DataFrame(out), W, H

def assign(c):
    """Split components into two birds by linear x-motion: big bird = larger median horizontal extent."""
    c = c[~c.trunc].copy()
    # duplicated first frame (frame 0 == frame 1 in 86 sim clips): the motion starts at frame 1; drop frame 0
    f0, f1 = c[c.frame == 0], c[c.frame == 1]
    if len(f0) and len(f0) == len(f1) and np.allclose(np.sort(f0.cx.to_numpy()), np.sort(f1.cx.to_numpy()), atol=0.5):
        c = c[c.frame != 0]
    # seed: frames with two components; bird id by side, then follow constant velocity
    two = c.groupby("frame").filter(lambda g: len(g) == 2)
    f0 = two.frame.min()
    a, b = two[two.frame == f0].sort_values("cx").cx.to_numpy()
    tracks = {0: [], 1: []}
    for f, g in c.groupby("frame"):
        for r in g.itertuples():
            tracks[0 if len(tracks[0]) == 0 and len(tracks[1]) == 0 else 0].append(r) if False else None
    # simple: fit per-frame nearest to two lines estimated from frames with two comps
    rows = []
    for f, g in two.groupby("frame"):
        g = g.sort_values("cx"); rows.append((f, g.iloc[0], g.iloc[1]))
    # decide whether left/right swap over time (birds crossing in 0089: no, they diverge)
    L = pd.DataFrame([r[1] for r in rows]); R = pd.DataFrame([r[2] for r in rows])
    pl = np.polyfit(L.frame, L.cx, 1); pr = np.polyfit(R.frame, R.cx, 1)
    lab = []
    for r in c.itertuples():
        dl = abs(r.cx - np.polyval(pl, r.frame)); dr = abs(r.cx - np.polyval(pr, r.frame))
        lab.append(0 if dl < dr else 1)
    c["bird"] = lab
    out = {}
    for k, p in ((0, pl), (1, pr)):
        t = c[c.bird == k]
        p = np.polyfit(t.frame, t.cx, 1); py = np.polyfit(t.frame, t.cy, 1)
        out[k] = dict(vx=p[0], vy=py[0], x_at=lambda f, p=p: np.polyval(p, f), y_at=lambda f, py=py: np.polyval(py, f),
                      w_med=float(t.w.median()), h_max=float(t.h.max()), h_med=float(t.h.median()), n=len(t),
                      frames=(int(t.frame.min()), int(t.frame.max())))
    big = 0 if out[0]["w_med"] > out[1]["w_med"] else 1
    return {"big": out[big], "small": out[1 - big]}

def main():
    res = {}
    for v in ("simulation_0088", "simulation_0089", "simulation_0090", "simulation_0091"):
        c, W, H = comps(v)
        b = assign(c)
        spd = {k: np.hypot(b[k]["vx"], b[k]["vy"]) * FPS for k in b}       # px/s
        res[v] = (b, spd)
        print(f"{v}: px/frame big {spd['big']/FPS:.1f} small {spd['small']/FPS:.1f} ratio {spd['big']/spd['small']:.3f} "
              f"(stated {STATED['big']/STATED['small']:.3f}); body w big {b['big']['w_med']:.0f} small {b['small']['w_med']:.0f}; "
              f"h max big {b['big']['h_max']:.0f} small {b['small']['h_max']:.0f}; frames big {b['big']['frames']} small {b['small']['frames']}")
    # scale per clip from the stated speeds (both birds: geometric mean)
    rows = []
    for v, (b, spd) in res.items():
        s_big, s_small = STATED["big"] / spd["big"], STATED["small"] / spd["small"]
        sc = float(np.sqrt(s_big * s_small))
        def dist(t, v=v, b=b):
            f = t * FPS
            return float(np.hypot(b["big"]["x_at"](f) - b["small"]["x_at"](f), b["big"]["y_at"](f) - b["small"]["y_at"](f)))
        rows.append(dict(video_id=v, scale=sc, scale_big=s_big, scale_small=s_small,
                         len_big=b["big"]["w_med"] * sc, len_small=b["small"]["w_med"] * sc,
                         span_big=b["big"]["h_max"] * sc, span_small=b["small"]["h_max"] * sc,
                         v_big=spd["big"] * sc, v_small=spd["small"] * sc,
                         d02=dist(0.2) * sc, d03=dist(0.3) * sc, d05=dist(0.5) * sc))
    R = pd.DataFrame(rows).set_index("video_id")
    pd.set_option("display.width", 200)
    print(R.round(4).to_string())
    R.to_csv(Path(__file__).parent / "out_birdfam_measure.csv")
    return R

if __name__ == "__main__":
    main()
