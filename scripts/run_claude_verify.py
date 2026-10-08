"""Verification pass (qp.claude_verify): one more Claude request per video that checks and corrects the
pixel measurements behind a scripts/run_claude.py run's answers, then recomputes the geometry.

    python scripts/run_claude_verify.py --split val --name val_verify_high --from val_opus_high --effort high
    python scripts/run_claude_verify.py --split val --name val_verify_high --from val_opus_high --mode batch
    python scripts/run_claude_verify.py --split val --name v --from val_opus_high --dry-run    # estimate only
    python scripts/run_claude_verify.py ... --save-evidence          # also write the evidence images as JPEGs

Reads the pass-1 records of <runs>/<from>/<split>/records (ok / partial), writes <runs>/<name>/<split>/records/
<video_id>.json (the verifier's raw text, parsed JSON, usage, cost and the request metadata: tracks,
specs, evidence regions, everything recompute needs) and batch.json (batch mode), then <runs>/<name>/<split>.csv
with run_claude's columns (id, parsed_value, geo_value, direct_value, method, flags, geo_method; so
scripts/combine_runs.py takes it) plus pass1_value, geo1_value, geo2_value, verdict, final_answer and verify_how.
Questions of videos without a verify record keep their pass-1 answer (verify_how "pass1_unverified"). The
report prints the MRA of every answer rule (qp.claude_verify.RULES) on the verified videos, so one run
compares verify / remeasure / pass1 without further API calls (--rule only picks what the CSV holds).
Request version: --verify-version (default vf2: the model re-reads every evidence measurement; vf1 = the
version of the single live test, which kept every track of a video whose pass-1 endpoints were right, so
it shows neither version's diligence: compare them on questions with a visible endpoint error first).

--dense: a .csv (id + parsed_value/geo_value: answers of a dense-tracking run, shown to the verifier) or
a .json file / folder of qid -> [RoleTrack dicts] replacing pass 1's tracks of those roles before verification.

Same budget discipline as run_claude.py (whose helpers this reuses): an estimate (count_tokens on the
first request, transferred to the others by their offline estimates) is checked against the cap
(QP_BUDGET_USD) before anything is sent; every request is held at its worst case (1.25 x input +
max_tokens) until its usage is in budget/ledger.jsonl; batches are held in the ledger and recovered
from it if batch.json is lost. Cached videos are skipped; a run refuses cached records made with other
settings. Rerunning a fully cached run sends nothing and re-scores it (--rule picks the answer rule).
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import math
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qp import budget  # noqa: E402
from qp import claude_annotate as ca  # noqa: E402
from qp import claude_verify as cvf  # noqa: E402
from qp import combine  # noqa: E402
from qp.mra import score  # noqa: E402


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_claude", ROOT / "scripts" / "run_claude.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rc = _load_runner()
VERIFY_KEYS = ("model", "effort", "from_run", "verify_version", "max_side", "max_overviews", "max_crops", "dense",
               "refine")


def verify_config(cfg) -> dict:
    return {"model": cfg.model, "effort": cfg.effort, "from_run": cfg.from_run, "verify_version": cfg.verify_version,
            "max_side": cfg.max_side, "max_overviews": cfg.max_overviews, "max_crops": cfg.max_crops,
            "dense": cfg.dense or "", "refine": not cfg.no_refine}


def config_diff(rec: dict, cfg) -> dict:
    have, cur = rec.get("config") or {}, verify_config(cfg)
    return {k: (have.get(k), cur[k]) for k in VERIFY_KEYS if k in have and have[k] != cur[k]}


def is_verify_record(rec: dict) -> bool:
    """A record written by this script (config names the pass-1 run / meta the verify version)."""
    return bool((rec.get("config") or {}).get("from_run")) or "verify_version" in (rec.get("meta") or {})


def foreign_ledger_entries(cfg, records: dict[str, dict]) -> list[dict]:
    """Ledger entries of run cfg.name and split cfg.label that are not this script's (a pass-1 run of the
    same name): run_claude's lost_videos / recover_batches key on the run name, so such entries would
    be taken for this run's. Verify entries: kind "verify" (sync usage, holds), a hold whose config
    names a pass-1 run, batch usage under such a hold ("<batch id>/<custom id>"), or (entries from
    before the kind tag) usage of a video whose record here is a verify record."""
    mine = [e for e in budget.entries() if e.get("run") == cfg.name and e.get("split") == cfg.label]
    holds = {e["id"] for e in mine if e.get("type") == "hold"
             and (e.get("kind") == "verify" or (e.get("config") or {}).get("from_run"))}
    out = []
    for e in mine:
        t = e.get("type", "usage")
        if t == "hold":
            ok = e["id"] in holds
        elif t == "usage":
            ok = e.get("kind") == "verify" or str(e.get("id", "")).split("/")[0] in holds or \
                is_verify_record(records.get(e.get("video_id")) or {})
        else:
            continue
        if not ok:
            out.append(e)
    return out


def check_names(cfg, runs_root: Path, pass1: dict[str, dict], records: dict[str, dict]) -> None:
    """Refuse a verify run that would share its folder or ledger namespace with a pass-1 run."""
    if cfg.name == cfg.from_run:
        raise SystemExit(f"--name {cfg.name!r} is the pass-1 run (--from): choose a new verify run name")
    if any(is_verify_record(r) for r in pass1.values()):
        raise SystemExit(f"--from {cfg.from_run!r} holds verify records, not pass-1 (scripts/run_claude.py) records")
    other = [v for v, r in records.items() if not is_verify_record(r)]
    if other:
        raise SystemExit(f"{runs_root / cfg.name / cfg.label / 'records'} holds {len(other)} record(s) that are not "
                         f"verify records (e.g. {other[0]}; a pass-1 run?): choose another --name")
    foreign = foreign_ledger_entries(cfg, records)
    if foreign:
        raise SystemExit(f"the ledger has {len(foreign)} entr(y/ies) of a run named {cfg.name!r} ({cfg.label}) that "
                         f"this script did not write (e.g. {foreign[0].get('type', 'usage')} {foreign[0].get('id')}): "
                         f"choose another --name")


# --------------------------------------------------------------------------- requests

def build_requests(df: pd.DataFrame, pass1: dict[str, dict], vids: list[str], cfg) -> dict[str, tuple[dict, dict]]:
    """{video_id: (params, meta)} for `vids` (videos whose request cannot be built are reported and left out)."""
    if not vids:
        return {}
    dense = cvf.load_dense(cfg.dense) if cfg.dense else None
    ctxs = cvf.build_contexts(df[df.video_id.isin(vids)], {v: pass1[v] for v in vids if v in pass1},
                              refine_priors=not cfg.no_refine, dense=dense)
    out = {}
    for v in vids:
        if v not in ctxs:
            print(f"  skipping {v}: no usable pass-1 annotation")
            continue
        try:
            params, meta = cvf.build_request(ctxs[v], cfg.effort, cfg.max_tokens, cfg.model, cfg.max_side,
                                             cfg.max_overviews, cfg.max_crops, version=cfg.verify_version)
        except Exception as e:  # noqa: BLE001 - one bad video must not stop the run
            print(f"  skipping {v}: {type(e).__name__}: {e}")
            continue
        meta["from_run"] = cfg.from_run
        out[v] = (params, meta)
        if cfg.save_evidence:
            save_evidence(cfg.out_dir / "evidence" / rc.safe_id(v), params)
    return out


def save_evidence(folder: Path, params: dict) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    texts, k = [], 0
    for b in params["messages"][0]["content"]:
        if b["type"] == "text":
            texts.append(b["text"])
        else:
            k += 1
            (folder / f"img{k:02d}.jpg").write_bytes(base64.b64decode(b["source"]["data"]))
            texts.append(f"<img{k:02d}.jpg>")
    (folder / "prompt.txt").write_text(params["system"][0]["text"] + "\n\n=====\n\n" + "\n\n".join(texts))


def estimate(client, reqs: dict[str, tuple[dict, dict]], cfg, records: dict) -> dict | None:
    """rc.guard-compatible estimate: input by offline estimate per request, calibrated by count_tokens on
    the first (unless --local-estimate); output by rc.output_per_question; per-video worst case."""
    if not reqs:
        return None
    vids = list(reqs)
    offline = {v: ca.estimate_input_tokens(reqs[v][0]) for v in vids}
    if cfg.local_estimate or client is None:
        ratio, how, first_in = 1.0, "offline estimate", offline[vids[0]]
    else:
        params = reqs[vids[0]][0]
        counted = client.messages.count_tokens(**{k: v for k, v in params.items() if k != "max_tokens"})
        first_in = int(counted.input_tokens)
        ratio, how = first_in / max(1, offline[vids[0]]), "count_tokens"
    per_q, out_how = rc.output_per_question(cfg, records)
    batch = cfg.mode == "batch"
    per_video = {v: max(first_in if v == vids[0] else 0, math.ceil(offline[v] * ratio)) for v in vids}
    worst = {v: budget.estimate_usd(rc.INPUT_MARGIN * per_video[v], reqs[v][0]["max_tokens"], cfg.model, batch)
             for v in vids}
    n_q = sum(len(reqs[v][1]["questions"]) for v in vids)
    total_in, total_out = sum(per_video.values()), per_q * n_q
    return {"usd": budget.estimate_usd(total_in, total_out, cfg.model, batch), "worst_usd": sum(worst.values()),
            "todo": vids, "videos": len(vids), "questions": n_q, "first_input_tokens": first_in, "how": how,
            "input_tokens": total_in, "output_tokens": total_out, "out_per_question": per_q, "out_how": out_how,
            "per_video_in": per_video, "worst": worst}


# --------------------------------------------------------------------------- sync

def run_sync(client, reqs, todo, cfg, rec_dir: Path, est: dict) -> None:
    config = verify_config(cfg)

    def work(vid: str) -> dict:
        params, meta = reqs[vid]
        with budget.reserve(est["worst"][vid]):
            msg, request_id = rc.call(client, params)
            usd = budget.price(msg.usage, cfg.model)
            budget.record(cfg.name, cfg.model, "sync", request_id or msg.id, msg.usage, usd,
                          video_id=vid, split=cfg.label, kind="verify")
        rec = rc.message_record(msg, vid, meta, config, usd, mode="sync", request_id=request_id)
        rc.save_record(rec_dir, rec)
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

def submit(client, reqs, vids: list[str], cfg, state_path: Path, state: dict, est: dict) -> list[str]:
    """Batches of as many of `vids` as fit under the cap at their worst case (ledger hold per batch)."""
    chunk, size, sent, used = [], 0, [], set()
    config = verify_config(cfg)

    def flush():
        nonlocal chunk, size
        if not chunk:
            return
        worst, usd = sum(c[3] for c in chunk), sum(c[4] for c in chunk)
        budget.check(worst)
        batch = client.messages.batches.create(requests=[{"custom_id": c[0], "params": c[1]} for c in chunk])
        cids = {c[0]: c[2]["video_id"] for c in chunk}
        budget.hold(cfg.name, batch.id, worst, split=cfg.label, custom_ids=cids, config=config, est_usd=round(usd, 4),
                    kind="verify")
        state["batches"].append({"id": batch.id, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                 "collected": False, "model": cfg.model, "effort": cfg.effort, "config": config,
                                 "est_usd": round(usd, 4), "hold_usd": round(worst, 4), "custom_ids": cids,
                                 "meta": {c[2]["video_id"]: c[2] for c in chunk}})
        rc.save_state(state_path, state)
        sent.extend(cids.values())
        print(f"  submitted batch {batch.id}: {len(chunk)} videos, est ${usd:.2f}, held ${worst:.2f} (worst case)")
        chunk, size = [], 0

    for vid in vids:
        worst = est["worst"][vid]
        room = budget.cap() - budget.committed() - sum(c[3] for c in chunk)
        if worst > room:
            flush()
            print(f"  budget: {len(vids) - len(sent)} video(s) wait: worst case ${worst:.2f} > headroom "
                  f"${max(room, 0):.2f}")
            break
        params, meta = reqs[vid]
        cid = rc.safe_id(vid)
        while cid in used:
            cid = f"{cid[:60]}_{len(used) % 1000}"
        used.add(cid)
        n = len(json.dumps(params))
        if chunk and (size + n > cfg.batch_mb * 1e6 or len(chunk) >= cfg.chunk_videos):
            flush()
        chunk.append((cid, params, meta, worst, budget.estimate_usd(
            est["per_video_in"][vid], est["out_per_question"] * len(meta["questions"]), cfg.model, batch=True)))
        size += n
    flush()
    return sent


def fill_meta(entry: dict, df: pd.DataFrame, pass1: dict, cfg) -> None:
    """Rebuild the request metadata of a batch recovered from the ledger (deterministic) so that
    rc.collect can write its records."""
    missing = [v for v in entry.get("custom_ids", {}).values() if v not in entry.setdefault("meta", {})]
    if missing:
        stored = entry.get("config") or {}
        sub = argparse.Namespace(**{**vars(cfg), **{k: stored[k] for k in ("effort", "max_side", "max_overviews",
                                                                         "max_crops", "verify_version")
                                                    if k in stored}})
        sub.save_evidence = False
        for v, (_, meta) in build_requests(df, pass1, missing, sub).items():
            entry["meta"][v] = meta


def run_batch(client, df, pass1, groups, cfg, rec_dir: Path, state: dict, skip=()) -> None:
    state_path = cfg.out_dir / "batch.json"
    attempted = set(skip)
    while True:
        pending = [e for e in state["batches"] if not e.get("collected")]
        if pending:
            print(f"{len(pending)} uncollected batch(es)")
        for e in pending:
            fill_meta(e, df, pass1, cfg)
            if not rc.wait_and_collect(client, e, cfg, rec_dir, state_path, state):
                print("still running; rerun later to collect")
                return
        records = rc.load_records(rec_dir)
        todo = [v for v in rc.todo_videos(groups, records, cfg.retry_failed, skip=attempted) if v in pass1]
        if not todo:
            return
        reqs = build_requests(df, pass1, todo, cfg)
        est = estimate(None if cfg.local_estimate else client, reqs, cfg, records)
        if not rc.guard(est, cfg):
            return
        try:
            sent = submit(client, reqs, est["todo"], cfg, state_path, state, est)
        except budget.BudgetExceeded as e:
            print(f"stopped submitting: {e}")
            sent = []
        if not sent and not any(not e.get("collected") for e in state["batches"]):
            return
        attempted.update(sent)


# --------------------------------------------------------------------------- results

def build_results(df: pd.DataFrame, records: dict[str, dict], pass1: dict[str, dict], cfg) -> pd.DataFrame:
    """Verified videos: qp.claude_verify.recompute(rule). Others: run_claude's pass-1 answers."""
    rows = []
    for vid, rec in records.items():
        if vid in set(df.video_id) and rec.get("status") in rc.USABLE and rec.get("meta", {}).get("tracks"):
            rows += cvf.recompute(rec["meta"], rec.get("parsed"), cfg.rule, cfg.pass1_rule)
    done = {r["id"] for r in rows}
    rest = df[~df.qid.isin(done)]   # unverified videos, and questions pass 1 left unanswered
    if len(rest):
        res = rc.build_results(rest, {v: r for v, r in pass1.items() if v in set(rest.video_id)}, cfg.pass1_rule)
        res["pass1_value"] = res["parsed_value"]
        res["geo1_value"] = res["geo_value"]
        res["verdict"] = "unverified"
        res["verify_how"] = "pass1_unverified"
        rows += res.to_dict("records")
    out = pd.DataFrame(rows)
    for c in cvf.COLUMNS:
        if c not in out.columns:
            out[c] = math.nan
    order = {q: i for i, q in enumerate(df.qid)}
    return out[cvf.COLUMNS].sort_values("id", key=lambda s: s.map(order)).reset_index(drop=True)


def _macro(sc: dict) -> str:
    """The official macro MRA, or (when a category is absent) the mean over the categories present."""
    if math.isfinite(sc["mra"]):
        return f"{sc['mra']:.3f}"
    vals = list(sc["per_category"].values())
    return f"{sum(vals) / len(vals):.3f}*" if vals else "nan"


def rule_table(df: pd.DataFrame, records: dict[str, dict], cfg) -> list[tuple[str, dict]]:
    """MRA of every answer rule on the verified videos' questions (needs answers)."""
    out = []
    ver = {v: r for v, r in records.items() if r.get("status") in rc.USABLE and r.get("meta", {}).get("tracks")}
    if not ver or "answer" not in df.columns:
        return out
    m = df[df.video_id.isin(ver)][["qid", "category", "answer"]]
    for rule in cvf.RULES:
        rows = [row for r in ver.values() for row in cvf.recompute(r["meta"], r.get("parsed"), rule, cfg.pass1_rule)]
        out.append((rule, score(m.merge(pd.DataFrame(rows), left_on="qid", right_on="id"), "parsed_value")))
    return out


def report(df: pd.DataFrame, res: pd.DataFrame, records: dict[str, dict], cfg=None) -> None:
    print("records:", dict(Counter(r.get("status") for r in records.values())))
    print("verdicts:", dict(Counter(res.verdict)), " answers from:", dict(Counter(res.verify_how)))
    d = res.delta_px.dropna()
    if len(d):
        print(f"verifier readings vs pass 1 (max per question, px): median {d.median():.1f}, "
              f">=2 px on {int((d >= 2).sum())} of {len(d)}")
    usd = sum(float(r.get("usd") or 0) for r in records.values())
    print(f"run cost so far ${usd:.3f}; ledger total ${budget.spent():.2f} of cap ${budget.cap():.2f}")
    if "answer" not in df.columns:
        return
    m = df[["qid", "video_id", "category", "answer"]].merge(res, left_on="qid", right_on="id")
    for col in ("parsed_value", "pass1_value", "geo1_value", "geo2_value", "final_answer"):
        if m[col].notna().any():
            sc = score(m, col)
            cats = " ".join(f"{c}={v:.3f}" for c, v in sc["per_category"].items())
            print(f"MRA {col}: {_macro(sc)} ({cats}; missing values score 0; * = mean of the categories present)")
    if cfg is not None:
        for rule, sc in rule_table(df, records, cfg):
            cats = " ".join(f"{c}={v:.3f}" for c, v in sc["per_category"].items())
            print(f"  verified videos only, rule {rule:<14} MRA {_macro(sc)} ({cats})")
    if len(m) <= 40:
        for r in m.itertuples():
            rel = lambda v: f"{(v - r.answer) / r.answer:+.1%}" if cvf.valid(v) else "-"  # noqa: E731
            print(f"  qid {r.qid}: gt {r.answer:.4g} | pass1 {r.pass1_value:.4g} ({rel(r.pass1_value)}) | "
                  f"geo2 {r.geo2_value:.4g} ({rel(r.geo2_value)}) | verifier {r.final_answer:.4g} "
                  f"({rel(r.final_answer)}) | final {r.parsed_value:.4g} ({rel(r.parsed_value)}) | "
                  f"{r.verdict} -> {r.verify_how}")


# --------------------------------------------------------------------------- main

def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--split", choices=["val", "val_hires", "test"])
    ap.add_argument("--csv", help="questions CSV (validation format) instead of --split (as run_claude.py)")
    ap.add_argument("--video-dir", help="videos for --csv (default: the CSV's folder)")
    ap.add_argument("--name", required=True, help="verify run name (output folder)")
    ap.add_argument("--from", dest="from_run", required=True, help="pass-1 run name (scripts/run_claude.py --name)")
    ap.add_argument("--out-root", help="folder for runs (default: env QP_RUNS, else runs/)")
    ap.add_argument("--model", default=cvf.MODEL)
    ap.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"], default="high",
                    help="model effort (the single medium-effort live test cannot tell whether medium suffices)")
    ap.add_argument("--verify-version", choices=list(cvf.SYSTEMS), default=cvf.VERIFY_VERSION,
                    help="request version (qp.claude_verify.SYSTEMS)")
    ap.add_argument("--mode", choices=["sync", "batch"], default="sync")
    ap.add_argument("--dense", default="", help="dense tracks (.json / folder) or dense answers (.csv); see above")
    ap.add_argument("--rule", choices=list(cvf.RULES), default=cvf.DEFAULT_RULE,
                    help="answer rule after verification (qp.claude_verify; no API effect)")
    ap.add_argument("--pass1-rule", choices=list(combine.RULES), default=combine.DEFAULT_RULE,
                    help="geometry / direct selection (qp.combine), as in run_claude.py")
    ap.add_argument("--limit-videos", type=int, default=0, help="only the first N videos")
    ap.add_argument("--videos", default="", help="comma-separated video ids")
    ap.add_argument("--max-tokens", type=int, default=0, help="0 = 8k + 3k per question + 600 per track (max 64k)")
    ap.add_argument("--max-side", type=int, default=cvf.MAX_SIDE, help="long-edge cap of full-frame evidence images")
    ap.add_argument("--max-overviews", type=int, default=cvf.MAX_OVERVIEWS, help="full-frame images per request")
    ap.add_argument("--max-crops", type=int, default=cvf.MAX_CROPS, help="zoomed crops per request")
    ap.add_argument("--no-refine", action="store_true", help="do not refine motion priors by optical flow first")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--est-output-per-question", type=int, default=0)
    ap.add_argument("--max-usd", type=float, default=0.0, help="refuse runs estimated above this")
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--rebuy-lost", action="store_true")
    ap.add_argument("--local-estimate", action="store_true", help="estimate input offline (no count_tokens)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--save-evidence", action="store_true", help="write evidence JPEGs + prompt under the run folder")
    ap.add_argument("--no-wait", action="store_true")
    ap.add_argument("--poll-interval", type=float, default=60.0)
    ap.add_argument("--batch-mb", type=float, default=120.0)
    ap.add_argument("--chunk-videos", type=int, default=100)
    args = ap.parse_args(argv)
    if not args.split and not args.csv:
        ap.error("one of --split or --csv is required")
    return args


def main(argv=None, client=None) -> pd.DataFrame | None:
    cfg = parse_args(argv)
    rc.load_env()
    df, cfg.label = rc.load_questions(cfg)
    runs_root = Path(cfg.out_root or os.environ.get("QP_RUNS") or ROOT / "runs")
    p1_dir = runs_root / cfg.from_run / cfg.label / "records"
    if not p1_dir.exists():
        raise SystemExit(f"no pass-1 records at {p1_dir}")
    pass1 = rc.load_records(p1_dir)
    if cfg.videos:
        df = df[df.video_id.isin(cfg.videos.split(","))]
    vids = list(dict.fromkeys(df.video_id))
    if cfg.limit_videos:
        vids = vids[:cfg.limit_videos]
    df = df[df.video_id.isin(vids)].reset_index(drop=True)
    usable = {v: r for v, r in pass1.items() if v in vids and r.get("status") in rc.USABLE}
    groups = {v: g.reset_index(drop=True) for v, g in df.groupby("video_id", sort=False) if v in usable}
    missing = [v for v in vids if v not in usable]
    if missing:
        print(f"{len(missing)} video(s) have no usable pass-1 record and keep no answer from this pass "
              f"(e.g. {missing[0]})")
    cfg.out_dir = runs_root / cfg.name / cfg.label
    rec_dir = cfg.out_dir / "records"
    check_names(cfg, runs_root, pass1, rc.load_records(rec_dir) if rec_dir.exists() else {})  # before any write
    rec_dir.mkdir(parents=True, exist_ok=True)
    if not (cfg.out_dir / "config.json").exists():
        (cfg.out_dir / "config.json").write_text(json.dumps({k: str(v) if isinstance(v, Path) else v
                                                             for k, v in vars(cfg).items()}, indent=2))
    records = rc.load_records(rec_dir)
    state_path = cfg.out_dir / "batch.json"
    state = rc.load_state(state_path)
    if n := rc.recover_batches(state, cfg, records, groups):
        rc.save_state(state_path, state)
        print(f"recovered {n} batch(es) of this run from the ledger (missing from batch.json)")
    in_batch = rc.pending_videos(state) & set(groups)
    todo = rc.todo_videos(groups, records, cfg.retry_failed, skip=in_batch)
    lost = [] if cfg.rebuy_lost else rc.lost_videos(cfg, todo, records)
    if lost:
        print(f"not re-sending {len(lost)} video(s) the ledger shows as paid but without a record "
              f"(e.g. {lost[0]}; restore {rec_dir} or pass --rebuy-lost)")
        todo = [v for v in todo if v not in lost]
    stale = {v: d for v in groups if v not in todo and records.get(v, {}).get("status") in rc.USABLE
             and (d := config_diff(records[v], cfg))}
    if stale:
        v, d = next(iter(stale.items()))
        raise SystemExit(f"{len(stale)} cached record(s) were made with other settings (e.g. {v}: "
                         + ", ".join(f"{k} {a} vs {b}" for k, (a, b) in d.items()) + "); use a new --name")
    print(f"{len(groups)} videos ({int(df.video_id.isin(groups).sum())} questions) from {cfg.from_run}: "
          f"{len(groups) - len(todo) - len(in_batch)} verified, {len(in_batch)} in uncollected batches, "
          f"{len(todo)} to run; {cfg.model} effort={cfg.effort} mode={cfg.mode}")

    if cfg.dry_run:
        if todo:
            reqs = build_requests(df, usable, todo, cfg)
            rc.guard(estimate(client or (None if cfg.local_estimate else rc._client()), reqs, cfg, records), cfg)
        return None
    if cfg.mode == "batch" and (todo or in_batch):
        run_batch(client or rc._client(), df, usable, groups, cfg, rec_dir, state, skip=lost)
    elif cfg.mode == "sync" and todo:
        client = client or rc._client()
        reqs = build_requests(df, usable, todo, cfg)
        est = estimate(None if cfg.local_estimate else client, reqs, cfg, records)
        if rc.guard(est, cfg):
            run_sync(client, reqs, est["todo"], cfg, rec_dir, est)

    records = rc.load_records(rec_dir)
    res = build_results(df, records, usable, cfg)
    out_csv = runs_root / cfg.name / f"{cfg.label}.csv"
    res.to_csv(out_csv, index=False)
    print(f"wrote {out_csv}")
    report(df, res, records, cfg)
    return res


if __name__ == "__main__":
    main()
