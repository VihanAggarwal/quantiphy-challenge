"""GPU runner of RUN_PRESET "agent" (qp.open.agent_loop): one open-weight measuring agent per clip (Track B).

    python -m qp.open.run_agent --split val_hires --out outputs/trackb_agent/val
    python -m qp.open.run_agent --split test --out outputs/trackb_agent/test --max-hours 6 \
        --fallback-csv outputs/trackb_v1/test/caw/caw.csv

One model load (vLLM offline engine, qp.open.ctx_annot.CtxVLLM; default Qwen/Qwen3.6-27B-FP8, Apache-2.0) serves all
clips; --concurrency clip conversations run at once and every round's model turns go to vLLM as one batch. Python
actions run in sandboxed subprocesses on the CPU (cwd = the clip workspace under --ws-root, no network, no tokens in
the environment, reads outside the workspace refused). Nothing here calls a closed model.

Outputs under --out (resumable: clips with an answers file are skipped; a clip cut by a disconnect is run again):
    answers/<video>.json       {"answers": {qid: value}, "source": {qid: agent|forced|workspace_file|twin:...}, ...}
    transcripts/<video>.json   every turn (visible replies, thinking length + tail, observations, image captions)
    agent.csv                  id, parsed_value (agent answers only; NaN where none), video_id, source
    agent_filled.csv           the same with --fallback-csv values where the agent gave none
    config_agent.json, summary_agent.json
Segmented twins (<video>_segmented) take the original clip's answer to the same normalised question when the original
is in the split (--no-twin-reuse to run them in full).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qp.open import agent_loop as AL  # noqa: E402

CLOSED_HINTS = ("claude", "anthropic", "gpt-", "openai/", "gemini", "o1-", "o3-", "o4-")


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", required=True, choices=["val", "val_hires", "test"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=AL.DEFAULT_MODEL)
    ap.add_argument("--fallback-model", default=AL.FALLBACK_MODEL, help="loaded when --model fails ('' = none)")
    ap.add_argument("--backend", choices=["vllm", "hf"], default="vllm")
    ap.add_argument("--gpu-mem", type=float, default=0.88)
    ap.add_argument("--max-model-len", type=int, default=65536)
    ap.add_argument("--prefix-caching", choices=["auto", "on", "off"], default="auto",
                    help="vLLM enable_prefix_caching (auto = the engine default)")
    ap.add_argument("--concurrency", type=int, default=32, help="clip conversations at once")
    ap.add_argument("--tool-workers", type=int, default=0, help="parallel Python / frame tools (0 = CPU count, <= 16)")
    ap.add_argument("--max-steps", type=int, default=30)
    ap.add_argument("--clip-minutes", type=float, default=8.0)
    ap.add_argument("--py-timeout", type=float, default=60.0)
    ap.add_argument("--obs-chars", type=int, default=4096)
    ap.add_argument("--max-images", type=int, default=12)
    ap.add_argument("--mm-max-pixels", type=int, default=0,
                    help="cap the image processor's pixel budget (vLLM mm_processor_kwargs size.longest_edge; 0 = "
                         "model default). Our images are <= --frame-max-side anyway; set e.g. 1638400 if vLLM's memory "
                         "profiling of max-size dummy images fails")
    ap.add_argument("--frame-max-side", type=int, default=1280)
    ap.add_argument("--no-thinking", action="store_true", help="no reasoning before actions (faster, weaker)")
    ap.add_argument("--max-tokens-think", type=int, default=8192)
    ap.add_argument("--max-hours", type=float, default=0.0, help="stop starting clips after this; active clips are "
                                                                  "forced to answer (0 = no limit)")
    ap.add_argument("--fallback-csv", default="", help="id,parsed_value file for qids the agent leaves unanswered "
                                                        "(agent_filled.csv only)")
    ap.add_argument("--ws-root", default="", help="clip workspaces (local disk; default /content or the temp dir)")
    ap.add_argument("--keep-ws", action="store_true")
    ap.add_argument("--no-twin-reuse", action="store_true")
    ap.add_argument("--limit-videos", type=int, default=0)
    ap.add_argument("--videos", default="")
    ap.add_argument("--seed", type=int, default=0)
    return ap.parse_args(argv)


def check_open(model: str) -> None:
    """Track B: only open-weight models may answer. Refuse model ids that name a closed API model."""
    m = str(model).lower()
    if any(h in m for h in CLOSED_HINTS):
        raise SystemExit(f"refusing {model!r}: Track B allows open-weight models only")


def load_backend(args):
    from qp.open.ctx_annot import make_backend
    errors = []
    for m in [args.model] + ([args.fallback_model] if args.fallback_model and args.fallback_model != args.model else []):
        check_open(m)
        try:
            kw = {}
            if args.backend == "vllm":
                kw = {"max_model_len": args.max_model_len, "gpu_memory_utilization": args.gpu_mem,
                      "max_images": args.max_images}
                if args.mm_max_pixels > 0:
                    kw["mm_processor_kwargs"] = {"size": {"longest_edge": args.mm_max_pixels, "shortest_edge": 65536}}
                if args.prefix_caching != "auto":
                    kw["enable_prefix_caching"] = args.prefix_caching == "on"
            be = make_backend(args.backend, m, **kw)
            print(f"loaded {m} ({args.backend})", flush=True)
            return be, m
        except Exception as e:  # noqa: BLE001 - try the fallback, then give up with a clear message
            errors.append(f"{m}: {type(e).__name__}: {str(e)[:400]}")
            print(f"could not load {m}: {errors[-1]}", flush=True)
    raise SystemExit("no model could be loaded: " + " | ".join(errors))


def read_fallback(path: str) -> dict[int, float]:
    if not path or not Path(path).exists():
        return {}
    import pandas as pd
    d = pd.read_csv(path)
    d = d.rename(columns={d.columns[0]: "id"})
    out = {}
    for q, v in zip(d.id, pd.to_numeric(d.parsed_value, errors="coerce")):
        if v == v and math.isfinite(v) and v != 0:
            out[int(q)] = abs(float(v))
    return out


def main(argv=None, backend=None) -> int:
    args = parse_args(argv)
    check_open(args.model)
    from qp.data import load_split
    df = load_split(args.split).drop(columns=["answer"], errors="ignore")   # labels never reach the agent
    if args.videos:
        df = df[df.video_id.isin(args.videos.split(","))]
    vids = list(dict.fromkeys(df.video_id))
    if args.limit_videos:
        vids = vids[:args.limit_videos]
    df = df[df.video_id.isin(vids)].reset_index(drop=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "config_agent.json").write_text(json.dumps(vars(args), indent=2))
    missing = set(df.video_id[df.video_path == ""])
    if missing and len(missing) == len(vids):
        raise SystemExit(f"none of the {len(vids)} videos found locally")
    clips = [c for c in AL.clips_from_df(df) if c.video_id not in missing]
    if not args.no_twin_reuse:
        AL.plan_twins(clips)
    # originals first, so the twins that still have own questions run after the clips they reuse answers from
    clips.sort(key=lambda c: c.video_id.endswith("_segmented"))
    cfg = AL.AgentConfig(max_steps=args.max_steps, max_wall_s=args.clip_minutes * 60, py_timeout=args.py_timeout,
                         obs_chars=args.obs_chars, thinking=not args.no_thinking,
                         max_tokens_think=args.max_tokens_think, max_model_len=args.max_model_len,
                         max_images=args.max_images, keep_images=max(2, min(8, args.max_images - 4)),
                         frame_max_side=args.frame_max_side, seed=args.seed)
    ws_root = Path(args.ws_root) if args.ws_root else AL.default_ws_root(args.split)
    ws_root.mkdir(parents=True, exist_ok=True)
    deny = [str(ROOT), "/content/drive", str(ROOT / "data"), str(ROOT / "outputs"), str(ROOT / "runs")]
    done = AL.load_answers(out)
    todo = [c for c in clips if c.questions and c.video_id not in done]
    print(f"{len(vids)} videos ({len(df)} questions), {len(missing)} missing, {len(clips) - len(todo)} done or "
          f"twin-only; to run: {len(todo)} (twins reusing answers: {sum(1 for c in clips if c.reuse)})", flush=True)
    model = args.model
    stats = {}
    if todo:
        if backend is None:
            backend, model = load_backend(args)
        deadline = time.time() + args.max_hours * 3600 if args.max_hours > 0 else None
        workers = args.tool_workers or min(16, os.cpu_count() or 4)
        stats = AL.run_clips(backend, clips, out, cfg, ws_root, model=model, concurrency=args.concurrency,
                             tool_workers=workers, deadline=deadline, deny=deny)
        print(f"agent run: {json.dumps(stats)}", flush=True)
    n_tw = AL.fill_twins(clips, out, model)
    if n_tw:
        print(f"twins: {n_tw} answers file(s) written from their original clip", flush=True)
    AL.write_csvs(df, out, read_fallback(args.fallback_csv))
    have = AL.load_answers(out)
    summ = {"videos": len(vids), "done": sum(1 for v in vids if v in have),
            "answered": sum(len(r.get("answers", {})) for v, r in have.items() if v in set(vids)),
            "questions": len(df), "forced": sum(1 for r in have.values() if r.get("forced")),
            "ends": {e: sum(1 for r in have.values() if r.get("end") == e)
                     for e in sorted({str(r.get("end")) for r in have.values()})},
            "last_run": stats, "model": model}
    (out / "summary_agent.json").write_text(json.dumps(summ, indent=2))
    print(f"summary: {json.dumps(summ)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
