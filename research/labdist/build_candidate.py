"""Lab distance candidates on probe 8 (research/labdist). Test inputs and our own cached answers only; validation
labels are read only by evaluate_val.py.

Label procedure (QuantiPhy App. C.2 / D.2): annotators hand-click the centre of each object, read the ToF depth at
the clicked pixel (visible surface) and back-project with the intrinsics; a distance label is the Euclidean distance
of the two 3D points. Renders of one lab event (captured_X, Xs, Xx) are pixel-identical in the object regions, carry
identical depth_info and share their labels, so each render's answer is a sample of ONE label.

Rules (each row changed by at most one rule; stated-fact rows and validation-overlap rows are never changed):
  R1 render copy   an s/x render row answered by Claude's direct answer takes the original render's probe-8 value
                   (validation, all lab kinds, 20 rows: original-render direct .680 vs own-render direct .610).
                   Not when the original's value is below the stated-depth lower bound of the row (see R4).
  R2 family median a family whose probe-8 values for one question spread by more than 15% takes the log-median
                   of its renders' values (renders share the label; variance reduction).
  R3 looming fix   0054b/0054bs "orange ball - soccer ball at 1.0 s" use the soccer ball's only depth entry (t=2.0 s,
                   3.254 m) at t=1.0 s, after which the ball rolled away (box 60 px -> 45 px); the sibling render
                   0054bx carries the boxes and its geometry follows the looming (1.33 m): the family takes 0054bx's.
  R4 emulation     (variant "emu" only) ball-to-floor / ball-to-desk rows of families 0008 and 0009: the clicked-point
                   procedure with the stated depths (ball at the asked time, floor / desk point) and Claude's floor /
                   desk click that lies on the ball's own vertical (the one most collinear with the fall); range
                   convention, f from LAB_FOV_DEG, as qp.geometry. Probe 8 answers there are Claude's direct
                   "depth difference" (a lower bound of any 3D distance between the two clicked points), a
                   camera-y projection, or values below that bound.

    python research/labdist/build_candidate.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from backproject import point  # noqa: E402
from qp.data import load_split  # noqa: E402

BASE = ROOT / "submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv"
REC = ROOT / "runs/test_v1_high_854/test/records"
OUT = HERE / "out"
SPREAD = 1.15
R_BASKET = 0.232 / 2          # stated in test priors: "diameter of the basketball = 23.2 cm"


def family(v):
    return re.sub(r"(captured_\d+[ab]?)[sxX]?$", r"\1", v)


def rec(v):
    return json.loads((REC / f"{v}.json").read_text())


def obs_px(v, name_re, frame=None):
    """[(frame, (u, v) original px, box width px)] of a record's tracks whose object matches name_re."""
    r = rec(v)
    sc = r["meta"]["scale"]
    out = {}
    for q in r["parsed"]["questions"]:
        for tr in q["tracks"]:
            if not re.search(name_re, tr["object"]):
                continue
            for o in tr["obs"]:
                if frame is not None and o["frame"] != frame:
                    continue
                p = o.get("point")
                b = o.get("box")
                key = (tr["object"], o["frame"])
                cur = out.get(key, (None, None))
                out[key] = ((p[0] / sc, p[1] / sc) if p else cur[0], ((b[2] - b[0]) / sc) if b else cur[1])
    return out


def stated_numbers(t):
    nums = set()
    for p in t.loc[t.video_source == "lab", "prior"]:
        for m in re.findall(r"=\s*([0-9]*\.?[0-9]+)", str(p)):
            nums.add(round(float(m), 6))
    return nums


def emulate():
    """R4 values {qid: (value in the row's unit, note)} for families 0008 and 0009."""
    out = {}
    # 0009: ball held at t=0 (depth 1.321 stated at t=0), apex at 1.92 s (1.5795), floor 2.0285; Claude's floor click
    # "floor below ball" in captured_0009 (the floor is masked out in the s/x renders)
    o = obs_px("captured_0009", r"^basketball|^floor")
    b0 = o[("basketball initial", 0)][0]
    apex = o[("basketball", 46)][0]
    fl = o[("floor below ball", 0)][0]
    P0, Pa, Pf = point(*b0, 1.321), point(*apex, 1.5795), point(*fl, 2.0285)
    fall = (Pa - P0) / np.linalg.norm(Pa - P0)
    down = (Pf - Pa) / np.linalg.norm(Pf - Pa)
    ang = float(np.degrees(np.arccos(fall @ down)))
    init9, reb9 = 100 * np.linalg.norm(P0 - Pf), 100 * np.linalg.norm(Pa - Pf)
    note9 = f"0009 clicked-point emulation: ball(0) {b0[0]:.0f},{b0[1]:.0f}@1.321 apex {apex[0]:.0f},{apex[1]:.0f}@1.5795 " \
            f"floor {fl[0]:.0f},{fl[1]:.0f}@2.0285 (fall vs apex->floor {ang:.1f} deg)"
    for q in (2176, 2181, 2186):
        out[q] = (float(init9), note9 + " initial")
    for q in (2178, 2183, 2188):
        out[q] = (float(reb9), note9 + " apex")
    # 0008: depth of the held ball at t=0 from its box width vs t=1.0 s (stated 1.401 m, surface), impact at 1.2 s
    # (stated 1.564, Claude's 'basketball falling' centre at frame 29), apex at 1.5 s (1.5225); the desk point (1.725)
    # is the Claude desk click whose apex->desk direction is most parallel to the fall (t=0 -> impact: the vertical)
    o = obs_px("captured_0008", r"^basketball")
    b0, w0 = o[("basketball initial", 0)]
    w1 = o[("basketball falling", 24)][1]
    d0 = (1.401 + R_BASKET) * w1 / w0 - R_BASKET
    imp = o[("basketball falling", 29)][0]
    apex = o[("basketball apex", 36)][0]
    P0, Pi, Pa = point(*b0, d0), point(*imp, 1.564), point(*apex, 1.5225)
    fall = (Pi - P0) / np.linalg.norm(Pi - P0)
    clicks = []
    for v in ("captured_0008", "captured_0008s", "captured_0008x"):
        for (name, fr), (p, _) in obs_px(v, r"desk").items():
            if p is not None:
                Pd = point(*p, 1.725)
                down = (Pd - Pa) / np.linalg.norm(Pd - Pa)
                clicks.append((float(np.degrees(np.arccos(fall @ down))), v, name, p, Pd))
    clicks.sort(key=lambda c: c[0])
    ang, v, name, p, Pd = clicks[0]
    init8, reb8 = 100 * np.linalg.norm(P0 - Pd), 100 * np.linalg.norm(Pa - Pd)
    note8 = f"0008 clicked-point emulation: ball(0) {b0[0]:.0f},{b0[1]:.0f}@{d0:.3f} (box {w0:.0f}->{w1:.0f} px) apex " \
            f"{apex[0]:.0f},{apex[1]:.0f}@1.5225 desk {p[0]:.0f},{p[1]:.0f}@1.725 ({v} '{name}', {ang:.1f} deg from the fall; " \
            f"others " + ", ".join(f"{c[1][-5:]} '{c[2]}' {c[0]:.0f} deg" for c in clicks[1:]) + ")"
    for q in (2161, 2166, 2171):
        out[q] = (float(init8), note8 + " initial")
    for q in (2163, 2168, 2173):
        out[q] = (float(reb8), note8 + " apex")
    return out


def main():
    t = load_split("test").set_index("qid")
    ft = pd.read_csv(OUT / "family_table.csv").set_index("id")
    base = pd.read_csv(BASE).set_index("id").parsed_value.astype(float)
    nums = stated_numbers(t)
    ft["stated"] = [round(v, 6) in nums for v in ft.p8]
    ft["fam"] = ft.video_id.map(family)
    ft["qn"] = ft.question.str.strip().str.lower()
    ft = ft[ft.kind != "camera_distance"]
    ch = {}   # qid -> (new, rule, note)

    def put(q, val, rule, note):
        r = ft.loc[q]
        if r.overlap or r.stated or q in ch or not np.isfinite(val) or val <= 0:
            return
        if abs(val / r.p8 - 1) < 0.02:
            return
        ch[q] = (float(val), rule, note)

    cur = ft.p8.astype(float).copy()   # values after the rules applied so far (R2 pools these)
    # R3 (explicit, before the generic rules)
    bx = ft.loc[2900, "p8"]
    for q in (2876, 2888):
        put(q, bx, "R3", "0054b family: soccer ball at 1.0 s placed at its 2.0 s depth; 0054bx geometry follows the looming")
        cur[q] = bx
    for (fam, qn), g in ft.groupby(["fam", "qn"]):
        if len(g) < 2:
            continue
        # R1 render copy for direct rows of s/x renders (0009 rebound excluded: the original's 30.07 cm is below the
        # stated-depth bound |1.5795 - 2.0285| = 44.9 cm of a ball-floor distance at 1.92 s)
        orig = g[g.video_id == fam]
        if len(orig):
            ov = float(orig.p8.iloc[0])
            for q, r in g.iterrows():
                own_direct = np.isfinite(r.direct) and abs(r.p8 / r.direct - 1) < 1e-6
                if r.video_id != fam and own_direct and q not in (2183, 2188) and q not in ch:
                    put(q, ov, "R1", f"render copy from {fam} (own direct {r.p8:g})")
                    if not (r.overlap or r.stated):
                        cur[q] = ov
        # R2 family log-median of the current values
        vals = cur[g.index]
        if vals.max() / vals.min() <= SPREAD:
            continue
        med = float(np.exp(np.median(np.log(vals))))
        for q in g.index:
            put(q, med, "R2", f"family log-median of {', '.join(f'{v:g}' for v in vals.round(3))}")
    fam_ch = dict(ch)
    emu = emulate()
    emu_ch = {q: v for q, v in fam_ch.items() if q not in emu}
    for q, (val, note) in emu.items():
        r = ft.loc[q]
        if not (r.overlap or r.stated) and abs(val / r.p8 - 1) >= 0.02:
            emu_ch[q] = (val, "R4", note)
    for name, chs in (("fam", fam_ch), ("emu", emu_ch)):
        write(name, base, chs, t, ft)


def write(name, base, chs, t, ft):
    out = base.copy()
    rows = []
    for q, (val, rule, note) in sorted(chs.items()):
        rows.append(dict(qid=q, video_id=t.loc[q, "video_id"], category=t.loc[q, "category"], question=t.loc[q, "question"],
                         old=base[q], new=val, ratio=val / base[q], rule=rule, note=note))
        out[q] = val
    tmp = OUT / f"_tmp_{name}.csv"
    pd.DataFrame({"id": out.index, "parsed_value": out.values}).to_csv(tmp, index=False)
    dst = ROOT / f"submissions/trackA_cand_labdist_{name}_on_p8.csv"
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), str(tmp), str(dst)], check=True)
    tmp.unlink()
    c = pd.DataFrame(rows)
    c.to_csv(OUT / f"trackA_cand_labdist_{name}_on_p8_changes.csv", index=False)
    chk = pd.read_csv(dst).set_index("id").parsed_value
    diff = ~np.isclose(chk.reindex(base.index), base, rtol=1e-9)
    print(f"{dst.name}: {int(diff.sum())} rows differ from probe 8 "
          f"({t.category.reindex(base.index[diff]).value_counts().to_dict()}), by rule {c.rule.value_counts().to_dict()}")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 70)
    print(c[["qid", "video_id", "category", "old", "new", "ratio", "rule", "question"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
