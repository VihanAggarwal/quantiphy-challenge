"""Event screen for 2D-simulation speed / acceleration questions at a time t (test inputs only, no API).
Per clip: median background (fixed Blender camera) -> per-frame foreground components; the target object is the
component under the annotator's target track (out/replay_s2.pkl), linked frame to frame. Per question: the label
operator on that per-frame track (Blender: backward difference at frame round(t*fps)) vs the pipeline geometry's
smoothed px speed (debug target_px).   python evtrack.py [video_id ...]  -> out/evtrack.csv"""
from __future__ import annotations
import pickle, re, sys
from pathlib import Path
import cv2, numpy as np, pandas as pd
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp.data import load_test

MAXW = 1280

def load_frames(vid):
    cap = cv2.VideoCapture(str(ROOT / "data/QuantiPhy" / f"{vid}.mp4")); fr = []
    while True:
        ok, img = cap.read()
        if not ok: break
        h, w = img.shape[:2]; s = min(1.0, MAXW / w)
        fr.append(cv2.resize(img, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else img)
    return fr, s

def components(fr, thr=25):
    bg = np.median(np.stack(fr), axis=0).astype(np.int16)
    out = []
    for img in fr:
        d = np.abs(img.astype(np.int16) - bg).max(axis=2)
        m = (d > thr).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
        out.append([dict(x0=st[k, 0], y0=st[k, 1], x1=st[k, 0] + st[k, 2], y1=st[k, 1] + st[k, 3], a=st[k, 4],
                         cx=cen[k][0], cy=cen[k][1]) for k in range(1, n) if st[k, 4] >= 15])
    return out

def follow(comps, anchors, s, nfr):
    """anchors: {frame: (x, y) in original px}. Returns per-frame bbox-centre track (scaled px) or NaN."""
    tr = np.full((nfr, 4), np.nan)  # cx, cy (bbox centre), w, h
    def pick(f, x, y, prev=None):
        best, bd = None, 1e9
        for c in comps[f]:
            inside = c["x0"] - 3 <= x <= c["x1"] + 3 and c["y0"] - 3 <= y <= c["y1"] + 3
            bx, by = (c["x0"] + c["x1"]) / 2, (c["y0"] + c["y1"]) / 2
            dd = np.hypot(bx - x, by - y) - (50 if inside else 0)
            if prev is not None:
                dd += 0.5 * abs(np.log((c["a"] + 1) / (prev + 1))) * 20
            if dd < bd: best, bd = c, dd
        return best, bd
    for f, (x, y) in anchors.items():
        if 0 <= f < nfr:
            c, d = pick(f, x * s, y * s)
            if c is not None and d < 40:
                tr[f] = [(c["x0"] + c["x1"]) / 2, (c["y0"] + c["y1"]) / 2, c["x1"] - c["x0"], c["y1"] - c["y0"]]
    # fill gaps by linking from nearest anchored frame (forward and backward)
    for direction in (1, -1):
        rng = range(nfr) if direction == 1 else range(nfr - 1, -1, -1)
        last = None
        for f in rng:
            if not np.isnan(tr[f, 0]):
                last = tr[f].copy(); continue
            if last is None: continue
            c, d = pick(f, last[0], last[1])
            if c is not None and d < max(25, 0.6 * max(last[2], last[3])) and abs(np.log((c["x1"] - c["x0"] + 1) / (last[2] + 1))) < 0.4:
                tr[f] = [(c["x0"] + c["x1"]) / 2, (c["y0"] + c["y1"]) / 2, c["x1"] - c["x0"], c["y1"] - c["y0"]]
                last = tr[f].copy()
    return tr / np.array([s, s, s, s])

def main():
    rp = pickle.load(open(HERE / "out/replay_s2.pkl", "rb"))
    t = load_test().set_index("qid")
    sel = [q for q, o in rp.items() if o["spec"].target.kind in ("speed", "acceleration") and o["spec"].target.time is not None
           and t.category[q] in ("S2", "D2")]
    vids = sorted({rp[q]["video_id"] for q in sel})
    if len(sys.argv) > 1: vids = [v for v in vids if v in sys.argv[1:]]
    rows = []
    for v in vids:
        fr, s = load_frames(v); comps = components(fr); nfr = len(fr)
        for q in [q for q in sel if rp[q]["video_id"] == v]:
            o = rp[q]; fps = o["fps"]; tq = o["spec"].target.time
            tg = [tr for tr in o["tracks"] if tr.role == "target"]
            if not tg: continue
            anchors = {}
            for ob in tg[0].obs:
                p = ob.point or ([(ob.box[0] + ob.box[2]) / 2, (ob.box[1] + ob.box[3]) / 2] if ob.box else None)
                if p is not None: anchors[int(round(ob.t * fps))] = p
            tr = follow(comps, anchors, s, nfr)
            i = int(round(tq * fps))
            if i < 3 or i >= nfr - 2: 
                rows.append(dict(qid=q, video_id=v, ok=False)); continue
            sp = np.r_[np.nan, np.hypot(np.diff(tr[:, 0]), np.diff(tr[:, 1]))] * fps   # px/s backward
            def lin(a, b):
                j = np.arange(max(0, a), min(nfr, b + 1)); j = j[~np.isnan(tr[j, 0])]
                if len(j) < 3: return np.nan
                return float(np.hypot(np.polyfit(j / fps, tr[j, 0], 1)[0], np.polyfit(j / fps, tr[j, 1], 1)[0]))
            w = int(round(0.25 * fps))
            pre = np.nanmedian(sp[max(1, i - w):i]) if i > 1 else np.nan
            post = np.nanmedian(sp[i + 1:i + 1 + w])
            rows.append(dict(qid=q, video_id=v, cat=t.category[q], kind=o["spec"].target.kind, t=tq, fps=fps, ok=True,
                             geo=o["value"], scale=o["debug"].get("scale_m_per_px"), geo_px=o["debug"].get("target_px"),
                             pf=sp[i], b2=sp[i - 1:i + 1].mean() if not np.isnan(sp[i - 1:i + 1]).any() else np.nan,
                             back3=lin(i - 3, i), cen5=lin(i - 2, i + 2), pre=pre, post=post,
                             nvalid=int((~np.isnan(tr[max(0, i - w):i + w + 1, 0])).sum()), size=np.nanmedian(tr[:, 2:4].max(axis=1)),
                             acc_pf=(sp[i] - sp[i - 1]) * fps if i > 1 else np.nan))
        print(v, "done", flush=True)
    pd.DataFrame(rows).to_csv(HERE / "out/evtrack.csv", index=False)

if __name__ == "__main__":
    main()
