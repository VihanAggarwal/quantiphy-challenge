"""Per 2D-simulation clip: pixel motion of every tracked object (from the pipeline's own replayed tracks,
research/path85_s2sim/out/replay_s2.pkl) and the clip's own geometry scale; for each sibling-stated motion fact
(out_links.csv) the anchored scale / own scale ratio r. Test inputs only."""
from __future__ import annotations
import pickle, sys
from collections import defaultdict
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp

rp = pickle.load(open(ROOT / "research/path85_s2sim/out/replay_s2.pkl", "rb"))

def centre(ob):
    if ob.point: return ob.point
    if ob.box: return [(ob.box[0] + ob.box[2]) / 2, (ob.box[1] + ob.box[3]) / 2]
    if ob.extent: return [(ob.extent[0][0] + ob.extent[1][0]) / 2, (ob.extent[0][1] + ob.extent[1][1]) / 2]
    return None

def motion(tr):
    obs = sorted([(o.t, c) for o in tr.obs if (c := centre(o)) is not None])
    if len(obs) < 3: return None
    T = np.array([a for a, _ in obs]); P = np.array([b for _, b in obs], float)
    T, idx = np.unique(T, return_index=True); P = P[idx]
    if len(T) < 3 or np.ptp(T) < 0.2: return None
    vx, vy = np.polyfit(T, P[:, 0], 1)[0], np.polyfit(T, P[:, 1], 1)[0]
    d = np.array([vx, vy]) / (np.hypot(vx, vy) + 1e-9)
    s = P @ d
    acc = 2 * np.polyfit(T, s, 2)[0] if len(T) >= 5 else np.nan
    return dict(v=float(np.hypot(vx, vy)), a=float(abs(acc)), n=len(T), span=(float(T.min()), float(T.max())), src=tr.source)

def clip_tracks():
    by = defaultdict(lambda: defaultdict(list)); scale = defaultdict(list)
    for q, o in rp.items():
        v = o["video_id"]
        sc = o["debug"].get("scale_m_per_px")
        if sc: scale[v].append(sc)
        for tr in o["tracks"]:
            m = motion(tr)
            if m: by[v][" ".join(pp._tokens(pp._clean_object(tr.object)))].append(m)
    return by, {v: float(np.median(s)) for v, s in scale.items()}

def best(ms):
    return max(ms, key=lambda m: m["n"]) if ms else None

def find(by, v, obj):
    cands = [(pp._same_object(k, obj), k) for k in by.get(v, {})]
    cands = [c for c in cands if c[0] >= 0.8]
    if not cands: return None, None
    k = max(cands)[1]; return k, best(by[v][k])

def main():
    by, scale = clip_tracks()
    L = pd.read_csv(HERE / "out_links.csv")
    rows = []
    for r in L.itertuples():
        for clip, role in ((r.C, "C"), (r.S, "S")):
            k, m = find(by, clip, r.obj)
            if m is None or clip not in scale: continue
            px = m["v"] if r.kind == "speed" else m["a"]
            si = float(pd.Series([r.fact]).str.extract(r"=\s*(-?[\d.]+)")[0].iloc[0])
            si = abs(si)
            anchor = si / px if px > 0 else np.nan
            rows.append(dict(C=r.C, S=r.S, role=role, clip=clip, cat=r.cat, fact=r.fact, obj=k, n=m["n"], src=m["src"],
                             span=m["span"], px=px, own_scale=scale[clip], anchor=anchor, r=anchor / scale[clip]))
    d = pd.DataFrame(rows).drop_duplicates(["clip", "fact"])
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
    print(d.round(4).to_string())
    d.to_csv(HERE / "out_measure2d.csv", index=False)

if __name__ == "__main__":
    main()
