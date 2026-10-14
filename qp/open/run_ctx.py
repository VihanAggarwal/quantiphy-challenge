"""GPU runner of RUN_PRESET "ctx" (qp.open.ctx_annot): Track-A-style open annotation (ta) and context extents (cx).

    python -m qp.open.run_ctx --split val_hires --out outputs/trackb_ctx/val --task ta,cx
    python -m qp.open.run_ctx --split test      --out outputs/trackb_ctx/test --task ta,cx --model Qwen/Qwen3.6-27B-FP8

One model load serves both tasks. Every video's records are written atomically after its chunk, finished videos
are skipped, and failed generations (backend reply None) are never cached, so Run all resumes after a disconnect.
ta: a reply without usable JSON (thinking cut at max_tokens, no closing tag, unparsable) is asked again once
without thinking and with JSON-schema decoding; the better of the two (more questions answered) is kept.
Outputs under --out: ta/specs, ta/annotate, ta/direct (+ ta/direct.csv), cx/<video>.json, config_ctx.json.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qp.open import ctx_annot as C  # noqa: E402
from qp.open.ctx_merge import _rov  # noqa: E402
from qp.spec import QuestionSpec  # noqa: E402


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", required=True, choices=["val", "val_hires", "test"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--task", default="ta,cx", help="comma list of ta, cx")
    ap.add_argument("--model", default=C.DEFAULT_MODEL)
    ap.add_argument("--fallback-model", default=C.FALLBACK_MODEL, help="loaded when --model fails to load ('' = none)")
    ap.add_argument("--backend", choices=["vllm", "hf"], default="vllm")
    ap.add_argument("--gpu-mem", type=float, default=0.88)
    ap.add_argument("--max-model-len", type=int, default=65536)
    ap.add_argument("--no-thinking", action="store_true", help="ta without thinking (faster, weaker)")
    ap.add_argument("--no-guided-retry", action="store_true")
    ap.add_argument("--no-zoom", action="store_true", help="cx: skip the zoomed second pass")
    ap.add_argument("--cx-frames", type=int, default=C.CX_FRAMES)
    ap.add_argument("--ta-chunk", type=int, default=48, help="ta: videos per generate() call (vLLM batches them)")
    ap.add_argument("--cx-chunk", type=int, default=8, help="cx: videos per generate() call")
    ap.add_argument("--limit-videos", type=int, default=0)
    ap.add_argument("--videos", default="")
    ap.add_argument("--workers", type=int, default=8, help="threads decoding frames while requests are built")
    return ap.parse_args(argv)


def _load(args, rov):
    errors = []
    for m in [args.model] + ([args.fallback_model] if args.fallback_model and args.fallback_model != args.model else []):
        try:
            kw = {"max_model_len": args.max_model_len, "gpu_memory_utilization": args.gpu_mem} if args.backend == "vllm" else {}
            be = C.make_backend(args.backend, m, **kw)
            print(f"loaded {m} ({args.backend})", flush=True)
            return be, m
        except Exception as e:  # noqa: BLE001 - try the fallback, then give up with a clear message
            errors.append(f"{m}: {type(e).__name__}: {str(e)[:400]}")
            print(f"could not load {m}: {errors[-1]}", flush=True)
    raise SystemExit("no model could be loaded: " + " | ".join(errors))


def _complete(rec: dict | None, key: str, qids) -> bool:
    return bool(rec) and all(str(int(q)) in (rec.get(key) or {}) for q in qids)


def run_ta(gen, model: str, groups: dict, todo: list[str], out: Path, rov, args) -> None:
    d = out / "ta"
    step = max(1, args.ta_chunk)
    for i in range(0, len(todo), step):
        chunk, t0 = todo[i:i + step], time.time()
        built = {}

        def build(v):
            try:
                return v, C.ta_request(groups[v], thinking=not args.no_thinking)
            except Exception as e:  # noqa: BLE001 - unreadable video: skipped, retried next run
                print(f"  {v}: request not built ({type(e).__name__}: {e})")
                return v, None
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:   # frame decoding releases the GIL
            for v, b in ex.map(build, chunk):
                if b is not None:
                    built[v] = b
        vids = list(built)
        replies = dict(zip(vids, gen([built[v][0] for v in vids]))) if vids else {}
        parsed = {}
        retry = []
        for v in vids:
            if replies[v] is None:
                continue
            parsed[v] = C.parse_ta(replies[v], built[v][1], groups[v])
            n_ok = parsed[v][1]["n_answered"]
            if n_ok == 0 or (n_ok < len(groups[v]) and not args.no_thinking):
                retry.append(v)
        if retry and not args.no_guided_retry:
            rb = {v: C.ta_request(groups[v], thinking=False, guided=True) for v in retry}
            texts = gen([rb[v][0] for v in retry])
            if all(t is None for t in texts):   # e.g. the JSON schema was refused by the backend: plain decoding
                for v in retry:
                    rb[v][0].json_schema = None
                texts = gen([rb[v][0] for v in retry])
            for v, text in zip(retry, texts):
                if text is None:
                    continue
                p2 = C.parse_ta(text, rb[v][1], groups[v])
                if v not in parsed or p2[1]["n_answered"] > parsed[v][1]["n_answered"]:
                    p2[1]["retry"] = "no_thinking_guided"
                    parsed[v], replies[v] = p2, text
        for v, (res, info) in parsed.items():
            recs = C.ta_records(v, res, built[v][1], model, replies[v], info)
            for sub in ("specs", "annotate", "direct"):
                rov.save_json(d / sub / f"{rov.safe_id(v)}.json", recs[sub])
        ans = sum(p[1]["n_answered"] for p in parsed.values())
        nq = sum(len(groups[v]) for v in parsed)
        print(f"  ta {min(i + len(chunk), len(todo))}/{len(todo)} videos: {len(parsed)} written, {ans}/{nq} questions "
              f"answered, {len(retry)} retried, {time.time() - t0:.0f}s", flush=True)


def run_cx(gen, groups: dict, todo: list[str], out: Path, rov, args) -> None:
    specs = rov.specs_from(out / "ta" / "specs") if (out / "ta" / "specs").exists() else {}
    ta = rov.load_dir(out / "ta" / "annotate")
    step = max(1, args.cx_chunk)
    for i in range(0, len(todo), step):
        chunk, t0 = todo[i:i + step], time.time()
        plans = {}

        def plan(v):
            try:
                return v, C.CXPlan(groups[v], specs, ta.get(v), frames_k=args.cx_frames, zoom=not args.no_zoom)
            except Exception as e:  # noqa: BLE001
                print(f"  {v}: cx plan failed ({type(e).__name__}: {e})")
                return v, None
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
            for v, pl in ex.map(plan, chunk):
                if pl is not None:
                    plans[v] = pl
        r1 = {v: p.requests1() for v, p in plans.items()}
        flat = [r for v in plans for r in r1[v]]
        rep = gen(flat) if flat else []
        z, k = {}, 0
        for v, p in plans.items():
            z[v] = p.apply1(rep[k:k + len(r1[v])])
            k += len(r1[v])
        flat = [r for v in plans for r in z[v]]
        rep = gen(flat) if flat else []
        k = 0
        n_items = 0
        for v, p in plans.items():
            p.apply2(rep[k:k + len(z[v])])
            k += len(z[v])
            rec = p.record()
            if rec.get("error"):
                print(f"  {v}: cx not cached ({rec['error']}); retried next run")
                continue
            n_items += len(rec["items"])
            rov.save_json(out / "cx" / f"{rov.safe_id(v)}.json", rec)
        print(f"  cx {min(i + len(chunk), len(todo))}/{len(todo)} videos: {n_items} items, {time.time() - t0:.0f}s",
              flush=True)


def main(argv=None, backend=None) -> int:
    args = parse_args(argv)
    rov = _rov()
    from qp.data import load_split
    df = load_split(args.split).drop(columns=["answer"], errors="ignore")
    if args.videos:
        df = df[df.video_id.isin(args.videos.split(","))]
    vids = list(dict.fromkeys(df.video_id))
    if args.limit_videos:
        vids = vids[:args.limit_videos]
    df = df[df.video_id.isin(vids)].reset_index(drop=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "config_ctx.json").write_text(json.dumps(vars(args), indent=2))
    missing = set(df.video_id[df.video_path == ""])
    if missing and len(missing) == len(vids):
        raise SystemExit(f"none of the {len(vids)} videos found locally")
    groups = {v: g.reset_index(drop=True) for v, g in df.groupby("video_id", sort=False)}
    tasks = [t for t in args.task.split(",") if t]
    todo = {}
    if "ta" in tasks:
        have = rov.load_dir(out / "ta" / "annotate")
        todo["ta"] = [v for v in vids if v not in missing and not _complete(have.get(v), "tracks", groups[v].qid)]
    if "cx" in tasks:
        have = rov.load_dir(out / "cx")
        todo["cx"] = [v for v in vids if v not in missing and v not in have]
    print(f"{len(vids)} videos ({len(df)} questions), {len(missing)} missing; to run: "
          + ", ".join(f"{t} {len(v)}" for t, v in todo.items()), flush=True)
    model = args.model
    if any(todo.values()):
        if backend is None:
            backend, model = _load(args, rov)

        def gen(reqs):
            try:
                return list(backend.generate(reqs))
            except Exception as e:  # noqa: BLE001 - a failed batch is retried one by one, then left pending
                print(f"  generate failed for {len(reqs)} requests ({type(e).__name__}: {str(e)[:300]}); one by one")
                outs = []
                for r in reqs:
                    try:
                        outs.append(backend.generate([r])[0])
                    except Exception:  # noqa: BLE001
                        outs.append(None)
                return outs
        if todo.get("ta"):
            run_ta(gen, model, groups, todo["ta"], out, rov, args)
        if todo.get("cx"):
            run_cx(gen, groups, todo["cx"], out, rov, args)
    if "ta" in tasks and (out / "ta" / "direct").exists():
        rov.write_direct_csv(df, out / "ta" / "direct", out / "ta" / "direct.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
