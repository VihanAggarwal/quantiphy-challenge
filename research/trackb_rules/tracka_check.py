"""No-damage check of the extended rules on the Track A best file (submissions/trackA_best_p16_p8_labnoiseS3D3.csv).

Runs the Track B preset (and each extended rule alone) on the Track A test answers; reports rows changed per rule and
category and the size of the changes, and scores the test rows that repeat a validation question (same clip,
normalised question; labels read here for evaluation only, these rows are unscored on the leaderboard).

    .venv/bin/python research/trackb_rules/tracka_check.py"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import CATS, ROOT, load_split, load_validation, pp  # noqa: E402
from qp.mra import item_scores  # noqa: E402

A = ROOT / "submissions/trackA_best_p16_p8_labnoiseS3D3.csv"

if __name__ == "__main__":
    t = load_split("test")
    T = t.set_index("qid")
    a = pd.read_csv(A).set_index("id").parsed_value.astype(float).reindex(t.qid)
    val = load_validation()
    vk = dict(zip(zip(val.video_id, val.question.map(pp.norm_question)), val.answer))
    gt = pd.Series([vk.get((v, pp.norm_question(q)), np.nan) for v, q in zip(t.video_id, t.question)], index=t.qid)
    gt = gt.dropna()
    pre = pp.PRESETS["trackb"]
    configs = {r: ((r,), {k: v for k, v in pre["options"].items() if k == r}, pre["speed_guard"])
               for r in pp.EXTENDED_RULES}
    configs["facts (guard 0)"] = (("facts",), {}, 0.0)
    configs["preset trackb"] = (pre["rules"], pre["options"], pre["speed_guard"])
    configs["preset trackb, guards 2x"] = (pre["rules"], {**pre["options"], "motionfam": {"guard": 2.0}}, 2.0)

    def items(p):
        s = pd.Series(item_scores(p.reindex(gt.index).to_numpy(), gt.to_numpy()), index=gt.index)
        return {c: s[T.category[gt.index] == c].mean() for c in CATS}, s
    b, bs = items(a)
    print(f"{len(gt)} test rows repeat a validation question; Track A best on them: " +
          " ".join(f"{c} {b[c]:.3f}" for c in CATS) + f" | mean {bs.mean():.4f}")
    for name, (rules, opts, sg) in configs.items():
        new, log = pp.apply_rules(a, t, rules=rules, speed_guard=sg, options=opts)
        ch = pd.Series(~np.isclose(new, a, rtol=1e-9), index=a.index)
        lr = np.abs(np.log(new[ch] / a[ch]))
        s, ss = items(new)
        print(f"{name:32s} changed {int(ch.sum()):4d} {T.category[ch[ch].index].value_counts().reindex(list(CATS)).fillna(0).astype(int).to_dict()}"
              f" median |dlog| {np.median(lr) if len(lr) else 0:.3f}, >10%: {int((lr > np.log(1.1)).sum())}"
              f" | overlap rows changed {int(ch.reindex(gt.index).sum())}, item mean {bs.mean():.4f}->{ss.mean():.4f} "
              + " ".join(f"{c} {s[c] - b[c]:+.3f}" for c in CATS))
