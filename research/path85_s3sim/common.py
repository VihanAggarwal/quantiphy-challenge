"""Shared helpers for the S3/D3 simulation study (research/path85_s3sim/). Test inputs + cached Claude runs only.
Labels: (1) validation answers of identical test questions (EVALUATION ONLY), (2) exact stated facts from scene
families (qp.postprocess facts rule, label-free on test)."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp import postprocess as pp  # noqa: E402
from qp.data import load_split, load_validation  # noqa: E402
from qp.mra import item_scores  # noqa: E402

BASE = ROOT / "submissions/trackA_cand_physb2_on_p21.csv"
REPLAY = ROOT / "research/simfov/out/replay.csv"
RUNS = ["test_v1_high_854", "test_3dnl_v1_high_b", "test_3dnl_v2_high"]


def lmed(x: pd.DataFrame) -> pd.Series:
    with np.errstate(all="ignore"):
        L = np.log(x.where(x > 0))
        return np.exp(L.median(axis=1, skipna=True))


def read_sub(p=BASE) -> pd.Series:
    d = pd.read_csv(p, float_precision="round_trip")
    return d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"].astype(float)


_TEST = None


def test_df():
    global _TEST
    if _TEST is None:
        _TEST = load_split("test")
    return _TEST


def val_labels() -> pd.Series:
    """Validation answers keyed by the identical test qid (evaluation only)."""
    test, val = test_df(), load_validation()
    key = lambda d: list(zip(d.video_id, d.question.map(pp.norm_question)))  # noqa: E731
    vmap = dict(zip(key(val), val.answer))
    return pd.Series([vmap.get(k, np.nan) for k in key(test)], index=test.qid).dropna()


def fact_labels(pred: pd.Series | None = None) -> tuple[pd.Series, pd.DataFrame]:
    """Exact stated facts (label-free): the facts rule's applied rows (speed guard off)."""
    test = test_df()
    p = (pred if pred is not None else pd.Series(1.0, index=test.qid)).reindex(test.qid).fillna(1.0)
    _, log = pp.apply_rules(p, test, rules=("facts",), speed_guard=0)
    f = log[log.applied]
    return pd.Series(f.new.to_numpy(float), index=f.qid.astype(int)), f


def boot_delta(a: pd.Series, b: pd.Series, clusters: pd.Series, n=2000, seed=0):
    """Mean of (a - b) and a cluster-bootstrap 90% CI."""
    d = (a - b).groupby(clusters).agg(["sum", "size"])
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n):
        k = rng.integers(0, len(d), len(d))
        dd = d.iloc[k]
        bs.append(dd["sum"].sum() / dd["size"].sum())
    return float((a - b).mean()), float(np.percentile(bs, 5)), float(np.percentile(bs, 95))


def clip_cluster(v: pd.Series) -> pd.Series:
    return v.astype(str).str.replace("_segmented", "", regex=False)
