"""Validation: emulation on vs off per category (labels used for evaluation only).

    .venv/bin/python research/blenderemu/evaluate_val.py <dir with *_off.csv / *_on.csv> [tag ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split  # noqa: E402
from qp.mra import item_scores, score  # noqa: E402


def compare(d: Path, tag: str, split: str) -> dict:
    df = load_split(split)[["qid", "video_id", "category", "answer"]]
    off = pd.read_csv(d / f"{tag}_off.csv").rename(columns={"id": "qid"})
    on = pd.read_csv(d / f"{tag}_on.csv").rename(columns={"id": "qid"})
    m = df.merge(off[["qid", "parsed_value", "geo_value", "method"]], on="qid") \
          .merge(on[["qid", "parsed_value", "geo_value", "flags"]], on="qid", suffixes=("_off", "_on"))
    so, sn = score(m, "parsed_value_off"), score(m, "parsed_value_on")
    m["it_off"], m["it_on"] = item_scores(m.parsed_value_off, m.answer), item_scores(m.parsed_value_on, m.answer)
    ch = ~np.isclose(m.parsed_value_off, m.parsed_value_on, equal_nan=True)
    rows = m[ch]
    print(f"\n== {tag}: MRA off {so['mra']:.4f} on {sn['mra']:.4f} (d {sn['mra'] - so['mra']:+.4f}); "
          f"changed answers {int(ch.sum())}, geo values changed "
          f"{int((~np.isclose(m.geo_value_off, m.geo_value_on, equal_nan=True)).sum())}")
    for c in so["per_category"]:
        r = rows[rows.category == c]
        ratio = (r.parsed_value_on / r.parsed_value_off)
        print(f"  {c}: off {so['per_category'][c]:.4f} on {sn['per_category'][c]:.4f} "
              f"(d {sn['per_category'][c] - so['per_category'][c]:+.4f}) | changed {len(r)}, "
              f"median ratio {ratio.median() if len(r) else float('nan'):.4f}, item d sum {(r.it_on - r.it_off).sum():+.2f}")
    if len(rows):
        # does the change move toward the label? log(on/off) vs log(gt/off)
        lr, lg = np.log(rows.parsed_value_on / rows.parsed_value_off), np.log(rows.answer / rows.parsed_value_off)
        print(f"  toward GT: {int((np.sign(lr) == np.sign(lg)).sum())} of {len(rows)}; "
              f"median |log err| off {np.median(np.abs(lg)):.4f} on {np.median(np.abs(np.log(rows.answer / rows.parsed_value_on))):.4f}")
        for r in rows.itertuples():
            print(f"    qid {r.qid} {r.video_id} {r.category}: gt {r.answer:.4g} off {r.parsed_value_off:.4g} "
                  f"on {r.parsed_value_on:.4g} (x{r.parsed_value_on / r.parsed_value_off:.4f}) item {r.it_off:.2f}->{r.it_on:.2f}")
    return {"tag": tag, "off": so, "on": sn, "changed": int(ch.sum())}


if __name__ == "__main__":
    d = Path(sys.argv[1])
    for tag in sys.argv[2:]:
        split = "val_hires" if tag.startswith("val_hires") else "val"
        compare(d, tag, split)
