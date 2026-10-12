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
            put(qid, 0.178, "EL", "0014 book long side on the rectified table plane: 17.6 / 18.0 cm")
            done.add(qid)
    # RP render pooling (not for props the base already pools across events)
    pooled_keys = {(s.loc[q, "obj"], s.loc[q, "dim"]) for q in s.index if pooled[q]}
    for (ev, qn), g in s.groupby(["event", "qn"]):
        if len(g) < 2:
            continue
        vals = new[g.index] * g.usc
        if any(q in done for q in g.index) or (g.obj.iloc[0], g.dim.iloc[0]) in pooled_keys:
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
    for variant in ("main", "wb"):
        new, log = build(variant)
        log.to_csv(OUT / f"changes_{variant}.csv", index=False)
        print(f"== {variant}: {len(log)} rows changed")
        print(log.groupby(["rule", "cat"]).agg(n=("qid", "size"), med_ratio=("ratio", "median")).round(3))
        print(log[["qid", "video", "cat", "rule", "obj", "dim", "p8", "new", "ratio"]].round(3).to_string())
        write(new, variant)
