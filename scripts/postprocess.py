"""Apply the model-free post-processing rules (qp/postprocess.py) to a prediction CSV.

    python scripts/postprocess.py runs/opus/test.csv runs/opus/test_post.csv --log runs/opus/post_log.csv
    python scripts/make_submission.py runs/opus/test_post.csv submissions/opus_post.csv

IN.csv: first column = question id (`id` / `qid`), plus `parsed_value` (other columns are ignored, except
`method` with --render-direct-only). OUT.csv: `id,parsed_value` in IN's row order. Rules read only the
questions' inputs (video ids, frames, question / prior / depth_info text), never answers. Frame checks
are cached under runs/_postprocess_cache/, so a re-run takes seconds.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qp import postprocess as pp  # noqa: E402


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("predictions", help="input CSV: question id column first, parsed_value")
    ap.add_argument("out", help="output CSV (id,parsed_value)")
    ap.add_argument("--rules", nargs="+", choices=pp.RULES, default=list(pp.RULES),
                    help="rules to apply (always in the order facts, render, twin); default: all")
    ap.add_argument("--log", help="write the decision log (one row per applied or guarded change) here")
    ap.add_argument("--split", choices=["val", "val_hires", "test"], default="test",
                    help="question table the predictions belong to (default: test)")
    ap.add_argument("--csv", help="questions CSV (validation format) instead of --split")
    ap.add_argument("--video-dir", help="videos (default: the split's / the CSV's folder)")
    ap.add_argument("--cache-dir", default=str(pp.DEFAULT_CACHE), help="frame-check cache (default: %(default)s)")
    ap.add_argument("--no-frames", action="store_true",
                    help="skip frame checks (no twin copies, no frame-based family links)")
    ap.add_argument("--speed-guard", type=float, default=pp.SPEED_GUARD,
                    help="skip a transferred speed this many times off the clip's own answer (0 = off)")
    ap.add_argument("--render-direct-only", action="store_true",
                    help="render rule only on rows whose input `method` column is 'direct' (Track A probes)")
    return ap.parse_args(argv)


def load_questions(args) -> pd.DataFrame:
    """Question inputs only: answer columns are dropped here and again inside apply_rules."""
    if args.csv:
        from qp.data import _finalize

        raw = pd.read_csv(args.csv)
        if str(raw.columns[0]).startswith("Unnamed"):
            raw = raw.rename(columns={raw.columns[0]: "qid"})
        elif "qid" not in raw.columns:
            raw.insert(0, "qid", range(len(raw)))
        raw = raw.drop(columns=[c for c in ("ground_truth_posterior", "answer") if c in raw.columns])
        raw = raw.rename(columns={"ground_truth_prior": "prior"})
        return _finalize(raw, Path(args.video_dir) if args.video_dir else Path(args.csv).parent)
    from qp.data import load_split

    return load_split(args.split).drop(columns=["answer"], errors="ignore")


def main(argv=None) -> int:
    args = parse_args(argv)
    raw = pd.read_csv(args.predictions)
    raw = raw.rename(columns={raw.columns[0]: "id"})
    if "parsed_value" not in raw.columns:
        raise SystemExit(f"{args.predictions}: no parsed_value column")
    pred = pd.Series(pd.to_numeric(raw["parsed_value"], errors="coerce").to_numpy(), index=raw["id"].astype(int))
    if pred.index.duplicated().any():
        raise SystemExit(f"{args.predictions}: duplicate ids")
    mask = None
    if args.render_direct_only:
        if "method" not in raw.columns:
            raise SystemExit("--render-direct-only needs a `method` column in the input CSV")
        mask = pd.Series((raw["method"].astype(str) == "direct").to_numpy(), index=pred.index)
    questions = load_questions(args)
    t0 = time.time()
    new, log = pp.apply_rules(pred, questions, rules=tuple(args.rules), video_root=args.video_dir,
                              cache_dir=args.cache_dir or None, render_mask=mask,
                              speed_guard=args.speed_guard, use_frames=not args.no_frames)
    out = pd.DataFrame({"id": raw["id"].astype(int), "parsed_value": new.reindex(raw["id"].astype(int)).to_numpy()})
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
        log.to_csv(args.log, index=False)
    s = pp.summary(log, questions)
    print(s.to_string(index=False) if len(s) else "no rule fired")
    changed = int((~(out.parsed_value.to_numpy() == pred.reindex(out.id).to_numpy())
                   & out.parsed_value.notna().to_numpy()).sum())
    print(f"wrote {args.out}: {len(out)} rows, {changed} changed ({time.time() - t0:.1f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
