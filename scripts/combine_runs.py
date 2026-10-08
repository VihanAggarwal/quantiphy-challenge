"""Combine one or more Track A run CSVs into one answer per question (qp.combine).

    python scripts/combine_runs.py runs/val_opus_med/val.csv runs/val_opus_high/val.csv --split val \\
        --out runs/combined/val.csv --cv
    python scripts/combine_runs.py runs/test_opus/test.csv --split test --out runs/combined/test.csv

Each run CSV (scripts/run_claude.py output: id, parsed_value, geo_value, direct_value, method, flags[,
geo_method]) is re-selected with one rule (--rule, default qp.combine.DEFAULT_RULE: the same rule
run_claude.py applies to a single run), using the split's video_type / video_source; several runs are
then combined by the median in log space of their selected values. Writes id, parsed_value,
geo_value, direct_value, method, flags, n_runs. With answers (--split val) it prints the MRA of every
input run and of the combination, and with --cv the leave-one-video-out CV of the rule choice.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qp import combine  # noqa: E402
from qp.data import load_split  # noqa: E402
from qp.mra import score  # noqa: E402


def _fmt(sc: dict) -> str:
    return f"{sc['mra']:.3f} (" + " ".join(f"{c}={v:.3f}" for c, v in sc["per_category"].items()) + ")"


def main(argv=None) -> pd.DataFrame:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("runs", nargs="+", help="run CSVs (scripts/run_claude.py output)")
    ap.add_argument("--split", choices=["val", "test"], required=True, help="question metadata (and answers)")
    ap.add_argument("--rule", choices=list(combine.RULES), default=combine.DEFAULT_RULE)
    ap.add_argument("--out", help="combined CSV to write")
    ap.add_argument("--cv", action="store_true", help="leave-one-video-out CV of the rule choice (val)")
    args = ap.parse_args(argv)

    meta = load_split(args.split)
    runs = [pd.read_csv(p) for p in args.runs]
    selected = [combine.select_table(r, meta, args.rule) for r in runs]
    out = combine.combine_tables(selected)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(args.out, index=False)
        print(f"wrote {args.out}: {len(out)} questions, {int(out.parsed_value.notna().sum())} answered, "
              f"rule {args.rule}, {len(runs)} run(s)")
    if "answer" in meta.columns:
        m = meta[["qid", "category", "answer"]]
        for path, t in zip(args.runs, selected):
            sc = score(m.merge(t, left_on="qid", right_on="id", how="left"), "parsed_value")
            print(f"MRA {Path(path).parent.name or path}: {_fmt(sc)}")
        if len(runs) > 1:
            print(f"MRA combined ({len(runs)} runs): "
                  f"{_fmt(score(m.merge(out, left_on='qid', right_on='id', how='left'), 'parsed_value'))}")
        if args.cv:
            cv = combine.lovo_cv(runs, meta)
            print("in-sample MRA (mean over runs) by rule: "
                  + ", ".join(f"{k} {v:.3f}" for k, v in cv["in_sample"].items()))
            picks = pd.Series(cv["chosen"]).value_counts().to_dict()
            print(f"LOVO CV, rule chosen per held-out video {picks}")
            for path, v, cats in zip(args.runs, cv["per_run"], cv["per_category"]):
                print(f"  CV MRA {Path(path).parent.name or path}: {v:.3f} ("
                      + " ".join(f"{c}={x:.3f}" for c, x in cats.items()) + ")")
            if len(runs) > 1:
                cvc = combine.lovo_cv(runs, meta, combined=True)
                print(f"  CV MRA combined: {cvc['per_run'][0]:.3f} ("
                      + " ".join(f"{c}={x:.3f}" for c, x in cvc["per_category"][0].items()) + "), rules "
                      + str(pd.Series(cvc["chosen"]).value_counts().to_dict()))
    return out


if __name__ == "__main__":
    main()
