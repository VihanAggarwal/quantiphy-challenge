"""Apply the model-free post-processing rules (qp/postprocess.py) to a prediction CSV.

    python scripts/postprocess.py runs/opus/test.csv runs/opus/test_post.csv --log runs/opus/post_log.csv
    python scripts/postprocess.py raw.csv post.csv --preset trackb            # Track B rule set
    python scripts/postprocess.py raw.csv post.csv --rules facts pool --pool-unit base --pool-max-dev 1.6
    python scripts/make_submission.py runs/opus/test_post.csv submissions/opus_post.csv

IN.csv: first column = question id (`id` / `qid`), plus `parsed_value` (other columns are ignored, except
`method` with --render-direct-only). OUT.csv: `id,parsed_value` in IN's row order. Rules read only the
questions' inputs (video ids, frames, question / prior / depth_info text) and the answers being processed, never
labels. Frame checks are cached under runs/_postprocess_cache/, so a re-run takes seconds.

Rules (always applied in this order; --rules picks any subset, default = twin render facts):
  facts      stated-fact transfer within scene families          motionfam  sim3d motion facts from sibling cameras
  freefall   3D-sim free fall from rest -> 9.8 m/s^2              labfacts   lab prop sizes stated by another event
  kscale     per-clip scale from the clip's stated facts          pool       per-object pooling across family clips
  labpool    lab prop sizes pooled across events                  render     lab s/x render copy (motion)
  twin       segmented twin copy
"""

from __future__ import annotations

import argparse
import json
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
    ap.add_argument("--preset", choices=sorted(pp.PRESETS), default="default",
                    help="rule set and settings (default: twin, render, facts as before); flags below override it")
    ap.add_argument("--rules", nargs="+", choices=pp.RULES, default=None,
                    help="rules to apply (always in the fixed order); default: the preset's")
    ap.add_argument("--log", help="write the decision log (one row per applied or guarded change) here")
    ap.add_argument("--split", choices=["val", "val_hires", "test"], default="test",
                    help="question table the predictions belong to (default: test)")
    ap.add_argument("--csv", help="questions CSV (validation format) instead of --split")
    ap.add_argument("--video-dir", help="videos (default: the split's / the CSV's folder)")
    ap.add_argument("--cache-dir", default=str(pp.DEFAULT_CACHE), help="frame-check cache (default: %(default)s)")
    ap.add_argument("--no-frames", action="store_true",
                    help="skip frame checks (no twin copies, no frame-based family links, no free fall)")
    ap.add_argument("--speed-guard", type=float, default=None,
                    help="facts: skip a transferred speed this many times off the clip's own answer (0 = off; "
                         f"default: the preset's, {pp.SPEED_GUARD:g} for default)")
    ap.add_argument("--render-direct-only", action="store_true",
                    help="render rule only on rows whose input `method` column is 'direct' (Track A probes)")
    g = ap.add_argument_group("extended rule settings (override the preset)")
    g.add_argument("--pool-unit", choices=["clip", "base"], help="pool: one vote per clip or per base clip")
    g.add_argument("--pool-tau", type=float, help="pool: votes within this log distance of the median are averaged")
    g.add_argument("--pool-max-dev", type=float, help="pool: skip rows whose own vote is this many times off (0 = off)")
    g.add_argument("--pool-scope", choices=["family", "base"], help="pool: whole scene family or one base clip")
    g.add_argument("--motionfam-guard", type=float, help="motionfam: 2x-style guard (0 = off)")
    g.add_argument("--cats", nargs="+", metavar="RULE=CAT,CAT",
                   help="restrict a rule to categories, e.g. kscale=D3 pool=D2,D3")
    g.add_argument("--options", help="JSON {rule: {setting: value}} merged over the preset (see qp.postprocess.apply_rules)")
    return ap.parse_args(argv)


def settings(args) -> tuple[tuple, float, dict]:
    """(rules, speed_guard, options) from the preset and the override flags."""
    pre = pp.PRESETS[args.preset]
    rules = tuple(args.rules) if args.rules else tuple(pre["rules"])
    guard = pre["speed_guard"] if args.speed_guard is None else args.speed_guard
    opts = {k: dict(v) for k, v in pre["options"].items()}

    def put(rule, key, value):
        if value is not None:
            opts.setdefault(rule, {})[key] = value
    put("pool", "unit", args.pool_unit)
    put("pool", "tau", args.pool_tau)
    if args.pool_max_dev is not None:
        opts.setdefault("pool", {})["max_dev"] = args.pool_max_dev or None
    put("pool", "scope", args.pool_scope)
    put("motionfam", "guard", args.motionfam_guard)
    for item in args.cats or []:
        rule, _, cats = item.partition("=")
        if rule not in pp.RULES or not cats:
            raise SystemExit(f"--cats {item}: expected RULE=CAT[,CAT...] with RULE in {pp.RULES}")
        opts.setdefault(rule, {})["cats"] = tuple(c.strip() for c in cats.split(",") if c.strip())
    if args.options:
        for rule, kv in json.loads(args.options).items():
            opts.setdefault(rule, {}).update(kv)
    return rules, guard, opts


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
    rules, guard, opts = settings(args)
    questions = load_questions(args)
    t0 = time.time()
    new, log = pp.apply_rules(pred, questions, rules=rules, video_root=args.video_dir,
                              cache_dir=args.cache_dir or None, render_mask=mask,
                              speed_guard=guard, use_frames=not args.no_frames, options=opts)
    out = pd.DataFrame({"id": raw["id"].astype(int), "parsed_value": new.reindex(raw["id"].astype(int)).to_numpy()})
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
        log.to_csv(args.log, index=False)
    s = pp.summary(log, questions)
    print(f"rules: {', '.join(r for r in pp.RULES if r in rules)}; speed guard {guard:g}; options {opts}")
    print(s.to_string(index=False) if len(s) else "no rule fired")
    changed = int((~(out.parsed_value.to_numpy() == pred.reindex(out.id).to_numpy())
                   & out.parsed_value.notna().to_numpy()).sum())
    print(f"wrote {args.out}: {len(out)} rows, {changed} changed ({time.time() - t0:.1f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
