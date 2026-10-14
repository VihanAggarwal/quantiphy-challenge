"""Track B candidate from open-model Track-A-format runs (run_open_pipeline.py) plus the trackb_v1 Colab methods.

    .venv/bin/python research/r86/trackb_opt/build_open.py OUT.csv \
        --port runs/val_q38_a/val.csv:runs/test_q38_a/test.csv [--port ... more runs] \
        [--tb /tmp/claude-0/tb3/x/trackb_v1] [--sets '{"S2": ["port"], ...}'] [--preset trackb|default]

Methods: "port" = log-median of the --port runs' parsed_value (one run = that run), "port_dir" = their
direct_value, "port_geo" = their geo_value, plus every trackb_build.METHODS member found under --tb.
Prints validation MRA (raw) of each method and of the per-category sets, applies scripts/postprocess.py
(--preset) to val and test, prints the post-processed validation MRA, then scripts/make_submission.py.
Validation labels are read only for scoring. Open weights only: never pass a Claude/GPT run as --port.
Note: on the 24 validation videos alone the family rules barely fire (they need the test-wide scene families),
so gate on the RAW validation MRA; research/trackb_dense/build_v4.py shows how to score rules with the
validation rows put back into the test table. Plumbing check (cvq_geometry as "port"): raw val .5621.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from qp.data import load_split, load_validation  # noqa: E402
from trackb_build import METHODS, item, read  # noqa: E402

CATS = ("S2", "D2", "S3", "D3")
DEFAULT_SETS = {c: ["port"] for c in CATS}


def logmed(series: list[pd.Series]) -> pd.Series:
    L = np.log(np.vstack([s.to_numpy(dtype=float) for s in series]))
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return pd.Series(np.exp(np.nanmedian(L, 0)), index=series[0].index)


def col(path: str, name: str, index) -> pd.Series:
    d = pd.read_csv(path)
    d = d.rename(columns={d.columns[0]: "id"}).set_index("id")
    s = pd.to_numeric(d.get(name, d["parsed_value"]), errors="coerce").abs()
    return s.where(np.isfinite(s) & (s > 0)).reindex(index)


def methods(split: str, df: pd.DataFrame, ports: list[tuple[str, str]], tb: Path) -> dict[str, pd.Series]:
    idx = df.qid
    P = {m: read(tb / split / f, idx) for m, f in METHODS.items() if (tb / split / f).exists()}
    k = 0 if split == "val" else 1
    for name, c in (("port", "parsed_value"), ("port_dir", "direct_value"), ("port_geo", "geo_value")):
        runs = [col(p[k], c, idx) for p in ports]
        P[name] = logmed(runs) if len(runs) > 1 else runs[0]
    return {m: s.set_axis(df.index) for m, s in P.items()}


def macro(pred: pd.Series, df: pd.DataFrame) -> dict:
    sc = item(pred, df.answer)
    r = {c: float(sc[(df.category == c).to_numpy()].mean()) for c in CATS}
    r["MRA"] = float(np.mean([r[c] for c in CATS]))
    return r


def combine(P: dict, df: pd.DataFrame, sets: dict) -> pd.Series:
    out = pd.Series(np.nan, index=df.index)
    for c in CATS:
        m = (df.category == c).to_numpy()
        out[m] = logmed([P[x] for x in sets[c] if x in P])[m]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--port", action="append", required=True, help="VAL_CSV:TEST_CSV of one open-model run")
    ap.add_argument("--tb", default="/tmp/claude-0/tb3/x/trackb_v1")
    ap.add_argument("--sets", default=json.dumps(DEFAULT_SETS))
    ap.add_argument("--preset", default="trackb")
    a = ap.parse_args(argv)
    ports = [tuple(p.split(":", 1)) for p in a.port]
    sets = json.loads(a.sets)
    val = load_validation().reset_index(drop=True)
    test = load_split("test").reset_index(drop=True)
    Pv, Pt = methods("val", val, ports, Path(a.tb)), methods("test", test, ports, Path(a.tb))
    rows = {m: macro(s, val) for m, s in Pv.items()}
    raw_v = combine(Pv, val, sets)
    rows["SETS (raw)"] = macro(raw_v, val)
    print(pd.DataFrame(rows).T.round(4).sort_values("MRA", ascending=False).to_string())
    raw_t = combine(Pt, test, sets)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for split, df, raw in (("val", val, raw_v), ("test", test, raw_t)):
            pd.DataFrame({"id": df.qid, "parsed_value": raw}).to_csv(td / f"raw_{split}.csv", index=False)
            rc = subprocess.run([sys.executable, str(ROOT / "scripts/postprocess.py"), str(td / f"raw_{split}.csv"),
                                 str(td / f"post_{split}.csv"), "--preset", a.preset, "--split", split]).returncode
            if rc:
                print(f"postprocess failed on {split}; using raw answers")
                (td / f"post_{split}.csv").write_bytes((td / f"raw_{split}.csv").read_bytes())
        post_v = col(str(td / "post_val.csv"), "parsed_value", val.qid).set_axis(val.index)
        print("validation after postprocess:", {k: round(v, 4) for k, v in macro(post_v, val).items()})
        subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), str(td / "post_test.csv"), a.out],
                       check=True)


if __name__ == "__main__":
    main()
