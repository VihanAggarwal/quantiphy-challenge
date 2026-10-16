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
Segmented twins (<video>_segmented) take the original clip's answer to the same question (normalised question, exact
prior and depth_info, unit) when the original is in the split (--no-twin-reuse to run them in full).

Prefix caching is ON by default (--prefix-caching on: enable_prefix_caching=True with mamba_cache_mode "align"):
Qwen3.6 is a hybrid (Gated DeltaNet + full attention) model, for which vLLM 0.19 leaves prefix caching off by default,
and every agent turn resends the whole conversation. The log says which mode is active.
Exit code 0 when the run ended normally, 3 when the engine died / kept failing (finished clips are saved; clips with
status "failed" in answers/ run again on the next call).
"""

from __future__ import annotations

import argparse
import dataclasses
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
    ap.add_argument("--prefix-caching", choices=["auto", "on", "off"], default="on",
                    help="vLLM prefix caching: on = enable_prefix_caching=True + mamba_cache_mode 'align' (default; "
                         "vLLM 0.19 turns it off for hybrid models such as Qwen3.6), off, auto = the engine default")
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
    ap.add_argument("--max-tokens-think", type=int, default=4096,
                    help="max tokens of a thinking turn (reasoning + action; a cut turn is retried without thinking)")
    ap.add_argument("--elapsed-factor", type=float, default=4.0,
                    help="real elapsed-time cap per clip = factor x clip-minutes x max(1, concurrency / 8); 0 = no "
                         "real-time cap (the clip's own-time cap --clip-minutes always applies)")
    ap.add_argument("--tool-wait-s", type=float, default=15.0,
                    help="before each batched generate(), wait up to this long for running tools")
    ap.add_argument("--sandbox", choices=["auto", "off"], default="auto",
                    help="auto: as root, scripts run as uid 65534 in their own network namespace; off: guard only")
    ap.add_argument("--sandbox-mem-mb", type=int, default=0,
                    help="address-space limit per Python run (0 = min(16384, (MemAvailable - 40000) / tool workers), "
                         ">= 2048)")
    ap.add_argument("--no-lock-deny", action="store_true",
                    help="do not close the deny roots (repo, Drive) to other users while an unprivileged sandbox runs")
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


def _engine_fields() -> set[str] | None:
    """Field names of vllm's EngineArgs (None when vllm is not importable)."""
    try:
        from vllm.engine.arg_utils import EngineArgs
        return {f.name for f in dataclasses.fields(EngineArgs)}
    except Exception:  # noqa: BLE001
        return None


def prefix_caching_kwargs(mode: str, fields: set[str] | None = None) -> tuple[dict, str]:
    """(engine kwargs, description) for --prefix-caching. "on": enable_prefix_caching=True and, when this vLLM has the
    option, mamba_cache_mode "align" (the hybrid GDN layers' state is cached at block boundaries of each step);
    "off": False; "auto": nothing (the engine default, off for hybrid models in vLLM 0.19)."""
    if mode == "off":
        return {"enable_prefix_caching": False}, "OFF (enable_prefix_caching=False)"
    if mode == "auto":
        return {}, "AUTO (the engine default; vLLM 0.19 leaves it off for hybrid models such as Qwen3.6)"
    kw = {"enable_prefix_caching": True}
    if fields is None:
        fields = _engine_fields()
    if fields is not None and "mamba_cache_mode" in fields:
        kw["mamba_cache_mode"] = "align"
        return kw, "ON (enable_prefix_caching=True, mamba_cache_mode='align')"
    return kw, "ON (enable_prefix_caching=True; this vLLM has no mamba_cache_mode option)"


def engine_cache_info(be) -> str:
    """The cache settings the engine actually uses (vLLM may override the requested ones)."""
    try:
        cc = be.llm.llm_engine.vllm_config.cache_config
        return (f"enable_prefix_caching={getattr(cc, 'enable_prefix_caching', '?')}, "
                f"mamba_cache_mode={getattr(cc, 'mamba_cache_mode', '?')}")
    except Exception:  # noqa: BLE001
        return "not readable from this engine"


def load_backend(args):
    from qp.open import ctx_annot
    errors = []
    for m in [args.model] + ([args.fallback_model] if args.fallback_model and args.fallback_model != args.model else []):
        check_open(m)
        kw, pkw = {}, {}
        if args.backend == "vllm":
            kw = {"max_model_len": args.max_model_len, "gpu_memory_utilization": args.gpu_mem,
                  "max_images": args.max_images}
            if args.mm_max_pixels > 0:
                kw["mm_processor_kwargs"] = {"size": {"longest_edge": args.mm_max_pixels, "shortest_edge": 65536}}
            pkw, desc = prefix_caching_kwargs(args.prefix_caching)
            print(f"prefix caching: {desc}", flush=True)
        # an engine that rejects the prefix-caching options is retried once with the engine default (logged)
        attempts = [{**kw, **pkw}] + ([kw] if pkw.get("enable_prefix_caching") else [])
        for k, attempt in enumerate(attempts):
            try:
                be = ctx_annot.make_backend(args.backend, m, **attempt)
                print(f"loaded {m} ({args.backend})", flush=True)
                if args.backend == "vllm":
                    print(f"prefix caching in the engine: {engine_cache_info(be)}", flush=True)
                return be, m
            except Exception as e:  # noqa: BLE001 - try the fallback, then give up with a clear message
                msg = f"{type(e).__name__}: {str(e)[:400]}"
                if k + 1 < len(attempts) and any(w in msg.lower() for w in ("prefix", "mamba")):
                    print(f"prefix caching: WARNING: the engine refused it ({msg}); loading {m} again with the "
                          f"engine default (AUTO)", flush=True)
                    continue
                errors.append(f"{m}: {msg}")
                print(f"could not load {m}: {errors[-1]}", flush=True)
                break
    raise SystemExit("no model could be loaded: " + " | ".join(errors))


def deny_roots() -> list[str]:
    """Folders a sandboxed script must never read (the Python guard refuses them; as root they are also closed to
    other users while the run lasts): the repo (labels in data/, Claude's Track A material in research/ and
    submissions/), Drive, the outputs, and the notebook's scratch clones on /content: data_sync (hard links to the
    validation files, labels included, when SYNC_DATA_TO_GITHUB ran in this runtime) and outputs_push (the pushed
    outputs branch)."""
    return [str(ROOT), "/content/drive", str(ROOT / "data"), str(ROOT / "outputs"), str(ROOT / "runs"),
            "/content/data_sync", "/content/outputs_push"]


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
                         frame_max_side=args.frame_max_side, seed=args.seed, max_elapsed_factor=args.elapsed_factor,
                         tool_wait_s=args.tool_wait_s, sandbox=args.sandbox, mem_mb=max(0, args.sandbox_mem_mb),
                         lock_deny=not args.no_lock_deny)
    ws_root = Path(args.ws_root) if args.ws_root else AL.default_ws_root(args.split)
    ws_root.mkdir(parents=True, exist_ok=True)
    deny = deny_roots()
    done = AL.load_answers(out)
    todo = [c for c in clips if c.questions and c.video_id not in done]
    print(f"{len(vids)} videos ({len(df)} questions), {len(missing)} missing, {len(clips) - len(todo)} done or "
          f"twin-only; to run: {len(todo)} (twins reusing answers: {sum(1 for c in clips if c.reuse)})", flush=True)
    model = args.model
    stats, aborted = {}, ""
    if todo:
        if backend is None:
            backend, model = load_backend(args)
        deadline = time.time() + args.max_hours * 3600 if args.max_hours > 0 else None
        workers = args.tool_workers or min(16, os.cpu_count() or 4)
        try:
            stats = AL.run_clips(backend, clips, out, cfg, ws_root, model=model, concurrency=args.concurrency,
                                 tool_workers=workers, deadline=deadline, deny=deny)
        except AL.BackendDead as e:      # finished clips are saved; write the CSVs / summary, then exit non-zero
            aborted = str(e)
            stats = dict(getattr(e, "stats", None) or {}, aborted=aborted)
            print(f"agent run STOPPED: the model backend is dead or keeps failing ({aborted})", flush=True)
        print(f"agent run: {json.dumps(stats)}", flush=True)
    n_tw = AL.fill_twins(clips, out, model)
    if n_tw:
        print(f"twins: {n_tw} answers file(s) written from their original clip", flush=True)
    AL.write_csvs(df, out, read_fallback(args.fallback_csv))
    have = AL.load_answers(out)
    failed = AL.load_answers(out, statuses=("failed",))
    summ = {"videos": len(vids), "done": sum(1 for v in vids if v in have),
            "failed": sorted(v for v in vids if v in failed and v not in have),
            "answered": sum(len(r.get("answers", {})) for v, r in have.items() if v in set(vids)),
            "questions": len(df), "forced": sum(1 for r in have.values() if r.get("forced")),
            "ends": {e: sum(1 for r in have.values() if r.get("end") == e)
                     for e in sorted({str(r.get("end")) for r in have.values()})},
            "last_run": stats, "model": model, "aborted": aborted or None}
    (out / "summary_agent.json").write_text(json.dumps(summ, indent=2))
    print(f"summary: {json.dumps(summ)}", flush=True)
    return 3 if aborted else 0


if __name__ == "__main__":
    sys.exit(main())
