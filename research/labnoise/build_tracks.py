"""Lab 3D tracks for the label-noise study (CPU only, cached Claude records, no API).

For every lab question of a split, re-solves with the fixed lab camera (f = 722 px at 1280 px width, depth_info
as range, the looming depth model of qp.geometry) and captures the 3D positions that qp.geometry measures for the
prior and the target tracks. Annotations get the usual post-steps (qp.refine of motion priors, dense motion
tracks from the local cache) so the tracks are the ones the pipeline uses.

Usage: python research/labnoise/build_tracks.py test|val_hires   -> research/labnoise/out/tracks_<split>.pkl
"""
import sys, pickle
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import numpy as np
from qp import geometry as G
from qp.data import load_split
import run_claude as rc
from qp import claude_annotate as ca

split = sys.argv[1]
RUN = {"test": ROOT / "runs/test_v1_high_854/test/records",
       "val_hires": ROOT / "runs/val_hr_v1_high/val_hires/records"}[split]
CACHE = {"test": ROOT / "runs/_dense_cache/test", "val_hires": ROOT / "runs/_dense_cache/val_hires"}[split]
OUT = Path(__file__).resolve().parent / "out"; OUT.mkdir(exist_ok=True)

df = load_split(split)
df = df[df.video_source == "lab"]
recs = rc.load_records(RUN)
recs = {k: v for k, v in recs.items() if k in set(df.video_id)}
recs = rc.prepare_records(df, recs)
anns = ca.load_annotations(recs)
anns = {q: a for q, a in anns.items() if q in set(df.qid)}
post = len(sys.argv) < 3 or sys.argv[2] != "raw"
if post:
    rc.post_steps(anns, df, recs, refine_priors=True, dense="motion", dense_cache=CACHE, dense_workers=1)

FIX = {"f": None}
G._map_f = lambda fn, value, width, f_cam: FIX["f"]
CAP = {}
_orig = G._measure


def cap(*args, **kw):
    a, va, role = args[1], args[3], args[7]
    try:
        if a is not None and a.rows and va.rng is not None and va.f is not None and abs(va.f - FIX["f"]) < 1e-6:
            t, uv = a.points()
            if len(t):
                CAP[role] = dict(t=np.asarray(t, float), uv=np.asarray(uv, float), P=va.pos(t, uv),
                                 rng=np.asarray(va.rng(t), float), name=a.name, f=va.f, c=np.asarray(va.c))
    except Exception as e:  # noqa: BLE001
        CAP[role + "_err"] = repr(e)
    return _orig(*args, **kw)


G._measure = cap
out = {}
for r in df.itertuples():
    a = anns.get(int(r.qid))
    if a is None:
        continue
    m = recs[r.video_id]["meta"]
    W, H = m["image_size"]
    FIX["f"] = 722.0 * W / 1280
    CAP.clear()
    try:
        ans = G.solve(a.spec, a.tracks, (W, H), float(m["fps"]), camera_fov_deg=84.0,
                      seen_scale=float(m.get("scale") or 1.0))
        res = dict(value=ans.value, flags=list(ans.flags), debug={k: v for k, v in ans.debug.items()
                                                                   if isinstance(v, (int, float, str, list, tuple))})
    except Exception as e:  # noqa: BLE001
        res = dict(value=None, flags=[f"err:{e!r}"], debug={})
    out[int(r.qid)] = dict(video=r.video_id, category=r.category, question=r.question, prior=r.prior,
                           depth_info=r.depth_info, spec=a.spec, direct=a.direct_answer, image_size=(W, H),
                           fps=float(m["fps"]), cap=dict(CAP), **res)
pickle.dump(out, open(OUT / f"tracks_{split}{'' if post else '_raw'}.pkl", "wb"))
print("saved", len(out), "questions;", sum("prior" in v["cap"] for v in out.values()), "with prior 3D track;",
      sum("target" in v["cap"] for v in out.values()), "with target 3D track")
