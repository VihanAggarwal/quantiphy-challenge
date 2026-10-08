"""Track B CV stage: Grounding DINO / OWLv2 + SAM 2 pixel tracks for every question of a split (GPU).

    python scripts/run_cv.py --split val --specs runs/qwen8b/val/specs --name cv
    python scripts/run_cv.py --split val --specs runs/qwen8b/val/specs --name cv --solve      # + geometry only
    python scripts/run_open_vlm.py --split val --task geometry --name cv \\
        --specs-from runs/qwen8b/val/specs --direct-from runs/qwen8b/val/direct.csv       # geometry + fallback
    python scripts/run_cv.py --csv "external/QuantiPhy/model_run_example/GT_CIB_Ready/CIB_Ready - test4.csv" \\
        --video-dir external/QuantiPhy/model_run_example/data/all_480p --specs rules --name cv_smoke

--specs: a parser run's spec folder or file (run_open_vlm specs/, run_claude records/, or a JSON / JSONL
of QuestionSpec dicts), or "rules" for qp.open.qwen_vl.rule_spec; questions without a spec fall back
to rule_spec (flagged) unless --no-rule-fallback.

Writes one record per video to --out (default runs/<name>/<split>/annotate/<video_id>.json), the
format run_open_vlm.py's geometry step reads: {"video_id", "model", "meta": {"image_size", "fps", ...},
"objects", "tracks": {qid: [RoleTrack dicts]}, "flags": {qid: [...]}}; detections and per-frame mask
features go to --cache (default <out>/../cv_cache). A video whose record covers every question with
an unchanged spec is skipped (resumable); --force rebuilds records from the cache, --fresh also redoes
detection and SAM 2 (an undetected phrase stays cached as such until --fresh). --solve also writes
<out>/../cv_geometry.csv (id, parsed_value, method, flags) from qp.geometry.solve alone.
A failing video is reported and skipped; the exit code is non-zero when every video to run failed or
more than --max-failed of them did (a model that fails to load stops the run at once).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qp.data import ROOT, _finalize, load_split  # noqa: E402
from qp.open import cv_track as cv  # noqa: E402
from qp.spec import QuestionSpec, RoleTrack  # noqa: E402


def safe_id(video_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(video_id).strip())[:80] or "video"


def load_questions(args) -> tuple[pd.DataFrame, str]:
    """(questions, split label); --csv: validation-format CSV with videos under --video-dir."""
    if not args.csv:
        return load_split(args.split), args.split
    raw = pd.read_csv(args.csv)
    if str(raw.columns[0]).startswith("Unnamed"):
        raw = raw.rename(columns={raw.columns[0]: "qid"})
    elif "qid" not in raw.columns:
        raw.insert(0, "qid", range(len(raw)))
    raw = raw.rename(columns={"ground_truth_prior": "prior", "ground_truth_posterior": "answer"})
    video_dir = Path(args.video_dir) if args.video_dir else Path(args.csv).parent
    return _finalize(raw, video_dir), args.split or safe_id(Path(args.csv).stem)


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, separators=(",", ":")))
    os.replace(tmp, path)


def get_specs(args, df: pd.DataFrame) -> tuple[dict[int, QuestionSpec], set[int]]:
    """Specs per qid and the qids whose spec came from the rule-based fallback."""
    texts = {int(q): str(t or "") for q, t in zip(df["qid"], df.get("depth_info", [""] * len(df)))}
    specs = {} if args.specs == "rules" else cv.load_specs(args.specs, depth_texts=texts)
    missing = [r for r in df.itertuples() if int(r.qid) not in specs]
    ruled = set()
    if missing and (args.specs == "rules" or not args.no_rule_fallback):
        try:
            from qp.open.qwen_vl import rule_spec
        except ImportError as e:
            print(f"no rule-based fallback ({e}); {len(missing)} questions without a spec are skipped")
            return specs, ruled
        for r in missing:
            try:
                specs[int(r.qid)] = rule_spec(r)
                ruled.add(int(r.qid))
            except Exception as e:  # noqa: BLE001 - the question just gets no tracks
                print(f"  qid {r.qid}: rule_spec failed: {type(e).__name__}: {e}")
    for r in df.itertuples():  # parsers may leave is_3d unset; the video type is authoritative
        s = specs.get(int(r.qid))
        if s is not None and str(r.video_type)[1:2] == "3":
            s.is_3d = True
    return specs, ruled


def solve_all(df: pd.DataFrame, specs: dict, out: Path) -> pd.DataFrame:
    from qp.geometry import solve
    recs = {v: read_json(out / f"{safe_id(v)}.json") for v in dict.fromkeys(df.video_id)}
    rows = []
    for r in df.itertuples():
        qid, rec, spec = int(r.qid), recs.get(r.video_id), specs.get(int(r.qid))
        value, method, flags = math.nan, "none", []
        if spec is None or not rec:
            flags.append("no_spec" if spec is None else "no_record")
        else:
            tracks = [RoleTrack.from_dict(t) for t in rec.get("tracks", {}).get(str(qid), [])]
            ans = solve(spec, tracks, tuple(rec["meta"]["image_size"]), float(rec["meta"]["fps"]))
            flags = ans.flags + rec.get("flags", {}).get(str(qid), [])
            if ans.value is not None:
                value, method = ans.value, ans.method
        rows.append({"id": qid, "parsed_value": value, "method": method, "flags": ";".join(flags)})
    return pd.DataFrame(rows, columns=["id", "parsed_value", "method", "flags"])


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--split", choices=["val", "test"])
    ap.add_argument("--csv", help="questions CSV (validation format) instead of --split")
    ap.add_argument("--video-dir", help="videos for --csv (default: the CSV's folder)")
    ap.add_argument("--specs", required=True, help='spec folder / file of a parser run, or "rules"')
    ap.add_argument("--no-rule-fallback", action="store_true", help="skip questions without a spec")
    ap.add_argument("--name", default="cv", help="run name: default output runs/<name>/<split>/annotate")
    ap.add_argument("--out", help="record folder (e.g. on Google Drive) instead of runs/<name>/<split>/annotate")
    ap.add_argument("--cache", help="detection / mask-feature cache folder (default <out>/../cv_cache)")
    ap.add_argument("--detector", choices=sorted(cv.DETECTOR_MODELS), default="gdino")
    ap.add_argument("--det-model", help="HF id (default: IDEA-Research/grounding-dino-base or owlv2-base)")
    ap.add_argument("--det-threshold", type=float, help="box score threshold (default 0.25 gdino, 0.1 owlv2)")
    ap.add_argument("--segmenter", choices=["auto", "official", "hf"], default="auto",
                    help="SAM 2 implementation: official sam2 package, transformers, or official if installed")
    ap.add_argument("--sam-model", default=cv.SAM_MODEL)
    ap.add_argument("--max-frames", type=int, default=cv.MAX_FRAMES, help="frames tracked per video (strided)")
    ap.add_argument("--keyframes", type=int, default=cv.N_KEYFRAMES, help="uniform detection keyframes")
    ap.add_argument("--point", choices=["centroid", "bottom", "top"], default="centroid")
    ap.add_argument("--device", help="cuda / cpu (default: cuda if available)")
    ap.add_argument("--limit-videos", type=int, default=0, help="only the first N videos")
    ap.add_argument("--videos", default="", help="comma-separated video ids")
    ap.add_argument("--force", action="store_true", help="rebuild records of finished videos (cache reused)")
    ap.add_argument("--fresh", action="store_true", help="ignore the cache: detect and segment again")
    ap.add_argument("--solve", action="store_true", help="run qp.geometry.solve and write cv_geometry.csv")
    ap.add_argument("--max-failed", type=float, default=0.05,
                    help="exit non-zero when more than this share of the videos to run failed (or all did)")
    args = ap.parse_args(argv)
    if not args.split and not args.csv:
        ap.error("one of --split or --csv is required")
    return args


def main(argv=None, tracker=None) -> pd.DataFrame | None:
    args = parse_args(argv)
    df, label = load_questions(args)
    if args.videos:
        df = df[df.video_id.isin(args.videos.split(","))]
    vids = list(dict.fromkeys(df.video_id))
    if args.limit_videos:
        vids = vids[:args.limit_videos]
    df = df[df.video_id.isin(vids)].reset_index(drop=True)
    eval_df, df = df, df.drop(columns=["answer"], errors="ignore")   # tracking never sees answers
    out = Path(args.out) if args.out else ROOT / "runs" / args.name / label / "annotate"
    cache_dir = Path(args.cache) if args.cache else out.parent / "cv_cache"
    out.mkdir(parents=True, exist_ok=True)
    (out.parent / "config_cv.json").write_text(json.dumps(vars(args), indent=2))
    specs, ruled = get_specs(args, df)
    print(f"{len(vids)} videos ({len(df)} questions): {len(specs)} specs ({len(ruled)} rule-based)")

    tracker = tracker or cv.CVTracker(args.detector, args.segmenter, args.det_model, args.sam_model, args.device,
                                      args.max_frames, args.keyframes, args.point, args.det_threshold)
    groups = {v: g.reset_index(drop=True) for v, g in df.groupby("video_id", sort=False)}
    sig = {str(q): hashlib.md5(json.dumps(s.to_dict(), sort_keys=True, default=str).encode()).hexdigest()[:12]
           for q, s in specs.items()}   # a record is stale when its question's spec changed
    todo = []
    for v in vids:
        rec = read_json(out / f"{safe_id(v)}.json")
        qids = [str(int(q)) for q in groups[v].qid if int(q) in specs]
        fresh = rec and rec.get("model") == tracker.source and rec.get("meta", {}).get("point_mode") == args.point
        if args.force or args.fresh or not fresh or any(rec.get("spec_sig", {}).get(q) != sig[q] for q in qids):
            todo.append(v)
    missing = sorted(set(df.video_id[(df.video_path == "") & df.video_id.isin(todo)]))
    if missing:
        raise SystemExit(f"{len(missing)} videos not found locally (e.g. {missing[0]}); run scripts/download_data.py")
    print(f"{len(vids) - len(todo)} cached, {len(todo)} to run -> {out}")

    t_start, failed = time.time(), {}
    for i, v in enumerate(todo, 1):
        t0 = time.time()
        cache_path = cache_dir / f"{safe_id(v)}.json"
        try:
            rec, cache = tracker.track_video(groups[v], specs, None if args.fresh else read_json(cache_path))
        except cv.ModelLoadError as e:  # every remaining video would fail the same way
            print(f"  [{i}/{len(todo)}] {v}: {e}; stopping")
            failed.update(dict.fromkeys(todo[i - 1:], str(e)))
            break
        except Exception as e:  # noqa: BLE001 - one bad video must not stop the run; it stays pending
            failed[v] = f"{type(e).__name__}: {e}"
            print(f"  [{i}/{len(todo)}] {v}: failed: {failed[v]}")
            continue
        for q in groups[v].qid:
            if int(q) in ruled:
                rec["flags"].setdefault(str(int(q)), []).append("rule_spec")
        rec["spec_sig"] = {q: sig[q] for q in rec["tracks"]}
        save_json(cache_path, cache)
        save_json(out / f"{safe_id(v)}.json", rec)
        n_obj = len(rec["objects"])
        n_ok = sum(o.get("n_frames", 0) > 0 for o in rec["objects"].values())
        print(f"  [{i}/{len(todo)}] {v}: {n_ok}/{n_obj} objects tracked, {time.time() - t0:.1f}s "
              f"(elapsed {(time.time() - t_start) / 60:.1f} min)")

    recs = [read_json(out / f"{safe_id(v)}.json") or {} for v in vids]
    flags = Counter(f.split(":", 1)[-1] for r in recs for fl in r.get("flags", {}).values() for f in fl)
    n_q = sum(bool(t) for r in recs for t in r.get("tracks", {}).values())
    print(f"questions with tracks: {n_q} of {len(df)}; flags: {dict(flags)}")
    res = None
    if args.solve:
        res = solve_all(df, specs, out)
        out_csv = out.parent / "cv_geometry.csv"
        res.to_csv(out_csv, index=False)
        print(f"wrote {out_csv}: {int(res.parsed_value.notna().sum())} of {len(res)} solved; methods "
              f"{dict(Counter(res.method))}")
        if "answer" in eval_df.columns and eval_df.answer.notna().any():
            from qp.mra import score
            m = eval_df[["qid", "category", "answer"]].merge(res, left_on="qid", right_on="id")
            s = score(m)
            cats = " ".join(f"{k}={v:.3f}" for k, v in s["per_category"].items())
            mra = f"{s['mra']:.3f}" if math.isfinite(s["mra"]) else "n/a (not all four categories)"
            print(f"MRA (geometry only, unsolved score 0): {mra} ({cats})")
    if failed:
        v, why = next(iter(failed.items()))
        msg = f"{len(failed)} of {len(todo)} videos failed (e.g. {v}: {why[:300]}); a rerun retries them"
        if len(failed) == len(todo) or len(failed) > args.max_failed * len(todo):
            raise SystemExit(msg)
        print("WARNING:", msg)
    return res


if __name__ == "__main__":
    main()
