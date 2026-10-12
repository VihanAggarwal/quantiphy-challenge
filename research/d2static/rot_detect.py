"""Gravity-prior 2D clips: is gravity along the image x axis (a portrait phone video stored sideways)?
For every track of the clip with >= 4 points, fit x(t), y(t) with parabolas; report |a_x| / |a_y| of the
longest-moving track. Test and validation inputs (no labels)."""
import re, sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import *

GRAV = re.compile(r"gravit|free.?fall|=\s*9\.[78]\d*\s*m\s*/\s*s", re.I)


def detect(split):
    df = load_split(split)
    recs = records(split); sp = specs(recs)
    rows = []
    for v, g in df[df.category.isin(["S2", "D2"]) & df.prior.str.contains(GRAV)].groupby("video_id"):
        if v not in recs:
            continue
        m = recs[v]["meta"]; fps = float(m["fps"]); sc = m["scale"]
        best = None
        for q in g.qid:
            s = sp.get(int(q))
            if not s: continue
            for tr in s["tracks"]:
                obs = [(o["frame"], o["point"] or ([(o["box"][0] + o["box"][2]) / 2, (o["box"][1] + o["box"][3]) / 2] if o.get("box") else None)) for o in tr["obs"]]
                obs = sorted({f: p for f, p in obs if p is not None}.items())
                if len(obs) < 4: continue
                P = np.array([p for _, p in obs], float) / sc
                path = np.linalg.norm(np.diff(P, axis=0), axis=1).sum()
                if best is None or path > best[0]:
                    best = (path, tr["object"], np.array([f for f, _ in obs], float) / fps, P)
        if best is None:
            rows.append(dict(video_id=v, n=0)); continue
        path, obj, t, P = best
        ax = 2 * np.polyfit(t, P[:, 0], 2)[0]; ay = 2 * np.polyfit(t, P[:, 1], 2)[0]
        rows.append(dict(video_id=v, cat=g.category.iloc[0], prior=g.prior.iloc[0][:40], obj=obj, n=len(t), path_px=path,
                         ax=ax, ay=ay, ratio=abs(ax) / max(abs(ay), 1e-9), W=m["image_size"][0], H=m["image_size"][1]))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    for split in ("test", "val_hires"):
        r = detect(split)
        r.to_csv(ROOT / f"research/d2static/out/rot_detect_{split}.csv", index=False)
        print(split); print(r.round(2).to_string(index=False))
