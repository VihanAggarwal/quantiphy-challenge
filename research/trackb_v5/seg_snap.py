"""L6: re-measure 2D questions of segmented clips and of originals with a pixel-aligned segmented twin on the
twin's foreground (white background -> exact connected components). The cvq tracks (SAM 2 masks prompted by
Qwen's boxes; open-weight) choose the component(s); each box is replaced by the bounding box of the components lying
mostly inside it (accepted only if IoU(new, old) >= 0.5), the point by their area-weighted centroid, then
qp.geometry.solve. Writes out/<split>_cvq_seg.csv (id, geo_value, geo_si, snapped, n_obs) for the affected rows.

    .venv/bin/python research/trackb_v5/seg_snap.py val|test
"""
import copy
import pickle
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "trackb_dense"))
from solve import annotations  # noqa: E402
from tbcommon import questions  # noqa: E402
from qp.data import load_split  # noqa: E402
from qp.geometry import solve  # noqa: E402

CACHE = Path("/tmp/claude-0/trackb_v5_cache")
CACHE.mkdir(parents=True, exist_ok=True)
THR, MIN_AREA, INSIDE, IOU_OK = 25, 20, 0.5, 0.5


def components(path: str):
    cf = CACHE / (Path(path).stem + ".comps.pkl")
    if cf.exists():
        return pickle.load(open(cf, "rb"))
    cap = cv2.VideoCapture(path)
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fg = (255 - f.min(axis=2)) > THR
        fg = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(fg, connectivity=8)
        keep = [(st[i, 0], st[i, 1], st[i, 0] + st[i, 2], st[i, 1] + st[i, 3], st[i, 4], cen[i, 0], cen[i, 1])
                for i in range(1, n) if st[i, 4] >= MIN_AREA]
        out.append(np.array(keep, float).reshape(-1, 7))
    pickle.dump(out, open(cf, "wb"))
    return out


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0.0


def snap(box, comps):
    if comps is None or not len(comps):
        return None
    w, h = box[2] - box[0], box[3] - box[1]
    ex = [box[0] - .1 * w, box[1] - .1 * h, box[2] + .1 * w, box[3] + .1 * h]
    sel = []
    for c in comps:
        ix = max(0, min(c[2], ex[2]) - max(c[0], ex[0]))
        iy = max(0, min(c[3], ex[3]) - max(c[1], ex[1]))
        if ix * iy >= INSIDE * (c[2] - c[0]) * (c[3] - c[1]):
            sel.append(c)
    if not sel:
        return None
    S = np.array(sel)
    nb = [S[:, 0].min(), S[:, 1].min(), S[:, 2].max(), S[:, 3].max()]
    if iou(nb, box) < IOU_OK:
        return None
    a = S[:, 4]
    return nb, [float((S[:, 5] * a).sum() / a.sum()), float((S[:, 6] * a).sum() / a.sum())]


def main(split):
    df = questions(split)
    test = load_split("test")
    vids = set(test.video_id)
    paths = dict(zip(test.video_id, test.video_path))
    df = df[df.video_type.str[1] == "2"]
    twin = {v: (v if v.endswith("_segmented") else v + "_segmented") for v in df.video_id.unique()}
    twin = {v: t for v, t in twin.items() if t in vids}
    df = df[df.video_id.isin(twin)]
    anns, _, meta = annotations(split, "cvq", df)
    rows = []
    for v, g in df.groupby("video_id"):
        tp, op = paths[twin[v]], paths[v]
        c1, c2 = cv2.VideoCapture(tp), cv2.VideoCapture(str(op))
        same = all(c1.get(k) == c2.get(k) for k in (3, 4, 7))
        if not same:
            print("skip (size/frames differ)", v, [c1.get(k) for k in (3, 4, 7)], [c2.get(k) for k in (3, 4, 7)])
            continue
        TW = c1.get(3)
        comps = components(tp)
        for r in g.itertuples():
            a = anns.get(int(r.qid))
            if a is None:
                continue
            fps, size, _ = meta[int(r.qid)]
            trs, n_obs, n_snap = [], 0, 0
            for tr in a.tracks:
                tr = copy.deepcopy(tr)
                for o in tr.obs:
                    if o.box is None:
                        continue
                    n_obs += 1
                    f = int(round(o.t * fps))
                    k = TW / size[0]
                    s = snap([x * k for x in o.box], comps[f] if 0 <= f < len(comps) else None)
                    if s is not None:
                        o.box, o.point = [float(x) / k for x in s[0]], [x / k for x in s[1]]
                        o.extent = None
                        n_snap += 1
                trs.append(tr)
            ans = solve(a.spec, trs, size, fps)
            ans0 = solve(a.spec, a.tracks, size, fps)
            rows.append(dict(id=int(r.qid), video_id=v, geo_value=ans.value or np.nan,
                             geo_si=ans.debug.get("value_si", np.nan), geo0=ans0.value or np.nan,
                             snapped=n_snap, n_obs=n_obs))
        print(v, len(g), "q; comps frames", len(comps), flush=True)
    R = pd.DataFrame(rows)
    R.to_csv(HERE / f"out_{split}_cvq_seg.csv", index=False)
    print(f"{split}: {len(R)} rows, snapped fraction {R.snapped.sum() / max(1, R.n_obs.sum()):.2f}, "
          f"median |log(new/old)| {np.nanmedian(np.abs(np.log(R.geo_value / R.geo0))):.3f}")


if __name__ == "__main__":
    main(sys.argv[1])
