"""Candidate on submissions/trackA_cand_path85_combo.csv: the two S2-simulation levers extended to D2/D3/S3, targeted
rows only. No API; answers come from test inputs only; validation labels are read ONLY in report() (evaluation).

E1  D2 extrapolation past the end of the target track (frame-edge exit). The droplet clips simulation_0198/0199/0200
    (60 fps, 14 frames) ask the speed at 0.2 s; the droplet leaves the frame bottom at 0.10 / 0.167 s (frames checked,
    out/grid_droplets.jpg), the geometry clamps to the track end. The prior states a constant 9.7 m/s^2, so
    v(0.2) = v(t_end) + 9.7 * (0.2 - t_end) in physical units (no pixel scale). These rows carried no
    'time_outside_track' flag, which is why research/path85_s2sim/extrap.py missed them. Kill test (lead B): the move
    goes toward Claude's independent direct answer in all 3 rows.
E2  D2 one free-fall event seen by two cameras: simulation_0191 (side) and _0192 (rear) show the same box drop onto
    the truck (out/grid_0189_0192.jpg; identical prior 'acceleration of the box before 0.6s = 9.8m/s'). The facts /
    scenario rules skip these clips because the prior matches the gravity pattern. 0191's box enters through the top
    edge (visible-part centre), 0192's geometry fails on the refine-on replay (prior_motion_below_noise); per-camera
    release-time fits disagree by +-0.02 s. The equivalent questions (speed at 0.2 s, at 0.4 s) are pooled across the
    four clips (2 originals + segmented twins) by the geometric mean (rule P), = g*t within 1%.
L1  S3 sibling-stated motion (name family, |id gap| <= 3, >= 2 shared object names): simulation_0019(_segmented)
    person speed <- 'speed of the person = 1.3m/s' stated by both 0016 and 0017 (two independent statements agree;
    guard 0.8-1.25x of the current answer, as the S2 namefam lever). Bird (0010-0013) and boat (0008) rows of the same
    screen are NOT used: the sibling statement is not confirmed label-free (0012's bird pixel speed rises 3.7x within the
    clip; in 0007 the boat's stated length and stated speed disagree by 8%).
L2  D2 same-camera scale consensus (out/samecam.csv: median-background NCC >= 0.97 within |id gap| <= 3).
    simulation_0154/0155/0156 (prior: shark 7 m/s) and 0158 (prior: turtle acceleration 2.639 m/s^2) share 0157's
    camera; their scales agree within 2.5% (9.50-9.74 m per image width) although they come from two different stated
    motions (the two-fact confirmation of the bird family). 0157 states the SAME turtle acceleration as 0158 (same
    event: the turtle's pixel speeds at 1 s / 1.5 s agree with 0158's within 1.4% / 2.7%) but its own fitted pixel
    acceleration reads 12.7% above 0158's, giving 8.64 m per width. 0157's geometry rows are rescaled to the sibling
    median (x1.113).
L3  D2 depth-correct scale from a same-camera sibling: simulation_0219 and _0220 have the identical camera (frames);
    0219's scale comes from the big robot (5.924 m/s), but the small robot walks IN FRONT of it (occludes it, frames
    28-40, out/crop_0219.jpg), i.e. nearer the camera, so 0219's single 2D scale overstates it. 0220 states the small
    robot's own speed (0.82 m/s): 0219's small-robot height = geometric mean of 0219's px height x 0220's scale and
    0220's answer (both at the small robot's depth). (The small robot's speed row in 0219 already holds the 0.82 fact.)
    .venv/bin/python research/path85b_fam/build_d2d3fam.py
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research/path85_strategy"))
from common import read_sub, clustered_boot, N_SCORED, SUB, table  # noqa: E402
from qp.mra import item_scores  # noqa: E402
from qp import postprocess as pp  # noqa: E402

COMBO = SUB / "trackA_cand_path85_combo.csv"
OUT = SUB / "trackA_cand_d2d3fam_on_combo.csv"
A_DROPLET = 9.7
# E1: qid -> (row answering the speed at the track end (same value, clamped), track end t_end, asked t)
E1 = {511: (513, 0.1000, 0.2), 520: (520, 1 / 6, 0.2), 528: (528, 1 / 6, 0.2)}
E2 = [[471, 1918, 476, 1923], [472, 1919, 477, 1924]]       # speed at 0.2 s / at 0.4 s, 0191, 0191s, 0192, 0192s
L1 = {1090: 1.3, 1659: 1.3}
L2 = {"rows": [361, 362, 363], "own": 8.636, "siblings": [9.502, 9.537, 9.683, 9.736]}   # m per image width (replay)
L3 = {"row": 646, "px": 294.51990632318507, "sib_scale": 0.003976702455893259, "sib_row": 648}


def build(t, base):
    new, log = base.copy(), []
    for q, (qe, te, tq) in E1.items():
        v = base[qe] + A_DROPLET * (tq - te)
        log.append(dict(qid=q, lever="E1 extrapolate past track end (droplet exits frame)", new=v))
    for grp in E2:
        v = float(np.exp(np.log(base[grp]).mean()))
        for q in grp:
            log.append(dict(qid=q, lever="E2 pool one free-fall event over 2 cameras + twins", new=v))
    for q, v in L1.items():
        assert 0.8 <= base[q] / v <= 1.25, q
        log.append(dict(qid=q, lever="L1 sibling-stated person speed (0016, 0017)", new=v))
    k = float(np.median(L2["siblings"])) / L2["own"]
    for q in L2["rows"]:
        log.append(dict(qid=q, lever=f"L2 same-camera scale consensus x{k:.3f}", new=base[q] * k))
    v = float(np.sqrt(L3["px"] * L3["sib_scale"] * base[L3["sib_row"]]))
    log.append(dict(qid=L3["row"], lever="L3 depth-correct scale from same-camera sibling 0220", new=v))
    log = pd.DataFrame(log).set_index("qid")
    assert log.index.is_unique
    for q, r in log.iterrows():
        new[q] = r.new
    log["old"] = base[log.index]
    log["ratio"] = log.new / log.old
    for c in ("video_id", "category", "question", "overlap"):
        log[c] = t.loc[log.index, c]
    log["direct"] = t.loc[log.index, "r_direct_value"]
    sib = {361: 364, 362: 365, 363: 366, 646: 648}
    log["sib_val"] = [base[sib[q]] if q in sib else np.nan for q in log.index]
    log["toward_direct"] = np.abs(np.log(log.new / log.direct)) < np.abs(np.log(log.old / log.direct))
    return new, log


def facts_untouched(t, base, new):
    """Stated-fact rows (facts / motionfam / freefall / labfacts rules) must not change."""
    df = t.reset_index()[["qid", "video_id", "video_path", "video_type", "fps", "question", "prior", "depth_info",
                          "video_source", "category", "target_unit"]]
    _, lg = pp.apply_rules(base, df, rules=("facts", "motionfam", "freefall", "labfacts"))
    stated = set(lg.qid[lg.applied])
    ch = set(t.index[~np.isclose(new, base, rtol=1e-12)])
    return stated, ch & stated


def expected(log):
    """Item gain under the physical answer each lever assumes (g*t / 9.7*t free fall; 1.3 m/s), with the Blender
    backward-difference variant as a second truth for the timed free-fall rows."""
    rows = []
    for q, r in log.iterrows():
        if r.lever.startswith("E1"):
            truths = {"a*t": A_DROPLET * 0.2, "bwdiff": A_DROPLET * (0.2 - 0.5 / 60)}
        elif r.lever.startswith("E2"):
            tq = 0.2 if q in E2[0] else 0.4
            truths = {"g*t": 9.8 * tq, "bwdiff": 9.8 * (tq - 0.5 / 120)}
        elif r.lever.startswith("L1"):
            truths = {"1.3": 1.3}
        else:   # L2/L3: the same-camera sibling's own answer to the same question (0158 / 0220)
            sib = {361: 364, 362: 365, 363: 366, 646: 648}[q]
            truths = {"sibling": float(log.loc[q, "sib_val"])}
        for k, g in truths.items():
            rows.append(dict(qid=q, cat=r.category, truth=k, gain=float(item_scores([r.new], [g])[0] - item_scores([r.old], [g])[0])))
    return pd.DataFrame(rows)


def report(t, base, new, log):
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
    print(log[["video_id", "category", "lever", "old", "new", "ratio", "direct", "toward_direct", "overlap"]].round(4).to_string())
    ch = ~np.isclose(new, base, rtol=1e-12)
    sc = ch & ~t.overlap
    print("\nchanged rows:", int(ch.sum()), t.category[ch].value_counts().to_dict(), "| scored:",
          t.category[sc].value_counts().to_dict(), "| validation-overlap rows changed:", int((ch & t.overlap).sum()))
    # validation: labels only to score; overlap rows the levers would touch
    m = t.overlap & t.val.notna() & ch
    if m.any():
        s0, s1 = item_scores(base[m].to_numpy(), t.val[m].to_numpy()), item_scores(new[m].to_numpy(), t.val[m].to_numpy())
        d = pd.Series(s1 - s0, index=t.index[m])
        print("validation overlap rows changed:", int(m.sum()), "clustered:", clustered_boot(d, t.video_id[m]))
    else:
        print("validation: no validation question is touched by these operators (n = 0); see notes")
    e = expected(log)
    print("\nexpected item gains per truth convention:")
    for k, g in e.groupby("truth"):
        print(f"  truth {k:7s}: rows {len(g)}, item gain {g.gain.sum():+.2f}")
    worst = e.groupby("qid").gain.min().reindex(log.index)
    best = e.groupby("qid").gain.max().reindex(log.index)
    for cat in ("S2", "D2", "S3", "D3"):
        k = log.category == cat
        if not k.any():
            continue
        lo, hi = worst[k].sum(), best[k].sum()
        print(f"  {cat}: rows {int(k.sum())}, item gain {lo:+.2f}..{hi:+.2f} -> category {lo / N_SCORED[cat]:+.5f}..{hi / N_SCORED[cat]:+.5f}"
              f", overall {lo / (4 * N_SCORED[cat]):+.5f}..{hi / (4 * N_SCORED[cat]):+.5f}")


def write(new, out):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": new.index, "parsed_value": new.to_numpy()}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, str(out)], check=True)


def main():
    t = table()
    base = read_sub(COMBO).reindex(t.index)
    new, log = build(t, base)
    assert len(new) == 3289 and np.isfinite(new).all() and (new > 0).all()
    assert not log.overlap.any(), "a validation-overlap row would change"
    stated, hit = facts_untouched(t, base, new)
    print(f"stated-fact rows (facts/motionfam/freefall/labfacts): {len(stated)}; touched by this candidate: {sorted(hit)}")
    assert not hit
    report(t, base, new, log)
    log.to_csv(HERE / "changes_d2d3fam.csv")
    write(new, OUT)
    chk = read_sub(OUT).reindex(t.index)
    d = t.index[~np.isclose(chk, base, rtol=1e-9)]
    assert set(d) == set(log.index), set(d) ^ set(log.index)
    print("wrote", OUT, "| differs from combo on", len(d), "rows")


if __name__ == "__main__":
    main()
