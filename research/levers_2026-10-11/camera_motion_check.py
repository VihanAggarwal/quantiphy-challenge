"""Camera-motion check for internet clips: background affine per frame pair (LK flow outside Claude's boxes, RANSAC),
chained between the frames of the prior track. Reports raw vs background-stabilised prior pixel path length."""
import json, sys, math
from pathlib import Path
import cv2, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/quantiphy-challenge")
from qp.data import load_split

R = Path("/home/user/quantiphy-challenge/runs")
RUNS = {"test": R / "test_v1_high_854/test/records", "val_hires": R / "val_hr_v1_high/val_hires/records"}

def tracks_of(rec):
    out = []
    for q in rec["parsed"]["questions"]:
        for t in q.get("tracks") or []:
            out.append((q["qid"], t["role"], t["object"], t["obs"]))
    return out

def interp_boxes(all_tracks, n):
    """per frame list of boxes (in sent pixels) from every track, linearly interpolated, dilated 15%."""
    per = [[] for _ in range(n)]
    for _, _, _, obs in all_tracks:
        ob = sorted([(o["frame"], o["box"]) for o in obs if o.get("box")], key=lambda x: x[0])
        if not ob: continue
        fr = np.array([f for f, _ in ob]); bx = np.array([b for _, b in ob], float)
        for k in range(n):
            if len(ob) == 1: b = bx[0]
            else:
                b = np.array([np.interp(k, fr, bx[:, c]) for c in range(4)])
            w, h = b[2] - b[0], b[3] - b[1]
            per[k].append([b[0] - .15 * w - 8, b[1] - .15 * h - 8, b[2] + .15 * w + 8, b[3] + .15 * h + 8])
    return per

def run(split, vid, path, rec):
    scale = rec["meta"].get("scale") or 1.0
    cap = cv2.VideoCapture(str(path)); frames = []
    while True:
        ok, f = cap.read()
        if not ok: break
        if scale != 1.0: f = cv2.resize(f, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
    n = len(frames)
    if n < 3: return None
    trs = tracks_of(rec)
    boxes = interp_boxes(trs, n)
    H, W = frames[0].shape
    A = [np.eye(3)]   # A[k]: maps frame k coords -> frame 0 coords (background)
    inl = []
    for k in range(1, n):
        m = np.full((H, W), 255, np.uint8)
        for b in boxes[k - 1]:
            x0, y0, x1, y1 = [int(round(v)) for v in b]
            m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = 0
        p0 = cv2.goodFeaturesToTrack(frames[k - 1], 400, 0.01, 8, mask=m)
        T = np.eye(3)
        if p0 is not None and len(p0) >= 12:
            p1, st, _ = cv2.calcOpticalFlowPyrLK(frames[k - 1], frames[k], p0, None, winSize=(21, 21), maxLevel=3)
            g = st.ravel() == 1
            if g.sum() >= 12:
                M, inliers = cv2.estimateAffinePartial2D(p1[g], p0[g], method=cv2.RANSAC, ransacReprojThreshold=1.5)
                if M is not None:
                    T = np.vstack([M, [0, 0, 1]]); inl.append(float(inliers.mean()))
        A.append(A[-1] @ T)
    res = []
    seen = set()
    for qid, role, obj, obs in trs:
        if role != "prior": continue
        pts = sorted([(o["frame"], o.get("point") or ([(o["box"][0] + o["box"][2]) / 2, (o["box"][1] + o["box"][3]) / 2] if o.get("box") else None)) for o in obs], key=lambda x: x[0])
        pts = [(f, p) for f, p in pts if p is not None and 0 <= f < n]
        key = tuple((f, tuple(p)) for f, p in pts)
        if len(pts) < 2 or key in seen: continue
        seen.add(key)
        raw = sum(math.dist(pts[i][1], pts[i + 1][1]) for i in range(len(pts) - 1))
        st = [(A[f] @ np.array([p[0], p[1], 1.0]))[:2] for f, p in pts]
        stab = sum(math.dist(st[i], st[i + 1]) for i in range(len(st) - 1))
        bg = [(A[f] @ np.array([W / 2, H / 2, 1.0]))[:2] for f, _ in pts]
        bgpath = sum(math.dist(bg[i], bg[i + 1]) for i in range(len(bg) - 1))
        zoom = float(np.sqrt(abs(np.linalg.det(A[pts[-1][0]][:2, :2]))) / np.sqrt(abs(np.linalg.det(A[pts[0][0]][:2, :2]))))
        res.append(dict(split=split, video_id=vid, qid=qid, object=obj, n_obs=len(pts), raw_px=raw, stab_px=stab,
                        ratio=stab / raw if raw > 0 else np.nan, bg_path_px=bgpath, zoom=zoom,
                        inlier=float(np.mean(inl)) if inl else np.nan, n_frames=n))
    return res

rows = []
for split in ("val_hires", "test"):
    df = load_split(split)
    df = df[df.video_source == "internet"]
    for vid, g in df.groupby("video_id"):
        p = RUNS[split] / f"{vid}.json"
        if not p.exists(): continue
        rec = json.loads(p.read_text())
        try:
            r = run(split, vid, g.iloc[0].video_path, rec)
        except Exception as e:
            print(vid, "ERR", e); continue
        if r: rows += r
        print(vid, split, [(round(x["ratio"], 3), round(x["bg_path_px"])) for x in (r or [])], flush=True)
out = pd.DataFrame(rows)
out.to_csv("/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/camo/camo.csv", index=False)
print(out.describe().round(3).to_string())
