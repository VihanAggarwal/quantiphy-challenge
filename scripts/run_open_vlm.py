"""Track B (open weights) on a GPU, e.g. Google Colab: Qwen3-VL specs / grounding / direct answers,
Code-as-World-VL-9B direct answers, and the geometry step (CPU).

    pip install "vllm==0.19.1" "transformers==5.11.0" "qwen-vl-utils==0.0.14" "decord==0.6.0"
    python scripts/run_open_vlm.py --split val --task specs    --name qwen8b
    python scripts/run_open_vlm.py --split val --task annotate --name qwen8b --geometry   # specs made if missing
    python scripts/run_open_vlm.py --split val --task direct   --name qwen8b
    python scripts/run_open_vlm.py --split val --task caw      --name caw9b
    python scripts/run_open_vlm.py --split val --task geometry --name qwen8b --direct-from runs/caw9b/val/caw.csv
    python scripts/run_open_vlm.py --csv "external/QuantiPhy/model_run_example/GT_CIB_Ready/CIB_Ready - test4.csv" \\
        --video-dir external/QuantiPhy/model_run_example/data/all_480p --task direct --name smoke

Outputs go to runs/<name>/<split>/ (or --out, e.g. a Google Drive folder): one JSON per video under
specs/, annotate/, direct/ or caw/ (written atomically after each chunk, so an interrupted run resumes
and finished videos are skipped), config.json, and CSVs: direct.csv / caw.csv (id, parsed_value) and
geometry.csv (id, parsed_value, geo_value, direct_value, method, flags; geometry when valid, else the
direct answer from --direct-from or this run's direct.csv / caw.csv; a geometry value beyond loose
physical bounds, or more than --max-disagree times off the direct answer, is replaced by the direct one).
Failed generations (backend errors such as CUDA OOM) are never cached, so the next run retries them.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qp.data import ROOT, _finalize, load_split  # noqa: E402
from qp.mra import score  # noqa: E402
from qp.spec import KIND_DIM, QuestionSpec, RoleTrack  # noqa: E402

TASKS = ("specs", "annotate", "direct", "caw", "geometry")
GEO_MAX_SI = {"L": 1e4, "V": 1e3, "A": 1e3}   # m, m/s, m/s^2: a geometry answer beyond this is a blow-up


def safe_id(video_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(video_id).strip())[:80] or "video"


def load_questions(args) -> tuple[pd.DataFrame, str]:
    """(questions, split label). --csv: validation-format CSV (first unnamed column = qid, else the
    row number), videos under --video-dir. Validation answers stay in the frame for scoring only."""
    if not args.csv:
        try:
            return load_split(args.split), args.split
        except (StopIteration, FileNotFoundError) as e:
            raise SystemExit(f"{args.split} data not found under data/ ({type(e).__name__}); "
                             "run scripts/download_data.py") from e
    raw = pd.read_csv(args.csv)
    if str(raw.columns[0]).startswith("Unnamed"):
        raw = raw.rename(columns={raw.columns[0]: "qid"})
    elif "qid" not in raw.columns:
        raw.insert(0, "qid", range(len(raw)))
    raw = raw.rename(columns={"ground_truth_prior": "prior", "ground_truth_posterior": "answer"})
    video_dir = Path(args.video_dir) if args.video_dir else Path(args.csv).parent
    return _finalize(raw, video_dir), args.split or safe_id(Path(args.csv).stem)


# --------------------------------------------------------------------------- records

def _json_default(o):
    if hasattr(o, "item"):
        return o.item()
    raise TypeError(type(o).__name__)


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, default=_json_default))   # inf times -> Infinity
    os.replace(tmp, path)


def load_dir(d: Path) -> dict[str, dict]:
    out = {}
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        try:
            rec = json.loads(p.read_text())
        except ValueError:
            continue
        out[rec["video_id"]] = rec
    return out


def specs_from(d: Path) -> dict[int, QuestionSpec]:
    return {int(q): QuestionSpec.from_dict(v["spec"]) for rec in load_dir(d).values()
            for q, v in rec.get("questions", {}).items()}


def load_specs(specs_dir: Path, override: str | None = None) -> dict[int, QuestionSpec]:
    """This run's specs, overridden by those of another run's specs folder (--specs-from)."""
    return specs_from(specs_dir) | (specs_from(Path(override)) if override else {})


def done(rec: dict | None, task: str, qids: list[int]) -> bool:
    if not rec:
        return False
    have = rec.get("tracks" if task == "annotate" else "questions", {})
    return all(str(q) in have for q in qids)


# --------------------------------------------------------------------------- runners

def make_runner(args):
    if args.task == "caw":
        from qp.open.caw import CAW, MODEL_ID, MODEL_REVISION
        kw = {"max_model_len": args.max_model_len} if args.max_model_len else {}
        return CAW(args.model or MODEL_ID, args.revision or MODEL_REVISION, backend=args.backend,
                   gpu_memory_utilization=args.gpu_mem or None, chat_template=args.chat_template, **kw)
    from qp.open.qwen_vl import DEFAULT_MODEL, QwenVL
    kw = {"revision": args.revision, "load_4bit": args.load_4bit}
    if args.backend == "vllm":
        kw.update(gpu_memory_utilization=args.gpu_mem or 0.85, max_model_len=args.max_model_len or 16384,
                  quantization=args.quantization, tensor_parallel_size=args.tp)
    return QwenVL(args.model or DEFAULT_MODEL, backend=args.backend, **kw)


def run_chunk(runner, task: str, groups: dict[str, pd.DataFrame], vids: list[str], dirs: dict[str, Path], args,
              specs: dict[int, QuestionSpec] | None = None) -> None:
    """One generate() batch over `vids`; writes one record per video. `specs` (annotate): the known
    specs (loaded once by main), extended in place with the ones parsed here. Failed generations
    are left out of the records, so those questions / videos are retried by the next run."""
    if task in ("specs", "annotate"):
        specs = {} if specs is None else specs
        need = [v for v in vids if task == "specs" or any(int(q) not in specs for q in groups[v].qid)]
        if need:
            rows = pd.concat([groups[v] for v in need])
            res = runner.parse_specs(rows, retries=args.retries, guided=not args.no_guided)
            for v in need:
                qs = {str(int(q)): {"spec": res[int(q)]["spec"].to_dict(),
                                    **{k: res[int(q)][k] for k in ("flags", "raw", "attempts", "source")}}
                      for q in groups[v].qid if not res[int(q)].get("error")}
                if len(qs) < len(groups[v]):
                    print(f"  {v}: {len(groups[v]) - len(qs)} spec(s) failed to generate; retried next run")
                save_json(dirs["specs"] / f"{safe_id(v)}.json", {"video_id": v, "model": runner.model, "questions": qs})
                for q in qs:
                    specs.setdefault(int(q), res[int(q)]["spec"])     # --specs-from keeps precedence
        if task == "specs":
            return
        recs = runner.annotate_videos([groups[v] for v in vids], specs, n_uniform=args.ground_frames,
                                      max_frames=args.max_ground_frames, extents=args.extents)
        for v, rec in recs.items():
            if rec.get("error"):
                print(f"  {v}: not cached ({rec['error']}); retried next run")
                continue
            save_json(dirs["annotate"] / f"{safe_id(v)}.json", rec)
        return
    ans = runner.direct_answer([groups[v] for v in vids], n_frames=args.frames)
    for v in vids:
        qs = {str(int(q)): ans[int(q)] for q in groups[v].qid if int(q) in ans and not ans[int(q)].get("error")}
        if len(qs) < len(groups[v]):   # errors are not cached: the video is retried by the next run
            print(f"  {v}: {len(groups[v]) - len(qs)} question(s) failed: "
                  f"{next((a.get('error') for a in ans.values() if a.get('error')), '')}")
        save_json(dirs[task] / f"{safe_id(v)}.json", {"video_id": v, "model": runner.model, "questions": qs})


def write_direct_csv(df: pd.DataFrame, d: Path, out_csv: Path) -> pd.DataFrame:
    recs = {int(q): v for rec in load_dir(d).values() for q, v in rec.get("questions", {}).items()}
    vals = [recs.get(int(q), {}).get("value") for q in df.qid]
    res = pd.DataFrame({"id": df.qid.astype(int), "parsed_value": [math.nan if v is None else v for v in vals]})
    res.to_csv(out_csv, index=False)
    print(f"wrote {out_csv} ({int(res.parsed_value.isna().sum())} of {len(res)} without a usable number)")
    return res


# --------------------------------------------------------------------------- geometry

def _valid(v) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(v) and v > 0


def read_values(path: Path | None) -> dict[int, float]:
    if path is None or not Path(path).exists():
        return {}
    d = pd.read_csv(path)
    d = d.rename(columns={d.columns[0]: "id"})
    return {int(i): float(v) for i, v in zip(d["id"], pd.to_numeric(d["parsed_value"], errors="coerce")) if _valid(v)}


def run_geometry(df: pd.DataFrame, out_dir: Path, direct_from: str | None = None,
                 specs_dir: str | None = None, max_disagree: float = 10.0) -> pd.DataFrame:
    """Specs + tracks of this run -> qp.geometry.solve; the direct answer fills in where geometry
    fails, where its SI value exceeds GEO_MAX_SI (flag geo_rejected_implausible), or where geometry
    and direct differ by more than `max_disagree` times (flag geo_rejected_disagree; 0 = keep geometry).
    geo_value keeps the raw geometry value."""
    try:
        from qp.geometry import solve
    except ImportError:
        solve = None
    if direct_from and not Path(direct_from).exists():
        raise SystemExit(f"--direct-from {direct_from} not found")
    specs = load_specs(out_dir / "specs", specs_dir)
    recs = load_dir(out_dir / "annotate")
    direct_path = Path(direct_from) if direct_from else next(
        (p for p in (out_dir / "direct.csv", out_dir / "caw.csv") if p.exists()), None)
    direct = read_values(direct_path)
    rows = []
    for r in df.itertuples():
        qid, rec, spec = int(r.qid), recs.get(r.video_id), specs.get(int(r.qid))
        flags, geo, method, geo_si = [], None, "", None
        if solve is None:
            flags.append("no_geometry_module")
        elif spec is None or rec is None or str(qid) not in rec.get("tracks", {}):
            flags.append("no_spec" if spec is None else "no_tracks")
        else:
            try:
                ans = solve(spec, [RoleTrack.from_dict(t) for t in rec["tracks"][str(qid)]],
                            tuple(rec["meta"]["image_size"]), float(rec["meta"]["fps"]))
                geo, method, geo_si = ans.value, ans.method, ans.debug.get("value_si")
                flags += [f"geo:{f}" for f in ans.flags]
            except Exception as e:  # noqa: BLE001 - one bad question must not stop the run
                flags.append(f"geo_error:{type(e).__name__}")
        d = direct.get(qid)
        use_geo = _valid(geo)
        if use_geo and _valid(geo_si) and geo_si > GEO_MAX_SI.get(KIND_DIM.get(spec.target.kind, "L"), math.inf):
            flags.append("geo_rejected_implausible")
            use_geo = False
        ratio = max(geo / d, d / geo) if use_geo and _valid(d) else 1.0
        if ratio > 3:
            flags.append("geo_direct_disagree")
        if max_disagree > 0 and ratio > max_disagree:
            flags.append("geo_rejected_disagree")
            use_geo = False
        if use_geo:
            value, how = geo, f"geometry:{method}" if method else "geometry"
        elif _valid(d):
            value, how = d, "direct"
        else:
            value, how = math.nan, "none"
        rows.append({"id": qid, "parsed_value": value, "geo_value": geo if _valid(geo) else math.nan,
                     "direct_value": d if _valid(d) else math.nan, "method": how, "flags": ";".join(sorted(set(flags)))})
    res = pd.DataFrame(rows, columns=["id", "parsed_value", "geo_value", "direct_value", "method", "flags"])
    out_csv = out_dir / "geometry.csv"
    res.to_csv(out_csv, index=False)
    print(f"wrote {out_csv}; {len(direct)} direct answers from {direct_path or 'none'}; methods "
          f"{dict(Counter(m.split(':')[0] for m in res.method))}")
    return res


def report(df: pd.DataFrame, res: pd.DataFrame, cols=("parsed_value",)) -> None:
    if "answer" not in df.columns or df.answer.isna().all():
        return
    m = df[["qid", "category", "answer"]].merge(res, left_on="qid", right_on="id")
    if set(m.category) >= {"S2", "D2", "S3", "D3"}:
        for c in cols:
            s = score(m, c)
            print(f"MRA {c}: {s['mra']:.3f} (" + " ".join(f"{k}={v:.3f}" for k, v in s["per_category"].items()) + ")")


# --------------------------------------------------------------------------- main

def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--split", choices=["val", "test"])
    ap.add_argument("--csv", help="questions CSV (validation format) instead of --split")
    ap.add_argument("--video-dir", help="videos for --csv (default: the CSV's folder)")
    ap.add_argument("--task", choices=TASKS, required=True)
    ap.add_argument("--name", required=True, help="run name: output folder runs/<name>/<split>")
    ap.add_argument("--out", help="output folder instead of runs/<name>/<split> (e.g. on Google Drive)")
    ap.add_argument("--model", help="HF model id (default Qwen/Qwen3-VL-8B-Instruct; caw: Code-as-World-VL-9B)")
    ap.add_argument("--revision", help="HF revision (caw default: the pinned one)")
    ap.add_argument("--backend", choices=["vllm", "hf"], default="vllm")
    ap.add_argument("--gpu-mem", type=float, default=0.0,
                    help="vLLM gpu_memory_utilization (0 = 0.85; caw: 0.5 as the authors on >= 60 GiB, else 0.9)")
    ap.add_argument("--max-model-len", type=int, default=0)
    ap.add_argument("--quantization", help="vLLM quantization, e.g. bitsandbytes or fp8")
    ap.add_argument("--load-4bit", action="store_true", help="hf backend: bitsandbytes NF4 (32B on 40 GB)")
    ap.add_argument("--tp", type=int, default=1, help="vLLM tensor parallel size")
    ap.add_argument("--chat-template", help="caw: path to the authors' qwen3_5_no_think.jinja")
    ap.add_argument("--limit-videos", type=int, default=0, help="only the first N videos")
    ap.add_argument("--videos", default="", help="comma-separated video ids")
    ap.add_argument("--chunk-videos", type=int, default=8, help="videos per generate() batch / cache write")
    ap.add_argument("--frames", type=int, default=32, help="direct: uniform frames per video")
    ap.add_argument("--ground-frames", type=int, default=16, help="annotate: uniform frames")
    ap.add_argument("--max-ground-frames", type=int, default=40, help="annotate: cap incl. frames at asked times")
    ap.add_argument("--extents", action="store_true", help="annotate: also ask endpoints of size dimensions")
    ap.add_argument("--retries", type=int, default=2, help="specs: sampled retries for unusable JSON")
    ap.add_argument("--no-guided", action="store_true", help="specs: no vLLM JSON-schema decoding")
    ap.add_argument("--specs-from", help="annotate/geometry: specs folder of another run (overrides)")
    ap.add_argument("--direct-from", help="geometry: CSV (id, parsed_value) used where geometry fails")
    ap.add_argument("--max-disagree", type=float, default=10.0,
                    help="geometry: use the direct answer when geometry differs from it by more than this "
                         "factor (0 = always geometry)")
    ap.add_argument("--geometry", action="store_true", help="run the geometry step after the task")
    args = ap.parse_args(argv)
    if not args.split and not args.csv:
        ap.error("one of --split or --csv is required")
    return args


def main(argv=None, runner=None) -> pd.DataFrame | None:
    args = parse_args(argv)
    df, label = load_questions(args)
    if args.videos:
        df = df[df.video_id.isin(args.videos.split(","))]
    vids = list(dict.fromkeys(df.video_id))
    if args.limit_videos:
        vids = vids[:args.limit_videos]
    df = df[df.video_id.isin(vids)].reset_index(drop=True)
    out_dir = Path(args.out) if args.out else ROOT / "runs" / args.name / label
    dirs = {t: out_dir / t for t in TASKS[:4]}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"config_{args.task}.json").write_text(json.dumps(vars(args), indent=2))
    eval_df = df
    df = df.drop(columns=["answer"], errors="ignore")   # inference never sees answers

    if args.task == "geometry":
        res = run_geometry(df, out_dir, args.direct_from, args.specs_from, args.max_disagree)
        report(eval_df, res, ("parsed_value", "geo_value", "direct_value"))
        return res
    missing = set() if args.task == "specs" else set(df.video_id[df.video_path == ""])   # specs: text only
    if missing and len(missing) == len(vids):
        raise SystemExit(f"none of the {len(vids)} videos found locally; run scripts/download_data.py")
    if missing:
        print(f"WARNING: {len(missing)} videos not found locally (e.g. {sorted(missing)[0]}): skipped")
    groups = {v: g.reset_index(drop=True) for v, g in df.groupby("video_id", sort=False)}
    rec_dir = dirs["specs" if args.task == "specs" else args.task]
    cached = load_dir(rec_dir)
    todo = [v for v in vids if v not in missing and not done(cached.get(v), args.task, list(groups[v].qid))]
    specs = load_specs(dirs["specs"], args.specs_from) if args.task == "annotate" else None
    print(f"{len(vids)} videos ({len(df)} questions): {len(vids) - len(todo) - len(missing)} cached, "
          f"{len(todo)} to run; task={args.task} backend={args.backend} out={out_dir}")
    if todo:
        runner = runner or make_runner(args)
    for i in range(0, len(todo), max(1, args.chunk_videos)):
        chunk = todo[i:i + max(1, args.chunk_videos)]
        try:
            run_chunk(runner, args.task, groups, chunk, dirs, args, specs)
        except Exception as e:  # noqa: BLE001 - retry the chunk's videos one by one, then move on
            print(f"  chunk {chunk[0]}..: {type(e).__name__}: {e}; retrying per video")
            for v in chunk:
                try:
                    run_chunk(runner, args.task, groups, [v], dirs, args, specs)
                except Exception as e2:  # noqa: BLE001 - stays pending for the next run
                    print(f"  {v}: failed: {type(e2).__name__}: {e2}")
        print(f"  {min(i + len(chunk), len(todo))}/{len(todo)} videos")

    res = None
    if args.task in ("direct", "caw"):
        res = write_direct_csv(df, rec_dir, out_dir / f"{args.task}.csv")
        report(eval_df, res)
    elif args.task == "specs":
        flags = Counter(f for rec in load_dir(rec_dir).values() for q in rec["questions"].values() for f in q["flags"])
        print(f"spec repairs: {dict(flags)}")
    if args.geometry:
        res = run_geometry(df, out_dir, args.direct_from, args.specs_from, args.max_disagree)
        report(eval_df, res, ("parsed_value", "geo_value", "direct_value"))
    return res


if __name__ == "__main__":
    main()
