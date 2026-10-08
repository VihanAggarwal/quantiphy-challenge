"""Loaders for the QuantiPhy validation set, test set and submission template.

Every loader returns a DataFrame with the same columns:

    qid              int    question id (validation: first CSV column; test: template `id`)
    video_id         str
    video_path       str    local .mp4 path ("" if the video is not downloaded)
    video_type       str    4-char code, e.g. "V3MS"; video_type[1] is "2" or "3"
    fps              float
    inference_type   str    "SS" | "SD" | "DS" | "DD"  (prior kind, target kind)
    question         str
    prior            str    free-text prior, e.g. "length of boat = 3.62m"
    depth_info       str    free text, present for 3D questions ("" otherwise)
    category         str    official key inference_type[0] + video_type[1]: S2 | D2 | S3 | D3
    target_unit      str    unit the question asks for ("m", "cm/s", "m/s^2", ...) or ""
    answer           float  ground truth (validation only)
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

from .parse import question_unit_full

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VAL_DIR = DATA / "QuantiPhy-validation"
TEST_DIR = DATA / "QuantiPhy"
TEMPLATE_CSV = DATA / "submission_template" / "quantiphy_submission_template.csv"

CATEGORIES = ("S2", "D2", "S3", "D3")

_TARGET_UNIT_RE = re.compile(
    r"\bin\s*(meters?|metres?|centimeters?|centimetres?|millimeters?|kilometers?|km/h|"
    r"[cmk]?m\s*/\s*s\s*(?:\^\s*2|²)?|[cmk]?m)\b",
    re.IGNORECASE,
)
_UNIT_WORDS = {"meter": "m", "metre": "m", "centimeter": "cm", "centimetre": "cm",
               "millimeter": "mm", "kilometer": "km"}


def target_unit(question: str) -> str:
    """Unit requested by the question (last 'in <unit>'), normalised to a short form.
    Spelled-out rates ("in meters per second", "in km per hour") are handled first."""
    full = question_unit_full(question)
    if full:
        return full
    found = _TARGET_UNIT_RE.findall(question or "")
    if not found:
        return ""
    u = re.sub(r"\s+", "", found[-1]).lower().replace("²", "^2")
    return _UNIT_WORDS.get(u.rstrip("s"), u)


def category(inference_type: str, video_type: str) -> str:
    return f"{inference_type[0]}{video_type[1]}"


@lru_cache(maxsize=None)
def _video_index(root: Path) -> dict[str, Path]:
    # Some files ship with a leading space in the name; strip it for lookup.
    return {p.stem.strip(): p for p in root.rglob("*.mp4")} if root.exists() else {}


def _finalize(df: pd.DataFrame, video_root: Path) -> pd.DataFrame:
    df = df.copy()
    index = _video_index(video_root)
    df["qid"] = df["qid"].astype(int)
    df["fps"] = pd.to_numeric(df["fps"], errors="coerce")
    df["video_path"] = [str(index.get(v, "")) for v in df["video_id"]]
    df["depth_info"] = df.get("depth_info", pd.Series([""] * len(df))).fillna("").astype(str)
    df["category"] = [category(i, v) for i, v in zip(df["inference_type"], df["video_type"])]
    df["target_unit"] = [target_unit(q) for q in df["question"]]
    cols = ["qid", "video_id", "video_path", "video_type", "fps", "inference_type",
            "question", "prior", "depth_info", "category", "target_unit"]
    if "answer" in df.columns:
        cols.append("answer")
    return df[cols].reset_index(drop=True)


def load_validation(csv_path: Path | None = None) -> pd.DataFrame:
    """159 questions with answers. The question id is the first (unnamed) CSV column,
    which is what the official evaluator matches on."""
    csv_path = csv_path or next(VAL_DIR.glob("*.csv"))
    raw = pd.read_csv(csv_path)
    raw = raw.rename(columns={raw.columns[0]: "qid", "ground_truth_prior": "prior",
                              "ground_truth_posterior": "answer"})
    return _finalize(raw, VAL_DIR)


def load_template(path: Path = TEMPLATE_CSV) -> pd.DataFrame:
    """Official submission template as-is: fill `parsed_value`, keep `id` and row order."""
    return pd.read_csv(path)


def load_test(template_path: Path = TEMPLATE_CSV) -> pd.DataFrame:
    """3,289 test questions (no answers); qid is the template `id`.

    The HF parquet and the template are row-aligned. The parquet is the corrected copy
    (typo fixes in 60 questions, depth info and 2D/3D labels filled in for a few videos), so
    its text is used while ids come from the template by position. Video, inference type,
    prior and fps must match exactly and questions must be near-identical, so a template
    update can't silently misalign ids.
    """
    from difflib import SequenceMatcher

    test = pd.read_parquet(next(TEST_DIR.rglob("*.parquet")))
    tmpl = load_template(template_path)
    if len(test) != len(tmpl):
        raise ValueError(f"row count mismatch: parquet={len(test)} template={len(tmpl)}")
    test = test.rename(columns={"ground_truth_prior": "prior"})
    tmpl = tmpl.rename(columns={"ground_truth_prior": "prior"})
    for col in ("video_id", "inference_type", "prior", "fps"):
        a, b = test[col].astype(str).to_numpy(), tmpl[col].astype(str).to_numpy()
        if not (a == b).all():
            raise ValueError(f"template and parquet disagree on {col!r} in {(a != b).sum()} rows")
    sim = [SequenceMatcher(None, a, b).ratio() if a != b else 1.0
           for a, b in zip(test["question"].astype(str), tmpl["question"].astype(str))]
    if min(sim) < 0.8:
        raise ValueError(f"template and parquet questions differ (min similarity {min(sim):.2f})")
    test = test.copy()
    test["qid"] = tmpl["id"].to_numpy()
    return _finalize(test, TEST_DIR)


def load_split(split: str) -> pd.DataFrame:
    if split == "val":
        return load_validation()
    if split == "test":
        return load_test()
    raise ValueError(f"unknown split {split!r} (expected 'val' or 'test')")
