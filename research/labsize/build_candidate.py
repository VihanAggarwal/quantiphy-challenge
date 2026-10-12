"""Lab SIZE candidates on probe 8 (research/labsize). Test inputs only; validation labels are read only by
evaluate_val.py. Every other row is probe 8.

TB  table: the lab table (one prop: same wood top, rounded corners, single pole in every table clip) measured by
    metric rectification of its top face in 6 views (table_views.py: corners refined on the uniform-background
    renders, plane scale from the clips' depth_info anchors, f 711-763 px): long side 74.7-77.2 cm, short side
    59.6-60.9 cm (per view 74-79 / 58-63). Table "length" -> 76.0 cm, "width" -> 60.3 cm (+ the 0013 "desk",
    the same table). Probe 8 pooled 68/70 and 57.6 (Claude's direct answers; the receding side is foreshortened).
BI  ball identity: a generic "ball" that the frames show is a prop whose size a test prior states:
      captured_0001 ball = the yellow tennis ball (felt, seam; tennis ball 6.7 cm stated in 0029/0031/0032/0034),
      captured_0010/X/s ball = the red ball hung on a string (pendulum, as in 0027 whose prior states the red
        ball = 7 cm; also 0030),
      captured_0054a/b (+renders) "orange ball" = the basketball (black seams; 23.2 cm stated in 0035a/b priors).
EL  elevated camera, captured_0014 (camera 91 cm above the table top): the cup's height is seen at
    sin(ray, table normal) = 0.891 -> median of renders / 0.891; flat objects measured on the rectified table plane
    (scale x0.970 so the table there matches the 6-view consensus): book long side 17.8 -> 17.3 cm (probe 8: 12.0-12.8,
    its long side recedes), pen 15.4 -> 14.9 cm for the pen of 0013/0014 (probe 8 pooled 12.1 from 0013's
    foreshortened view; 0014's own fronto-parallel geometry was 14.8-15.5). The light-blue notebook (same prop in
    0014/0023/0024: cover colour, elastic, page block) has one thickness: median of its 9 renders (1.46 cm; 0024 read
    1.00/1.05 from an elevated side view).
SP  (variant _s3p, S3 only) scene 0037-0040 (one camera set-up, table props): its stated size priors read high
    in all 12 renders (ping pong ball +5.5..+10.6%, credit card +7.4..+13.8%; Claude's card extent equals the
    segmented card, and the depth anchors agree on the table plane within +-3%), and Claude's direct answers run
    8-12% below geometry for these props (poker tower 9.2-10.1 vs 10.4: a tower of two leaning 8.9 cm playing
    cards cannot exceed 8.9 cm). Camera geometry and the stated priors disagree by ~8.5%, so these S3 answers move
    halfway (x0.958): if either calibration is right the error stays under ~4.5%.
RP  render pooling: X, Xs, Xx are pixel-aligned renders of one event (backgrounds replaced), so a question asked
    in each has one label; rows that are not stated facts / family pools take the median of the renders' answers
    when they spread by more than 5%.
WB  (variant _wb) whiteboard of captured_0062: self-rectification of the board lying on the floor (frame 34,
    depth 2.815 m at 1.4 s) in the base and x renders: 85.7 x 64.0 cm (s render 83.8 x 75.7, back corners
    blurred) -> length 85.7, width 64.0 (probe 8: 83-98 x 46-48, the board's receding side foreshortened).

    .venv/bin/python research/labsize/build_candidate.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import BASE, ROOT, read_sub, render_event, table  # noqa: E402

OUT = Path(__file__).parent / "out"
UNIT = {"cm": 1e-2, "mm": 1e-3, "m": 1.0}
LAB_STATED_SI = {0.232, 0.04, 0.07, 0.067, 0.0856}   # sizes stated in lab test priors
TABLE_LONG, TABLE_SHORT = 0.760, 0.603
WB_LONG, WB_SHORT = 0.857, 0.640
SCENE_3740 = {"captured_0037", "captured_0038", "captured_0039", "captured_0040"}
SP_FACTOR = float(np.exp(-0.0852 / 2))   # sizeconv/out/lab_priors_test.csv, 12 renders of 0037-0040
# captured_0014x plane scale vs the table consensus: the table measures 77.2 x 63.1 there (f 722) vs 76.0 x 60.3
K0014 = float(np.sqrt(76.0 / 77.2 * 60.3 / 63.1))


def lab_size_rows():
    t = table()
    s = t[t.kind == "size"].copy()
    s["obj"] = s.objs.map(lambda o: str(o[0]).lower() if o else "")
    s["event"] = s.video_id.map(render_event)
    s["qn"] = s.question.str.strip().str.lower()
    s["usc"] = s.target_unit.map(UNIT)
    return s


def protected(s, p8):
    si = (p8.reindex(s.index) * s.usc).round(6)
    stated = si.isin({round(x, 6) for x in LAB_STATED_SI})
    # family pool: the same value in >= 2 events
    ev = s.assign(si=si.round(9)).groupby("si").event.nunique()
    pooled = si.round(9).map(ev) >= 2
    return stated | pooled, stated, pooled


def build(variant=""):
    base = read_sub(BASE)
    p8 = base.parsed_value.astype(float)
    new = p8.copy()
    s = lab_size_rows()
    prot, stated, pooled = protected(s, p8)
    log = []

    def put(qid, si, rule, why):
        v = si / s.loc[qid, "usc"]
        log.append(dict(qid=qid, video=s.loc[qid, "video_id"], cat=s.loc[qid, "category"], rule=rule,
                        obj=s.loc[qid, "obj"], dim=s.loc[qid, "dim"], unit=s.loc[qid, "target_unit"],
                        p8=p8[qid], new=v, ratio=v / p8[qid], stated=bool(stated[qid]), pooled=bool(pooled[qid]),
                        why=why))
        new[qid] = v

    done = set()
    # TB table
    for qid, r in s.iterrows():
        if re.fullmatch(r"(the )?(table( in the video)?|desk)", r.obj) and r.dim in ("length", "width"):
            put(qid, TABLE_LONG if r.dim == "length" else TABLE_SHORT, "TB",
                "lab table rectified in 6 views: 74.7-77.2 x 59.6-60.9 cm")
            done.add(qid)
    # BI ball identity
    for qid, r in s.iterrows():
        ev = r.event
        if ev == "captured_0001" and r.obj == "ball":
            put(qid, 0.067, "BI", "the ball is the yellow tennis ball (tennis ball 6.7 cm stated in 0029/0031/0032/0034)")
        elif ev == "captured_0010" and r.obj == "ball":
            put(qid, 0.07, "BI", "red ball on a string = 0027's red ball (7 cm stated in 0027/0030)")
        elif ev in ("captured_0054a", "captured_0054b") and r.obj == "orange ball":
            put(qid, 0.232, "BI", "orange ball = the basketball (23.2 cm stated in 0035a/b)")
        else:
            continue
        done.add(qid)
    # WB whiteboard (variant)
    if "wb" in variant:
        for qid, r in s.iterrows():
            if r.event == "captured_0062" and r.obj == "whiteboard" and r.dim in ("length", "width"):
                put(qid, WB_LONG if r.dim == "length" else WB_SHORT, "WB",
                    "whiteboard self-rectified on the floor (base/x renders): 85.7 x 64.0 cm")
                done.add(qid)
    # EL elevated camera (captured_0014: camera 91 cm above the table top, rectified table plane): an upright
    # object's height is seen at sin(ray, table normal) = 0.891 (cup); the book lying flat has its long side
    # receding: plane-based length 17.6 / 18.0 cm on its two long edges (flat.py) vs 12.0-12.8 fronto-parallel.
    for qid, r in s.iterrows():
        if r.event == "captured_0014" and r.obj == "cup" and r.dim == "height":
            ev = s[(s.event == r.event) & (s.qn == r.qn)].index
            med = float(np.exp(np.median(np.log(p8[ev] * s.usc[ev]))))
            put(qid, med / 0.891, "EL", "0014 cup height / sin(ray, table normal)=0.891 (median of renders)")
            done.add(qid)
        elif r.event == "captured_0014" and r.obj == "book" and r.dim == "length":
            put(qid, 0.178 * K0014, "EL", "0014 book long side on the rectified table plane: 17.6 / 18.0 cm x0.970")
            done.add(qid)
        elif r.event in ("captured_0014", "captured_0023", "captured_0024") and r.obj == "book" and r.dim == "height":
            ev = s[s.event.isin(["captured_0014", "captured_0023", "captured_0024"]) & (s.obj == "book") & (s.dim == "height")].index
            med = float(np.median(p8[ev] * s.usc[ev]))
            put(qid, med, "EL", "light-blue notebook thickness pooled over 0014/0023/0024 (9 renders, median)")
            done.add(qid)
        elif r.event in ("captured_0013", "captured_0014") and r.obj == "pen" and r.dim == "length":
            put(qid, 0.154 * K0014, "EL", "pen (0013/0014, one prop) on the 0014 table plane: 15.4 cm x0.970")
            done.add(qid)
    # SP (variant _s3p) S3 scene 0037-0040: hedge halfway (in log) toward the stated priors' scale
    if "s3p" in variant:
        for qid, r in s.iterrows():
            if r.category == "S3" and r.event in SCENE_3740 and not stated[qid] and qid not in done:
                put(qid, p8[qid] * r.usc * SP_FACTOR, "SP",
                    "0037-0040 stated priors (ping pong ball, credit card; 12 renders) read +5.5..+13.8% "
                    "(median log +0.085) through the same geometry: x exp(-0.085/2)")
                done.add(qid)
    # RP render pooling (not for props the base already pools across events)
    pooled_keys = {(s.loc[q, "obj"], s.loc[q, "dim"]) for q in s.index if pooled[q]}
    for (ev, qn), g in s.groupby(["event", "qn"]):
        if len(g) < 2:
            continue
        vals = new[g.index] * g.usc
        if any(q in done for q in g.index) or (g.obj.iloc[0], g.dim.iloc[0]) in pooled_keys:
            continue
        if "rebounce" in qn or "maximum height" in qn:  # bounce heights: motion, research/labdist's rows
            continue
        free = [q for q in g.index if not prot[q]]
        if not free:
            continue
        med = float(np.exp(np.median(np.log(vals))))
        if np.ptp(np.log(vals)) <= 0.05:
            continue
        for q in free:
            if abs(np.log(vals[q] / med)) > 1e-9:
                put(q, med, "RP", f"median of {len(g)} renders " + " ".join(f"{x / g.usc.iloc[0]:.3g}" for x in vals))
    return new, pd.DataFrame(log)


def write(new, name):
    pred = OUT / f"pred_{name}.csv"
    pd.DataFrame({"id": new.index, "parsed_value": new.values}).to_csv(pred, index=False)
    sub = ROOT / f"submissions/trackA_cand_labsize_{name}_on_p8.csv"
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), str(pred), str(sub)], check=True)
    return sub


if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300); pd.set_option("display.max_colwidth", 60)
    for variant in ("main", "wb", "s3p"):
        new, log = build(variant)
        log.to_csv(OUT / f"changes_{variant}.csv", index=False)
        print(f"== {variant}: {len(log)} rows changed")
        print(log.groupby(["rule", "cat"]).agg(n=("qid", "size"), med_ratio=("ratio", "median")).round(3))
        print(log[["qid", "video", "cat", "rule", "obj", "dim", "p8", "new", "ratio"]].round(3).to_string())
        write(new, variant)
