"""Shared loaders for the leaderboard-strategy study (test inputs, cached runs, submissions; no API).
Validation labels are attached ONLY for evaluation (column `val`), never used to set an answer."""
from __future__ import annotations
import re, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_test, load_split  # noqa: E402
from qp.mra import item_scores  # noqa: E402

SUB = ROOT / "submissions"
BASE = SUB / "trackA_cand_physb2_on_p21.csv"
N_SCORED = {"S2": 553, "D2": 1137, "S3": 538, "D3": 933}
OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)


def read_sub(path) -> pd.Series:
    d = pd.read_csv(path)
    d = d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"].astype(float)
    return d


def fine_kind(q: str) -> str:
    s = q.lower()
    if "acceler" in s:
        return "acc"
    if re.search(r"average (speed|velocity)|mean speed", s):
        return "avgspeed"
    if "speed" in s or "veloc" in s:
        return "speed"
    if "travel" in s or "path" in s:
        return "path"
    if "distance" in s or "displacement" in s or "far" in s:
        return "dist"
    return "size"


def table() -> pd.DataFrame:
    t = load_test().set_index("qid")
    q = t.question.str.lower()
    t["motion"] = q.str.contains("acceler|veloc|speed|travel")
    t["kind"] = [fine_kind(x) for x in t.question]
    t["src"] = t.video_source.replace({"segmentation": "seg"})
    t["srcg"] = t.src.replace({"seg": "sim", "simulation": "sim"})
    vv = load_split("val_hires")
    vk = {(a, b.strip().lower()): ans for a, b, ans in zip(vv.video_id, vv.question, vv.answer)}
    t["overlap"] = [(a, b.strip().lower()) in vk for a, b in zip(t.video_id, t.question)]
    t["val"] = [vk.get((a, b.strip().lower()), np.nan) for a, b in zip(t.video_id, t.question)]
    run = pd.read_csv(ROOT / "runs/test_v1_high_854/test.csv").set_index("id").reindex(t.index)
    for c in ("parsed_value", "geo_value", "direct_value", "method", "flags"):
        t["r_" + c] = run[c]
    for nm, rn in (("d2", "test_3dnl_v1_high_b"), ("d3", "test_3dnl_v2_high")):
        r = pd.read_csv(ROOT / f"runs/{rn}/test.csv").set_index("id").reindex(t.index)
        t[nm] = r.direct_value
        t[nm + "_geo"] = r.geo_value
    t["d1"] = t.r_direct_value
    t["base"] = read_sub(BASE).reindex(t.index)
    t["p21"] = read_sub(SUB / "trackA_best_p21.csv").reindex(t.index)
    t["raw_in_base"] = np.isclose(t.base, t.r_parsed_value, rtol=1e-9)
    t["is_geo"] = t.r_method.fillna("").str.startswith("geometry")
    # subset labels used by the diagnostics
    t["sub"] = t.category + ":" + t.srcg + ":" + np.where(t.motion, "mot", "stat")
    return t


def clustered_boot(delta: pd.Series, groups: pd.Series, n=4000, seed=0):
    """Mean of delta and 90% CI of the mean, resampling groups (videos)."""
    rng = np.random.default_rng(seed)
    g = pd.DataFrame({"d": delta.values, "g": groups.values}).groupby("g").d.agg(["sum", "size"])
    s, c = g["sum"].to_numpy(), g["size"].to_numpy()
    k = len(s)
    if k == 0:
        return np.nan, np.nan, np.nan
    idx = rng.integers(0, k, size=(n, k))
    m = s[idx].sum(1) / c[idx].sum(1)
    return s.sum() / c.sum(), np.quantile(m, .05), np.quantile(m, .95)
