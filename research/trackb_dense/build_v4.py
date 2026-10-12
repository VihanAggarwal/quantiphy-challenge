"""Build submissions/trackB_v4.csv (Track B, open weights only) and its validation estimate.

    .venv/bin/python research/trackb_dense/build_v4.py [--sets NAME] [--no-labnoise] [--out submissions/trackB_v4.csv]

1. Per category, the log-median of the member set (candidates.SETS[NAME]) over the open-model methods
   (tbcommon.BASE + the re-solved geometry variants of out/<split>/, each with run_open_vlm's CaW fallback).
2. qp.postprocess preset "trackb" (model-free family rules; labels never read).
3. S3 lab motion rows (speed / path length / displacement; rows that received a stated fact excluded): the lab
   label-noise emulator factor (labnoise_open.factors; 3D tracks from Qwen's boxes with the fixed lab camera,
   noise sigma_z 2 cm fitted on the test speed priors measured on those tracks).
4. scripts/make_submission.py.
Validation: the same three steps on the validation questions put back into the test question table (as
research/trackb_rules/common.combined does), scored against the validation labels.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import labnoise_open as LN  # noqa: E402
from candidates import SETS  # noqa: E402
from select_sets import all_methods  # noqa: E402
from tbcommon import CATS, ROOT, item, log_median, questions  # noqa: E402
from qp import postprocess as pp  # noqa: E402

VAL_OFFSET = 100000
SZ_B, SZ_L = 0.02, 0.02          # labnoise_open fit on test priors (Qwen tracks): sigma_zb 0.02, sigma_zL 0.02


def raw_answers(split: str, sets: dict) -> pd.Series:
    df = questions(split)
    P = all_methods(split, df)
    out = pd.Series(np.nan, index=df.index)
    for c in CATS:
        m = (df.category == c).to_numpy()
        out[m] = log_median([P[x] for x in sets[c]])[m]
    return pd.Series(out.to_numpy(), index=df.qid.to_numpy())


def table(test: pd.DataFrame, val: pd.DataFrame):
    """Combined question table: test rows (minus those repeating a validation question) + validation rows."""
    vkey = set(zip(val.video_id, val.question.map(pp.norm_question)))
    dup = np.array([(v, pp.norm_question(q)) in vkey for v, q in zip(test.video_id, test.question)])
    paths = dict(zip(test.video_id, test.video_path))
    v2 = val.drop(columns=["answer"]).copy()
    v2["qid"] = v2.qid + VAL_OFFSET
    v2["video_path"] = v2.video_id.map(paths).fillna(v2.video_path)
    cols = [c for c in test.columns if c in v2.columns]
    return pd.concat([test[~dup][cols], v2[cols]], ignore_index=True), dup


def labnoise(post: pd.Series, log: pd.DataFrame, df: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """Multiply S3 lab motion rows by the emulator factor (both splits' tracks; val qids offset)."""
    stated = set(log[log.applied & log.rule.isin(["facts", "motionfam", "freefall", "labfacts"])].qid.astype(int))
    out = post.copy()
    frames = []
    for split, off in (("test", 0), ("val", VAL_OFFSET)):
        A = pd.Series({q - off: v for q, v in post.items() if (q >= VAL_OFFSET) == (off > 0)})
        F = LN.factors(split, "qwen", A, SZ_B, SZ_L)
        F["qid"] = F.id + off
        frames.append(F)
    F = pd.concat(frames)
    cat = df.set_index("qid").category
    F = F[F.qid.isin(cat.index) & (F.qid.map(cat) == "S3") & ~F.qid.isin(stated) & (F.factor != 1)]
    out.loc[F.qid] = out.loc[F.qid].to_numpy() * F.factor.to_numpy()
    return out, F


def score(pred: pd.Series, val: pd.DataFrame) -> dict:
    s = item(pd.Series(pred.reindex(val.qid + VAL_OFFSET).to_numpy(), index=val.index), val.answer)
    per = {c: float(s[val.category == c].mean()) for c in CATS}
    return dict(MRA=float(np.mean(list(per.values()))), **per)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="v3 fov")
    ap.add_argument("--no-labnoise", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "submissions/trackB_v4.csv"))
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    sets = SETS[a.sets]
    print("sets:", sets)
    test, val = questions("test"), questions("val")
    rt, rv = raw_answers("test", sets), raw_answers("val", sets)
    df, dup = table(test, val)
    pred = pd.concat([rt.reindex(test.qid[~dup]), pd.Series(rv.to_numpy(), index=val.qid.to_numpy() + VAL_OFFSET)])
    print("raw      ", {k: round(v, 4) for k, v in score(pred, val).items()})
    pr = pp.PRESETS["trackb"]
    post, log = pp.apply_rules(pred, df, rules=pr["rules"], speed_guard=pr["speed_guard"], options=pr["options"])
    print("+rules   ", {k: round(v, 4) for k, v in score(post, val).items()}, "rows changed (test)",
          int((~np.isclose(post, pred, rtol=1e-9, equal_nan=True))[post.index < VAL_OFFSET].sum()))
    final = post
    if not a.no_labnoise:
        final, F = labnoise(post, log, df)
        print("+labnoise", {k: round(v, 4) for k, v in score(final, val).items()},
              f"S3 lab motion rows changed: test {int((F.qid < VAL_OFFSET).sum())}, val {int((F.qid >= VAL_OFFSET).sum())}"
              f", test factor median {F[F.qid < VAL_OFFSET].factor.median():.3f}")
    if a.no_write:
        return final
    # test rows that repeat a validation question: rules ran on the val copy; take the test-table answer of the
    # same pipeline (raw answers of the test row, then the same rules on the full test table)
    full_post, full_log = pp.apply_rules(rt, test, rules=pr["rules"], speed_guard=pr["speed_guard"], options=pr["options"])
    sub = final.reindex(test.qid)
    miss = sub.isna()
    sub[miss] = full_post.reindex(test.qid)[miss]
    if not a.no_labnoise:     # the repeated rows' labnoise factor (computed on the full-table answers)
        rep = test.qid[dup & (test.category == "S3")].to_numpy()
        if len(rep):
            fin2, F2 = labnoise(full_post, full_log, test)
            sub.loc[rep] = fin2.reindex(rep).to_numpy()
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        pd.DataFrame({"id": test.qid, "parsed_value": sub.to_numpy()}).to_csv(fh, index=False)
    subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), fh.name, a.out], check=True)
    print("wrote", a.out)
    return final


if __name__ == "__main__":
    main()
