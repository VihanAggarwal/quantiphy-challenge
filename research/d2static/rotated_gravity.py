"""Sideways-gravity internet clips (portrait phone videos stored landscape without rotation metadata):
the pipeline forces gravity priors onto the image's vertical axis, so the falling object's motion (along x)
is 'below noise' and every question falls back to Claude's direct guess. Re-solve these clips with the
tracks rotated 90 deg (x, y) -> (H - y, x), so gravity is vertical again. Distances and sizes are
rotation-invariant; question axes ('vertical') then refer to the world vertical. Test inputs only.

    python research/d2static/rotated_gravity.py [video ...]
"""
import copy, sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from common import *
sys.path.insert(0, str(ROOT / "scripts"))
import run_claude as rc  # noqa: E402
from qp.geometry import solve  # noqa: E402

ROTATED = ["internet_0060", "internet_0061", "internet_0062", "internet_0063"]


def rot_track(tr, H):
    tr = copy.deepcopy(tr)
    for o in tr.obs:
        if o.point is not None:
            x, y = o.point; o.point = [H - y, x]
        if o.extent is not None:
            o.extent = [[H - p[1], p[0]] for p in o.extent]
        if o.box is not None:
            x1, y1, x2, y2 = o.box; o.box = [H - y2, x1, H - y1, x2]
    return tr


def run(videos, split="test"):
    df = load_split(split)
    sub = df[df.video_id.isin(videos)]
    recs = {v: r for v, r in records(split).items() if v in videos}
    anns = rc.annotations(sub, recs, dense="motion", dense_cache=ROOT / "runs/_dense_cache" / split)
    out = []
    for r in sub.itertuples():
        a = anns.get(int(r.qid))
        m = recs[r.video_id]["meta"]; W, H = m["image_size"]
        row = dict(qid=int(r.qid), video_id=r.video_id, question=r.question, direct=a.direct_answer if a else np.nan)
        for name, tracks, size in (("plain", a.tracks, (W, H)), ("rot", [rot_track(t, H) for t in a.tracks], (H, W))):
            ans = solve(a.spec, tracks, tuple(size), float(m["fps"]), seen_scale=float(m.get("scale") or 1.0))
            row[name] = ans.value if ans.value is not None else np.nan
            row[name + "_flags"] = ";".join(ans.flags)
        out.append(row)
    return pd.DataFrame(out)


if __name__ == "__main__":
    vids = sys.argv[1:] or ROTATED
    res = run(vids)
    res.to_csv(ROOT / "research/d2static/out/rotated_gravity.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
    print(res[["qid", "video_id", "question", "direct", "plain", "rot", "rot_flags"]].round(3).to_string(index=False))
