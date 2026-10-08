"""Dense CPU tracks for a cached Claude run (qp.dense_track): re-solve every question, no API calls.

    python scripts/dense_tracks.py --name val_opus_high --split val                  # motion (default)
    python scripts/dense_tracks.py --name val_opus_high --split val --what both --workers 4
    python scripts/dense_tracks.py --name val_hr_v2_high --split val_hires --overlays /tmp/ov

Reads <runs>/<name>/<split>/records (as scripts/run_claude.py wrote them; <runs> = --out-root, env
QP_RUNS, else runs/), replaces the annotator's tracks by dense ones where they pass qp.dense_track's
checks (--what: motion tracks, size extents or both), re-runs qp.geometry.solve and the answer selection
of scripts/run_claude.py (its build_results, so the same rule, refinement and guards), and writes
<runs>/<name>/<split>_dense.csv (--what motion, the default; else <split>_dense_<what>.csv) with columns id,
parsed_value, geo_value, direct_value, method, flags, geo_method. Prints MRA (final and geometry, per
category) of the original and the dense variant when the split has answers. Dense results are cached
per video and object under --cache-dir (default <runs>/_dense_cache/<split>), so reruns are fast.

--prior-refine first (default): qp.refine's optical-flow refinement of motion priors runs first, as in
run_claude, and dense tracking leaves the tracks it accepted alone; off: no qp.refine, dense tracking
for every track.
"""

from __future__ import annotations

import argparse
import contextlib
import math
import os
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_claude as rc  # noqa: E402

from qp import combine, refine  # noqa: E402
from qp import dense_track as dt  # noqa: E402
from qp.data import ROOT, load_split  # noqa: E402
from qp.mra import score  # noqa: E402


def video_maps(df: pd.DataFrame, records: dict, anns: dict) -> tuple[dict, dict]:
    """{qid: video path}, {qid: (fps, (W, H), annotator image scale)} for the annotated questions."""
    rows = [r for r in df.itertuples() if getattr(r, "video_path", "") and int(r.qid) in anns
            and (records.get(r.video_id) or {}).get("meta")]
    paths = {int(r.qid): str(r.video_path) for r in rows}
    meta = {}
    for r in rows:
        m = records[r.video_id]["meta"]
        meta[int(r.qid)] = (float(m["fps"]), tuple(m["image_size"]), float(m.get("scale") or 1.0))
    return paths, meta


def densify(anns: dict, df: pd.DataFrame, records: dict, what: str, prior_refine: str = "first",
            cache_dir=None, workers: int = 1, log: list | None = None, size_method: str = dt.SIZE_METHOD,
            motion_kinds=dt.MOTION) -> dict:
    """qp.refine (prior_refine "first") then dense tracks, in place."""
    paths, meta = video_maps(df, records, anns)
    skip = set()
    if prior_refine == "first":
        rlog: list = []
        try:
            refine.refine_annotations(anns, paths, {q: m[:2] for q, m in meta.items()}, log=rlog)
        except Exception as e:  # noqa: BLE001 - as run_claude: refinement is optional
            print(f"prior refinement skipped: {type(e).__name__}: {e}")
        skip = {(q, role) for q, role, info in rlog if info.get("why") == "refined"}
    dt.densify_annotations(anns, paths, meta, what=what, cache_dir=cache_dir, log=log, workers=workers,
                           skip=skip, size_method=size_method, motion_kinds=motion_kinds)
    return anns


@contextlib.contextmanager
def _dense_build(df, records, what, prior_refine, cache_dir, workers, log, size_method, motion_kinds):
    """run_claude.build_results with its annotations densified (and its own refinement switched off:
    densify runs it first when asked), so the answer selection is exactly run_claude's."""
    orig_load, orig_refine = rc.ca.load_annotations, rc.REFINE_PRIORS

    def load(recs):
        return densify(orig_load(recs), df, records, what, prior_refine, cache_dir, workers, log, size_method,
                       motion_kinds)
    rc.ca.load_annotations, rc.REFINE_PRIORS = load, False
    try:
        yield
    finally:
        rc.ca.load_annotations, rc.REFINE_PRIORS = orig_load, orig_refine


def build(df, records, what="motion", rule=combine.DEFAULT_RULE, prior_refine="first", cache_dir=None,
          workers=1, log=None, size_method=dt.SIZE_METHOD, motion_kinds=dt.MOTION) -> pd.DataFrame:
    """The run table with dense tracks (what "none": run_claude's own result)."""
    if what == "none":
        return rc.build_results(df, records, rule)
    with _dense_build(df, records, what, prior_refine, cache_dir, workers, log, size_method, motion_kinds):
        return rc.build_results(df, records, rule)


def mra_table(df: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """MRA (final = parsed_value, geo = geo_value) overall and per category for each named table."""
    out = []
    for name, res in tables.items():
        m = df[["qid", "category", "answer"]].merge(res, left_on="qid", right_on="id")
        for col, label in (("parsed_value", "final"), ("geo_value", "geo")):
            sc = score(m, col)
            out.append({"variant": name, "value": label, "MRA": sc["mra"], **sc["per_category"]})
    return pd.DataFrame(out)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--name", required=True, help="cached run_claude run")
    ap.add_argument("--split", required=True, choices=["val", "val_hires", "test"])
    ap.add_argument("--what", choices=["motion", "size", "both"], default="motion")
    ap.add_argument("--rule", choices=list(combine.RULES), default=combine.DEFAULT_RULE)
    ap.add_argument("--prior-refine", choices=["first", "off"], default="first")
    ap.add_argument("--size-method", choices=["grabcut", "snap"], default=dt.SIZE_METHOD)
    ap.add_argument("--with-distance", action="store_true",
                    help="also densify the point tracks of distance questions (default: motion quantities only)")
    ap.add_argument("--limit-videos", type=int, default=0, help="only the first N videos")
    ap.add_argument("--videos", default="", help="comma-separated video ids")
    ap.add_argument("--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)), help="videos in parallel")
    ap.add_argument("--out-root", help="runs folder (default: env QP_RUNS, else runs/)")
    ap.add_argument("--cache-dir", help="dense-track cache (default <runs>/_dense_cache/<split>)")
    ap.add_argument("--out", help="output CSV (default <runs>/<name>/<split>_dense[_<what>].csv)")
    ap.add_argument("--no-original", action="store_true", help="skip re-scoring the original run")
    ap.add_argument("--overlays", help="folder for overlay montages of the accepted motion tracks")
    return ap.parse_args(argv)


def write_overlays(df, records, out_dir: str, what: str, prior_refine: str, cache_dir, motion_kinds=dt.MOTION) -> int:
    """One montage per (video, object) of the accepted dense motion tracks."""
    anns = rc.ca.load_annotations(rc.prepare_records(df, records))
    sparse = {q: {tr.role: list(tr.obs) for tr in a.tracks} for q, a in anns.items()}
    densify(anns, df, records, what, prior_refine, cache_dir, motion_kinds=motion_kinds)
    paths, meta = video_maps(df, records, anns)
    n, seen = 0, set()
    for q, a in anns.items():
        for tr in a.tracks:
            key = (paths.get(q), tr.object.strip().casefold())
            if tr.source != "dense" or key in seen or not any(o.point is not None for o in tr.obs) \
                    or len(tr.obs) <= len(sparse[q][tr.role]):
                continue
            seen.add(key)
            vid = Path(paths[q]).stem.strip()
            safe = "".join(c if c.isalnum() else "_" for c in tr.object)[:40]
            dt.overlay(paths[q], sparse[q][tr.role], tr.obs, meta[q][0], str(Path(out_dir) / f"{vid}__{safe}.jpg"))
            n += 1
    return n


def main(argv=None) -> pd.DataFrame:
    args = parse_args(argv)
    df = load_split(args.split)
    runs_root = Path(args.out_root or os.environ.get("QP_RUNS") or ROOT / "runs")
    rec_dir = runs_root / args.name / args.split / "records"
    records = rc.load_records(rec_dir)
    if not records:
        raise SystemExit(f"no records under {rec_dir}")
    df = df[df.video_id.isin(records)]
    if args.videos:
        df = df[df.video_id.isin(args.videos.split(","))]
    vids = list(dict.fromkeys(df.video_id))[:args.limit_videos or None]
    df = df[df.video_id.isin(vids)].reset_index(drop=True)
    cache_dir = args.cache_dir or runs_root / "_dense_cache" / args.split
    print(f"{args.name}/{args.split}: {len(vids)} videos, {len(df)} questions; dense {args.what}, "
          f"prior refine {args.prior_refine}, size method {args.size_method}, {args.workers} workers")

    tables = {}
    if not args.no_original:
        tables["original"] = build(df, records, "none", args.rule)
    log: list = []
    t0 = time.time()
    kinds = dt.MOTION + (("distance",) if args.with_distance else ())
    res = build(df, records, args.what, args.rule, args.prior_refine, cache_dir, args.workers, log, args.size_method,
                kinds)
    print(f"dense tracks in {time.time() - t0:.1f} s")
    tables[f"dense_{args.what}"] = res
    out = Path(args.out) if args.out else runs_root / args.name / (
        f"{args.split}_dense.csv" if args.what == "motion" else f"{args.split}_dense_{args.what}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(out, index=False)
    print(f"wrote {out}")

    why = Counter((kind, info.get("why", "?").split(":")[0]) for _, _, kind, info in log)
    print("dense results:", dict(sorted(why.items())))
    if "answer" in df.columns and df["answer"].notna().any():
        tab = mra_table(df, tables)
        with pd.option_context("display.float_format", "{:.3f}".format, "display.width", 200):
            print(tab.to_string(index=False))
        if "original" in tables:
            m = df[["qid", "category", "answer"]].merge(tables["original"], left_on="qid", right_on="id") \
                .merge(res, on="id", suffixes=("_o", "_d"))
            ch = m[(m.parsed_value_o - m.parsed_value_d).abs() > 1e-9 * m.answer.abs()]
            for r in ch.itertuples():
                e = lambda v: f"{(v - r.answer) / r.answer:+.1%}" if rc._valid(v) else "-"  # noqa: E731
                print(f"  qid {r.qid} {r.category}: gt {r.answer:g} | original {r.parsed_value_o:.4g} "
                      f"({e(r.parsed_value_o)}) -> dense {r.parsed_value_d:.4g} ({e(r.parsed_value_d)}) [{r.method_d}]")
    if args.overlays:
        n = write_overlays(df, records, args.overlays, args.what, args.prior_refine, cache_dir, kinds)
        print(f"wrote {n} overlays to {args.overlays}")
    return res


if __name__ == "__main__":
    main()
