"""Shared helpers of research/trackb_agent (CPU only): clip types, agent answers, base tables, the routing rule."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TYPES = ("sim3", "sim2", "internet", "lab")
MARGIN = 0.02            # pre-registered (RESULT.md): agent if >= base + MARGIN, gm if within MARGIN, base otherwise


def clip_type(video_source: str, video_type: str) -> str:
    """research/blind/build_agent_sub.py's type logic on the question inputs: internet and lab by video_source, every
    other source (simulation, segmentation - including segmented internet clips, as srcg in the r86 master table) is
    a simulation, split by video_type[1] into sim3 / sim2."""
    src = str(video_source or "").strip().lower()
    if src == "internet":
        return "internet"
    if src == "lab":
        return "lab"
    return "sim3" if str(video_type)[1:2] == "3" else "sim2"


def twin_origin(source) -> tuple[str, int] | None:
    """'twin:<original video>:<original qid>' (qp.open.agent_loop.fill_twins / build_sub's fill) -> (video, qid)."""
    s = str(source or "")
    if not s.startswith("twin:"):
        return None
    ov, _, oq = s[len("twin:"):].rpartition(":")
    try:
        return (ov, int(oq)) if ov else None
    except ValueError:
        return None


def agent_answers(split_dir: Path, exclude=None) -> tuple[pd.Series, pd.Series, dict]:
    """(answer by qid, source by qid, per-video records) from <split_dir>/answers/*.json (run_agent output).
    `exclude`: clip ids whose answers are dropped (audit_clips), together with every answer a twin copied from them
    (source 'twin:<excluded clip>:<qid>'). The records of excluded clips are still returned (for reporting)."""
    ex = {str(x) for x in (exclude or ())}
    vals, srcs, recs = {}, {}, {}
    d = Path(split_dir) / "answers"
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        try:
            rec = json.loads(p.read_text())
        except ValueError:
            print("bad json", p)
            continue
        if not isinstance(rec, dict) or rec.get("status") != "done":
            continue
        vid = str(rec.get("video_id"))
        recs[vid] = rec
        if vid in ex:
            continue
        for q, x in (rec.get("answers") or {}).items():
            try:
                v = abs(float(x))
            except (TypeError, ValueError):
                continue
            s = (rec.get("source") or {}).get(str(q), "agent")
            tw = twin_origin(s)
            if tw is not None and tw[0] in ex:
                continue
            if math.isfinite(v) and v > 0:
                vals[int(q)] = v
                srcs[int(q)] = s
    return pd.Series(vals, dtype=float), pd.Series(srcs, dtype=object), recs


def route_types(q: pd.DataFrame, source: pd.Series | None = None) -> pd.Series:
    """Clip type each row is ROUTED by (q: question rows indexed by qid with video_id, video_source, video_type).
    clip_type of the row's own inputs, except
      - every row of a segmented twin (<clip>_segmented) whose original clip is in `q` takes the original clip's
        type: the twin is the same footage with the background removed, so a segmented internet twin (video_source
        "segmentation", typed sim2 by clip_type) follows the internet decision;
      - a row whose answer was copied from a twin's original (`source` 'twin:<orig>:<qid>', written by
        qp.open.agent_loop.fill_twins or by build_sub's fill) takes the type of that original row (else clip)."""
    own = pd.Series([clip_type(s, t) for s, t in zip(q.video_source, q.video_type)], index=q.index, dtype=object)
    by_clip = own.groupby(q.video_id.astype(str).to_numpy(), sort=False).first()
    out = own.copy()
    for i, v in zip(q.index, q.video_id.astype(str)):
        if v.endswith("_segmented") and v[: -len("_segmented")] in by_clip.index:
            out[i] = by_clip[v[: -len("_segmented")]]
    if source is not None:
        for i, s in source.reindex(q.index).items():
            tw = twin_origin(s)
            if tw is None:
                continue
            ov, oq = tw
            if oq in own.index:
                out[i] = own[oq]
            elif ov in by_clip.index:
                out[i] = by_clip[ov]
    return out


def agent_test_videos(q: pd.DataFrame, decision: dict) -> list[str]:
    """Test clips whose agent answers the build can use under `decision`: clips with a row routed (route_types) to a
    type not decided "base", plus the original clip of every segmented twin among them (the twin reuses its answers).
    In split order; the input of qp.open.run_agent --videos."""
    rt = route_types(q)
    keep = rt.map(lambda t: decision.get(t, "base") != "base").astype(bool)
    vids = set(q.video_id[keep].astype(str))
    present = set(q.video_id.astype(str))
    vids |= {v[: -len("_segmented")] for v in list(vids)
             if v.endswith("_segmented") and v[: -len("_segmented")] in present}
    return [v for v in dict.fromkeys(q.video_id.astype(str)) if v in vids]


# --------------------------------------------------------------------------- transcript audit (Track B rule)
# Assistant replies naming paths outside the clip workspace (labels, other runs, Track A outputs, the repo, Drive) and
# tool results showing a sandbox refusal (a read outside the workspace or a network call was attempted).
LEAK = re.compile(r"QuantiPhy-validation|ground_truth|submission_template|/data/QuantiPhy|quantiphy-challenge|"
                  r"/content/drive|outputs/trackb|\.\./", re.I)
REFUSALS = ("outside the workspace", "network access is disabled")
_AUDIT_LIST_KEYS = ("hits", "leaks", "reasons", "flags", "matches", "findings", "issues")
_AUDIT_BOOL_KEYS = ("flagged", "leak", "leaked", "suspicious")


def scan_transcript(tr: dict) -> list[str]:
    """Local fallback of qp.open.agent_loop.audit_transcript (the same string scan): reasons a transcript is flagged
    ([] = clean). Assistant turns: visible text and thinking tail against LEAK; user turns (tool results): REFUSALS."""
    hits = []
    for k, t in enumerate(tr.get("turns") or []):
        if not isinstance(t, dict):
            continue
        if t.get("role") == "assistant":
            for key in ("text", "thinking_tail"):
                m = LEAK.search(str(t.get(key) or ""))
                if m:
                    hits.append(f"turn {k} assistant {key}: {m.group(0)!r}")
        elif t.get("role") == "user":
            txt = str(t.get("text") or "")
            hits += [f"turn {k} tool result: {r!r}" for r in REFUSALS if r in txt]
    return hits


def _finding(x) -> bool:
    """One element of a findings list: a message, a dict, or a non-empty tuple of scalars such as (turn, match). Not
    an empty container or a bare number (a (hits, n_denied) pair is not a findings list)."""
    if isinstance(x, (str, dict)):
        return bool(x)
    return isinstance(x, (list, tuple)) and len(x) > 0 and all(isinstance(y, (str, int, float)) for y in x)


def _audit_result(res) -> list[str] | None:
    """Normalise what audit_transcript returned -> reasons ([] = clean), None when the shape is not understood."""
    if isinstance(res, bool):
        return ["flagged by audit_transcript"] if res else []
    if isinstance(res, str):
        return [res] if res.strip() else []
    if isinstance(res, (list, tuple, set)):
        return [str(x)[:200] for x in res] if all(_finding(x) for x in res) else None
    if isinstance(res, dict):
        lists = [str(x)[:200] for k in _AUDIT_LIST_KEYS if isinstance(res.get(k), (list, tuple, set)) for x in res[k]]
        if any(k in res for k in _AUDIT_BOOL_KEYS):
            return (lists or ["flagged by audit_transcript"]) if any(bool(res.get(k)) for k in _AUDIT_BOOL_KEYS) else []
        if "ok" in res or "clean" in res:
            return [] if bool(res.get("ok", res.get("clean"))) else (lists or ["flagged by audit_transcript"])
        if any(k in res for k in _AUDIT_LIST_KEYS):
            return lists
    return None


def _safe_id(video_id: str) -> str:   # qp.open.agent_loop.safe_id: the transcript / answers file stem
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(video_id).strip())[:80] or "video"


def audit_clips(split_dir: Path, recs: dict | None = None, verbose: bool = True) -> dict[str, list[str]]:
    """Audit every transcript of <split_dir>/transcripts with qp.open.agent_loop.audit_transcript (imported here, so
    this module works without it) AND scan_transcript, the same string scan -> {clip: reasons} of the clips to
    EXCLUDE. A clip is flagged when either flags it, so a result of audit_transcript whose shape is misread (e.g. a
    refusal count under a key not listed here) cannot clear a clip the scan flags; if the import fails, the call
    raises or the result is not understood, the scan alone decides. A clip with an answers record (`recs`) but no
    transcript is excluded too (it cannot be audited), except twin-only records (end 'twin': no conversation of
    their own; their answers follow the original clip's audit through agent_answers(exclude=...))."""
    try:
        from qp.open.agent_loop import audit_transcript as fn
        impl = "qp.open.agent_loop.audit_transcript + local scan_transcript"
    except Exception as e:  # noqa: BLE001 - not there yet / agent_loop not importable: the local scan
        fn, impl = None, f"local scan_transcript ({type(e).__name__} importing audit_transcript)"
    flagged: dict[str, list[str]] = {}
    seen, n, n_fb = set(), 0, 0
    by_stem = {_safe_id(v): v for v in (recs or {})}
    d = Path(split_dir) / "transcripts"
    for p in sorted(d.glob("*.json")) if d.exists() else []:
        seen.add(p.stem)
        n += 1
        try:
            tr = json.loads(p.read_text())
            assert isinstance(tr, dict)
        except (ValueError, AssertionError):
            flagged[by_stem.get(p.stem, p.stem)] = ["unreadable transcript"]
            continue
        vid = str(tr.get("video_id") or by_stem.get(p.stem, p.stem))
        hits = None
        if fn is not None:
            try:
                hits = _audit_result(fn(tr))
            except Exception:  # noqa: BLE001 - other signature / bad transcript: the local scan decides
                hits = None
        if hits is None:
            n_fb += fn is not None
            hits = []
        hits = list(hits) + [h for h in scan_transcript(tr) if h not in hits]   # either flags -> excluded
        if hits:
            flagged[vid] = list(hits)
    for vid, rec in (recs or {}).items():
        if _safe_id(vid) not in seen and str(rec.get("end")) != "twin" and vid not in flagged:
            flagged[vid] = ["no transcript: its answers cannot be audited"]
    if verbose:
        print(f"transcript audit ({impl}{f'; audit_transcript result not usable on {n_fb}, scan only' if n_fb else ''}"
              f"): {n} transcripts, "
              f"{len(flagged)} clip(s) excluded (their rows keep the base)"
              + "".join(f"\n  EXCLUDED {v}: {'; '.join(r[:3])}{' ...' if len(r) > 3 else ''}"
                        for v, r in sorted(flagged.items())))
    return flagged


def gm(a: pd.Series, b: pd.Series) -> pd.Series:
    """geometric mean where both exist, else whichever exists"""
    a, b = a.astype(float), b.astype(float)
    both = (a > 0) & (b > 0)
    out = a.where(a > 0, b)
    out[both] = np.exp((np.log(a[both]) + np.log(b[both])) / 2)
    return out


def routed(base: pd.Series, agent: pd.Series, types: pd.Series, stated: pd.Series, decision: dict) -> pd.Series:
    """Apply per-type decisions ("agent" / "gm" / "base"); rows set by a stated-fact rule always keep the base."""
    out = base.astype(float).copy()
    ag = agent.reindex(base.index)
    st = stated.reindex(base.index).fillna(0).astype(bool)
    for t, how in decision.items():
        m = (types.reindex(base.index) == t) & ~st & ag.notna()
        if how == "agent":
            out[m] = ag[m]
        elif how == "gm":
            out[m] = gm(ag[m], base[m])
    return out


def decide(score_agent: float, score_base: float, n_agent: int, margin: float = MARGIN) -> str:
    """The pre-registered rule (RESULT.md), per type, on validation item MRA (agent rows filled with the base)."""
    if n_agent == 0 or not np.isfinite(score_agent):
        return "base"
    d = score_agent - score_base
    if d >= margin - 1e-12:
        return "agent"
    if d > -margin + 1e-12:
        return "gm"
    return "base"


def load_base(name: str) -> pd.DataFrame:
    return pd.read_csv(HERE / name)
