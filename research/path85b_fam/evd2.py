"""Event screen + one-sided re-estimate on D2 2D-simulation timed speed / acceleration rows (test inputs only).
Per-frame target tracks (pftrack.py) -> two-piece (velocity-discontinuity) fits inside the pipeline's +-0.5 s window.
An event = the two-piece fit beats one quadratic by a large F and the velocity jumps at the break by >= 25% of the
speed (and >= 8 noise units). New px value = quadratic fit on the side of the break that holds the asked frame
(Blender backward difference: frame i uses p_i - p_{i-1}). Moves are scaled onto the base answer:
new = base * new_px / geo_px."""
from __future__ import annotations
import glob, pickle, sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp.data import load_test

HALF = 0.5

def qfit(f, P, deg=2):
    c = np.polyfit(f, P, deg)
    r = P - np.vander(f, deg + 1) @ c
    return c, float((r ** 2).sum())

def at(c, x, d):   # derivative d of the poly (cols) at x
    return np.array([np.polyval(np.polyder(c[:, j], d), x) for j in range(c.shape[1])])

def analyse(tr, fps, t, kind):
    nfr = len(tr); i = int(round(t * fps))
    w = int(round(HALF * fps))
    lo, hi = max(0, i - w), min(nfr - 1, i + w)
    J = np.arange(lo, hi + 1); J = J[~np.isnan(tr[J, 0])]
    if len(J) < 8 or i < 1 or i >= nfr:
        return None
    P = tr[J, :2]; f = J.astype(float)
    noise = float(np.median(np.linalg.norm(np.diff(P, 2, axis=0), axis=1)) / 2.9) if len(J) > 4 else 1.0
    noise = max(noise, 0.3)
    c1, s1 = qfit(f - i, P)
    v1 = np.linalg.norm(at(c1, 0, 1)) * fps; a1 = np.linalg.norm(at(c1, 0, 2)) * fps ** 2
    best = None
    for b in J[3:-3]:
        L, R = J <= b, J >= b
        if L.sum() < 4 or R.sum() < 4: continue
        cl, sl = qfit(f[L] - i, P[L]); cr, sr = qfit(f[R] - i, P[R])
        s2 = sl + sr
        jump = np.linalg.norm(at(cl, b - i, 1) - at(cr, b - i, 1)) * fps
        if best is None or s2 < best[1]:
            best = (b, s2, jump, cl, cr)
    if best is None: return None
    b, s2, jump, cl, cr = best
    dof = max(len(J) - 6, 1)
    F = (s1 - s2) / max(s2 / dof, (noise ** 2)) / 3
    vmax = max(np.linalg.norm(at(cl, b - i, 1)), np.linalg.norm(at(cr, b - i, 1))) * fps
    event = bool(F > 20 and jump >= 0.25 * vmax and jump >= 8 * noise * fps / 10)
    side = "pre" if i <= b - 1 or (i == b) else "post"      # backward difference at i spans (i-1, i)
    c = cl if side == "pre" else cr
    ns = (J <= b).sum() if side == "pre" else (J >= b).sum()
    v2 = np.linalg.norm(at(c, 0, 1)) * fps; a2 = np.linalg.norm(at(c, 0, 2)) * fps ** 2
    # one-frame backward difference on the raw per-frame track (reference only)
    pf = np.linalg.norm(tr[i, :2] - tr[i - 1, :2]) * fps if not (np.isnan(tr[i, 0]) or np.isnan(tr[i - 1, 0])) else np.nan
    return dict(i=i, b=int(b), dt_b=(b - i) / fps, F=F, jump=jump, vmax=vmax, noise=noise, event=event, side=side, n_side=int(ns),
                v1=v1, a1=a1, v2=v2, a2=a2, pf=pf, nJ=len(J))

def main():
    pf = {}
    for fn in glob.glob(str(HERE / "out/pftrack_*.pkl")):
        pf.update(pickle.load(open(fn, "rb")))
    rp = pickle.load(open(ROOT / "research/path85_s2sim/out/replay_s2.pkl", "rb"))
    t = load_test().set_index("qid")
    combo = pd.read_csv(ROOT / "submissions/trackA_cand_path85_combo.csv").set_index("id").parsed_value
    run = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id")
    rows = []
    for q, d in pf.items():
        o = rp[q]; sp = o["spec"].target
        r = analyse(d["track"], d["fps"], sp.time, sp.kind)
        if r is None: continue
        geo_px = o["debug"].get("target_px")
        rows.append(dict(qid=q, video_id=d["video_id"], kind=sp.kind, t=sp.time, fps=d["fps"], geo=o["value"], geo_px=geo_px,
                         base=combo[q], direct=run.direct_value.get(q), **r))
    x = pd.DataFrame(rows)
    x["own"] = np.where(x.kind == "speed", x.v1, x.a1)
    x["new_px"] = np.where(x.kind == "speed", x.v2, x.a2)
    x["track_ok"] = np.abs(np.log(x.own / x.geo_px)) < 0.15
    x["ratio"] = x.new_px / x.geo_px
    x["new"] = x.base * x.ratio
    x["toward_direct"] = np.abs(np.log(x.new / x.direct)) < np.abs(np.log(x.base / x.direct))
    x.to_csv(HERE / "out/evd2.csv", index=False)
    pd.set_option("display.width", 260); pd.set_option("display.max_rows", 300)
    cols = ["qid", "video_id", "kind", "t", "geo_px", "own", "track_ok", "b", "dt_b", "F", "jump", "vmax", "event", "side", "n_side",
            "new_px", "ratio", "base", "new", "direct", "toward_direct"]
    print(x[cols].round(3).to_string())
    e = x[x.event & x.track_ok & (np.abs(np.log(x.ratio)) > 0.05)]
    print("\nevents with |change| > 5%:", len(e)); print(e[cols].round(3).to_string())

if __name__ == "__main__":
    main()

def dense_tracks():
    """Same analysis on the pipeline's own target track (any source) put on the frame grid."""
    rp = pickle.load(open(ROOT / "research/path85_s2sim/out/replay_s2.pkl", "rb"))
    t = load_test().set_index("qid")
    out = {}
    for q, o in rp.items():
        sp = o["spec"].target
        if t.category[q] != "D2" or sp.kind not in ("speed", "acceleration") or sp.time is None: continue
        tg = [tr for tr in o["tracks"] if tr.role == "target"]
        if not tg: continue
        fps = o["fps"]; T = [ob.t for ob in tg[0].obs]
        nfr = int(round(max(T) * fps)) + 2
        tr = np.full((nfr, 4), np.nan)
        for ob in tg[0].obs:
            p = ob.point or ([(ob.box[0] + ob.box[2]) / 2, (ob.box[1] + ob.box[3]) / 2] if ob.box else None)
            if p is not None: tr[int(round(ob.t * fps)), :2] = p
        out[q] = dict(video_id=o["video_id"], track=tr, fps=fps, src=tg[0].source, nobs=len(T))
    return out
