"""Build one upload from a base submission plus per-category variants (leaderboard probes).

    python scripts/compose_submission.py submissions/trackA_opus55_high_v2.csv submissions/probe4.csv \
        --cat S2=variants/s2_x.csv --cat D3=variants/d3_y.csv

Each variant CSV (id, parsed_value) contributes ONLY the rows of its category, so one upload
measures up to four independent changes. Checks that every other row equals the base, then
writes through the same template checks as make_submission.py.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qp.data import CATEGORIES, load_test  # noqa: E402


def read_values(path: str) -> pd.Series:
    df = pd.read_csv(path)
    return df.rename(columns={df.columns[0]: "id"}).set_index("id")["parsed_value"].astype(float)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("out")
    ap.add_argument("--cat", action="append", default=[], metavar="CAT=CSV",
                    help="take this category's rows from CSV (repeatable, one per category)")
    args = ap.parse_args()

    cat_of = load_test().set_index("qid")["category"]
    base = read_values(args.base).reindex(cat_of.index)
    out = base.copy()
    seen = set()
    for item in args.cat:
        cat, path = item.split("=", 1)
        if cat not in CATEGORIES or cat in seen:
            raise SystemExit(f"bad or repeated category {cat!r}")
        seen.add(cat)
        var = read_values(path).reindex(cat_of.index)
        rows = cat_of.index[cat_of == cat]
        if var[rows].isna().any():
            raise SystemExit(f"{path}: {int(var[rows].isna().sum())} {cat} rows missing")
        out[rows] = var[rows]
        ch = ~np.isclose(out[rows], base[rows], rtol=1e-9)
        ratio = (out[rows][ch] / base[rows][ch]).abs()
        print(f"{cat}: {int(ch.sum())} of {len(rows)} answers changed (median new/old "
              f"{ratio.median() if ch.any() else float('nan'):.3f}) from {path}")
    other = cat_of.index[~cat_of.isin(seen)]
    assert np.allclose(out[other], base[other], rtol=1e-12, equal_nan=True)

    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": out.index, "parsed_value": out.to_numpy()}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_submission.py"), fh.name, args.out],
                   check=True)
    Path(fh.name).unlink()


if __name__ == "__main__":
    main()
