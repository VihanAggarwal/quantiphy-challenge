"""Verifier: simulation_0253 box, truncation-free leading-edge track. The box enters through the top border and
slides down-right; its leading (down-slope) extreme is never cut by the border. Median-background difference mask,
projection of foreground pixels on the slope direction; per frame the 99.5th-percentile projection = leading edge.
Speeds in m/s at the pipeline scale (0.006863 m/px). Test inputs only."""
import cv2, numpy as np
ROOT = "/home/user/quantiphy-challenge"
SC = 0.006863171052500991
cap = cv2.VideoCapture(f"{ROOT}/data/QuantiPhy/simulation_0253.mp4"); fr = []
while True:
    ok, im = cap.read()
    if not ok: break
    fr.append(im.astype(np.int16))
bg = np.median(np.stack(fr), axis=0).astype(np.int16)
# slope direction from the pipeline track between 0.75 s and 1.75 s (box centre moves along the slope)
import pickle, sys
sys.path.insert(0, ROOT)
rp = pickle.load(open(f"{ROOT}/research/path85_s2sim/out/replay_s2.pkl", "rb"))
tg = [tr for tr in rp[855]["tracks"] if tr.role == "target"][0]
P = sorted([(ob.t, ob.point or [(ob.box[0] + ob.box[2]) / 2, (ob.box[1] + ob.box[3]) / 2]) for ob in tg.obs])
T = np.array([p[0] for p in P]); X = np.array([p[1] for p in P], float)
m = (T > 0.7)
d = np.polyfit(X[m, 0], X[m, 1], 1)[0]; u = np.array([1, d]) / np.hypot(1, d)
print("slope dir (image)", u.round(3))
lead, trail, area = [], [], []
for i, f in enumerate(fr):
    mk = (np.abs(f - bg).max(axis=2) > 30).astype(np.uint8)
    mk = cv2.morphologyEx(mk, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    ys, xs = np.nonzero(mk[:700])           # upper part of the frame (box region during 0-1.9 s)
    if len(xs) < 30:
        lead.append(np.nan); trail.append(np.nan); area.append(len(xs)); continue
    pr = xs * u[0] + ys * u[1]
    lead.append(np.percentile(pr, 99.5)); trail.append(np.percentile(pr, 0.5)); area.append(len(xs))
lead = np.array(lead); trail = np.array(trail)
fps = 24.0
for i in range(4, 26):
    print(f"f{i:2d} t={i/fps:.3f} area={area[i]:6d} lead={lead[i]:7.1f} trail={trail[i]:7.1f} extent={lead[i]-trail[i]:6.1f}"
          f" v_lead(back)={(lead[i]-lead[i-1])*fps*SC:6.3f} m/s")
tt = np.arange(len(lead)) / fps
for lo, hi in ((0.4, 1.0), (0.45, 0.8), (0.4, 1.5), (0.5, 1.85)):
    k = (tt >= lo) & (tt <= hi) & ~np.isnan(lead)
    c = np.polyfit(tt[k], lead[k] * SC, 2)
    print(f"lead fit {lo}-{hi}: a={2*c[0]:.3f} v(0.5)={2*c[0]*0.5+c[1]:.3f} v(1.0)={2*c[0]+c[1]:.3f}")
i = 12
print("one-frame backward diff of leading edge at f12:", round((lead[12] - lead[11]) * fps * SC, 3),
      " 2-frame:", round((lead[12] - lead[10]) * fps / 2 * SC, 3))
