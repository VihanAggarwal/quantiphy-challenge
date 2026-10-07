"""Mean Relative Accuracy, matching the official evaluator.py (Paulineli/QuantiPhy).

    pred  = abs(to_numeric(parsed_value, errors="coerce"))
    hit_t = |pred - gt| / gt < 1 - t     for t in {0.1, ..., 0.9, 0.95}
    item  = mean over the 10 thresholds  (blank / non-numeric prediction -> 0)
    score = mean over S2, D2, S3, D3 of the per-category mean item score

So an item gets full credit at <5% relative error, 0.9 at <10%, ... and 0.1 at <90%.
Each category weighs 1/4 regardless of how many questions it has.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .data import CATEGORIES

THRESHOLDS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95)


def item_scores(pred, gt) -> np.ndarray:
    p = pd.to_numeric(pd.Series(list(pred), dtype=object), errors="coerce").abs().to_numpy(float)
    g = np.asarray(gt, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.abs(p - g) / g
        hits = sum((rel < 1 - t).astype(int) for t in THRESHOLDS)
    scores = hits / len(THRESHOLDS)
    scores[np.isnan(g) | (g == 0)] = np.nan
    return scores


def score(df: pd.DataFrame, pred_col: str = "parsed_value") -> dict:
    """`df` needs columns: category, answer, and `pred_col`. Missing predictions score 0."""
    items = item_scores(df[pred_col], df["answer"])
    per_cat = {c: float(np.nanmean(items[(df["category"] == c).to_numpy()]))
               for c in CATEGORIES if (df["category"] == c).any()}
    macro = float(np.mean([per_cat[c] for c in CATEGORIES])) if len(per_cat) == 4 else float("nan")
    return {"mra": macro, "per_category": per_cat, "n": int(np.sum(~np.isnan(items)))}
