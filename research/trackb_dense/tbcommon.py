"""Shared inputs for the Track B dense-geometry study (research/trackb_dense).

Open-weight inputs only: Qwen3-VL specs / grounding tracks (qwen/specs, qwen/annotate), Grounding DINO + SAM 2
tracks (cv/annotate), CaW / Qwen direct answers. Validation labels are read only by `score`.
"""
from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qp.data import load_split, load_validation  # noqa: E402
from qp.mra import THRESHOLDS  # noqa: E402
from qp.spec import KIND_DIM, QuestionSpec, RoleTrack  # noqa: E402

RUN = Path("/tmp/claude-0/tb3/x/trackb_v1")
HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
CACHE = Path("/tmp/claude-0/trackb_dense_cache")          # heavy CPU caches (dense tracks, KLT)
CATS = ("S2", "D2", "S3", "D3")
GEO_MAX_SI = {"L": 1e4, "V": 1e3, "A": 1e3}
LAB_FOV_DEG = None


def questions(split: str) -> pd.DataFrame:
    df = load_validation() if split == "val" else load_split("test")
    q, p = df.question.str.lower(), df.prior.str.lower()
    tk = np.select([q.str.contains("acceler"), q.str.contains("veloc|speed"),
                    q.str.contains("travel|distance|far|apart")], ["accel", "speed", "distance"], "size")
    pk = np.where(p.str.contains("acc|gravity|veloc|speed"), "motion", "size")
    return df.assign(tk=tk, pk=pk).reset_index(drop=True)


def load_dir(d: Path) -> dict[str, dict]:
    out = {}
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        try:
            rec = json.loads(p.read_text())
        except ValueError:
            continue
        out[rec["video_id"]] = rec
    return out


def specs(split: str) -> dict[int, QuestionSpec]:
    return {int(q): QuestionSpec.from_dict(v["spec"]) for rec in load_dir(RUN / split / "qwen" / "specs").values()
            for q, v in rec.get("questions", {}).items()}


def tracks(split: str, src: str) -> dict[str, dict]:
    """src 'qwen' -> qwen/annotate, 'cv' -> cv/annotate (records with meta + tracks per qid)."""
    return load_dir(RUN / split / src / "annotate")


def read_csv(path: Path, index) -> pd.Series:
    if not Path(path).exists():
        return pd.Series(np.nan, index=index)
    d = pd.read_csv(path)
    s = d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"]
    s = pd.to_numeric(s, errors="coerce").abs()
    return s.where(np.isfinite(s) & (s > 0)).reindex(index)


BASE = {"qwen_direct": "qwen/direct.csv", "caw": "caw/caw.csv", "qwen_geo": "qwen/geometry.csv",
        "cv_geo": "cv/geometry.csv", "cvq_geo": "cvq/geometry.csv", "qwen35": "qwen35/direct.csv",
        "gemma4": "gemma4/direct.csv"}


def base_preds(split: str, index) -> dict[str, pd.Series]:
    return {m: read_csv(RUN / split / f, index) for m, f in BASE.items()}


def item(pred: pd.Series, gt: pd.Series) -> pd.Series:
    e = (pred - gt).abs() / gt
    return pd.Series(np.mean([(e < 1 - t).to_numpy() for t in THRESHOLDS], axis=0), index=gt.index).where(pred.notna(), 0.0)


def macro(items: pd.Series, cat: pd.Series) -> float:
    return float(np.mean([items[cat == c].mean() for c in CATS if (cat == c).any()]))


def report(name: str, pred: pd.Series, val: pd.DataFrame) -> dict:
    s = item(pred.reindex(val.qid).set_axis(val.index), val.answer)
    per = {c: float(s[val.category == c].mean()) for c in CATS}
    m = float(np.mean(list(per.values())))
    print(f"{name:28s} MRA {m:.4f}  " + " ".join(f"{c} {per[c]:.3f}" for c in CATS)
          + f"  (answered {pred.reindex(val.qid).notna().mean():.0%})", flush=True)
    return dict(name=name, MRA=m, **per)


def log_median(preds: list[pd.Series]) -> pd.Series:
    L = np.log(np.vstack([p.to_numpy(dtype=float) for p in preds]))
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return pd.Series(np.exp(np.nanmedian(L, 0)), index=preds[0].index)


def valid(v) -> bool:
    return isinstance(v, (int, float, np.floating)) and math.isfinite(v) and v > 0


def with_fallback(geo: pd.Series, geo_si: pd.Series, kinds: pd.Series, direct: pd.Series,
                  max_disagree: float = 10.0) -> pd.Series:
    """run_open_vlm.run_geometry's rule: geometry unless implausible or > max_disagree x off the direct answer."""
    out = pd.Series(np.nan, index=geo.index)
    for q in geo.index:
        g, d = geo.get(q), direct.get(q)
        use = valid(g)
        if use and valid(geo_si.get(q)) and geo_si[q] > GEO_MAX_SI.get(KIND_DIM.get(kinds.get(q), "L"), math.inf):
            use = False
        if use and valid(d) and max(g / d, d / g) > max_disagree:
            use = False
        out[q] = g if use else (d if valid(d) else np.nan)
    return out
