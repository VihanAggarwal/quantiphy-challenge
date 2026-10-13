"""Shared helpers for research/path85_d3 (D3 non-lab + scene families). Test inputs + cached Claude runs only.
Labels used for EVALUATION only: validation answers of identical test questions; exact stated facts (label-free)."""
from __future__ import annotations
import sys, os, math
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault("ANTHROPIC_BASE_URL", "http://127.0.0.1:9")
os.environ.setdefault("QP_LEDGER", "/tmp/path85_d3_ledger.jsonl")
from qp import postprocess as pp  # noqa
from qp.data import load_split, load_validation  # noqa
from qp.mra import item_scores  # noqa

OUT = Path(__file__).resolve().parent / "out"
BASE = ROOT / "submissions/trackA_cand_physb2_on_p21.csv"
RUNS = ["test_v1_high_854", "test_3dnl_v1_high_b", "test_3dnl_v2_high"]
N_SCORED = dict(S2=553, D2=1137, S3=538, D3=933)


def read_sub(p=BASE) -> pd.Series:
    d = pd.read_csv(p, float_precision="round_trip")
    return d.set_index("id")["parsed_value"].astype(float)


_T = None


def test_df():
    global _T
    if _T is None:
        _T = load_split("test")
    return _T


def runs_direct() -> pd.DataFrame:
    out = {}
    for r in RUNS:
        d = pd.read_csv(ROOT / "runs" / r / "test.csv").set_index("id")
        out[r] = pd.to_numeric(d["direct_value"], errors="coerce")
    return pd.DataFrame(out)


def runs_geo() -> pd.DataFrame:
    out = {}
    for r in RUNS:
        d = pd.read_csv(ROOT / "runs" / r / "test.csv").set_index("id")
        out[r] = pd.to_numeric(d["geo_value"], errors="coerce")
    return pd.DataFrame(out)


def lmed(x: pd.DataFrame) -> pd.Series:
    with np.errstate(all="ignore"):
        L = np.log(x.where(x > 0))
        return np.exp(L.median(axis=1, skipna=True))


def val_labels() -> pd.Series:
    test, val = test_df(), load_validation()
    key = lambda d: list(zip(d.video_id, d.question.map(pp.norm_question)))  # noqa
    vmap = dict(zip(key(val), val.answer))
    return pd.Series([vmap.get(k, np.nan) for k in key(test)], index=test.qid).dropna()


def mra1(p, g):
    return float(item_scores([p], [g])[0])


def boot_delta(a: pd.Series, b: pd.Series, clusters: pd.Series, n=2000, seed=0):
    d = (a - b).groupby(clusters).agg(["sum", "size"])
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n):
        k = rng.integers(0, len(d), len(d))
        dd = d.iloc[k]
        bs.append(dd["sum"].sum() / dd["size"].sum())
    return float((a - b).mean()), float(np.percentile(bs, 5)), float(np.percentile(bs, 95))


def base_clip(v):
    return pp.base_id(v)
