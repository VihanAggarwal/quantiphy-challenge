"""Free-fall speed rows of the simulation drop families, emulating the Blender label convention of the paper's
appendix (speed = backward difference of the object origin between consecutive rendered frames).

For an object released at t0 with constant acceleration a (the clip's stated prior), sampled at frames t_k = k/fps:
    label(t_k) = |x_k - x_{k-1}| * fps = a * (t_k - t0 - 1/(2 fps))
t0 = vertex of the pixel parabola of the falling object (track_fall.py), taken from the clean side-view (2D) clips of
the same Blender event (pixel y is affine in the drop there); the 3D views of the same event share it.
Current answers are a * t (Claude's direct continuous kinematics), i.e. 1/(2 fps) + t0 later.

Writes (no API, test inputs only):
  submissions/trackA_cand_ffbd_d3_on_combo.csv     D3 rows only (0201, 0202, 0205, 0206, 0209)
  submissions/trackA_cand_ffbd_d2d3_on_combo.csv   + the D2 sibling clips (0198-0200, 0203, 0204, 0207, 0208)
  research/path85b_phys/changes_ffbd.csv
    .venv/bin/python research/path85b_phys/build_freefall.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402

BASE = ROOT / "submissions/trackA_cand_path85_combo.csv"
T0 = pd.read_csv(ROOT / "research/path85b_phys/fall_t0.csv").set_index("video_id")
# event -> (clips, acceleration, clean side-view clips whose fit gives t0)
EVENTS = {
    "magnifier": (["simulation_0202", "simulation_0203", "simulation_0204", "simulation_0205"], 9.8,
                  ["simulation_0203", "simulation_0204"]),
    "typewriter": (["simulation_0206", "simulation_0207", "simulation_0208", "simulation_0209"], 9.8,
                   ["simulation_0207"]),
    "droplet": (["simulation_0198", "simulation_0199", "simulation_0200", "simulation_0201"], 9.7,
                ["simulation_0199", "simulation_0200"]),
}
N = {"S2": 553, "D2": 1137, "S3": 538, "D3": 933}


def main():
    test = load_split("test").set_index("qid")
    base = pd.read_csv(BASE, float_precision="round_trip")
    cur = base.set_index("id").parsed_value
    rows = []
    for ev, (clips, a, clean) in EVENTS.items():
        assert (T0.loc[clean, "rms"] < 3.0).all()
        t0 = float(T0.loc[clean, "t0"].median())
        for v in clips:
            x = test[test.video_id == v]
            fps = float(x.fps.iloc[0])
            for q, r in x.iterrows():
                m = re.search(r"speed of the .* at time ([0-9.]+)\s*s", r.question)
                if not m:
                    continue
                t = float(m.group(1))
                k = round(t * fps)
                tk = k / fps
                new = a * (tk - t0 - 0.5 / fps)
                rows.append(dict(qid=q, video_id=v, category=r.category, event=ev, t=t, frame=k, t0=t0, a=a,
                                 old=float(cur[q]), new=new, cont=a * t))
    C = pd.DataFrame(rows)
    C["ratio"] = C.new / C.old
    # what each hypothesis implies for the changed rows (item points)
    C["gain_if_bd"] = item_scores(C.new, C.new) - item_scores(C.old, C.new)
    C["gain_if_cont"] = item_scores(C.new, C.cont) - item_scores(C.old, C.cont)
    C.to_csv(ROOT / "research/path85b_phys/changes_ffbd.csv", index=False)
    pd.set_option("display.width", 200)
    print(C.round(4).to_string())
    for name, cats in (("d3", ["D3"]), ("d2d3", ["D2", "D3"])):
        sel = C[C.category.isin(cats)]
        out = base.copy()
        m = out.id.isin(sel.qid)
        out.loc[m, "parsed_value"] = out.loc[m, "id"].map(sel.set_index("qid").new)
        assert len(out) == len(base) and np.isfinite(out.parsed_value).all() and (out.parsed_value > 0).all()
        p = ROOT / f"submissions/trackA_cand_ffbd_{name}_on_combo.csv"
        out.to_csv(p, index=False)
        print(f"\n{p.name}: {m.sum()} rows changed")
        for c, g in sel.groupby("category"):
            print(f"  {c}: {len(g)} rows; item points if bd {g.gain_if_bd.sum():+.1f} (overall {g.gain_if_bd.sum() / (4 * N[c]):+.4f}),"
                  f" if continuous {g.gain_if_cont.sum():+.1f} (overall {g.gain_if_cont.sum() / (4 * N[c]):+.4f})")


if __name__ == "__main__":
    main()
