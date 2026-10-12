"""Leave-one-fact-out check of the K (per-clip scale) rule on stated facts (test inputs only): each fact row's
answer is rescaled by median({0} U log ratios of the clip's OTHER stated facts, different statement lines) and
scored against its stated value."""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import combined, pp  # noqa: E402
from qp.mra import item_scores  # noqa: E402

if __name__ == "__main__":
    df, pred, _, _, _ = combined()
    T = df.set_index("qid")
    _, log = pp.apply_rules(pred, df, rules=("facts",))
    f = log[log.applied].copy()
    f["video"] = f.qid.map(T.video_id)
    f["cat"] = f.qid.map(T.category)
    from qp.open.qwen_vl import parse_question_text
    f["kind"] = f.qid.map(lambda q: parse_question_text(T.question[q])["kind"])
    f["lk"] = np.log(f.new / f.old)
    rows = []
    for v, g in f.groupby("video"):
        for r in g.itertuples():
            if r.kind not in ("size", "speed"):
                continue
            oth = g[(g.reason != r.reason) & g.kind.isin(["size", "speed"])]
            if not len(oth):
                continue
            k = float(np.median(np.r_[0.0, oth.lk.to_numpy()]))
            rows.append(dict(qid=r.qid, cat=r.cat, kind=r.kind, raw=item_scores([r.old], [r.new])[0],
                             K=item_scores([r.old * np.exp(k)], [r.new])[0], n_other=len(oth)))
    R = pd.DataFrame(rows)
    print(f"{len(R)} fact rows with another fact in their clip")
    print(R.groupby("cat")[["raw", "K"]].agg(["mean", "size"]).round(3))
    print(R.groupby(["cat", "kind"])[["raw", "K"]].mean().round(3))
