"""Per-frame target tracks for D2 (and S2 for reference) 2D-simulation timed speed/acceleration questions:
median-background foreground components linked to the annotator's own target track (replay_s2.pkl), as in
research/path85_s2sim/evtrack.py. Test input videos only.  -> out/pftrack.pkl {qid: dict(track=(nfr,4) array, fps)}
    python pftrack.py <worker> <nworkers>"""
from __future__ import annotations
import pickle, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research/path85_s2sim"))
from evtrack import load_frames, components, follow
from qp.data import load_test

def main(w, nw):
    rp = pickle.load(open(ROOT / "research/path85_s2sim/out/replay_s2.pkl", "rb"))
    t = load_test().set_index("qid")
    sel = [q for q, o in rp.items() if o["spec"].target.kind in ("speed", "acceleration") and o["spec"].target.time is not None
           and t.category[q] in ("D2",)]
    vids = sorted({rp[q]["video_id"] for q in sel})[w::nw]
    out = {}
    for v in vids:
        fr, s = load_frames(v); comps = components(fr); nfr = len(fr)
        H, W = fr[0].shape[:2]
        for q in [q for q in sel if rp[q]["video_id"] == v]:
            o = rp[q]; fps = o["fps"]
            tg = [tr for tr in o["tracks"] if tr.role == "target"]
            if not tg: continue
            anchors = {}
            for ob in tg[0].obs:
                p = ob.point or ([(ob.box[0] + ob.box[2]) / 2, (ob.box[1] + ob.box[3]) / 2] if ob.box else None)
                if p is not None: anchors[int(round(ob.t * fps))] = p
            tr = follow(comps, anchors, s, nfr)
            out[q] = dict(video_id=v, track=tr, fps=fps, img=(W / s, H / s))
        print(v, "done", flush=True)
    pickle.dump(out, open(HERE / f"out/pftrack_{w}.pkl", "wb"))

if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
