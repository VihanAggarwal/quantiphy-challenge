"""Score geometry variants (out/val/<tag>.csv) on validation with the direct fallback (caw, as run_geometry).

    .venv/bin/python research/trackb_dense/evaluate.py tag1 tag2 ... [--by source|tk|pk]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tbcommon import CATS, OUT, RUN, base_preds, item, questions, read_csv, report, with_fallback  # noqa: E402
from tbcommon import specs as load_specs  # noqa: E402


def geo_method(split: str, tag: str, df: pd.DataFrame, direct: pd.Series, max_disagree=10.0, raw=False):
    g = pd.read_csv(OUT / split / f"{tag}.csv").set_index("id").reindex(df.qid)
    if raw:
        return g.geo_value
    sp = load_specs(split)
    kinds = pd.Series({q: sp[q].target.kind for q in df.qid if q in sp})
    return with_fallback(g.geo_value, g.geo_si, kinds, direct, max_disagree)


def breakdown(name, pred, val, by):
    s = item(pred.reindex(val.qid).set_axis(val.index), val.answer)
    t = val.assign(s=s).groupby(["category", by]).s.agg(["mean", "size"]).round(3)
    print(name, t.unstack(0).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="*")
    ap.add_argument("--by", default="")
    ap.add_argument("--raw", action="store_true", help="no direct fallback")
    a = ap.parse_args()
    val = questions("val")
    base = base_preds("val", val.qid)
    for m, p in base.items():
        report(m, p, val)
    for tag in a.tags:
        p = geo_method("val", tag, val, base["caw"], raw=a.raw)
        report(tag, p, val)
        if a.by:
            breakdown(tag, p, val, a.by)
