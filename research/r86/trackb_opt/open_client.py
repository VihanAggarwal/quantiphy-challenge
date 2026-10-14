"""Anthropic-Messages-shaped client backed by an OpenAI-compatible server (vLLM / SGLang / any hosted
open-weight endpoint), so scripts/run_claude.py runs the Track A v1 pipeline UNCHANGED on an open model.

    vllm serve Qwen/Qwen3.8-27B-FP8 --max-model-len 131072 --reasoning-parser qwen3 \
        --limit-mm-per-prompt '{"image": 40}' --port 8000
    OPEN_BASE_URL=http://localhost:8000/v1 OPEN_MODEL=Qwen/Qwen3.8-27B-FP8 \
        python research/r86/trackb_opt/run_open_pipeline.py --split val --name val_q38_v1 --effort medium

What it does (research prototype; not wired into the repo code):
- converts ca.build_request params (system blocks, text + base64 image blocks, output_config json_schema,
  max_tokens, effort) into one chat.completions request with response_format json_schema;
- COORDS="rel1000" (default for Qwen-family ids): appends one instruction asking for 0-1000 normalized
  coordinates (the native grounding convention of Qwen3-VL / Qwen3.5+) and converts every point /
  extent / box in the reply back to pixels of the sent frames before the repo parser sees it;
- returns an object with the attributes run_claude.message_record / budget.usage_dict read
  (id, model, stop_reason, content[].type/.text, usage.input_tokens/output_tokens/cache_*).
Nothing here calls a paid API unless OPEN_BASE_URL points at one.
"""
from __future__ import annotations

import base64
import contextlib
import json
import os
import uuid
from dataclasses import dataclass, field

import cv2
import numpy as np

REL1000_NOTE = (
    "\n\nCOORDINATES: write every point, extent end point and box in normalized image coordinates from 0 to "
    "1000 (x = 1000 * pixel_x / image_width, y = 1000 * pixel_y / image_height) of the frame it refers to; "
    "boxes are [x1, y1, x2, y2] in the same normalized units.")
EFFORT_MAP = {"low": "low", "medium": "medium", "high": "medium", "xhigh": "xhigh", "max": "xhigh"}


@dataclass
class _Block:
    text: str
    type: str = "text"


@dataclass
class _Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation: dict = field(default_factory=dict)


@dataclass
class _Message:
    id: str
    model: str
    stop_reason: str
    content: list
    usage: _Usage
    stop_details: object = None


def _image_size(b64: str) -> tuple[int, int]:
    img = cv2.imdecode(np.frombuffer(base64.b64decode(b64), np.uint8), cv2.IMREAD_UNCHANGED)
    return int(img.shape[1]), int(img.shape[0])


def _scale_xy(p, sx: float, sy: float):
    if isinstance(p, (list, tuple)) and len(p) == 2 and all(isinstance(v, (int, float)) for v in p):
        return [p[0] * sx, p[1] * sy]
    return p


def rel1000_to_pixels(parsed: dict, width: int, height: int) -> dict:
    """In place: every obs point / extent / box from 0-1000 normalized to sent-frame pixels."""
    sx, sy = width / 1000.0, height / 1000.0
    for q in parsed.get("questions") or []:
        for tr in (q.get("tracks") or []) if isinstance(q, dict) else []:
            for o in (tr.get("obs") or []) if isinstance(tr, dict) else []:
                if not isinstance(o, dict):
                    continue
                o["point"] = _scale_xy(o.get("point"), sx, sy)
                ext = o.get("extent")
                if isinstance(ext, list):
                    o["extent"] = [_scale_xy(e, sx, sy) for e in ext]
                box = o.get("box")
                if isinstance(box, list) and len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
                    o["box"] = [box[0] * sx, box[1] * sy, box[2] * sx, box[3] * sy]
    return parsed


def to_openai(params: dict, coords: str, effort_style: str = "chat_template") -> tuple[dict, tuple[int, int]]:
    """chat.completions kwargs from Anthropic Messages params; also the sent frame size (w, h)."""
    system = "".join(b["text"] for b in params["system"]) if isinstance(params["system"], list) else params["system"]
    if coords == "rel1000":
        system += REL1000_NOTE
    content, size = [], None
    for b in params["messages"][0]["content"]:
        if b["type"] == "text":
            content.append({"type": "text", "text": b["text"]})
        elif b["type"] == "image":
            data = b["source"]["data"]
            size = size or _image_size(data)
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{data}"}})
    oc = params.get("output_config") or {}
    schema = (oc.get("format") or {}).get("schema")
    effort = EFFORT_MAP.get(oc.get("effort", "medium"), "medium")
    kw = {"messages": [{"role": "system", "content": system}, {"role": "user", "content": content}],
          "max_tokens": int(params["max_tokens"]), "temperature": 1.0, "top_p": 0.95}
    extra = {"top_k": 20}
    if effort_style == "chat_template":          # vLLM/SGLang serving Qwen3.8: template kwargs
        extra["chat_template_kwargs"] = {"enable_thinking": True, "reasoning_effort": effort}
    elif effort_style == "openai":               # hosted endpoints that accept reasoning_effort
        kw["reasoning_effort"] = effort
    if schema is not None:
        kw["response_format"] = {"type": "json_schema", "json_schema": {"name": "answers", "schema": schema}}
    kw["extra_body"] = extra
    return kw, size or (0, 0)


class _Messages:
    def __init__(self, outer: "OpenCompatClient"):
        self.o = outer

    def create(self, **params) -> _Message:
        return self.o._call(params)

    @contextlib.contextmanager
    def stream(self, **params):
        msg = self.o._call(params)

        class _S:
            request_id = msg.id

            def get_final_message(self_inner):
                return msg
        yield _S()

    def count_tokens(self, **params):   # run_claude --local-estimate avoids this
        raise NotImplementedError("use --local-estimate")


class OpenCompatClient:
    def __init__(self, base_url: str | None = None, model: str | None = None, coords: str = "auto",
                 effort_style: str = "chat_template", api_key: str | None = None, oa_client=None):
        self.model = model or os.environ["OPEN_MODEL"]
        self.coords = coords if coords != "auto" else ("rel1000" if "qwen" in self.model.lower() else "pixel")
        self.effort_style = effort_style
        if oa_client is None:
            import openai
            oa_client = openai.OpenAI(base_url=base_url or os.environ["OPEN_BASE_URL"],
                                      api_key=api_key or os.environ.get("OPEN_API_KEY", "EMPTY"), timeout=3600)
        self._oa = oa_client
        self.messages = _Messages(self)

    def _call(self, params: dict) -> _Message:
        kw, (w, h) = to_openai(params, self.coords, self.effort_style)
        r = self._oa.chat.completions.create(model=self.model, **kw)
        ch = r.choices[0]
        text = ch.message.content or ""
        if self.coords == "rel1000" and w and h:
            from qp.claude_annotate import parse_json
            parsed = parse_json(text)
            if isinstance(parsed, dict):
                text = json.dumps(rel1000_to_pixels(parsed, w, h))
        stop = {"length": "max_tokens"}.get(ch.finish_reason, "end_turn")
        u = getattr(r, "usage", None)
        usage = _Usage(input_tokens=int(getattr(u, "prompt_tokens", 0) or 0),
                       output_tokens=int(getattr(u, "completion_tokens", 0) or 0))
        return _Message(id=getattr(r, "id", None) or f"open-{uuid.uuid4().hex[:12]}", model=self.model,
                        stop_reason=stop, content=[_Block(text=text)], usage=usage)
