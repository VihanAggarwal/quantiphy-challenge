"""Probe 8 = probe 7b + four small label-free fixes verified by the 2026-10-11 lever investigation.

    python research/levers_2026-10-11/build_probe8.py

D2 (16 rows):
  a) simulation_0191 + _segmented (box in free fall): rows rescaled by the dense-track prior acceleration
     (1982/1984 px/s^2 vs the pipeline's 1717/1710 from Claude's far-bottom-edge points); 4 sibling clips of the
     same truck and box agree with the new truck length. Applied only while the rows hold the pipeline values.
  b) shark initial speed, simulation_0101/0102/0103 (+ twins): mask fit v0 = 2.036-2.049 m/s; the sibling clip
     simulation_0100 states the boat length (10 m), which on its own gives a = 1.00 m/s^2 (= the stated prior)
     and v0 = 2.00 m/s. Clips repeat their first frame, which the pipeline did not drop.
D3:
  c) lab capture clock (frame drops of the 25 -> 24 fps conversion), full pipeline re-solve with the dense tracks,
     D3 rows only (verifier-corrected file).
  d) lab 3D trajectory fits for families 0020 (free fall measured 9.85 m/s^2) and 0047 (current answers below the
     radial lower bound of its own depth anchors): 15 rows; they win over (c) where both touch a row.
S2, S3: unchanged (= probe 7b).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_test  # noqa: E402

HERE = Path(__file__).resolve().parent
BASE = ROOT / "submissions" / "trackA_probe7b_p5_ens_famext.csv"
OUT = ROOT / "submissions" / "trackA_probe8_p7b_d2fixes_d3labphys.csv"

FREEFALL = {466: 0.866042, 467: 0.866042, 468: 0.866042, 469: 0.866042, 470: 0.866042,
            1913: 0.861835, 1914: 0.861835, 1915: 0.861835, 1916: 0.861835, 1917: 0.861835}
FREEFALL_EXPECT = {466: 2.323259, 467: 1.129540, 468: 9.626765, 469: 4.056077, 470: 0.949841,
                   1913: 2.332499, 1914: 1.114702, 1915: 9.832578, 1916: 4.085095, 1917: 1.005165}


def read(path) -> pd.Series:
    d = pd.read_csv(path)
    return d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"].astype(float)


def main() -> None:
    test = load_test().set_index("qid")
    base = read(BASE).reindex(test.index)
    out = base.copy()
    log = []

    for q, f in FREEFALL.items():                                   # (a)
        assert np.isclose(base[q], FREEFALL_EXPECT[q], rtol=1e-5), (q, base[q])
        out[q] = base[q] * f
        log.append((q, "d2_freefall_0191"))

    shark = read(HERE / "cand_v3b_motion_frozen0.csv")              # (b)
    for q in (191, 196, 202, 1796, 1801, 1807):
        assert ("initial" in test.loc[q, "question"].lower() or "at 0.0s" in test.loc[q, "question"]) and test.loc[q, "category"] == "D2", q
        out[q] = shark[q]
        log.append((q, "d2_shark_v0"))

    clock = read(HERE / "trackA_verify_labclock_dense_on_p7b.csv").reindex(test.index)   # (c)
    ch = test.index[(test.category == "D3") & ~np.isclose(clock, base, rtol=1e-12)]
    out[ch] = clock[ch]
    log += [(q, "d3_lab_capture_clock") for q in ch]

    lab = read(HERE / "trackA_lab3d_strict_reduced_0020_0047.csv").reindex(test.index)  # (d)
    ch = test.index[~np.isclose(lab, base, rtol=1e-12)]
    assert (test.loc[ch, "category"] == "D3").all()
    out[ch] = lab[ch]
    log += [(q, "d3_lab3d_0020_0047") for q in ch]

    lg = pd.DataFrame(log, columns=["id", "fix"]).drop_duplicates("id", keep="last").set_index("id")
    lg["category"] = test.loc[lg.index, "category"]
    lg["video_id"] = test.loc[lg.index, "video_id"]
    lg["old"] = base[lg.index]
    lg["new"] = out[lg.index]
    lg["ratio"] = lg.new / lg.old
    changed = ~np.isclose(out, base, rtol=1e-12)
    assert set(test.index[changed]) <= set(lg.index)
    assert np.isfinite(out).all() and (out > 0).all()
    print(lg.groupby(["category", "fix"]).ratio.describe()[["count", "min", "50%", "max"]].round(3).to_string())
    print(f"changed rows: {int(changed.sum())} (by category: {test.loc[changed, 'category'].value_counts().to_dict()})")
    lg.to_csv(HERE / "probe8_changes.csv")

    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": out.index, "parsed_value": out.to_numpy()}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_submission.py"), fh.name, str(OUT)], check=True)
    Path(fh.name).unlink()


if __name__ == "__main__":
    main()
