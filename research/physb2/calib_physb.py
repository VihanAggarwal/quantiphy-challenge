"""Which PHYSB clips were physical? Expected item gain of the PHYSB rows per clip under 'physical' vs 'in-clip'
labels (lognormal label scatter SIG), against the observed D2 +.009 (1137 scored D2 rows -> 10.2 +- 0.6 item pts).
    .venv/bin/python research/physb2/calib_physb.py"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.mra import item_scores  # noqa: E402

pb = pd.read_csv(ROOT / "research/internet/out/log_physb.csv")
pb["clip"] = pb.note.str.extract(r"(internet_\d+)")
po = pb.note.str.extract(r"^([\d.e+-]+) -> ([\d.e+-]+)").astype(float)
pb["old"], pb["new"] = po[0], po[1]
rng = np.random.default_rng(0)


def e(pred, truth, sig, n=3000):
    g = truth[None, :] * np.exp(rng.normal(0, sig, (n, len(truth))))
    return np.array([item_scores(pred, gi) for gi in g]).mean(axis=0)


obs = 0.009 * 1137
for sig in (0.05, 0.08, 0.12, 0.18):
    gp = {c: float((e(g.new.values, g.new.values, sig) - e(g.old.values, g.new.values, sig)).sum()) for c, g in pb.groupby("clip")}
    gi = {c: float((e(g.new.values, g.old.values, sig) - e(g.old.values, g.old.values, sig)).sum()) for c, g in pb.groupby("clip")}
    print(f"SIG {sig}: per clip if physical {', '.join(f'{c[-4:]} {v:+.1f}' for c, v in gp.items())}; "
          f"if in-clip {', '.join(f'{c[-4:]} {v:+.1f}' for c, v in gi.items())}")
    fits = []
    for mask in itertools.product([0, 1], repeat=len(gp)):
        tot = sum(gp[c] if m else gi[c] for c, m in zip(gp, mask))
        fits.append((abs(tot - obs), tot, "".join(c[-2:] + ("P " if m else "I ") for c, m in zip(gp, mask))))
    for d, tot, lab in sorted(fits)[:3]:
        print(f"    {lab} total {tot:+.1f} (obs {obs:.1f})")
