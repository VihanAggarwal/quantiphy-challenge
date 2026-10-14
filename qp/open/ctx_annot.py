"""Context-aware open-weight annotation for Track B (RUN_PRESET "ctx" of notebooks/colab_pipeline.ipynb).

Why (research/trackb_next/RESULT.md): on validation the Track B geometry loses to the Track A geometry because of the
pixel tracks, not the question specs (same solver, Qwen specs: Qwen tracks .507 vs Claude's tracks .733 macro MRA);
with SAM 2 motion tracks in place, the remaining loss is the TARGET measurement - which segment a size question means
(a part, a gap, a path, a spacing) and where its ends are. Open grounding today sees one frame and only the object
name ("the two ends of the width of the lane"). This module gives an open VLM the context Claude has.

Two GPU tasks (qp/open/run_ctx.py), both writing run_open_vlm-format records:

ta  ("Track-A style"): ONE request per video with 16 uniform frames + frames at every mentioned time (max 32, long
    side 1024 px, each labelled "Frame <idx> (t=<s>s)") and ALL of the video's questions; the model (default
    Qwen3.6-27B, thinking on) returns per question a spec, tracks (points / extents / boxes on the 0-1000 grid of
    each frame, the Qwen grounding convention) and its own answer. Parsed with the Track A converter
    (qp.claude_annotate.to_annotations: reuse of earlier tracks, windows, gravity axis) after mapping the grid to
    sent-image pixels; specs repaired from the text with qp.open.qwen_vl.validate_spec (rule spec as fallback).
    -> ta/specs/<vid>.json, ta/annotate/<vid>.json (tracks in original pixels), ta/direct/<vid>.json, ta/direct.csv.
cx  ("context extents"): for every size target, size prior and two-object distance, single-image pointing requests
    that carry the FULL question and prior text, on up to 3 frames where the ta track shows the object, then the same
    request on a zoomed full-resolution crop around the two points. -> cx/<vid>.json (endpoints in original pixels).

ctx_merge.py (CPU) turns them into hybrid track records for qp.geometry (sizes from cx, motion from SAM 2 or ta).
Everything here is open-weight and model-free post-processing; no closed-model output is used anywhere.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from typing import Any

import numpy as np

from qp.claude_annotate import mentioned_times, select_frames, to_annotations, video_fps, video_info
from qp.open.qwen_vl import (Request, extract_json, parse_depth, parse_grounding, read_rgb, rule_spec, to_image,
                             uniform_indices, validate_spec, _structured)
from qp.spec import KIND_DIM, Obs, QuestionSpec, RoleTrack

DEFAULT_MODEL = "Qwen/Qwen3.6-27B-FP8"
FALLBACK_MODEL = "Qwen/Qwen3.6-27B"      # bf16 (55.6 GB) if the FP8 checkpoint fails to load
SOURCE_TA, SOURCE_CX = "ctx-ta", "ctx-cx"
TA_N_UNIFORM, TA_MAX_FRAMES, TA_MAX_SIDE = 16, 32, 1024
CX_MAX_SIDE, CX_ZOOM_SIDE, CX_FRAMES = 1280, 1024, 3
MAX_IMAGES = TA_MAX_FRAMES + 4
ROLES = ("prior", "prior2", "target", "target2")
SIZE_KINDS = ("size", "other")

# sampling: Qwen3.6 model card, "thinking mode for precise tasks" / greedy for pointing
THINK_SAMPLING = {"temperature": 0.6, "top_p": 0.95, "top_k": 20}
PLAIN_SAMPLING = {"temperature": 0.0, "top_p": 1.0, "top_k": -1}


@dataclass
class CtxRequest(Request):
    """qp.open.qwen_vl.Request plus a per-request thinking switch and nucleus / top-k sampling."""
    thinking: bool = False
    top_p: float = 1.0
    top_k: int = -1
    tag: dict | None = None        # bookkeeping (cx: qid / role / frame / crop box); never sent to the model


def split_thinking(text: str | None) -> tuple[str, str, bool]:
    """(thinking, answer, closed): the answer is the text after the last </think>. A reply of a thinking request that
    never closes its thinking (cut at max_tokens) has no answer (closed False). Replies without any think tag are
    answers as a whole."""
    if text is None:
        return "", "", False
    t = str(text)
    if "</think>" in t:
        head, ans = t.rsplit("</think>", 1)
        return head.replace("<think>", "").strip(), ans.strip(), True
    if "<think>" in t:
        return t.split("<think>", 1)[1].strip(), "", False
    return "", t.strip(), True


# --------------------------------------------------------------------------- backends (GPU, lazy imports)

def _chat(processor, messages: list[dict], thinking: bool) -> str:
    return processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=thinking)


class CtxVLLM:
    """vLLM offline engine allowing up to `max_images` images per prompt (qwen_vl.VLLMBackend allows one) and a
    thinking switch per request. Shared images go first in each prompt, so prefix caching reuses them."""

    def __init__(self, model: str = DEFAULT_MODEL, max_model_len: int = 65536, gpu_memory_utilization: float = 0.88,
                 max_images: int = MAX_IMAGES, quantization: str | None = None, tensor_parallel_size: int = 1,
                 seed: int = 0, revision: str | None = None, **engine_kw):
        import os
        os.environ.setdefault("VLLM_WORKER_MULTIPROC_METHOD", "spawn")
        from transformers import AutoProcessor
        from vllm import LLM
        self.model = model
        self.processor = AutoProcessor.from_pretrained(model, revision=revision)
        self.llm = LLM(model=model, revision=revision, max_model_len=max_model_len,
                       gpu_memory_utilization=gpu_memory_utilization, quantization=quantization,
                       tensor_parallel_size=tensor_parallel_size, seed=seed,
                       limit_mm_per_prompt={"image": max_images, "video": 0}, **engine_kw)

    def generate(self, reqs: list[Request]) -> list[str | None]:
        from vllm import SamplingParams
        inputs, params = [], []
        for r in reqs:
            inp: dict[str, Any] = {"prompt": _chat(self.processor, r.messages, bool(getattr(r, "thinking", False)))}
            if r.images:
                inp["multi_modal_data"] = {"image": list(r.images)}
            inputs.append(inp)
            kw: dict[str, Any] = {"top_p": float(getattr(r, "top_p", 1.0))}
            if int(getattr(r, "top_k", -1)) > 0:   # "all tokens" is spelled -1 or 0 depending on the vLLM version
                kw["top_k"] = int(r.top_k)
            params.append(SamplingParams(temperature=r.temperature, max_tokens=r.max_tokens, seed=r.seed, **kw,
                                         **(_structured(r.json_schema) if r.json_schema else {})))
        outs = self.llm.generate(inputs, params, use_tqdm=False)
        return [o.outputs[0].text if o.outputs else None for o in outs]


class CtxHF:
    """transformers fallback (batch 1, slow): same prompts; None for a request that raised."""

    def __init__(self, model: str = DEFAULT_MODEL, revision: str | None = None, **_):
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor
        self.torch, self.model_id = torch, model
        self.processor = AutoProcessor.from_pretrained(model, revision=revision)
        self.model = AutoModelForImageTextToText.from_pretrained(model, revision=revision, dtype=torch.bfloat16,
                                                                 device_map="auto").eval()

    def generate(self, reqs: list[Request]) -> list[str | None]:
        out: list[str | None] = []
        for r in reqs:
            try:
                prompt = _chat(self.processor, r.messages, bool(getattr(r, "thinking", False)))
                kw = {"images": list(r.images)} if r.images else {}
                inputs = self.processor(text=[prompt], return_tensors="pt", **kw).to(self.model.device)
                gen = {"max_new_tokens": r.max_tokens, "do_sample": r.temperature > 0}
                if r.temperature > 0:
                    gen.update(temperature=r.temperature, top_p=float(getattr(r, "top_p", 1.0)))
                with self.torch.inference_mode():
                    ids = self.model.generate(**inputs, **gen)
                out.append(self.processor.decode(ids[0, inputs["input_ids"].shape[1]:], skip_special_tokens=False))
            except Exception as e:  # noqa: BLE001 - one bad request must not stop the batch
                print(f"  hf generate failed: {type(e).__name__}: {e}")
                out.append(None)
        return out


def make_backend(name: str, model: str, **kw):
    if name == "vllm":
        return CtxVLLM(model, **kw)
    if name == "hf":
        return CtxHF(model, **kw)
    raise ValueError(f"unknown backend {name!r}")


# --------------------------------------------------------------------------- ta: prompt

TA_SYSTEM = """\
You are a precise measurement annotator for QuantiPhy, a benchmark of quantitative physical reasoning from video. \
You see frames from ONE video. Each image is preceded by a label "Frame <idx> (t=<sec>s)": idx is the frame index in \
the original video and t = idx / fps is its time in seconds.

COORDINATES: every point and box you give is on a 0-1000 grid of the frame image, the same grid you use for \
grounding: x from 0 (left edge) to 1000 (right edge), y from 0 (top edge) to 1000 (bottom edge).

The video comes with one or more questions. Each question states one known physical quantity (the prior), may give \
object-to-camera distances (depth info, 3D videos only), and asks for another quantity (the target) in a stated \
unit. Every answer is (metric scale from the prior) x (a pixel measurement), so for every question you must:
1. parse it into a structured spec,
2. mark the pixel positions of the prior object and the target object(s) on the frames, so that a geometry program \
can compute the answer from your marks, and
3. give your own best estimate of the answer, derived the same way.

Ground rules
- Measure on the frames and use the prior for scale. Never answer from world knowledge about typical sizes or \
speeds: many videos are simulations or staged scenes with unusual scales. The prior is exactly true for this video, \
even when it looks implausible.
- 2D videos: the motion happens roughly in a plane facing the camera, so one metres-per-pixel scale applies to the \
whole scene. 3D videos: the scale at an object is proportional to its camera distance (pinhole camera); use the depth \
info and mark the objects on the frames at (or nearest to) the times the depth info refers to.
- Be precise: a few grid units matter on small objects.

Spec fields (for both "target" and "prior")
- kind: "size" (extent of one object: length, height, width, diameter, wingspan, thickness ...), "distance" (between \
two objects or two points, at one time), "displacement" (straight-line distance an object moves between two times), \
"path_length" (distance travelled along the path), "speed" (magnitude of velocity at a time, or averaged over a \
window), "acceleration", "camera_distance" (object-to-camera distance, usually stated in the depth info), "other".
- objects: short noun phrases naming the object(s) as they look in the video, e.g. ["bird"]; two entries for a distance.
- dimension: for a size, the measured dimension ("length", "height", "width", "diameter", ...); otherwise "".
- time: the instant in seconds the quantity refers to ("at 1.5s", "t=1.5"); "final" -> the time of the last frame; \
"initial" -> 0; null if not time-specific.
- window: [t0, t1] in seconds for averages, displacements or path lengths over a stated time range; null otherwise.
- axis: "horizontal" or "vertical" when the question or prior says so (a gravity prior is vertical); else "any".

Tracks: one per role
- "prior": the object carrying the known quantity; "target": the object asked about; "target2": the second object of \
a distance between two objects; "prior2": the second object when the prior is a distance between two objects. When \
the prior and the target are the same object still give both tracks: the prior track with motion points, the target \
track with size extents.
- Each obs is one labelled frame: {"frame": idx, "point": [x, y] or null, "extent": [[x1, y1], [x2, y2]] or null, \
"box": [x1, y1, x2, y2] or null}. Only use frame indices from the labels.
- Sizes (prior or target): first decide which segment the question means (the whole object, a part of it, a gap \
between two things, the extent of a path, or the spacing of marks), then give extent = the two end points of exactly \
that segment (nose to tail for a length, wingtip to wingtip for a wingspan, top to bottom for a height, edge to edge \
through the centre for a diameter) plus the object's box, on 3-6 frames where it is clearly visible and fully shown \
(not foreshortened or occluded).
- Motion (speed, acceleration, displacement, path length): point = one consistent reference point on the object (its \
centre, or one fixed feature) on every labelled frame where the object is visible, especially the frames around the \
asked times and window ends, AND its tight box on the same frames.
- Gravity priors ("gravity acc = 9.8 m/s^2"): the prior object is the object in free fall or projectile flight; give \
its point and box on every labelled frame while it is in flight (not after it lands or is caught).
- Distance between two objects: give point tracks for both (target and target2) on the frames at the asked time; \
use the points the distance is measured between (centres unless the question implies edges or a gap).
- camera_distance targets are read from the depth info; their tracks may be empty.
- A track for an object you already marked earlier in this answer may give the same object name (spelled \
identically) and an empty obs list: the earlier track is reused (a size of another dimension needs its own extents).

Answer
- answer: your best estimate of the target in the asked unit, from your own marks, the prior and (3D) the depth \
info; a positive number. confidence: 0-1, how sure you are that it is within 10% of the truth.

Output: ONE JSON object and nothing else after your reasoning:
{"questions": [{"qid": <int>, "target": {"kind": ..., "objects": [...], "dimension": "...", "time": <s or null>, \
"window": [t0, t1] or null, "axis": "any"}, "prior": {same fields}, "tracks": [{"role": "prior", "object": "...", \
"obs": [{"frame": <idx>, "point": [x, y], "extent": null, "box": [x1, y1, x2, y2]}, ...]}, ...], "answer": <number>, \
"confidence": <0-1>}, ...]}
Answer every question, in the order given, using its qid."""

_Q_SCHEMA = {"type": "object", "properties": {
    "kind": {"type": "string"}, "objects": {"type": "array", "items": {"type": "string"}},
    "dimension": {"type": "string"}, "time": {"anyOf": [{"type": "number"}, {"type": "null"}]},
    "window": {"anyOf": [{"type": "array", "items": {"type": "number"}}, {"type": "null"}]},
    "axis": {"type": "string"}}, "required": ["kind", "objects", "dimension", "time", "window", "axis"]}
_PT = {"anyOf": [{"type": "array", "items": {"type": "number"}}, {"type": "null"}]}
TA_SCHEMA = {"type": "object", "properties": {"questions": {"type": "array", "items": {
    "type": "object", "properties": {
        "qid": {"type": "integer"}, "target": _Q_SCHEMA, "prior": _Q_SCHEMA,
        "tracks": {"type": "array", "items": {"type": "object", "properties": {
            "role": {"type": "string", "enum": list(ROLES)}, "object": {"type": "string"},
            "obs": {"type": "array", "items": {"type": "object", "properties": {
                "frame": {"type": "integer"}, "point": _PT,
                "extent": {"anyOf": [{"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
                                     {"type": "null"}]},
                "box": _PT}, "required": ["frame", "point", "extent", "box"]}}},
            "required": ["role", "object", "obs"]}},
        "answer": {"type": "number"}, "confidence": {"type": "number"}},
    "required": ["qid", "target", "prior", "tracks", "answer", "confidence"]}}}, "required": ["questions"]}


def _rows(rows) -> list:
    return list(rows.itertuples(index=False)) if hasattr(rows, "itertuples") else list(rows)


def _question_block(r) -> str:
    depth = str(r.depth_info).strip() if isinstance(r.depth_info, str) and r.depth_info.strip() else ""
    unit = getattr(r, "target_unit", "") or ""
    return (f"Question qid={int(r.qid)}\nPrior: {str(r.prior).strip()}\n"
            f"Depth info: {depth or 'none (2D video)'}\nQuestion: {str(r.question).strip()}\n"
            f"Asked unit: {unit or 'as stated in the question (SI: m, m/s or m/s^2 if none)'}")


def ta_max_tokens(n_questions: int, thinking: bool) -> int:
    return int(min(32768, (10000 if thinking else 1500) + 2000 * max(1, n_questions)))


def ta_request(rows, n_uniform: int = TA_N_UNIFORM, max_frames: int = TA_MAX_FRAMES, max_side: int = TA_MAX_SIDE,
               thinking: bool = True, guided: bool = False, max_tokens: int = 0) -> tuple[CtxRequest, dict]:
    """One request for all questions of one video (rows: qp.data rows of one video_id) and the metadata that maps
    the reply back (claude_annotate meta format + sent_size)."""
    rs = _rows(rows)
    first = rs[0]
    path = str(first.video_path)
    fps, from_container = video_fps(first.fps, path)
    n_total, W, H = video_info(path)
    texts = [t for r in rs for t in (r.question, r.prior, r.depth_info)]
    idxs = select_frames(n_total, fps, mentioned_times(texts), n_uniform, max_frames)
    got = read_rgb(path, idxs)
    idxs = sorted(got)
    H, W = got[idxs[0]].shape[:2]
    imgs = [to_image(got[i], max_side) for i in idxs]
    w, h = imgs[0].size
    is_3d = str(first.video_type)[1:2] == "3"
    content: list[dict] = [{"type": "text", "text": (
        f"Video {first.video_id}: {'3D video with camera distances' if is_3d else '2D video'}; {W}x{H} px; "
        f"{fps:g} fps; {n_total} frames (~{n_total / fps:.2f} s). {len(idxs)} frames follow.")}]
    for i in idxs:
        content.append({"type": "text", "text": f"Frame {i} (t={i / fps:.3f}s)"})
        content.append({"type": "image"})
    blocks = "\n\n".join(_question_block(r) for r in rs)
    content.append({"type": "text", "text": f"{len(rs)} question(s) about this video:\n\n{blocks}\n\n"
                                            "Reply with the JSON object described in the instructions."})
    samp = THINK_SAMPLING if thinking else PLAIN_SAMPLING
    req = CtxRequest(messages=[{"role": "system", "content": TA_SYSTEM}, {"role": "user", "content": content}],
                     images=imgs, max_tokens=max_tokens or ta_max_tokens(len(rs), thinking), thinking=thinking,
                     temperature=samp["temperature"], top_p=samp["top_p"], top_k=samp["top_k"], seed=0,
                     json_schema=TA_SCHEMA if guided and not thinking else None)
    meta = {"video_id": str(first.video_id), "fps": fps, "fps_from_container": from_container,
            "video_type": str(first.video_type), "n_frames_total": n_total, "scale": w / W,
            "image_size": [W, H], "sent_size": [w, h], "frames": idxs,
            "questions": [{"qid": int(r.qid), "target_unit": getattr(r, "target_unit", "") or "",
                           "prior": str(r.prior), "depth_info": str(r.depth_info or "")} for r in rs],
            "prompt_version": "v1"}
    return req, meta


# --------------------------------------------------------------------------- ta: parsing

def _grid(v, n: int) -> list[float] | None:
    if isinstance(v, (list, tuple)) and len(v) == n:
        try:
            out = [float(x) for x in v]
        except (TypeError, ValueError):
            return None
        return out if all(math.isfinite(x) for x in out) else None
    return None


def _to_sent(v: list[float], w: float, h: float) -> list[float]:
    """0-1000 grid -> sent-image pixels (x, y, x, y, ...), clipped to the image."""
    return [min(max(x / 1000.0 * (w if i % 2 == 0 else h), 0.0), float(w if i % 2 == 0 else h))
            for i, x in enumerate(v)]


def _frame(x) -> int | None:
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, float) and x.is_integer():
        return int(x)
    if isinstance(x, str) and re.fullmatch(r"\s*\d+\s*", x):
        return int(x)
    return None


def grid_tracks_to_sent(tracks, sent_size, flags: list[str]) -> list[dict]:
    """Model tracks (0-1000 grid) -> claude_annotate track dicts in sent-image pixels."""
    w, h = (float(v) for v in sent_size)
    out = []
    for tr in tracks if isinstance(tracks, list) else []:
        if not isinstance(tr, dict):
            continue
        obs = []
        for o in tr.get("obs") or []:
            if not isinstance(o, dict):
                continue
            f = _frame(o.get("frame"))
            if f is None:
                continue
            pt, box = _grid(o.get("point"), 2), _grid(o.get("box"), 4)
            ext = o.get("extent")
            ext = [_grid(ext[0], 2), _grid(ext[1], 2)] if isinstance(ext, (list, tuple)) and len(ext) == 2 else None
            ext = ext if ext and all(ext) else None
            vals = (pt or []) + (box or []) + ([c for p in ext for c in p] if ext else [])
            if any(v > 1000.5 or v < -0.5 for v in vals):
                flags.append("coord_outside_grid")
            obs.append({"frame": f, "point": _to_sent(pt, w, h) if pt else None,
                        "extent": [_to_sent(ext[0], w, h), _to_sent(ext[1], w, h)] if ext else None,
                        "box": _to_sent(box, w, h) if box else None})
        out.append({"role": tr.get("role"), "object": str(tr.get("object") or ""), "obs": obs})
    return out


def _num(x) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def parse_ta(text: str | None, meta: dict, rows) -> tuple[dict[int, dict], dict]:
    """Model reply -> ({qid: {"spec", "tracks", "direct", "confidence", "flags", "spec_source"}}, info).
    Questions the reply misses get the rule spec, no tracks and no answer (flag "missing_in_reply")."""
    thinking, answer, closed = split_thinking(text)
    info = {"thinking_chars": len(thinking), "closed": closed, "answer_chars": len(answer)}
    data = extract_json(answer) if answer else None
    if not (isinstance(data, dict) and isinstance(data.get("questions"), list)) and text and '{"questions"' in str(text):
        data = extract_json(str(text)[str(text).rfind('{"questions"'):])   # tags stripped / JSON inside the thinking
        info["json_from_tail"] = True
    if isinstance(data, list):
        data = {"questions": data}
    qs = data.get("questions") if isinstance(data, dict) else None
    qs = qs if isinstance(qs, list) else []
    rs = {int(r.qid): r for r in _rows(rows)}
    by_qid, flags_v = {}, []
    for q in qs:
        if isinstance(q, dict) and _frame(q.get("qid")) in rs and _frame(q.get("qid")) not in by_qid:
            by_qid[_frame(q.get("qid"))] = q
    claude_like = {"questions": []}
    for qid, q in by_qid.items():
        fl: list[str] = []
        claude_like["questions"].append({
            "qid": qid, "spec": {"target": q.get("target") if isinstance(q.get("target"), dict) else {},
                                 "prior": q.get("prior") if isinstance(q.get("prior"), dict) else {}, "depth": []},
            "tracks": grid_tracks_to_sent(q.get("tracks"), meta["sent_size"], fl),
            "direct_answer": q.get("answer"), "confidence": q.get("confidence")})
        flags_v.append((qid, fl))
    anns = to_annotations(claude_like, meta, source=SOURCE_TA) if claude_like["questions"] else {}
    out: dict[int, dict] = {}
    for qid, r in rs.items():
        q = by_qid.get(qid)
        if q is None or qid not in anns:
            out[qid] = {"spec": rule_spec(r), "tracks": [], "direct": None, "confidence": None,
                        "flags": ["missing_in_reply"], "spec_source": "rules"}
            continue
        ann = anns[qid]
        spec, sflags = validate_spec({"target": q.get("target"), "prior": q.get("prior"),
                                      "notes": str(q.get("notes") or "")}, r)
        src = "model"
        if spec is None:
            spec, src = rule_spec(r), "rules"
        spec.depth = parse_depth(r.depth_info)
        d = _num(q.get("answer"))
        fl = sorted(set(ann.flags + sflags + dict(flags_v).get(qid, [])))
        out[qid] = {"spec": spec, "tracks": ann.tracks, "direct": d if d is not None and d > 0 else None,
                    "confidence": _num(q.get("confidence")), "flags": fl, "spec_source": src}
    info["n_answered"] = sum(1 for v in out.values() if "missing_in_reply" not in v["flags"])
    return out, info


def ta_records(video_id: str, parsed: dict[int, dict], meta: dict, model: str, reply: str | None,
               info: dict) -> dict[str, dict]:
    """{"specs": rec, "annotate": rec, "direct": rec} in run_open_vlm formats."""
    specs = {"video_id": video_id, "model": model, "questions": {
        str(q): {"spec": v["spec"].to_dict(), "flags": v["flags"], "raw": [], "attempts": 1,
                 "source": model if v["spec_source"] == "model" else "rules"} for q, v in parsed.items()}}
    thinking, answer, _ = split_thinking(reply)
    ann = {"video_id": video_id, "meta": {"video_id": video_id, "fps": meta["fps"], "image_size": meta["image_size"],
                                          "n_frames_total": meta["n_frames_total"], "frames": meta["frames"],
                                          "sent_size": meta["sent_size"], "model": model, "coord_mode": "rel1000",
                                          "source": SOURCE_TA},
           "objects": {}, "tracks": {str(q): [t.to_dict() for t in v["tracks"]] for q, v in parsed.items()},
           "flags": {str(q): v["flags"] for q, v in parsed.items()}, "info": info,
           "reply": answer[-20000:], "thinking_tail": thinking[-4000:]}
    direct = {"video_id": video_id, "model": model, "questions": {
        str(q): {"value": v["direct"], "confidence": v["confidence"]} for q, v in parsed.items()
        if v["direct"] is not None}}
    return {"specs": specs, "annotate": ann, "direct": direct}


# --------------------------------------------------------------------------- cx: items, frames, prompts

CX_PROMPT = """\
{intro}A question about the video: "{question}"
Known fact: "{prior}"
{task}
Answer with JSON only: [{{"point_2d": [x, y], "label": "{l1}"}}, {{"point_2d": [x, y], "label": "{l2}"}}] on the \
0-1000 grid of this image (x from the left edge, y from the top edge). If it is not visible in this image, answer []."""

INTRO_FULL = "This image is one frame of a video. "
INTRO_ZOOM = "This image is a zoomed-in crop of one frame of a video (the region around the marked segment). "


def cx_items(spec: QuestionSpec, row) -> list[dict]:
    """Measurements the cx stage asks for: size targets, size priors (their extents) and two-object distances."""
    items = []
    t, p = spec.target, spec.prior
    if t.kind in SIZE_KINDS and t.objects:
        items.append({"qid": int(spec.qid), "role": "target", "kind": "size", "objects": [t.objects[0]],
                      "dimension": t.dimension or "length", "time": t.time})
    elif t.kind == "distance" and len(t.objects) >= 2:
        items.append({"qid": int(spec.qid), "role": "distance", "kind": "distance", "objects": list(t.objects[:2]),
                      "dimension": "", "time": t.time})
    if p.kind in SIZE_KINDS and p.objects:
        items.append({"qid": int(spec.qid), "role": "prior", "kind": "size", "objects": [p.objects[0]],
                      "dimension": p.dimension or "length", "time": p.time})
    return items


def cx_task(item: dict) -> tuple[str, str, str]:
    """(task sentence, label 1, label 2)."""
    o = item["objects"]
    if item["kind"] == "distance":
        return (f"Point to the two points the asked distance is measured between: first on the {o[0]}, second on the "
                f"{o[1]} (their centres unless the question implies edges or a gap).", o[0], o[1])
    who = ("the known fact gives the real length of this segment" if item["role"] == "prior"
           else "the question asks for the real length of this segment")
    return (f"Mark the measurement: point to the two end points of the {item['dimension']} of the {o[0]} - exactly "
            f"the segment meant ({who}): nose to tail for a length, top to bottom for a height, side to side for a "
            f"width, edge to edge through the centre for a diameter; if the words mean a part of the object, a gap, "
            f"the extent of a path or the spacing of marks, mark exactly that.", "end 1", "end 2")


def cx_request(img, item: dict, row, zoom: bool = False) -> CtxRequest:
    task, l1, l2 = cx_task(item)
    text = CX_PROMPT.format(intro=INTRO_ZOOM if zoom else INTRO_FULL, question=str(row.question).strip(),
                            prior=str(row.prior).strip(), task=task, l1=l1, l2=l2)
    return CtxRequest(messages=[{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": text}]}],
                      images=[img], max_tokens=160, thinking=False, temperature=0.0)


def _spread(xs: list[int], k: int) -> list[int]:
    if len(xs) <= k:
        return list(xs)
    return [xs[i] for i in sorted(set(np.linspace(0, len(xs) - 1, k).round().astype(int).tolist()))]


def cx_frames(item: dict, ta_rec: dict | None, n_total: int, fps: float, k: int = CX_FRAMES) -> list[int]:
    """Frames to ask on: where the ta track of the role shows the object (extent first, then box / point), spread;
    a distance at a time -> the frame nearest that time; else k uniform frames (10%-90% of the clip)."""
    last = max(n_total - 1, 0)
    tm = item.get("time")
    if item["kind"] == "distance" and isinstance(tm, (int, float)) and math.isfinite(tm):
        return [int(min(max(round(tm * fps), 0), last))]
    role = "target" if item["role"] in ("target", "distance") else "prior"
    tracks = ((ta_rec or {}).get("tracks") or {}).get(str(item["qid"]), [])
    fr_ext, fr_any = [], []
    for t in tracks:
        if t.get("role") != role:
            continue
        for o in t.get("obs") or []:
            f = int(round(float(o.get("t", 0.0)) * fps))
            if not 0 <= f <= last:
                continue
            (fr_ext if o.get("extent") else fr_any).append(f)
    fr = sorted(set(fr_ext)) or sorted(set(fr_any))
    if item["kind"] == "distance" and fr:
        return [fr[len(fr) // 2]]
    if fr:
        return _spread(fr, k)
    n = 1 if item["kind"] == "distance" else k
    return [int(round(x)) for x in np.linspace(0.1 * last, 0.9 * last, n)] if n > 1 else [last // 2]


def two_points(text: str | None) -> list[list[float]] | None:
    """The first two points of a pointing reply (0-1000 grid), or None."""
    pts = [c["point"] for c in parse_grounding(text) if c.get("point")]
    if len(pts) < 2:
        return None
    a, b = pts[0], pts[1]
    if a == b:
        return None
    return [list(map(float, a)), list(map(float, b))]


def zoom_window(p1, p2, W: int, H: int, min_frac: float = 0.04, pad: float = 0.35,
                max_area: float = 0.5) -> tuple[int, int, int, int] | None:
    """Crop (x0, y0, x1, y1) in original pixels around a segment, or None when it would cover > max_area of the
    frame (nothing to gain). Pad = max(pad x segment span, min_frac x frame side)."""
    xs, ys = (p1[0], p2[0]), (p1[1], p2[1])
    span = max(abs(xs[1] - xs[0]), abs(ys[1] - ys[0]))
    m = max(pad * span, min_frac * max(W, H))
    x0, x1 = max(0, int(math.floor(min(xs) - m))), min(W, int(math.ceil(max(xs) + m)))
    y0, y1 = max(0, int(math.floor(min(ys) - m))), min(H, int(math.ceil(max(ys) + m)))
    if x1 - x0 < 8 or y1 - y0 < 8 or (x1 - x0) * (y1 - y0) > max_area * W * H:
        return None
    return x0, y0, x1, y1


def grid_to_orig(pt, box: tuple[int, int, int, int]) -> list[float]:
    """0-1000 grid point of an image showing `box` (x0, y0, x1, y1 in original pixels) -> original pixels."""
    x0, y0, x1, y1 = box
    return [x0 + min(max(pt[0], 0.0), 1000.0) / 1000.0 * (x1 - x0), y0 + min(max(pt[1], 0.0), 1000.0) / 1000.0 * (y1 - y0)]


def crop_image(rgb: np.ndarray, box: tuple[int, int, int, int], side: int = CX_ZOOM_SIDE):
    """The crop resized so its long side is `side` (up to 4x upsampling)."""
    import cv2
    from PIL import Image
    x0, y0, x1, y1 = box
    c = rgb[y0:y1, x0:x1]
    h, w = c.shape[:2]
    s = min(4.0, side / max(h, w))
    if abs(s - 1.0) > 1e-3:
        c = cv2.resize(c, (max(1, round(w * s)), max(1, round(h * s))),
                       interpolation=cv2.INTER_CUBIC if s > 1 else cv2.INTER_AREA)
    return Image.fromarray(np.ascontiguousarray(c))


def seg_len(p) -> float:
    return float(math.hypot(p[1][0] - p[0][0], p[1][1] - p[0][1]))


def choose_cx(full, zoom, max_ratio: float = 2.0):
    """The zoom-refined segment unless missing or > max_ratio x off the full-frame one (a different segment)."""
    if zoom is None:
        return full, "full"
    if full is None:
        return zoom, "zoom"
    a, b = seg_len(full), seg_len(zoom)
    if a > 0 and b > 0 and max(a / b, b / a) <= max_ratio:
        return zoom, "zoom"
    return full, "full_zoom_rejected"


class CXPlan:
    """The cx measurements of one video, in two passes so a runner can batch several videos per generate():
    plan = CXPlan(rows, specs, ta_rec); replies = gen(plan.requests1()); zreqs = plan.apply1(replies);
    plan.apply2(gen(zreqs)); rec = plan.record(). A failed request (reply None) marks the record "error"."""

    def __init__(self, rows, specs: dict[int, QuestionSpec], ta_rec: dict | None, frames_k: int = CX_FRAMES,
                 zoom: bool = True, max_side: int = CX_MAX_SIDE):
        rs = _rows(rows)
        first = rs[0]
        self.video_id, self.zoom = str(first.video_id), zoom
        path = str(first.video_path)
        self.fps = video_fps(first.fps, path)[0]
        self.n_total, W, H = video_info(path)
        self.by_q = {int(r.qid): r for r in rs}
        self.items, seen = [], {}
        for q, r in self.by_q.items():
            spec = specs.get(q) or rule_spec(r)
            for it in cx_items(spec, r):
                key = ("prior", it["objects"][0].casefold(), it["dimension"].casefold(), str(r.prior).strip()) \
                    if it["role"] == "prior" else None
                if key is not None and key in seen:
                    seen[key]["qids"].append(q)
                    continue
                it["qids"] = [q]
                it["frames"] = cx_frames(it, ta_rec, self.n_total, self.fps, frames_k)
                self.items.append(it)
                if key is not None:
                    seen[key] = it
        need = sorted({f for it in self.items for f in it["frames"]})
        self.rgb = read_rgb(path, need) if need else {}
        if self.rgb:
            H, W = next(iter(self.rgb.values())).shape[:2]
        self.W, self.H = W, H
        self.imgs = {f: to_image(self.rgb[f], max_side) for f in self.rgb}
        for it in self.items:
            it["frames"] = [f for f in it["frames"] if f in self.imgs]
        self.res: dict[tuple[int, int], dict] = {}
        self.failed = 0
        self._z: list[tuple[int, int, tuple]] = []

    def requests1(self) -> list[CtxRequest]:
        self._w1 = [(k, f) for k, it in enumerate(self.items) for f in it["frames"]]
        out = []
        for k, f in self._w1:
            r = cx_request(self.imgs[f], self.items[k], self.by_q[self.items[k]["qid"]])
            r.tag = {"video_id": self.video_id, "qid": self.items[k]["qid"], "role": self.items[k]["role"],
                     "frame": f, "box": [0, 0, self.W, self.H], "zoom": False}
            out.append(r)
        return out

    def apply1(self, replies: list[str | None]) -> list[CtxRequest]:
        """Store the full-frame points; return the zoom requests (empty without zoom)."""
        self.failed += sum(r is None for r in replies)
        for (k, f), text in zip(self._w1, replies):
            pts = two_points(text)
            self.res[(k, f)] = {"full": [grid_to_orig(p, (0, 0, self.W, self.H)) for p in pts] if pts else None,
                                "reply_full": text}
        zreqs, self._z = [], []
        if not self.zoom:
            return zreqs
        for (k, f), v in self.res.items():
            if v["full"] is None or self.items[k]["kind"] == "distance":
                continue
            box = zoom_window(v["full"][0], v["full"][1], self.W, self.H)
            if box is None:
                continue
            v["zoom_box"] = list(box)
            r = cx_request(crop_image(self.rgb[f], box), self.items[k], self.by_q[self.items[k]["qid"]], zoom=True)
            r.tag = {"video_id": self.video_id, "qid": self.items[k]["qid"], "role": self.items[k]["role"],
                     "frame": f, "box": list(box), "zoom": True}
            zreqs.append(r)
            self._z.append((k, f, box))
        return zreqs

    def apply2(self, replies: list[str | None]) -> None:
        self.failed += sum(r is None for r in replies)
        for (k, f, box), text in zip(self._z, replies):
            pts = two_points(text)
            self.res[(k, f)]["zoom"] = [grid_to_orig(p, box) for p in pts] if pts else None
            self.res[(k, f)]["reply_zoom"] = text

    def record(self) -> dict:
        out_items = []
        for k, it in enumerate(self.items):
            per = {}
            for f in it["frames"]:
                v = self.res.get((k, f), {})
                seg, how = choose_cx(v.get("full"), v.get("zoom"))
                per[str(f)] = {**v, "chosen": seg, "how": how}
            out_items.append({**it, "per_frame": per})
        rec = {"video_id": self.video_id, "meta": {"fps": self.fps, "image_size": [self.W, self.H],
                                                   "n_frames_total": self.n_total, "source": SOURCE_CX},
               "items": out_items}
        if self.failed:
            rec["error"] = f"{self.failed} requests failed"
        return rec


def cx_video(gen, rows, specs: dict[int, QuestionSpec], ta_rec: dict | None, **kw) -> dict:
    """All cx measurements of one video with gen(list[Request]) -> list[str | None] (two passes)."""
    plan = CXPlan(rows, specs, ta_rec, **kw)
    zreqs = plan.apply1(gen(plan.requests1()) if plan.items else [])
    plan.apply2(gen(zreqs) if zreqs else [])
    return plan.record()


def cx_tracks(cx_rec: dict | None, qid: int, fps: float) -> dict[str, list[Obs]]:
    """{role: [Obs]} from a cx record for one question: "target" / "prior" sizes as extents; a distance as point
    obs of "target" and "target2"."""
    out: dict[str, list[Obs]] = {}
    for it in (cx_rec or {}).get("items", []):
        if int(qid) not in [int(x) for x in it.get("qids") or [it.get("qid", -1)]]:
            continue
        for f, v in (it.get("per_frame") or {}).items():
            seg = v.get("chosen")
            if not seg or len(seg) != 2:
                continue
            t = int(f) / fps
            if it["kind"] == "distance":
                out.setdefault("target", []).append(Obs(t=t, point=list(seg[0])))
                out.setdefault("target2", []).append(Obs(t=t, point=list(seg[1])))
            else:
                out.setdefault(it["role"], []).append(Obs(t=t, extent=[list(seg[0]), list(seg[1])]))
    return out
