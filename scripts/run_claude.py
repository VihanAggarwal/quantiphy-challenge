"""Track A: one Claude request per video -> question specs, pixel tracks and direct answers.

    python scripts/run_claude.py --split val --name opus_ann --effort medium
    python scripts/run_claude.py --split test --name opus_ann --mode batch      # 50% off; rerun resumes
    python scripts/run_claude.py --split val --name opus_ann --dry-run          # estimate only
    python scripts/run_claude.py --csv "external/QuantiPhy/model_run_example/GT_CIB_Ready/CIB_Ready - test4.csv" \\
        --video-dir external/QuantiPhy/model_run_example/data/all_480p --name smoke --effort low --max-frames 16

Writes under <runs>/<name>/<split>/ (<runs> = --out-root, env QP_RUNS, else runs/): records/<video_id>.json
(raw text, parsed JSON, usage, cost, settings, frame metadata) and batch.json (batch mode), then
<runs>/<name>/<split>.csv with columns id, parsed_value (geometry value if valid and plausible, else
Claude's direct answer), geo_value, direct_value, method, flags. Cached videos are skipped; failed or partial ones
(refusal, max_tokens, missing qids, errored, expired ...) are retried only with --retry-failed. Cached
records made with other settings (model, effort, frames) make the run refuse: use a new --name.

Budget: every response's usage is appended to budget/ledger.jsonl (env QP_LEDGER). The run refuses to
start when its expected cost would push spend past the cap (QP_BUDGET_USD), and every request is held
against the cap at its worst case (1.25 x estimated input + max_tokens output) until its usage is
recorded, so spend stays under the cap: batch mode submits only as many videos as fit, then waits,
collects and submits more. Each batch's hold in the ledger names its run, split and custom ids, so a batch whose
batch.json was lost (container / Colab reset) is found and collected instead of being bought again, and
videos the ledger shows as paid but whose records are gone are not re-sent without --rebuy-lost.
On Colab keep ONE ledger and persistent records: run inside a clone of this repo on Google Drive (or set
QP_RUNS / QP_LEDGER to Drive paths and copy the ledger back into budget/ and commit it afterwards).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qp import budget  # noqa: E402
from qp import claude_annotate as ca  # noqa: E402
from qp.data import ROOT, _finalize, load_split  # noqa: E402
from qp.mra import score  # noqa: E402
from qp.spec import KIND_DIM  # noqa: E402

OK, PARTIAL = "ok", "partial"
USABLE = (OK, PARTIAL)                 # records whose annotations are used
CONFIG_KEYS = ("model", "effort", "frames", "max_frames")  # settings a cached record must match
EST_OUTPUT_PER_QUESTION = {"low": 1500, "medium": 2500, "high": 4000, "xhigh": 6000, "max": 8000}
INPUT_MARGIN = 1.25                    # worst case: input estimate error + system-prompt cache writes
GEO_MAX_SI = {"L": 1e4, "V": 1e3, "A": 1e3}   # m, m/s, m/s^2: a geometry answer beyond this is a blow-up
MAX_DISAGREE = 10.0                    # geometry this many times off the direct answer: use the direct one
                                       # (same policy as run_open_vlm.py's geometry step)


def load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                if v.strip():
                    os.environ.setdefault(k.strip(), v.strip())


def safe_id(video_id: str) -> str:
    """Batch custom_id / file name: [A-Za-z0-9_-]{1,64}."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(video_id).strip())[:64] or "video"


def load_questions(args) -> tuple[pd.DataFrame, str]:
    """(questions, split label). --csv takes a validation-format CSV (first unnamed column = qid,
    otherwise the row number is used) with videos under --video-dir."""
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


def run_config(cfg) -> dict:
    return {k: getattr(cfg, k, None) for k in CONFIG_KEYS}


def max_tokens_for(rows: pd.DataFrame, cfg) -> int:
    return cfg.max_tokens or ca.default_max_tokens(len(rows))


# --------------------------------------------------------------------------- records

def record_path(rec_dir: Path, video_id: str) -> Path:
    return rec_dir / f"{safe_id(video_id)}.json"


def load_records(rec_dir: Path) -> dict[str, dict]:
    out = {}
    for p in sorted(rec_dir.glob("*.json")):
        rec = json.loads(p.read_text())
        out[rec["video_id"]] = rec
    return out


def save_record(rec_dir: Path, rec: dict) -> None:
    rec_dir.mkdir(parents=True, exist_ok=True)
    path = record_path(rec_dir, rec["video_id"])
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1))
    os.replace(tmp, path)


def _dump(x):
    return x.to_dict() if hasattr(x, "to_dict") else x


def message_record(msg, video_id: str, meta: dict, config: dict, usd: float, **ids) -> dict:
    """Record for one Message (sync or batch).
    status: ok | partial (some qids missing) | refusal | max_tokens | parse_error."""
    text = ca.response_text(msg)
    parsed = ca.parse_json(text) if msg.stop_reason != "refusal" else None
    missing: list[int] = []
    if msg.stop_reason == "refusal":
        status = "refusal"
    elif msg.stop_reason == "max_tokens":
        status = "max_tokens"
    elif parsed is None or not isinstance(parsed.get("questions"), list):
        status = "parse_error"
    else:
        got = {q.get("qid") for q in parsed["questions"] if isinstance(q, dict)}
        missing = [q["qid"] for q in meta["questions"] if q["qid"] not in got]
        status = PARTIAL if missing else OK
    return {"video_id": video_id, "status": status, "stop_reason": msg.stop_reason,
            "stop_details": _dump(getattr(msg, "stop_details", None)), "message_id": msg.id,
            "model": config["model"], "effort": config["effort"], "config": config,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **ids,
            "usage": budget.usage_dict(msg.usage), "usd": round(usd, 6), "missing_qids": missing,
            "meta": meta, "raw_text": text, "parsed": parsed}


def todo_videos(groups: dict[str, pd.DataFrame], records: dict[str, dict], retry_failed: bool,
                skip=()) -> list[str]:
    return [v for v in groups if v not in skip
            and (v not in records or (retry_failed and records[v].get("status") != OK))]


def config_diff(rec: dict, cfg) -> dict:
    """{setting: (record's, this run's)} for settings a cached record differs in (unknown ones skipped)."""
    have = {"model": rec.get("model"), "effort": rec.get("effort"), **(rec.get("config") or {})}
    cur = run_config(cfg)
    return {k: (have[k], cur[k]) for k in CONFIG_KEYS if have.get(k) is not None and have[k] != cur[k]}


def lost_videos(cfg, vids: list[str], records: dict[str, dict]) -> list[str]:
    """Videos the ledger shows this run already paid for but whose record is gone (runs/ lost)."""
    paid = {e.get("video_id") for e in budget.entries() if e.get("type", "usage") == "usage"
            and e.get("run") == cfg.name and e.get("split") == cfg.label}
    return [v for v in vids if v not in records and v in paid]


# --------------------------------------------------------------------------- estimate

def _image_tokens(w: int, h: int) -> int:
    return math.ceil(w * h / 750)


def _request_shape(rows: pd.DataFrame, cfg) -> tuple[int, int, int]:
    """(n_frames, w, h) a video's request will have, without decoding frames."""
    first = rows.iloc[0]
    n_total, w, h = ca.video_info(str(first.video_path))
    fps, _ = ca.video_fps(first.fps, str(first.video_path))
    texts = [t for r in rows.itertuples() for t in (r.question, r.prior, r.depth_info)]
    idxs = ca.select_frames(n_total, fps, ca.mentioned_times(texts), cfg.frames, cfg.max_frames)
    return len(idxs), w, h


def output_per_question(cfg, records: dict[str, dict]) -> tuple[int, str]:
    """Expected output tokens per question: --est-output-per-question (0 = a default per effort),
    raised to what this run's records with the same model/effort used (>= 3 videos)."""
    base = cfg.est_output_per_question or EST_OUTPUT_PER_QUESTION[cfg.effort]
    how = "flag" if cfg.est_output_per_question else f"default for effort {cfg.effort}"
    seen = [r for r in records.values() if r.get("usage") and r.get("meta")
            and r.get("model") == cfg.model and r.get("effort") == cfg.effort]
    if len(seen) >= 3:
        obs = sum(r["usage"]["output_tokens"] for r in seen) / max(1, sum(len(r["meta"]["questions"]) for r in seen))
        if obs > base:
            return math.ceil(obs), f"observed on {len(seen)} videos"
    return base, how


def estimate(client, groups: dict[str, pd.DataFrame], todo: list[str], cfg, records=None) -> dict | None:
    """Input tokens: count_tokens (or an offline estimate) on the first video's request, transferred
    to the other videos by their frame count and size. Output: output_per_question. Also each
    video's worst case (INPUT_MARGIN x input + max_tokens output). Videos whose request cannot be
    built (unreadable file, no fps ...) are reported and left out ("todo" lists the rest); None if
    no video is left."""
    shapes, skipped = {}, {}
    for v in todo:
        try:
            shapes[v] = _request_shape(groups[v], cfg)
        except Exception as e:  # noqa: BLE001 - one bad video must not stop the run
            skipped[v] = f"{type(e).__name__}: {e}"
    params = meta = None
    for v in list(shapes):
        try:
            params, meta = ca.build_request(groups[v], cfg.frames, cfg.max_frames, cfg.effort,
                                            cfg.max_tokens, cfg.model)
            break
        except Exception as e:  # noqa: BLE001
            skipped[v] = f"{type(e).__name__}: {e}"
            del shapes[v]
    for v, why in skipped.items():
        print(f"  skipping {v}: {why}")
    if params is None:
        return None
    vids = list(shapes)
    if cfg.local_estimate:
        first_in, how = ca.estimate_input_tokens(params), "offline estimate"
    else:
        counted = client.messages.count_tokens(**{k: v for k, v in params.items() if k != "max_tokens"})
        first_in, how = int(counted.input_tokens), "count_tokens"
    w, h = meta["image_size"]
    overhead = first_in - len(meta["frames"]) * _image_tokens(w, h)
    per_q, out_how = output_per_question(cfg, records or {})
    batch = cfg.mode == "batch"
    per_video, worst = {}, {}
    for v in vids:
        n, w, h = shapes[v]
        per_video[v] = max(first_in if v == vids[0] else 0, overhead + n * _image_tokens(w, h))
        worst[v] = budget.estimate_usd(INPUT_MARGIN * per_video[v], max_tokens_for(groups[v], cfg),
                                       cfg.model, batch)
    n_q = sum(len(groups[v]) for v in vids)
    total_in, total_out = sum(per_video.values()), per_q * n_q
    return {"usd": budget.estimate_usd(total_in, total_out, cfg.model, batch), "worst_usd": sum(worst.values()),
            "todo": vids, "videos": len(vids), "questions": n_q, "first_input_tokens": first_in, "how": how,
            "input_tokens": total_in, "output_tokens": total_out, "out_per_question": per_q,
            "out_how": out_how, "per_video_in": per_video, "worst": worst}


def guard(est: dict | None, cfg) -> bool:
    """Print the estimate and refuse when it exceeds the cap (or --max-usd). True = go."""
    if est is None:
        print("nothing to send: no video request could be built")
        return False
    print(f"estimate: {est['videos']} videos, {est['questions']} questions; first request "
          f"{est['first_input_tokens']} input tokens ({est['how']}); total ~{est['input_tokens']} in + "
          f"{est['output_tokens']} out ({est['out_per_question']}/question, {est['out_how']}) -> "
          f"${est['usd']:.2f}{' (batch 50% off)' if cfg.mode == 'batch' else ''}; "
          f"worst case (max_tokens) ${est['worst_usd']:.2f}")
    print(f"budget: committed ${budget.committed():.2f} of cap ${budget.cap():.2f}; requests are held at "
          "their worst case until their usage is recorded")
    if cfg.max_usd and est["usd"] > cfg.max_usd:
        print(f"refusing: estimate exceeds --max-usd {cfg.max_usd:.2f}")
        return False
    try:
        budget.check(est["usd"])
    except budget.BudgetExceeded as e:
        print(f"refusing: {e}")
        return False
    return not cfg.dry_run


# --------------------------------------------------------------------------- sync

def call(client, params: dict, retries: int = 2):
    """One streamed request (no 10-minute non-streaming limit); returns (Message, request_id)."""
    for attempt in range(retries + 1):
        try:
            with client.messages.stream(**params) as stream:
                return stream.get_final_message(), stream.request_id
        except Exception as e:  # noqa: BLE001 - only transient API errors are retried
            status = getattr(e, "status_code", None)
            transient = type(e).__name__ in ("APIConnectionError", "APITimeoutError") or (status or 0) >= 500
            if not transient or attempt == retries:
                raise
            print(f"  {type(e).__name__}: retrying in {10 * 2 ** attempt}s")
            time.sleep(10 * 2 ** attempt)
    raise AssertionError("unreachable")


def run_sync(client, groups, todo, cfg, rec_dir: Path, est: dict) -> None:
    config = run_config(cfg)

    def work(vid: str) -> dict:
        rows = groups[vid]
        params, meta = ca.build_request(rows, cfg.frames, cfg.max_frames, cfg.effort, cfg.max_tokens, cfg.model)
        with budget.reserve(est["worst"][vid]):  # worst case, so concurrent requests cannot pass the cap
            msg, request_id = call(client, params)
            usd = budget.price(msg.usage, cfg.model)
            budget.record(cfg.name, cfg.model, "sync", request_id or msg.id, msg.usage, usd,
                          video_id=vid, split=cfg.label)
        rec = message_record(msg, vid, meta, config, usd, mode="sync", request_id=request_id)
        save_record(rec_dir, rec)
        return rec

    with ThreadPoolExecutor(max(1, cfg.workers)) as pool:
        futures = {pool.submit(work, v): v for v in todo}
        for i, fut in enumerate(as_completed(futures), 1):
            vid = futures[fut]
            try:
                rec = fut.result()
                print(f"  [{i}/{len(todo)}] {vid}: {rec['status']} ${rec['usd']:.3f} "
                      f"(in {rec['usage']['input_tokens']} out {rec['usage']['output_tokens']})")
            except budget.BudgetExceeded as e:
                print(f"  [{i}/{len(todo)}] {vid}: skipped, {e}")
            except Exception as e:  # noqa: BLE001 - keep going; the video stays pending
                print(f"  [{i}/{len(todo)}] {vid}: failed: {type(e).__name__}: {e}")


# --------------------------------------------------------------------------- batch

def load_state(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {"batches": []}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1))
    os.replace(tmp, path)


def pending_videos(state: dict) -> set[str]:
    """Videos in submitted batches that are not collected yet."""
    return {v for e in state["batches"] if not e.get("collected") for v in e.get("custom_ids", {}).values()}


def recover_batches(state: dict, cfg, records: dict[str, dict], split_groups: dict) -> int:
    """Add this run's batches that the ledger knows but batch.json lacks (it was lost): every open
    hold, and released ones holding results for videos whose record is missing. Returns how many."""
    known, open_ids, n = {e["id"] for e in state["batches"]}, set(budget.open_holds()), 0
    for h in budget.entries():
        if h.get("type") != "hold" or h.get("run") != cfg.name or h.get("split") != cfg.label or h["id"] in known:
            continue
        cids = h.get("custom_ids") or {}
        if h["id"] not in open_ids and not any(v in split_groups and v not in records for v in cids.values()):
            continue
        if not cids:
            print(f"warning: open batch {h['id']} has no custom ids in the ledger; collect it by hand")
            continue
        conf = h.get("config") or {}
        state["batches"].append({"id": h["id"], "created_at": h.get("ts"), "collected": False, "recovered": True,
                                 "model": conf.get("model", cfg.model), "effort": conf.get("effort", cfg.effort),
                                 "config": conf, "custom_ids": cids, "meta": {}})
        known.add(h["id"])
        n += 1
    return n


def _entry_meta(entry: dict, vid: str, cfg, split_groups: dict | None) -> dict | None:
    """Request metadata of `vid` in a batch: stored, or rebuilt (deterministic) for recovered batches."""
    if vid in entry.get("meta", {}):
        return entry["meta"][vid]
    if not split_groups or vid not in split_groups:
        return None
    conf = {**run_config(cfg), **(entry.get("config") or {})}
    return ca.build_request(split_groups[vid], conf["frames"], conf["max_frames"], conf["effort"],
                            0, conf["model"])[1]


def collect(client, entry: dict, cfg, rec_dir: Path, split_groups: dict | None = None) -> Counter:
    """Write a record per result of an ended batch. Idempotent: usage already in the ledger is not
    recorded again, results already stored are skipped, and an ok record from elsewhere is kept."""
    records, counts = load_records(rec_dir), Counter()
    config = {**run_config(cfg), "model": entry.get("model", cfg.model), "effort": entry.get("effort", cfg.effort),
              **(entry.get("config") or {})}
    model = config["model"]
    paid = {e["id"] for e in budget.entries() if e.get("type", "usage") == "usage"}
    for res in client.messages.batches.results(entry["id"]):
        vid, r = entry["custom_ids"].get(res.custom_id), res.result
        ledger_id = f"{entry['id']}/{res.custom_id}"
        if r.type == "succeeded" and ledger_id not in paid:
            budget.record(cfg.name, model, "batch", ledger_id, r.message.usage,
                          budget.price(r.message.usage, model, batch=True), video_id=vid, split=cfg.label)
        old = records.get(vid)
        if vid is None:
            counts["unknown_custom_id"] += 1
            continue
        if old and old.get("batch_id") == entry["id"]:
            counts["already_collected"] += 1
            continue
        if old and old.get("status") == OK:  # e.g. answered by a sync run meanwhile
            counts["kept_existing"] += 1
            continue
        meta = _entry_meta(entry, vid, cfg, split_groups)
        if meta is None:
            counts["no_meta"] += 1
            continue
        ids = {"mode": "batch", "batch_id": entry["id"], "custom_id": res.custom_id}
        if r.type == "succeeded":
            rec = message_record(r.message, vid, meta, config, budget.price(r.message.usage, model, batch=True),
                                 **ids)
        else:
            rec = {"video_id": vid, "status": r.type, "error": _dump(getattr(r, "error", None)), **ids,
                   "model": model, "effort": config["effort"], "config": config, "usd": 0.0, "meta": meta,
                   "parsed": None}
        save_record(rec_dir, rec)
        counts[rec["status"]] += 1
    return counts


def wait_and_collect(client, entry: dict, cfg, rec_dir: Path, state_path: Path, state: dict,
                     split_groups: dict | None = None) -> bool:
    """Poll until the batch ends, then collect it. False if --no-wait and it is still running."""
    while True:
        b = client.messages.batches.retrieve(entry["id"])
        rc = b.request_counts
        print(f"  batch {entry['id']}: {b.processing_status} (processing {rc.processing}, "
              f"succeeded {rc.succeeded}, errored {rc.errored}, expired {rc.expired}, canceled {rc.canceled})")
        if b.processing_status == "ended":
            break
        if cfg.no_wait:
            return False
        time.sleep(cfg.poll_interval)
    counts = collect(client, entry, cfg, rec_dir, split_groups)
    entry["collected"] = True
    save_state(state_path, state)
    if entry["id"] in budget.open_holds():
        budget.release(entry["id"])
    print(f"  collected {entry['id']}: {dict(counts)}")
    return True


def submit(client, groups, vids: list[str], cfg, state_path: Path, state: dict, est: dict) -> list[str]:
    """Create batches for as many of `vids` as fit under the cap at their worst case (each batch's
    ledger hold), split at --chunk-videos videos / --batch-mb of request body. Returns the videos sent."""
    chunk, size, sent, used = [], 0, [], set()
    config = run_config(cfg)

    def flush():
        nonlocal chunk, size
        if not chunk:
            return
        worst, usd = sum(c[3] for c in chunk), sum(c[4] for c in chunk)
        budget.check(worst)
        batch = client.messages.batches.create(requests=[{"custom_id": c[0], "params": c[1]} for c in chunk])
        cids = {c[0]: c[2]["video_id"] for c in chunk}
        budget.hold(cfg.name, batch.id, worst, split=cfg.label, custom_ids=cids, config=config,
                    est_usd=round(usd, 4))
        state["batches"].append({"id": batch.id, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                 "collected": False, "model": cfg.model, "effort": cfg.effort, "config": config,
                                 "est_usd": round(usd, 4), "hold_usd": round(worst, 4), "custom_ids": cids,
                                 "meta": {c[2]["video_id"]: c[2] for c in chunk}})
        save_state(state_path, state)
        sent.extend(cids.values())
        print(f"  submitted batch {batch.id}: {len(chunk)} videos, est ${usd:.2f}, held ${worst:.2f} (worst case)")
        chunk, size = [], 0

    for vid in vids:
        worst = est["worst"][vid]
        room = budget.cap() - budget.committed() - sum(c[3] for c in chunk)
        if worst > room:
            flush()
            print(f"  budget: {len(vids) - len(sent)} video(s) wait: worst case ${worst:.2f} > headroom "
                  f"${max(room, 0):.2f}; they are submitted once earlier batches are collected")
            break
        rows = groups[vid]
        try:
            params, meta = ca.build_request(rows, cfg.frames, cfg.max_frames, cfg.effort, cfg.max_tokens, cfg.model)
        except Exception as e:  # noqa: BLE001 - skip the video, keep the others
            print(f"  skipping {vid}: {type(e).__name__}: {e}")
            continue
        cid = safe_id(vid)
        while cid in used:
            cid = f"{cid[:60]}_{len(used) % 1000}"
        used.add(cid)
        n = len(json.dumps(params))
        if chunk and (size + n > cfg.batch_mb * 1e6 or len(chunk) >= cfg.chunk_videos):
            flush()
        chunk.append((cid, params, meta, worst, budget.estimate_usd(
            est["per_video_in"][vid], est["out_per_question"] * len(rows), cfg.model, batch=True)))
        size += n
    flush()
    return sent


def run_batch(client, groups, split_groups, cfg, out_dir: Path, rec_dir: Path, state: dict, skip=()) -> None:
    """Collect pending batches, submit what fits, wait, repeat until every video is done or the
    budget / --no-wait stops it (a rerun resumes from batch.json and the ledger)."""
    state_path = out_dir / "batch.json"
    attempted = set(skip)
    while True:
        pending = [e for e in state["batches"] if not e.get("collected")]
        if pending:
            print(f"{len(pending)} uncollected batch(es)")
        for e in pending:
            if not wait_and_collect(client, e, cfg, rec_dir, state_path, state, split_groups):
                print("still running; rerun later to collect")
                return
        records = load_records(rec_dir)
        todo = todo_videos(groups, records, cfg.retry_failed, skip=attempted)
        if not todo:
            return
        est = estimate(client, groups, todo, cfg, records)
        if not guard(est, cfg):
            return
        try:
            sent = submit(client, groups, est["todo"], cfg, state_path, state, est)
        except budget.BudgetExceeded as e:
            print(f"stopped submitting: {e}")
            sent = []
        if not sent and not any(not e.get("collected") for e in state["batches"]):
            return
        attempted.update(sent)


# --------------------------------------------------------------------------- results

def _valid(v) -> bool:
    return v is not None and isinstance(v, (int, float)) and math.isfinite(v) and v > 0


def build_results(df: pd.DataFrame, records: dict[str, dict]) -> pd.DataFrame:
    """One row per question: geometry value when the solver returns a valid one, else direct. A geometry
    value beyond GEO_MAX_SI or more than MAX_DISAGREE times off the direct answer is replaced by the
    direct one (flags geo_rejected_implausible / geo_rejected_disagree; geo_value keeps it)."""
    try:
        from qp.geometry import solve
    except ImportError:
        solve = None
    anns = ca.load_annotations(records)
    out = []
    for r in df.itertuples():
        a, rec = anns.get(int(r.qid)), records.get(r.video_id, {})
        if a is None:
            status = rec.get("status", "not_run")
            out.append({"id": int(r.qid), "parsed_value": math.nan, "geo_value": math.nan,
                        "direct_value": math.nan, "method": "missing",
                        "flags": status if status not in USABLE else "qid_not_in_response"})
            continue
        flags, geo, method, geo_si = list(a.flags), None, "", None
        if solve is None:
            flags.append("no_geometry_module")
        else:
            try:
                ans = solve(a.spec, a.tracks, tuple(rec["meta"]["image_size"]), float(rec["meta"]["fps"]))
                geo, method, geo_si = ans.value, ans.method, ans.debug.get("value_si")
                flags += [f"geo:{f}" for f in ans.flags]
            except Exception as e:  # noqa: BLE001 - one bad question must not stop the run
                flags.append(f"geo_error:{type(e).__name__}")
        direct = a.direct_answer
        use_geo = _valid(geo)
        if use_geo and _valid(geo_si) and geo_si > GEO_MAX_SI.get(KIND_DIM.get(a.spec.target.kind, "L"), math.inf):
            flags.append("geo_rejected_implausible")
            use_geo = False
        ratio = max(geo / direct, direct / geo) if use_geo and _valid(direct) else 1.0
        if ratio > 3:
            flags.append("geo_direct_disagree")
        if ratio > MAX_DISAGREE:
            flags.append("geo_rejected_disagree")
            use_geo = False
        if use_geo:
            value, how = geo, f"geometry:{method}" if method else "geometry"
        elif _valid(direct):
            value, how = direct, "direct"
        else:
            value, how = math.nan, "none"
        out.append({"id": int(r.qid), "parsed_value": value, "geo_value": geo if _valid(geo) else math.nan,
                    "direct_value": direct if _valid(direct) else math.nan, "method": how,
                    "flags": ";".join(sorted(set(flags)))})
    return pd.DataFrame(out, columns=["id", "parsed_value", "geo_value", "direct_value", "method", "flags"])


def report(df: pd.DataFrame, res: pd.DataFrame, records: dict[str, dict]) -> None:
    print("records:", dict(Counter(r.get("status") for r in records.values())))
    print("methods:", dict(Counter(m.split(":")[0] for m in res.method)))
    print(f"geometry valid {int(res.geo_value.notna().sum())}, direct valid {int(res.direct_value.notna().sum())}, "
          f"no value {int(res.parsed_value.isna().sum())} of {len(res)}")
    usd = sum(float(r.get("usd") or 0) for r in records.values())
    print(f"run cost so far ${usd:.3f}; ledger total ${budget.spent():.2f} of cap ${budget.cap():.2f}")
    if "answer" in df.columns:
        m = df[["qid", "category", "answer"]].merge(res, left_on="qid", right_on="id")
        for col in ("parsed_value", "geo_value", "direct_value"):
            sc = score(m, col)
            cats = " ".join(f"{c}={v:.3f}" for c, v in sc["per_category"].items())
            print(f"MRA {col}: {sc['mra']:.3f} ({cats}; missing values score 0)")
    if "answer" in df.columns and len(res) <= 30:
        m = df[["qid", "answer"]].merge(res, left_on="qid", right_on="id")
        for r in m.itertuples():
            rel = lambda v: f"{abs(v - r.answer) / r.answer:+.0%}" if _valid(v) else "-"  # noqa: E731
            print(f"  qid {r.qid}: gt {r.answer:g} | direct {r.direct_value:.4g} ({rel(r.direct_value)}) | "
                  f"geo {r.geo_value:.4g} ({rel(r.geo_value)}) | {r.method}")


# --------------------------------------------------------------------------- main

def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--split", choices=["val", "test"])
    ap.add_argument("--csv", help="questions CSV (validation format) instead of --split")
    ap.add_argument("--video-dir", help="videos for --csv (default: the CSV's folder)")
    ap.add_argument("--name", required=True, help="run name, used as the output folder")
    ap.add_argument("--out-root", help="folder for run outputs (default: env QP_RUNS, else runs/)")
    ap.add_argument("--model", default=ca.MODEL)
    ap.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"], default="medium")
    ap.add_argument("--frames", type=int, default=16, help="uniform frames per video")
    ap.add_argument("--max-frames", type=int, default=32, help="cap incl. frames at mentioned times")
    ap.add_argument("--max-tokens", type=int, default=0, help="0 = 12k + 4k per question (max 64k)")
    ap.add_argument("--mode", choices=["sync", "batch"], default="sync")
    ap.add_argument("--limit-videos", type=int, default=0, help="only the first N videos")
    ap.add_argument("--videos", default="", help="comma-separated video ids to run")
    ap.add_argument("--workers", type=int, default=4, help="parallel requests (sync)")
    ap.add_argument("--est-output-per-question", type=int, default=0,
                    help="expected output tokens per question (0 = by effort: "
                         + ", ".join(f"{k} {v}" for k, v in EST_OUTPUT_PER_QUESTION.items()) + ")")
    ap.add_argument("--max-usd", type=float, default=0.0, help="refuse runs estimated above this")
    ap.add_argument("--retry-failed", action="store_true", help="re-send videos whose record is not ok")
    ap.add_argument("--rebuy-lost", action="store_true",
                    help="re-send videos the ledger shows as paid whose records are missing")
    ap.add_argument("--local-estimate", action="store_true", help="estimate input offline (no count_tokens)")
    ap.add_argument("--dry-run", action="store_true", help="print the estimate and stop")
    ap.add_argument("--no-wait", action="store_true", help="batch: do not poll, exit after submit/status")
    ap.add_argument("--poll-interval", type=float, default=60.0)
    ap.add_argument("--batch-mb", type=float, default=120.0, help="max request body per batch")
    ap.add_argument("--chunk-videos", type=int, default=100, help="max videos per batch")
    args = ap.parse_args(argv)
    if not args.split and not args.csv:
        ap.error("one of --split or --csv is required")
    return args


def _client():
    import anthropic
    return anthropic.Anthropic(max_retries=5)


def main(argv=None, client=None) -> pd.DataFrame | None:
    args = parse_args(argv)
    load_env()
    df, args.label = load_questions(args)
    split_groups = {v: g.reset_index(drop=True) for v, g in df.groupby("video_id", sort=False)}
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
    out_dir = runs_root / args.name / args.label
    rec_dir = out_dir / "records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    if not (out_dir / "config.json").exists():  # settings of the first invocation; records carry their own
        (out_dir / "config.json").write_text(json.dumps(vars(args), indent=2))
    records = load_records(rec_dir)
    state_path = out_dir / "batch.json"
    state = load_state(state_path)
    if n := recover_batches(state, args, records, split_groups):
        save_state(state_path, state)
        print(f"recovered {n} batch(es) of this run from the ledger (missing from batch.json)")
    in_batch = pending_videos(state) & set(groups)
    todo = todo_videos(groups, records, args.retry_failed, skip=in_batch)
    lost = [] if args.rebuy_lost else lost_videos(args, todo, records)
    if lost:
        print(f"not re-sending {len(lost)} video(s) the ledger shows as paid but without a record "
              f"(e.g. {lost[0]}; restore {rec_dir} or pass --rebuy-lost)")
        todo = [v for v in todo if v not in lost]
    stale = {v: d for v in groups if v not in todo and records.get(v, {}).get("status") in USABLE
             and (d := config_diff(records[v], args))}
    if stale:
        v, d = next(iter(stale.items()))
        raise SystemExit(f"{len(stale)} cached record(s) were made with other settings (e.g. {v}: "
                         + ", ".join(f"{k} {a} vs {b}" for k, (a, b) in d.items())
                         + "); use a new --name or the original settings")
    print(f"{len(groups)} videos ({len(df)} questions): {len(groups) - len(todo) - len(in_batch)} cached, "
          f"{len(in_batch)} in uncollected batches, {len(todo)} to run; "
          f"{args.model} effort={args.effort} mode={args.mode}")
    if in_batch and args.mode == "sync":
        print(f"  {len(in_batch)} video(s) are in uncollected batches and are not re-sent; "
              "rerun with --mode batch to collect them")

    if args.dry_run:
        if todo:
            guard(estimate(client or (None if args.local_estimate else _client()), groups, todo, args, records),
                  args)
        return None
    if args.mode == "batch" and (todo or in_batch):
        run_batch(client or _client(), groups, split_groups, args, out_dir, rec_dir, state, skip=lost)
    elif args.mode == "sync" and todo:
        client = client or _client()
        est = estimate(client, groups, todo, args, records)
        if guard(est, args):
            run_sync(client, groups, est["todo"], args, rec_dir, est)

    records = load_records(rec_dir)
    res = build_results(df, records)
    out_csv = runs_root / args.name / f"{args.label}.csv"
    res.to_csv(out_csv, index=False)
    print(f"wrote {out_csv}")
    report(df, res, records)
    return res


if __name__ == "__main__":
    main()
