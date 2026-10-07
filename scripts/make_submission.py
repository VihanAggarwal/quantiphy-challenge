"""Fill the official template's `parsed_value` from a test prediction CSV and check it.

    python scripts/make_submission.py runs/opus_measure/test.csv submissions/opus_measure.csv

Checks: template ids and row order unchanged, every value numeric, finite and non-zero
(the evaluator counts blank / non-numeric / zero as invalid and scores them 0),
file under the portal's 2 MB limit. Missing values are filled with --fallback.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qp.data import load_template  # noqa: E402

MAX_BYTES = 2 * 1024 * 1024


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("predictions")
    ap.add_argument("out")
    ap.add_argument("--fallback", type=float, default=1.0,
                    help="value used where a prediction is missing or unusable")
    args = ap.parse_args()

    tmpl = load_template()
    pred = pd.read_csv(args.predictions)
    pred = pred.rename(columns={pred.columns[0]: "id"}).set_index("id")["parsed_value"]
    extra = set(pred.index) - set(tmpl["id"])
    if extra:
        raise SystemExit(f"{len(extra)} prediction ids are not in the template, e.g. {sorted(extra)[:5]}")

    vals = pd.to_numeric(tmpl["id"].map(pred), errors="coerce").abs()
    bad = vals.isna() | (vals == 0) | ~vals.map(lambda v: math.isfinite(v) if pd.notna(v) else False)
    if bad.any():
        print(f"warning: {int(bad.sum())} rows missing/unusable -> filled with {args.fallback}")
        vals[bad] = args.fallback

    out = tmpl.copy()
    out["parsed_value"] = vals.to_numpy()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)

    check = pd.read_csv(args.out)
    assert list(check["id"]) == list(tmpl["id"]), "id column changed"
    assert list(check.columns) == list(tmpl.columns), "columns changed"
    size = Path(args.out).stat().st_size
    assert size <= MAX_BYTES, f"{size} bytes > 2 MB portal limit"
    print(f"wrote {args.out}: {len(check)} rows, {size / 1024:.0f} KB, ready to upload")


if __name__ == "__main__":
    main()
