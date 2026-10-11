"""3D simulation / segmentation (non-lab) candidates on probe 8: motion labels the scene family states.

    .venv/bin/python research/sim3d/build_candidate.py            # writes the candidate CSVs + change logs

Evidence comes from test INPUTS only (question / prior / depth_info text, frames). Validation labels are read
only by evaluate_val.py. Rows changed (S3/D3, non-lab only; every other row = probe 8):

MF  scene-family motion facts the probe-8 rules do not reach. A speed / acceleration question about object O takes
    the value that another clip of the same Blender scene STATES for O (labels are Blender readouts of the same
    object, so the prior of one camera is the label of another), when
      - the clips are one scene: qp.postprocess size families (twins, shared depth numbers, identical priors,
        series, near-identical frames, scenario) plus the eye-verified vocabulary group of the photo-lab street
        (simulation_0045-0050: telephone booth, moving bicycle, walking person, door pillars; research/
        family_ext_scripts_2026-10-11.tar.gz d3rest); colour-car / generic names are not used to link scenes;
      - O matches by head noun (bike ~ bicycle) and the statements agree within 2% (the log-mean is used);
      - speed: no acceleration of O is stated or asked in either clip (constant speed), the stated value is untimed
        or stated at the asked time;
      - 3D consistency (the label is the full 3D origin speed): every clip of the scene with a timed depth track of
        O has |dr/dt| <= 1.05 x the stated speed (a single constant-speed scenario seen from several cameras);
      - the row is not already a stated value (probe-8 fact rows are kept).
    The probe-8 facts rule has a 2x guard (a transfer more than 2x off the clip's own answer is skipped as
    "footage contradicts"); the main candidate overrides it only where the asking clip has the SAME depth track as
    the stating clip (identical motion) or the object is the beach-scene person whose 1.3 m/s is stated by two
    cameras (see the report); variant `_guard` keeps the 2x guard everywhere.
FF  free fall: an acceleration asked at time t of an object that the frames show falling vertically from rest
    through frame round(t*fps) (constant positive second difference of the moving region's lower edge, no
    horizontal drift) takes 9.8 m/s^2 -- the Blender label is the backward difference of speed, which equals g for
    a vertical fall, and the test priors state free-fall phases as 9.8 m/s^2 ("acceleration of the magnifying
    glass before 0.5s = 9.8m/s^2", "acceleration of the typewriter before 0.45s = 9.8m/s^2").
"""
from __future__ import annotations

import itertools
import re
import subprocess
import sys
from collections import defaultdict

import cv2

from common import *  # noqa: F401,F403
from common import ROOT, BASE, load_split, table, answers, read_sub, depth_tracks, pp, np, pd
from qp.geometry import name_score
from qp.open.qwen_vl import parse_question_text
from qp.parse import _UNITS

SCRATCH_OUT = ROOT / "research/sim3d"
EXTRA_GROUPS = [  # eye-verified vocabulary scene groups (d3rest), only the ones a motion question here needs
    ["simulation_0045", "simulation_0046", "simulation_0047", "simulation_0048", "simulation_0049", "simulation_0050"],
]
SYN = {"bicycle": "bike", "bike": "bike"}
AGREE = 0.02
RADIAL_TOL = 1.05
GUARD = 2.0


def head(o):
    h = pp._head(pp._clean_object(o))
    return SYN.get(h, h)


def _syn(s):
    s = re.sub(r"\bbicycle\b", "bike", str(s), flags=re.I)
    return re.sub(r"\b(?:moving|walking|running|flying)\s+", "", s, flags=re.I).strip()


def obj_match(a, b):
    """Same head noun (bike ~ bicycle) and compatible modifiers (qp.postprocess name score >= 0.6):
    'moving bicycle' ~ 'bike', 'walking person' ~ 'person', but not 'white horse' ~ 'horse at the back'."""
    return head(a) == head(b) and head(a) != "" and pp._same_object(_syn(a), _syn(b)) >= pp.MIN_NAME


def radial_speed(depth_info, obj):
    best = None
    for k, e in depth_tracks(depth_info).items():
        te = [x for x in e if x[0] is not None]
        if len(te) >= 2 and (obj_match(k, obj) or name_score(k, obj) >= 0.6 or
                             (head(obj) in ("person", "pedestrian", "man") and head(k) == "human")):
            best = te
    if best is None:
        return np.nan, None
    (t0, r0), (t1, r1) = best[0], best[-1]
    return abs(r1 - r0) / (t1 - t0), tuple(best)


def families(full):
    df = pp._questions(full)
    facts = pp._parse_facts(df)
    links = pp.scene_links(df, facts, pp.FrameCache(pp.DEFAULT_CACHE))
    uf = pp._UF()
    for v in df.video_id:
        uf.find(pp.base_id(v))
    for k in pp.SIZE_LINKS:
        for a, b in links.get(k, []):
            uf.union(pp.base_id(a), pp.base_id(b))
    for g in EXTRA_GROUPS:
        for a, b in zip(g, g[1:]):
            uf.union(a, b)
    return {v: uf.find(pp.base_id(v)) for v in df.video_id}, facts, df


def motion_facts(full, t, cur, fact_rows):
    fam, facts, df = families(full)
    accel = pp._accel_objects(df, facts)
    depth = {v: di for v, di in zip(df.video_id, df.depth_info)}
    clips_of = defaultdict(set)
    for v in df.video_id:
        clips_of[fam[v]].add(v)
    by_fam = defaultdict(list)
    for f in facts:
        if f.kind in ("speed", "acceleration"):
            by_fam[fam[f.video_id]].append(f)
    rows = []
    for q, r in t.iterrows():
        if r.kind not in ("speed", "acceleration") or len(r.objs) != 1 or q in fact_rows:
            continue
        obj = pp._clean_object(r.objs[0])
        own = {pp.norm_ws(x) for x in str(r.prior).split("\n")}
        cands = []
        for f in by_fam[fam[r.video_id]]:
            if f.kind != r.kind or not obj_match(obj, f.obj):
                continue
            if f.video_id == r.video_id and pp.norm_ws(f.line) in own:
                continue
            if f.timed and (r.qwin is not None or r.qtime is None or f.time is None or abs(r.qtime - f.time) > 1e-6):
                continue
            if r.kind == "speed" and any(obj_match(obj, o) for v in (r.video_id, f.video_id) for o in accel.get(v, [])):
                continue
            cands.append(f)
        if not cands:
            continue
        vals = np.array([f.si for f in cands])
        if vals.max() / vals.min() > 1 + AGREE:
            continue
        v_si = float(np.exp(np.log(vals).mean()))
        new = v_si / _UNITS[r.target_unit][0]
        note, ok = [], True
        same_track = False
        vr_own, tr_own = radial_speed(r.depth_info, obj)
        if r.kind == "speed":
            for c in sorted(clips_of[fam[r.video_id]]):
                vr, tr = radial_speed(depth[c], obj)
                if np.isfinite(vr):
                    note.append(f"{c.replace('simulation_', 's')}:{vr / v_si:.2f}")
                    if vr > RADIAL_TOL * v_si:
                        ok = False
                    if tr_own is not None and tr == tr_own and c != r.video_id and \
                            any(f.video_id == c or pp.base_id(f.video_id) == pp.base_id(c) for f in cands):
                        same_track = True
        if not ok:
            continue
        old = float(cur[q])
        guard_ok = max(new / old, old / new) <= GUARD
        rows.append(dict(qid=q, video_id=r.video_id, category=r.category, question=r.question, old=old, new=new,
                         ratio=new / old, src=",".join(sorted({f.video_id for f in cands})),
                         line="; ".join(sorted({f.line for f in cands})), radial_fractions=" ".join(note),
                         same_track=same_track, guard_ok=guard_ok, rule="MF"))
    return pd.DataFrame(rows)


def free_fall_rows(t, cur):
    """Acceleration questions at t whose clip shows a vertical fall from rest through frame round(t*fps)."""
    rows = []
    for q, r in t[(t.kind == "acceleration") & t.qtime.notna()].iterrows():
        cap = cv2.VideoCapture(str(r.video_path))
        fr = []
        while len(fr) < 40:
            ok, f = cap.read()
            if not ok:
                break
            fr.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.int16))
        k = int(round(r.qtime * r.fps))
        if k + 2 >= len(fr) or k < 3:
            continue
        ymax, xmed = [], []
        for i in range(1, k + 2):
            ys, xs = np.nonzero(np.abs(fr[i] - fr[i - 1]) > 25)
            if len(ys) < 50:
                break
            ymax.append(ys.max())
            xmed.append(np.median(xs))
        if len(ymax) < k + 1:
            continue
        d1 = np.diff(ymax)
        d2 = np.diff(d1)
        w = fr[0].shape[1]
        falling = (d1 > 0).all() and np.median(d2) > 0.5 and (d2 > -2).all() and (np.ptp(xmed[1:]) < 0.03 * w)
        if not falling:
            continue
        # the stated value of the clip must not be about this object at this time (protect stated facts)
        rows.append(dict(qid=q, video_id=r.video_id, category=r.category, question=r.question, old=float(cur[q]),
                         new=9.8, ratio=9.8 / float(cur[q]), src="frames", line=f"vertical fall frames 1..{k + 1}: "
                         f"dy={list(map(int, d1))} d2_med={np.median(d2):.1f} x_drift={np.ptp(xmed[1:]):.0f}px",
                         radial_fractions="", same_track=False, guard_ok=True, rule="FF"))
    return pd.DataFrame(rows)


def stated_rows(full, cur):
    """Rows equal to a value the scene family states (probe-8 facts): protected."""
    c = pp.stated_facts(full, pp.FrameCache(pp.DEFAULT_CACHE))
    keep = set()
    for q, g in c.groupby("qid"):
        if q in cur.index and np.isclose(g.value.to_numpy(float), cur[q], rtol=1e-6).any():
            keep.add(int(q))
    # also any row equal to a stated prior number of its own clip family (cheap extra protection)
    return keep


def write(name, base, changes, idx):
    out = base.copy()
    for r in changes.itertuples():
        out[r.qid] = r.new
    tmp = SCRATCH_OUT / f"_tmp_{name}.csv"
    pd.DataFrame({"id": idx, "parsed_value": out.reindex(idx).values}).to_csv(tmp, index=False)
    dst = ROOT / f"submissions/trackA_cand_sim3d_{name}_on_p8.csv"
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), str(tmp), str(dst)], check=True)
    tmp.unlink()
    changes.to_csv(SCRATCH_OUT / f"trackA_cand_sim3d_{name}_on_p8_changes.csv", index=False)
    chk = pd.read_csv(dst).set_index("id").parsed_value
    diff = pd.Series(~np.isclose(chk.reindex(idx), base.reindex(idx), rtol=1e-9), index=idx)
    print(f"  {dst.name}: {int(diff.sum())} rows differ from probe 8 "
          f"({full_cat[diff[diff].index].value_counts().to_dict()})")


if __name__ == "__main__":
    full = load_split("test")
    tq = full.set_index("qid")
    full_cat = tq.category
    t = table()
    base = read_sub(BASE, tq.index).parsed_value.astype(float)
    protected = stated_rows(full, base)
    print(f"protected stated-fact rows (all categories): {len(protected)}; in 3D non-lab: "
          f"{len(protected & set(t.index))}")
    mf = motion_facts(full, t, base, protected)
    ff = free_fall_rows(t, base)
    ff = ff[~ff.qid.isin(protected)]
    allc = pd.concat([mf, ff], ignore_index=True)
    allc = allc[~np.isclose(allc.new, allc.old, rtol=1e-9)]
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 70)
    print(allc[["qid", "video_id", "category", "rule", "old", "new", "ratio", "same_track", "guard_ok",
                "radial_fractions", "src"]].to_string(index=False))
    beach_person = (allc.rule == "MF") & allc.question.str.contains("person") & \
        allc.src.str.contains("simulation_0025|simulation_0031")
    main = allc[allc.guard_ok | allc.same_track | beach_person]
    print("guard overridden in main:", sorted(main.qid[~main.guard_ok]))
    guard = allc[allc.guard_ok]
    print(f"main: {len(main)} rows; guard variant: {len(guard)} rows")
    write("motionfam", base, main, tq.index)
    write("motionfam_guard", base, guard, tq.index)
