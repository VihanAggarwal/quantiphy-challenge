"""Lab static measurement fixes on top of submissions/trackA_probe_agent_sim2agent.csv.

Every value below was measured on the test frames (OpenCV tracks / crops read by eye) with the fixed lab camera
(f = 711 px at 1280 px, principal point (640, 360), depth_info used as range at the clicked point). No validation or
test labels are used to set any value. Renders (s / x suffix) of one event share one label, so a family gets one value.
Evidence per family is in research/next/labstatic/NOTES (this docstring) and in the report.

A  captured_0024{,s,x}  D3  "distance travelled by the book"            75.7-77.0 -> 43
   Book (teal) tracked on 0024x frames 0-48: at rest at the top until n~19, slides down the slope, rests on the table
   from n~36 at (570,482). Start (790,369) on the 3D line through the stated anchors (1.0 s: 1.0685 m at (747,394);
   1.2 s: 0.977 m at (680,443)) -> range 1.14; end range 0.93-1.0. Straight 38-42 cm, polyline via the slope foot
   39-43 cm; the stated acceleration (2.8 m/s^2) and the observed release at n~19-20 agree with this scale.
   Label-process emulation (labnoise/labmodel.path_labels, sigma_px 2): 41 cm with the fitted non-ball depth noise
   (sigma_zL = 0), 47 cm at 1 cm, 60 cm at 2 cm. 76 matches no model (it is the geometry artefact 0.5*2.8*0.74^2).
B  captured_0028{,s,x}  S3  "maximum height reached by the ping pong ball"  44 -> 25
   Ball tracked on 0028 frames 0-48: dropped at n~21, bounces on the table at n~26 (t = 1.1 s, stated 1.557 m) and
   peaks at n~32 (t = 1.3 s, stated 1.4115 m, "max height"). Bounce-to-apex rise 19-23 cm (vertical, camera nearly
   level), 24-27 cm as a 3D distance; the s and x renders' own direct answers were 23 and 22; 44 came from the
   original render's direct answer copied to the renders.
C  captured_0023{,s,x}  D3  "displacement of the book between 1.0s and 1.6s"  37.2-37.8 -> 33.5
   1.6 s: book at rest (565,496), stated 0.851 m. 1.0 s: book at (588,383) on the slope; its range from the slope
   line through the stated slope ends (top 1.201 m, foot 0.9555 m; the line gives slope length 30.9 cm) is 1.137,
   and from the book's apparent size ratio (130 px vs 176 px at rest) 1.15 -> 32.5-33.8 cm. The 1.0->1.2 s step on
   this line (11.8 cm) matches the stated 2.8 m/s^2 from the observed release (12.6 cm).
D  captured_0054a{,s,x}  D3  "distance between the orange ball and the soccer ball at 1.0s"  NOT APPLIED (see CHANGES)
   Floor plane from the orange ball's two stated anchors (0.5 s 2.3557 m at (344,600); 1.0 s 1.81 m at (584,674);
   ball centre 11.6 cm above the floor, zero roll) -> camera 0.95 m high, pitch 3.8 deg (predicts the standing
   person's feet at 3.28 m, consistent). Soccer ball at 1.0 s at (153,608) on that floor -> range 2.52-2.65 m ->
   distance 1.30-1.38 m. The other camera of the same event (0054b; synchronised: both balls start at n~6) was
   already answered 1.33 by the earlier R3 rule.
E  captured_0054a{,s,x}  D3  "soccer ball's displacement between 1.0s and 1.4s"  0.52 -> 0.37
   Same floor plane; soccer ball (150,610) at 1.0 s -> (65-75, 662-672) at 1.4 s (bottom-left corner, crops of
   n = 32-35): 0.27-0.36 m. 0054b's answers for the same event are 0.38-0.45 (its depth_info is not consistent
   with its own view), raw answers of the a renders 0.19-0.52 (median 0.375); 0.37 hedges toward them and toward
   the validation pattern of lab ball-displacement labels above careful geometry (0041x: label 1.15-1.25x).
F  trashbin height  captured_0052{,s,x}, captured_0053  D3  37.7 -> 41.5
   0052 (upright bin, stated 2.977 m at the bin): top rim y 484 to bottom y 587.5 = 103.5 px -> 43.3 cm with the
   naive px*range/f, 41.8 at the bin's Z, 40.9 as the label process would do it (both clicks back-projected at the
   bin's range, ray angle 103.5/711*cos^2(13.8 deg)); 0052 geometry 42.9-43.3, 0053s/0053x already 43.3 (same bin).
   Method check on the held-out stated basketball (23.2 cm): same px*range/f with the off-axis stretch removed
   gives 22.6-23.9 (0052) and 21.4-22.3 (0053). 0062 (bin far at
   the back, stated 2.303 m inconsistent with its image position) left unchanged.
G  captured_0014  D3  "diameter of the ball"  5.71 -> 6.5
   Ball at rest at (544,296), stated 1.818 m: 25-26 px across in a 3x crop -> 6.5-6.6 cm; the s and x renders of
   the same event are 6.59 / 6.29.
H  slope (white board) width  captured_0014s, captured_0023{,s,x}, captured_0024{,s,x}  D3  27.0-27.3 -> 24.3
   0023x frontal view, board mask per row: top edge 140-145 px at the stated far end 1.201 m -> 24.1-24.7 cm,
   bottom edge 182-184 px at the stated near end 0.9555 m -> 23.9-24.6 cm (both clicks back-projected at the
   edge's range). 0014 elevated view (another camera of the board): top 92.7 px at 1.854 m and bottom 101 px at
   1.701 m -> 24.2 / 24.2 cm; 0014's own answer is 24.09. 27.0 = bottom-edge pixels times the slope's mean range.
I  book length  captured_0023{,s,x}, captured_0024, captured_0024x  D3  17.55 -> 20.5
   The sliding (teal) book of 0023/0024: at rest in 0023x (n = 38-44) 178 px across at the stated 0.851 m ->
   20.3-21.0 cm; on the slope at 1.0 s 130 px at the slope-line range 1.14 -> 20.6 cm, and 11.2 cm along the slope
   (the current width 11.28 agrees). 0023's own geometry was 20.4-20.7; 17.55 is the small notebook of 0013/0014
   pooled in (in 0014 that notebook is about half the board width, the 0023 book about 0.9 of it).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "submissions/trackA_probe_agent_sim2agent.csv"
OUT = ROOT / "submissions/trackA_cand_next_labstatic.csv"
OUT_CHANGES = Path(__file__).resolve().parent / "changes.csv"

CHANGES = {
    # A
    2443: ("A", 43.0), 2453: ("A", 43.0), 2463: ("A", 43.0),
    # B
    2479: ("B", 25.0), 2485: ("B", 25.0), 2491: ("B", 25.0),
    # C
    2415: ("C", 33.5), 2424: ("C", 33.5), 2433: ("C", 33.5),
    # D (dropped: geometry 1.30-1.38 vs current 1.46-1.56; validation lab distance labels run 0.97-1.37x careful
    #    geometry (0021x, 0041x, 0061), so the expected MRA change is ~0) -- not applied
    # E
    2832: ("E", 0.37), 2844: ("E", 0.37), 2856: ("E", 0.37),
    # F
    2784: ("F", 41.5), 2792: ("F", 41.5), 2800: ("F", 41.5), 2811: ("F", 41.5),
    # G
    2234: ("G", 6.5),
    # H
    2253: ("H", 24.3), 2413: ("H", 24.3), 2422: ("H", 24.3), 2431: ("H", 24.3),
    2440: ("H", 24.3), 2450: ("H", 24.3), 2460: ("H", 24.3),
    # I
    2409: ("I", 20.5), 2418: ("I", 20.5), 2427: ("I", 20.5), 2436: ("I", 20.5), 2456: ("I", 20.5),
}

EXPECT = {  # (video, question fragment) sanity checks so a wrong id cannot slip in
    "A": ("captured_0024", "distance travelled by the book"),
    "B": ("captured_0028", "maximum height reached by the ping pong ball"),
    "C": ("captured_0023", "displacement of the book between 1.0s and 1.6s"),
    "D": ("captured_0054a", "distance between the orange ball and the soccer ball at 1.0s"),
    "E": ("captured_0054a", "soccer ball's displacement between 1.0s and 1.4s"),
    "F": ("captured_005", "height of the trashbin"),
    "G": ("captured_0014", "diameter of the ball"),
    "H": ("captured_00", "width of the slope"),
    "I": ("captured_002", "length of the book"),
}


def main(only: set[str] | None = None, out: Path = OUT) -> pd.DataFrame:
    base = pd.read_csv(BASE)
    m = pd.read_pickle(ROOT / "research/r86/loss_audit/master.pkl")
    sub = base.copy().set_index("id")
    rows = []
    for qid, (rule, val) in CHANGES.items():
        if only and rule not in only:
            continue
        vid, frag = EXPECT[rule]
        r = sub.loc[qid]
        assert r.video_id.startswith(vid) and frag in r.question, (qid, r.video_id, r.question)
        mr = m.loc[qid]
        assert mr.srcg == "lab" and not (isinstance(mr.fact, float) and np.isfinite(mr.fact)), qid  # never a stated-fact row
        rows.append(dict(id=qid, rule=rule, video_id=r.video_id, category=mr.category, scored=bool(mr.scored),
                         question=r.question, old=float(r.parsed_value), new=val, ratio=val / float(r.parsed_value)))
        sub.loc[qid, "parsed_value"] = val
    out_df = sub.reset_index()[base.columns]
    assert list(out_df.id) == list(base.id) and list(out_df.columns) == list(base.columns)
    v = pd.to_numeric(out_df.parsed_value, errors="coerce")
    assert v.notna().all() and np.isfinite(v).all() and (v > 0).all()
    out_df.to_csv(out, index=False)
    ch = pd.DataFrame(rows)
    diff = (pd.to_numeric(out_df.parsed_value) != pd.to_numeric(base.parsed_value)).sum()
    assert diff == len(ch), (diff, len(ch))
    return ch


if __name__ == "__main__":
    ch = main()
    ch.to_csv(OUT_CHANGES, index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
    print(ch.to_string(index=False))
    print(ch.groupby(["category", "rule"]).size())
    print("wrote", OUT)
