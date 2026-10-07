"""Score prediction CSVs (columns: id, parsed_value) on the validation set.

    python scripts/score.py runs/*/val.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qp.data import load_validation  # noqa: E402
from qp.mra import score  # noqa: E402


def main(paths: list[str]) -> None:
    gt = load_validation()
    rows = []
    for p in paths:
        pred = pd.read_csv(p)
        merged = gt.merge(pred.rename(columns={pred.columns[0]: "qid"})[["qid", "parsed_value"]],
                          on="qid", how="left")
        s = score(merged)
        rows.append({"file": p, "MRA": s["mra"], **s["per_category"],
                     "missing": int(merged.parsed_value.isna().sum())})
    print(pd.DataFrame(rows).round(4).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1:])
