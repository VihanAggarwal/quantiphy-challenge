"""Agentic measurement loop (qp.claude_agent): Claude Opus 5.5 measures each video's questions itself with
client-side tools (frames / zoomed crops, tracker, segmentation, the geometry solver) and submits specs,
pixel tracks and direct answers.

    python scripts/run_claude_agent.py --split val --name val_agent_med --effort medium --videos simulation_0196
    python scripts/run_claude_agent.py --split val --name val_agent_med --effort medium --dry-run   # estimate only
    python scripts/run_claude_agent.py --split val_hires --name val_hr_agent --effort high --workers 3

Writes <runs>/<name>/<split>/records/<video_id>.json (status, the claude_annotate-format "parsed" answers and
"meta", usage, cost, every request's usage, every tool call, the transcript without image bytes), the
images the model saw under <runs>/<name>/<split>/images/<video_id>/ (unless --no-save-images), then
<runs>/<name>/<split>.csv with scripts/run_claude.py's columns (id, parsed_value, geo_value, direct_value,
method, flags, geo_method), built by run_claude.build_results: qp.geometry.solve on the submitted specs and
tracks, picked against the direct answers by qp.combine (--rule), so scripts/combine_runs.py takes the CSV.
Cached videos are skipped (resumable); failed / partial ones are re-run only with --retry-failed; cached
records made with other settings (model, effort, agent version) make the run refuse: use a new --name.
A fully cached run sends nothing and re-scores with the current code.

Budget: before anything is sent, every video's cost is estimated (offline token counts of its first message,
a per-turn cost model by effort, or the observed cost per question of this run's records) and the total is
checked against the ledger cap (QP_BUDGET_USD) and --max-usd. Inside a video every request is held against
the cap at its worst case until its usage is in budget/ledger.jsonl, its max_tokens shrinks to fit the
per-video cap (--max-usd-video), and the loop stops at --max-turns / the per-video output-token cap.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qp import budget  # noqa: E402
from qp import claude_agent as ag  # noqa: E402
from qp import combine  # noqa: E402
from qp.data import load_split  # noqa: E402

USABLE = ("ok", "partial")
CONFIG_KEYS = ("model", "effort", "agent_version")   # a cached record must match these


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_claude", ROOT / "scripts" / "run_claude.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rc = _load_runner()


def _json_default(x):
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    if isinstance(x, np.ndarray):
        return x.tolist()
    return str(x)


def save_record(rec_dir: Path, rec: dict) -> Path:
    rec_dir.mkdir(parents=True, exist_ok=True)
    path = rc.record_path(rec_dir, rec["video_id"])
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=_json_default))
    os.replace(tmp, path)
    return path


def agent_config(args) -> ag.AgentConfig:
    return ag.AgentConfig(model=args.model, effort=args.effort, max_turns=args.max_turns, max_tokens=args.max_tokens,
                          max_usd=args.max_usd_video, max_output_tokens=args.max_output_tokens,
                          strict=not args.no_strict, task_budget=args.task_budget,
                          overview_frames=args.overview_frames, run=args.name, split=args.split)


def config_diff(rec: dict, cfg: ag.AgentConfig) -> dict:
    have, cur = rec.get("config") or {}, cfg.settings()
    return {k: (have.get(k), cur[k]) for k in CONFIG_KEYS if have.get(k) is not None and have.get(k) != cur[k]}


def todo_videos(groups: dict, records: dict, retry_failed: bool) -> list[str]:
    return [v for v in groups if v not in records or (retry_failed and records[v].get("status") != "ok")]


# --------------------------------------------------------------------------- estimate

def estimate(groups: dict, todo: list[str], cfg: ag.AgentConfig, records: dict) -> dict:
    """Per-video expected cost: the cost model on the offline token count of each video's first message,
    raised to the observed cost per question of this run's records (>= 2 videos with the same effort);
    each capped at the per-video cap. Videos whose session cannot be built are reported and left out."""
    seen = [r for r in records.values() if r.get("usd") and r.get("effort") == cfg.effort and r.get("meta")]
    per_q = (sum(r["usd"] for r in seen) / max(1, sum(len(r["meta"]["questions"]) for r in seen))
             if len(seen) >= 2 else 0.0)
    per_video, skipped, first = {}, {}, {}
    for v in todo:
        try:
            s = ag.AgentSession(groups[v])
            first[v] = ag.estimate_content_tokens(s.initial_content(cfg.overview_frames, cfg.max_turns, cfg.max_usd))
        except Exception as e:  # noqa: BLE001 - one bad video must not stop the run
            skipped[v] = f"{type(e).__name__}: {e}"
            continue
        n_q = len(groups[v])
        est = ag.estimate_video_usd(first[v], n_q, cfg.effort, cfg.max_turns, cfg.model)
        per_video[v] = min(cfg.max_usd, max(est, per_q * n_q))
    for v, why in skipped.items():
        print(f"  skipping {v}: {why}")
    return {"per_video": per_video, "usd": sum(per_video.values()), "first_tokens": first,
            "how": f"observed ${per_q:.3f}/question on {len(seen)} videos" if per_q else "cost model",
            "worst": cfg.max_usd * len(per_video)}


def guard(est: dict, args) -> bool:
    n = len(est["per_video"])
    if not n:
        print("nothing to send")
        return False
    print(f"estimate: {n} videos, ~${est['usd']:.2f} ({est['how']}); worst case ${est['worst']:.2f} "
          f"(per-video cap ${args.max_usd_video:.2f}); first messages "
          f"{min(est['first_tokens'].values())}-{max(est['first_tokens'].values())} tokens")
    print(f"budget: committed ${budget.committed():.2f} of cap ${budget.cap():.2f}; every request is held at its "
          "worst case until its usage is recorded")
    if args.max_usd and est["usd"] > args.max_usd:
        print(f"refusing: estimate exceeds --max-usd {args.max_usd:.2f}")
        return False
    try:
        budget.check(est["usd"])
    except budget.BudgetExceeded as e:
        print(f"refusing: {e}")
        return False
    return not args.dry_run


# --------------------------------------------------------------------------- run

def run_videos(client, groups: dict, todo: list[str], args, out_dir: Path, rec_dir: Path, est: dict) -> None:
    cfg = agent_config(args)
    spent = {"usd": 0.0}

    def work(vid: str) -> dict:
        need = est["per_video"][vid]
        if args.max_usd and spent["usd"] + cfg.max_usd > args.max_usd:
            raise budget.BudgetExceeded(f"run spend ${spent['usd']:.2f} + per-video cap would pass --max-usd")
        budget.check(need)
        img_dir = None if args.no_save_images else out_dir / "images" / rc.safe_id(vid)
        session = ag.AgentSession(groups[vid], image_dir=img_dir)
        rec = ag.run_video(client, session, cfg)
        rec["split"] = args.split
        spent["usd"] += rec["usd"]
        save_record(rec_dir, rec)
        return rec

    with ThreadPoolExecutor(max(1, args.workers)) as pool:
        futures = {pool.submit(work, v): v for v in todo if v in est["per_video"]}
        for i, fut in enumerate(as_completed(futures), 1):
            vid = futures[fut]
            try:
                rec = fut.result()
                u = rec["usage"]
                print(f"  [{i}/{len(futures)}] {vid}: {rec['status']} ({rec['stop']}) ${rec['usd']:.3f}, "
                      f"{rec['turns']} turns, tools {rec['tool_counts']}, in {u.get('input_tokens', 0)} "
                      f"cache_read {u.get('cache_read_input_tokens', 0)} cache_write "
                      f"{u.get('cache_creation_input_tokens', 0)} out {u.get('output_tokens', 0)}")
            except budget.BudgetExceeded as e:
                print(f"  [{i}/{len(futures)}] {vid}: skipped, {e}")
            except Exception as e:  # noqa: BLE001 - keep going; the video stays pending
                print(f"  [{i}/{len(futures)}] {vid}: failed: {type(e).__name__}: {e}")


def agent_report(records: dict) -> None:
    if not records:
        return
    rows = []
    for v, r in sorted(records.items()):
        u = r.get("usage") or {}
        rows.append({"video": v, "status": r.get("status"), "stop": r.get("stop"), "turns": r.get("turns"),
                     "tools": sum((r.get("tool_counts") or {}).values()),
                     "errors": sum(c.get("is_error", False) for c in r.get("tool_calls") or []),
                     "in": u.get("input_tokens", 0), "cache_read": u.get("cache_read_input_tokens", 0),
                     "cache_write": u.get("cache_creation_input_tokens", 0), "out": u.get("output_tokens", 0),
                     "usd": round(float(r.get("usd") or 0), 3), "sec": r.get("seconds")})
    t = pd.DataFrame(rows)
    print(t.to_string(index=False))
    tools = Counter()
    for r in records.values():
        tools.update(r.get("tool_counts") or {})
    print(f"tool calls: {dict(tools)}; total ${t.usd.sum():.3f}")


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--split", required=True, choices=["val", "val_hires", "test"])
    ap.add_argument("--name", required=True, help="run name, used as the output folder")
    ap.add_argument("--out-root", help="folder for run outputs (default: env QP_RUNS, else runs/)")
    ap.add_argument("--model", default=ag.MODEL)
    ap.add_argument("--effort", choices=list(ag.EFFORTS), default="medium")
    ap.add_argument("--max-turns", type=int, default=ag.MAX_TURNS, help="API requests per video")
    ap.add_argument("--max-tokens", type=int, default=ag.TURN_MAX_TOKENS, help="max_tokens per request")
    ap.add_argument("--max-usd-video", type=float, default=ag.MAX_USD_VIDEO, help="per-video cost cap")
    ap.add_argument("--max-output-tokens", type=int, default=ag.MAX_OUT_VIDEO, help="per-video output-token cap")
    ap.add_argument("--max-usd", type=float, default=0.0, help="refuse / stop the run beyond this total (0 = only the ledger cap)")
    ap.add_argument("--overview-frames", type=int, default=ag.OVERVIEW_FRAMES)
    ap.add_argument("--task-budget", type=int, default=0,
                    help="API task budget in tokens (beta task-budgets-2026-03-13; 0 = off, untested)")
    ap.add_argument("--no-strict", action="store_true", help="tools without strict schemas")
    ap.add_argument("--limit-videos", type=int, default=0, help="only the first N videos")
    ap.add_argument("--videos", default="", help="comma-separated video ids to run")
    ap.add_argument("--workers", type=int, default=2, help="videos in parallel")
    ap.add_argument("--retry-failed", action="store_true", help="re-run videos whose record is not ok")
    ap.add_argument("--rule", choices=list(combine.RULES), default=combine.DEFAULT_RULE,
                    help="answer selection between geometry and the direct answer (qp.combine; no API effect)")
    ap.add_argument("--refine-priors", action="store_true",
                    help="optical-flow refinement of motion-prior tracks (qp.refine) when scoring; off: the "
                         "agent's tracks are already tool-measured")
    ap.add_argument("--no-save-images", action="store_true", help="do not write the images the model saw")
    ap.add_argument("--dry-run", action="store_true", help="print the estimate and stop")
    return ap.parse_args(argv)


def main(argv=None, client=None) -> pd.DataFrame | None:
    args = parse_args(argv)
    rc.load_env()
    df = load_split(args.split)
    if args.videos:
        df = df[df.video_id.isin(args.videos.split(","))]
    vids = list(dict.fromkeys(df.video_id))
    if args.limit_videos:
        vids = vids[:args.limit_videos]
    df = df[df.video_id.isin(vids)].reset_index(drop=True)
    missing = sorted(set(df.video_id[df.video_path == ""]))
    if missing:
        raise SystemExit(f"{len(missing)} videos not found locally (e.g. {missing[0]}); run scripts/download_data.py")
    groups = {v: g.reset_index(drop=True) for v, g in df.groupby("video_id", sort=False)}
    runs_root = Path(args.out_root or os.environ.get("QP_RUNS") or ROOT / "runs")
    out_dir = runs_root / args.name / args.split
    rec_dir = out_dir / "records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    if not (out_dir / "config.json").exists():
        (out_dir / "config.json").write_text(json.dumps(vars(args), indent=2))
    cfg = agent_config(args)
    records = {v: r for v, r in rc.load_records(rec_dir).items() if v in groups}
    todo = todo_videos(groups, records, args.retry_failed)
    stale = {v: d for v, r in records.items() if v not in todo and r.get("status") in USABLE
             and (d := config_diff(r, cfg))}
    if stale:
        v, d = next(iter(stale.items()))
        raise SystemExit(f"{len(stale)} cached record(s) were made with other settings (e.g. {v}: "
                         + ", ".join(f"{k} {a} vs {b}" for k, (a, b) in d.items()) + "); use a new --name")
    print(f"{len(groups)} videos ({len(df)} questions): {len(groups) - len(todo)} cached, {len(todo)} to run; "
          f"{args.model} effort={args.effort} max_turns={args.max_turns} per-video cap ${args.max_usd_video:.2f}")
    if todo:
        est = estimate(groups, todo, cfg, records)
        if guard(est, args):
            run_videos(client or rc._client(), groups, todo, args, out_dir, rec_dir, est)
        elif args.dry_run:
            return None
    records = {v: r for v, r in rc.load_records(rec_dir).items() if v in groups}
    rc.REFINE_PRIORS = bool(args.refine_priors)
    res = rc.build_results(df, records, args.rule)
    out_csv = runs_root / args.name / f"{args.split}.csv"
    res.to_csv(out_csv, index=False)
    print(f"wrote {out_csv}")
    rc.report(df, res, records)
    agent_report(records)
    return res


if __name__ == "__main__":
    main()
