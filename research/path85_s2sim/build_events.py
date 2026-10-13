"""Event fixes (C): timed speed / acceleration rows where an event or a frame-edge cut at the asked time breaks the
smoothed fit; values measured on per-frame masks / the pipeline's own dense track, at the pipeline's scale. Test
inputs only; no validation labels are copied (0171's validation labels only judged the per-frame operator).
  263, 1830  simulation_0121(_segmented) left ball at 1.0 s (30 fps): the collision is at frame 28 (0.93 s); on
             the segmented-twin masks the ball then creeps 1 px/frame (frames 28-33) -> 30 px/s x 0.012355 m/px
             (pipeline scale, ball 2 m = 161.9 px) = 0.371 m/s. Base 0.971 (ICI window straddles the collision).
  855, 859   simulation_0253 box at 0.5 s: the box is still entering through the top-left frame corner (annotator
             box touches the border), so the visible-part centre lags (1.90 m/s, 15.07 m/s^2). Constant-acceleration
             fit of the pipeline's dense track over the clean part (0.6-1.85 s): v(0.5) = 3.545 m/s, a = 5.254 m/s^2
             (Claude's direct answers: 3.5, 5.1).
  1874       simulation_0171_segmented astronaut speed at 0.5 s: take-off at ~0.6 s (pixel speed x1.8 within
             0.25 s); one-frame backward difference of the segmented-twin mask box centre at frame 12 = 274 px/s
             x 0.00609 m/px (p21 scale) = 1.67 m/s (base 2.09). (Validation: on 0171 the same operator gives
             1.64-1.67 vs label 1.72; the smoothed base 2.09.)
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from qp.data import load_test
from build_candidates import overlap_mask, write

FIX = {263: 0.371, 1830: 0.371, 855: 3.545, 859: 5.254, 1874: 1.67}
# D: time outside the target track -> speed extrapolated with the edge acceleration (extrap.py), |change| >= 2%;
#    segmented-twin copies of a changed row follow it
EXTRAP_MIN = 0.02

def extrap_rows(t, base):
    from qp import postprocess as pp
    d = pd.read_csv(HERE / "out/extrap.csv")
    d = d[(np.abs(d.ratio - 1) >= EXTRAP_MIN) & (d.cat == "S2")]
    out = {}
    key = t.video_id.str.replace("_segmented", "", regex=False) + "|" + t.question.map(pp.norm_question)
    for r in d.itertuples():
        out[r.qid] = base[r.qid] * r.ratio
        for q2 in t.index[(key == key[r.qid]) & (t.index != r.qid)]:
            if np.isclose(base[q2], base[r.qid], rtol=1e-9):
                out[q2] = base[q2] * r.ratio
    return out

def apply(base, t, ov, extra=None):
    new = base.copy(); log = []
    for q, v in {**FIX, **(extra or {})}.items():
        assert not ov[q], q
        log.append(dict(qid=q, video_id=t.video_id[q], category=t.category[q], question=t.question[q], old=base[q], new=v))
        new[q] = v
    return new, pd.DataFrame(log)

def main():
    t = load_test().set_index("qid"); ov = overlap_mask(t)
    phys = pd.read_csv(ROOT / "submissions/trackA_cand_physb2_on_p21.csv").set_index("id").parsed_value.astype(float).reindex(t.index)
    nf = pd.read_csv(ROOT / "submissions/trackA_cand_s2namefam_on_physb2.csv").set_index("id").parsed_value.astype(float).reindex(t.index)
    D = extrap_rows(t, phys)
    C, lc = apply(phys, t, ov, D)
    ALL, _ = apply(nf, t, ov, extrap_rows(t, nf))
    pd.set_option("display.width", 220)
    print(lc.round(4).to_string(index=False))
    lc.to_csv(HERE / "out_changes_events.csv", index=False)
    write(C, ROOT / "submissions/trackA_cand_s2events_on_physb2.csv")
    write(ALL, ROOT / "submissions/trackA_cand_s2all_on_physb2.csv")
    for name, s in (("events", C), ("all", ALL)):
        ch = ~np.isclose(s, phys, rtol=1e-12)
        print(name, "changed rows vs physb2:", int(ch.sum()), t.category[ch].value_counts().to_dict(),
              "scored:", int((ch & ~ov).sum()))

if __name__ == "__main__":
    main()
