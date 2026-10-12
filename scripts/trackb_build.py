"""Track B: combine the open-model methods of a Colab run into one submission (open weights only).

    python scripts/trackb_build.py outputs/trackb_v1 submissions/trackB_v1.csv [--min-cell 8]

Methods (any that exist; each is a CSV id,parsed_value for val and test):
  qwen_direct  <run>/{split}/qwen/direct.csv        Qwen3-VL direct answers
  caw          <run>/{split}/caw/caw.csv            Code-as-World-VL direct answers
  qwen_geo     <run>/{split}/qwen/geometry.csv      geometry on Qwen's grounding tracks (+ direct fallback)
  cv_geo       <run>/{split}/cv/geometry.csv        geometry on Grounding DINO + SAM 2 tracks (+ direct fallback)
  cv_geo_only  <run>/{split}/cv/cv_geometry.csv     CV geometry without fallback
Routing: each cell (category x target kind x prior kind) takes the method with the best validation MRA among methods
answering >= 80% of the cell, when the cell has >= --min-cell validation questions; smaller cells use the prior
category x target-kind cell, then the category, then the default order (public Track B repos agree: geometry for
size priors, direct answers under motion priors). Missing answers fall through the cell's ranked methods. Then
qp.postprocess (model-free: segmented-twin copy, lab render copy, stated facts within scene families) and
scripts/make_submission.py. Prints the leave-one-video-out validation MRA of the routing.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qp.data import load_split, load_validation  # noqa: E402
from qp.mra import THRESHOLDS  # noqa: E402

METHODS = {"qwen_direct": "qwen/direct.csv", "caw": "caw/caw.csv", "qwen_geo": "qwen/geometry.csv",
           "cv_geo": "cv/geometry.csv", "cv_geo_only": "cv/cv_geometry.csv"}
CATS = ("S2", "D2", "S3", "D3")


def kinds(df: pd.DataFrame) -> pd.DataFrame:
    q, p = df.question.str.lower(), df.prior.str.lower()
    tk = np.select([q.str.contains("acceler"), q.str.contains("veloc|speed"), q.str.contains("travel|distance|far|apart")],
                   ["accel", "speed", "distance"], "size")
    pk = np.where(p.str.contains("acc|gravity|veloc|speed"), "motion", "size")
    return df.assign(tk=tk, pk=pk)


def read(path: Path, index) -> pd.Series:
    if not path.exists():
        return pd.Series(np.nan, index=index)
    d = pd.read_csv(path)
    s = d.rename(columns={d.columns[0]: "id"}).set_index("id")["parsed_value"]
    s = pd.to_numeric(s, errors="coerce").abs()
    return s.where(np.isfinite(s) & (s > 0)).reindex(index)


def item(pred: pd.Series, gt: pd.Series) -> pd.Series:
    e = (pred - gt).abs() / gt
    return pd.Series(np.mean([(e < 1 - t).to_numpy() for t in THRESHOLDS], axis=0), index=gt.index).where(pred.notna(), 0.0)


def route(val: pd.DataFrame, preds: dict, min_cell: int, default: list[str]):
    """Ranked methods per (cat, tk, pk) from validation rows `val` (with scores per method)."""
    scores = {m: item(preds[m].reindex(val.index), val.answer) for m in preds}
    cover = {m: preds[m].reindex(val.index).notna() for m in preds}

    def rank(mask):
        if mask.sum() < min_cell:
            return None
        ok = [m for m in preds if cover[m][mask].mean() >= 0.8]
        return sorted(ok, key=lambda m: -scores[m][mask].mean()) or None

    table = {}
    for c in CATS:
        for tk in ("size", "speed", "accel", "distance"):
            for pk in ("size", "motion"):
                m = (val.category == c) & (val.tk == tk) & (val.pk == pk)
                r = (rank(m) or rank((val.category == c) & (val.tk == tk)) or rank(val.category == c)
                     or [x for x in default if x in preds])
                table[(c, tk, pk)] = r + [x for x in default if x in preds and x not in r]
    return table


def apply(df: pd.DataFrame, preds: dict, table: dict) -> pd.Series:
    out = pd.Series(np.nan, index=df.index)
    for q, r in df.iterrows():
        for m in table[(r.category, r.tk, r.pk)]:
            v = preds[m].get(q, np.nan)
            if np.isfinite(v):
                out[q] = v
                break
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("out")
    ap.add_argument("--min-cell", type=int, default=8)
    ap.add_argument("--no-postprocess", action="store_true")
    a = ap.parse_args()
    run = Path(a.run)
    val = kinds(load_validation().set_index("qid"))
    test = kinds(load_split("test").set_index("qid"))
    pv = {m: read(run / "val" / f, val.index) for m, f in METHODS.items()}
    pt = {m: read(run / "test" / f, test.index) for m, f in METHODS.items()}
    present = [m for m in METHODS if pv[m].notna().mean() > 0.3 and pt[m].notna().mean() > 0.3]
    pv, pt = {m: pv[m] for m in present}, {m: pt[m] for m in present}
    default = [m for m in ("cv_geo", "qwen_geo", "caw", "qwen_direct", "cv_geo_only") if m in present]
    print("methods:", {m: f"val {pv[m].notna().mean():.0%} test {pt[m].notna().mean():.0%}" for m in present})

    def macro(s):
        return np.mean([s[val.category == c].mean() for c in CATS])
    for m in present:
        s = item(pv[m], val.answer)
        print(f"  {m:12s} val MRA {macro(s):.3f}  " + " ".join(f"{c} {s[val.category == c].mean():.3f}" for c in CATS))
    # leave-one-video-out estimate of the routing
    lovo = pd.Series(np.nan, index=val.index)
    for v in val.video_id.unique():
        held = val.video_id == v
        tab = route(val[~held], pv, a.min_cell, default)
        lovo[held] = apply(val[held], pv, tab)
    s = item(lovo, val.answer)
    print(f"routing (leave-one-video-out) val MRA {macro(s):.3f}  " + " ".join(f"{c} {s[val.category == c].mean():.3f}" for c in CATS))

    table = route(val, pv, a.min_cell, default)
    ans = apply(test, pt, table)
    print("test answered:", f"{ans.notna().mean():.1%}", "| chosen first methods:",
          pd.Series([table[(r.category, r.tk, r.pk)][0] for _, r in test.iterrows()]).value_counts().to_dict())
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw.csv"
        pd.DataFrame({"id": ans.index, "parsed_value": ans.values}).to_csv(raw, index=False)
        src = raw
        if not a.no_postprocess:
            post = Path(td) / "post.csv"
            if subprocess.run([sys.executable, str(ROOT / "scripts/postprocess.py"), str(raw), str(post)]).returncode == 0:
                src = post
        subprocess.run([sys.executable, str(ROOT / "scripts/make_submission.py"), str(src), a.out], check=True)


if __name__ == "__main__":
    main()
