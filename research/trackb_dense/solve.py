"""Re-solve the geometry on open-model tracks (Qwen grounding / SAM 2) with Track A's post-steps.

    .venv/bin/python research/trackb_dense/solve.py val|test [--src qwen|cv] [--dense off|motion] [--refine]
                     [--lab-fov] [--seen-scale] [--tag NAME] [--workers 4]

Writes out/<split>/<tag>.csv: id, geo_value, geo_si, flags, method, prior_px, target_px (no fallback; the
direct fallback and scoring are applied by evaluate.py). Dense tracks are cached under common.CACHE.
"""
from __future__ import annotations

import argparse
import copy
import pickle
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tbcommon import CACHE, OUT, ROOT, questions, specs, tracks  # noqa: E402
from qp import combine  # noqa: E402
from qp.claude_annotate import LAB_FOV_DEG, Annotation  # noqa: E402
from qp.geometry import solve  # noqa: E402
from qp.spec import RoleTrack  # noqa: E402


def annotations(split: str, src: str, df: pd.DataFrame):
    """{qid: Annotation}, {qid: video path}, {qid: (fps, (W, H), seen_scale)}, {qid: video record meta}."""
    sp = specs(split)
    recs = tracks(split, src)
    anns, paths, meta = {}, {}, {}
    for r in df.itertuples():
        q, rec = int(r.qid), recs.get(r.video_id)
        if q not in sp or rec is None or str(q) not in rec.get("tracks", {}):
            continue
        trs = [RoleTrack.from_dict(t) for t in rec["tracks"][str(q)]]
        anns[q] = Annotation(copy.deepcopy(sp[q]), trs, None, None, [])
        m = rec["meta"]
        paths[q] = str(r.video_path)
        meta[q] = (float(m.get("fps") or r.fps), tuple(int(v) for v in m["image_size"]), 1.0)
    return anns, paths, meta


def post(anns, paths, meta, split: str, src: str, dense: str, refine_on: bool, workers: int):
    refined = set()
    if refine_on:
        from qp import refine
        rlog: list = []
        refine.refine_annotations(anns, paths, {q: m[:2] for q, m in meta.items()}, log=rlog)
        refined = {(q, role) for q, role, info in rlog if info.get("why") == "refined"}
    if dense != "off":
        from qp import dense_track as dt
        log: list = []
        dt.densify_annotations(anns, paths, meta, what=dense, cache_dir=CACHE / f"dense_{src}_{split}", log=log,
                               workers=workers, skip=refined)
        return log
    return []


def solve_all(anns, df, meta, lab_fov: bool, seen_scale: float | None = None) -> pd.DataFrame:
    rows = []
    for r in df.itertuples():
        q = int(r.qid)
        a = anns.get(q)
        row = dict(id=q, geo_value=float("nan"), geo_si=float("nan"), flags="no_tracks", method="",
                   prior_px=float("nan"), target_px=float("nan"))
        if a is not None:
            fov = LAB_FOV_DEG if lab_fov and r.video_source in combine.CAMERA_SOURCES and a.spec.is_3d else None
            ans = solve(a.spec, a.tracks, meta[q][1], meta[q][0], seen_scale=seen_scale,
                        **({"camera_fov_deg": fov} if fov else {}))
            row.update(geo_value=ans.value if ans.value else float("nan"),
                       geo_si=ans.debug.get("value_si", float("nan")), flags=";".join(ans.flags + a.flags),
                       method=ans.method or "", prior_px=ans.debug.get("prior_px", float("nan")),
                       target_px=ans.debug.get("target_px", float("nan")))
        rows.append(row)
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("split")
    ap.add_argument("--src", default="qwen")
    ap.add_argument("--dense", default="off")
    ap.add_argument("--refine", action="store_true")
    ap.add_argument("--lab-fov", action="store_true")
    ap.add_argument("--tag", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--save-anns", action="store_true")
    a = ap.parse_args(argv)
    df = questions(a.split)
    anns, paths, meta = annotations(a.split, a.src, df)
    log = post(anns, paths, meta, a.split, a.src, a.dense, a.refine, a.workers)
    res = solve_all(anns, df, meta, a.lab_fov)
    tag = a.tag or f"{a.src}_{a.dense}{'_refine' if a.refine else ''}{'_labfov' if a.lab_fov else ''}"
    (OUT / a.split).mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT / a.split / f"{tag}.csv", index=False)
    if a.save_anns:
        CACHE.mkdir(parents=True, exist_ok=True)
        pickle.dump(anns, open(CACHE / f"anns_{a.split}_{tag}.pkl", "wb"))
    if log:
        acc = pd.Series([str(i.get("why", "")) for _, _, _, i in log]).value_counts()
        print("dense log:", acc.head(12).to_dict())
    print(f"wrote {OUT / a.split / (tag + '.csv')}: {res.geo_value.notna().sum()} of {len(res)} solved")


if __name__ == "__main__":
    main()
