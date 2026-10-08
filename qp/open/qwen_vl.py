"""Qwen3-VL (open weights, Track B): question specs, grounding tracks and direct answers.

    from qp.open.qwen_vl import QwenVL
    vl = QwenVL("Qwen/Qwen3-VL-8B-Instruct", backend="vllm")       # or backend="hf"
    specs = vl.parse_specs(rows)                   # {qid: {"spec": QuestionSpec, "flags", "raw", ...}}
    recs = vl.annotate_videos([rows_of_one_video, ...], {qid: spec})   # {video_id: record with RoleTracks}
    answers = vl.direct_answer([rows_of_one_video, ...])            # {qid: {"reply", "value", ...}}

Every task builds backend-neutral `Request`s (HF chat messages + PIL images or one video), so the
vLLM backend (batched, prefix caching; preferred on Colab) and the transformers fallback (batch 1)
see the same prompts. torch / vllm / transformers are imported inside the backends only.

Grounding convention (QwenLM/Qwen3-VL cookbooks 2d_grounding.ipynb and spatial_understanding.ipynb,
commit 96588727): Qwen3-VL answers [{"bbox_2d": [x1, y1, x2, y2], "label": ...}] or "point_2d": [x, y]
in RELATIVE coordinates on a 0-1000 grid of the image it was shown ("changed from the absolute
coordinates used in Qwen2.5-VL"; the cookbooks map back with v / 1000 * width), so the mapping to
original pixels does not depend on resizing (coord_mode "rel1000"; "abs" = pixels of the sent image,
the Qwen2.5-VL convention).

Models (Apache-2.0 open weights; ids from the Qwen3-VL README and HF collection):
  Qwen/Qwen3-VL-8B-Instruct            default; bf16 ~17 GB: L4 24 GB, A100 40/80 GB, H100
  Qwen/Qwen3-VL-32B-Instruct           bf16 ~67 GB: A100 80 GB / H100 80 GB
  Qwen/Qwen3-VL-32B-Instruct-FP8       ~35 GB (vLLM; FP8 W8A16 Marlin kernels on A100): 80 GB cards
  Qwen/Qwen3-VL-30B-A3B-Instruct-FP8   MoE, 3B active, ~31 GB: fits A100 40 GB and is fast
On a 40 GB card the dense 32B needs 4-bit: backend "hf" with load_4bit=True (bitsandbytes NF4) or
vLLM quantization="bitsandbytes". The "-FP8" ids follow the official naming (README: "FP8 version of
the Qwen3-VL models" in the collection; example Qwen3-VL-235B-A22B-Instruct-FP8); huggingface.co was
not reachable when this was written, so confirm with huggingface_hub.model_info(...) on Colab. The repo
lists no official AWQ release for Qwen3-VL.
"""

from __future__ import annotations

import ast
import json
import math
import os
import re
from dataclasses import asdict, dataclass, field
from typing import Any

import cv2
import numpy as np

from qp import prompts
from qp.claude_annotate import mentioned_times, video_fps, video_info
from qp.data import target_unit as question_unit
from qp.parse import _ANS_RE, _UNITS, _to_float, canonical_unit, parse_answer, question_unit_full
from qp.spec import KIND_DIM, KINDS, DepthEntry, Obs, Quantity, QuestionSpec, RoleTrack

MODEL_8B = "Qwen/Qwen3-VL-8B-Instruct"
MODELS = {
    "8b": MODEL_8B,
    "32b": "Qwen/Qwen3-VL-32B-Instruct",
    "32b-fp8": "Qwen/Qwen3-VL-32B-Instruct-FP8",
    "30b-a3b": "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "30b-a3b-fp8": "Qwen/Qwen3-VL-30B-A3B-Instruct-FP8",
}
DEFAULT_MODEL = MODEL_8B
SOURCE = "qwen3vl"
FACTOR = 32                    # Qwen3-VL: patch 16 x spatial merge 2
FRAME_PIXELS = 640 * 360       # per-frame pixel budget of video inputs (direct answers)
IMAGE_MAX_SIDE = 1280          # grounding frames are sent at native size up to this long edge
AXES = ("any", "horizontal", "vertical")
ROLES = ("prior", "prior2", "target", "target2")


@dataclass
class Request:
    """One generation. `messages` are HF chat messages whose media items are placeholders
    ({"type": "image"} / {"type": "video"}) filled, in order, from `images` / `video`."""
    messages: list[dict]
    images: list = field(default_factory=list)          # PIL images
    video: tuple | None = None                          # (frames [T, H, W, 3] uint8 RGB, metadata dict)
    max_tokens: int = 128
    temperature: float = 0.0
    seed: int | None = None
    json_schema: dict | None = None                     # vLLM structured output (ignored by "hf")


# --------------------------------------------------------------------------- backends

def _structured(schema: dict) -> dict:
    """SamplingParams kwargs constraining output to `schema` (API renamed across vLLM versions)."""
    try:
        from vllm.sampling_params import StructuredOutputsParams
        return {"structured_outputs": StructuredOutputsParams(json=schema)}
    except ImportError:
        pass
    try:
        from vllm.sampling_params import GuidedDecodingParams
        return {"guided_decoding": GuidedDecodingParams(json=schema)}
    except ImportError:
        return {}


def video_kwargs(frames: np.ndarray) -> dict:
    """Processor kwargs that keep pre-sampled, pre-resized frames as they are: no frame sampling, and
    a T x H x W pixel budget equal to the input (the processor's budget is over the whole clip)."""
    px = int(np.prod(frames.shape[:3]))
    return {"do_sample_frames": False, "size": {"longest_edge": px, "shortest_edge": min(4096, px)}}


class VLLMBackend:
    """vLLM offline engine; one generate() call per request list (continuous batching, prefix
    caching: put shared media before the varying text)."""

    def __init__(self, model: str = DEFAULT_MODEL, revision: str | None = None, max_model_len: int = 16384,
                 gpu_memory_utilization: float = 0.85, quantization: str | None = None,
                 tensor_parallel_size: int = 1, seed: int = 0, **engine_kw):
        os.environ.setdefault("VLLM_WORKER_MULTIPROC_METHOD", "spawn")
        from transformers import AutoProcessor
        from vllm import LLM
        self.processor = AutoProcessor.from_pretrained(model, revision=revision)
        self.llm = LLM(model=model, revision=revision, max_model_len=max_model_len,
                       gpu_memory_utilization=gpu_memory_utilization, quantization=quantization,
                       tensor_parallel_size=tensor_parallel_size, seed=seed,
                       limit_mm_per_prompt={"image": 1, "video": 1}, **engine_kw)

    def generate(self, reqs: list[Request]) -> list[str | None]:
        from vllm import SamplingParams
        inputs, params = [], []
        for r in reqs:
            inp: dict[str, Any] = {"prompt": self.processor.apply_chat_template(
                r.messages, tokenize=False, add_generation_prompt=True)}
            mm: dict[str, Any] = {}
            if r.images:
                mm["image"] = list(r.images)
            if r.video is not None:
                mm["video"] = [r.video]
                inp["mm_processor_kwargs"] = video_kwargs(r.video[0])
            if mm:
                inp["multi_modal_data"] = mm
            inputs.append(inp)
            params.append(SamplingParams(temperature=r.temperature, max_tokens=r.max_tokens, seed=r.seed,
                                         **(_structured(r.json_schema) if r.json_schema else {})))
        outs = self.llm.generate(inputs, params)
        return [o.outputs[0].text if o.outputs else None for o in outs]


class HFBackend:
    """transformers fallback, batch size 1, greedy unless a request sets a temperature."""

    def __init__(self, model: str = DEFAULT_MODEL, revision: str | None = None, load_4bit: bool = False,
                 attn_implementation: str = "sdpa"):
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor
        kw: dict[str, Any] = dict(revision=revision, dtype=torch.bfloat16, device_map="auto",
                                  attn_implementation=attn_implementation)
        if load_4bit:
            from transformers import BitsAndBytesConfig
            kw["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16)
        self.torch = torch
        self.processor = AutoProcessor.from_pretrained(model, revision=revision)
        self.model = AutoModelForImageTextToText.from_pretrained(model, **kw).eval()

    def _one(self, r: Request) -> str:
        torch = self.torch
        prompt = self.processor.apply_chat_template(r.messages, tokenize=False, add_generation_prompt=True)
        kw: dict[str, Any] = {}
        if r.images:
            kw["images"] = list(r.images)
        if r.video is not None:
            from transformers.video_utils import VideoMetadata
            frames, meta = r.video
            kw.update(videos=[frames], video_metadata=[VideoMetadata(**meta)], **video_kwargs(frames))
        inputs = self.processor(text=[prompt], return_tensors="pt", **kw).to(self.model.device)
        gen: dict[str, Any] = {"max_new_tokens": r.max_tokens, "do_sample": r.temperature > 0}
        if r.temperature > 0:
            gen["temperature"] = r.temperature
        if r.seed is not None:
            torch.manual_seed(r.seed)
        with torch.inference_mode():
            out = self.model.generate(**inputs, **gen)
        return self.processor.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    def generate(self, reqs: list[Request]) -> list[str | None]:
        """Replies in order; None for a request that raised (e.g. CUDA OOM), so callers can tell a
        failure from an empty answer and leave it uncached."""
        out: list[str | None] = []
        for r in reqs:
            try:
                out.append(self._one(r))
            except Exception as e:  # noqa: BLE001 - one bad request must not stop the batch
                print(f"  hf generate failed: {type(e).__name__}: {e}")
                if "out of memory" in str(e).lower() and self.torch.cuda.is_available():
                    self.torch.cuda.empty_cache()
                out.append(None)
        return out


def make_backend(name: str, model: str = DEFAULT_MODEL, **kw):
    if name == "vllm":
        return VLLMBackend(model, **{k: v for k, v in kw.items() if k != "load_4bit"})
    if name == "hf":
        keep = ("revision", "load_4bit", "attn_implementation")
        return HFBackend(model, **{k: v for k, v in kw.items() if k in keep})
    raise ValueError(f"unknown backend {name!r} (expected 'vllm' or 'hf')")


# --------------------------------------------------------------------------- frames / coordinates

def smart_resize(height: int, width: int, factor: int = FACTOR, min_pixels: int = 128 * FACTOR ** 2,
                 max_pixels: int = FRAME_PIXELS) -> tuple[int, int]:
    """(h, w) divisible by `factor`, pixel count within [min_pixels, max_pixels], aspect kept
    (qwen-vl-utils smart_resize, Apache-2.0)."""
    h = max(factor, round(height / factor) * factor)
    w = max(factor, round(width / factor) * factor)
    if h * w > max_pixels:
        beta = math.sqrt(height * width / max_pixels)
        h = max(factor, math.floor(height / beta / factor) * factor)
        w = max(factor, math.floor(width / beta / factor) * factor)
    elif h * w < min_pixels:
        beta = math.sqrt(min_pixels / (height * width))
        h, w = math.ceil(height * beta / factor) * factor, math.ceil(width * beta / factor) * factor
    return h, w


def read_rgb(path: str, indices: list[int]) -> dict[int, np.ndarray]:
    """{index: RGB uint8 frame} by sequential decoding (exact for any codec)."""
    want, out = set(int(i) for i in indices), {}
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(path)
    i = 0
    while want and cap.grab():
        if i in want:
            ok, img = cap.retrieve()
            if ok:
                out[i] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            want.discard(i)
        i += 1
    cap.release()
    if not out:
        raise RuntimeError(f"no frames decoded from {path}")
    return out


def uniform_indices(n_total: int, n: int) -> list[int]:
    return sorted(set(np.linspace(0, max(n_total - 1, 0), max(1, min(n, n_total))).round().astype(int).tolist()))


def video_input(path: str, fps: float, n_frames: int = 32, max_pixels: int = FRAME_PIXELS) -> tuple[np.ndarray, dict]:
    """`n_frames` uniform frames as a Qwen3-VL video: frames [T, H, W, 3] (T even, sides multiples
    of 32 within the pixel budget, so the processor does not resize again) and metadata whose fps
    is the dataset fps, so the model's "<t seconds>" labels are idx / fps."""
    n_total = video_info(path)[0]
    got = read_rgb(path, uniform_indices(n_total, n_frames))
    idxs = sorted(got)
    if len(idxs) % 2:  # temporal patch size 2
        idxs.append(idxs[-1])
    H, W = got[idxs[0]].shape[:2]
    h, w = smart_resize(H, W, max_pixels=max_pixels)
    frames = np.stack([cv2.resize(got[i], (w, h), interpolation=cv2.INTER_AREA) for i in idxs])
    meta = {"fps": float(fps), "frames_indices": idxs, "total_num_frames": int(max(n_total, idxs[-1] + 1)),
            "duration": n_total / float(fps), "video_backend": "opencv"}
    return frames, meta


def to_image(rgb: np.ndarray, max_side: int = IMAGE_MAX_SIDE):
    from PIL import Image
    h, w = rgb.shape[:2]
    s = min(1.0, max_side / max(h, w))
    if s < 1.0:
        rgb = cv2.resize(rgb, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
    return Image.fromarray(rgb)


def to_pixels(vals, size: tuple[int, int], sent: tuple[int, int] | None = None,
              mode: str = "rel1000") -> list[float]:
    """Model x, y, x, y, ... -> ORIGINAL-frame pixels (clipped to the frame). size = (W, H) original;
    sent = (w, h) of the image the model saw (only used by mode "abs")."""
    W, H = size
    if mode == "rel1000":
        sx, sy = W / 1000.0, H / 1000.0
    elif mode == "abs":
        sw, sh = sent or size
        sx, sy = W / sw, H / sh
    else:
        raise ValueError(f"unknown coord mode {mode!r}")
    return [min(max(float(v) * (sx if i % 2 == 0 else sy), 0.0), float(W if i % 2 == 0 else H))
            for i, v in enumerate(vals)]


def box_to_pixels(box, size, sent=None, mode="rel1000") -> list[float]:
    x1, y1, x2, y2 = to_pixels(box, size, sent, mode)
    return [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]


# --------------------------------------------------------------------------- JSON from messy replies

_FENCE = re.compile(r"```(?:json|JSON)?\s*(.*?)(?:```|$)", re.DOTALL)
_THINK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _balanced(text: str, start: int) -> str | None:
    """Substring from text[start] ({ or [) to its matching bracket, respecting strings."""
    pairs, stack, in_str, esc, quote = {"{": "}", "[": "]"}, [], False, False, ""
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                in_str = False
        elif c in "\"'":
            in_str, quote = True, c
        elif c in pairs:
            stack.append(pairs[c])
        elif c in "}]":
            if not stack or c != stack.pop():
                return None
            if not stack:
                return text[start:i + 1]
    return None


def _loads(s: str):
    try:
        return json.loads(s)
    except ValueError:
        pass
    fixed = re.sub(r",\s*([}\]])", r"\1", s)                      # trailing commas
    fixed = re.sub(r"\bNone\b", "null", fixed)
    fixed = re.sub(r"\bTrue\b", "true", re.sub(r"\bFalse\b", "false", fixed))
    fixed = re.sub(r"(?<![\w.\"])-?(?:NaN|nan)\b", "null", fixed)
    fixed = re.sub(r"//[^\n\"]*$", "", fixed, flags=re.MULTILINE)  # line comments
    try:
        return json.loads(fixed)
    except ValueError:
        pass
    try:
        return ast.literal_eval(re.sub(r"\bnull\b", "None", re.sub(r"\btrue\b", "True",
                                                                    re.sub(r"\bfalse\b", "False", fixed))))
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        return None


def _truncated_list(s: str):
    """A list cut off mid-item (max_tokens): keep the complete items."""
    end = s.rfind("}")
    while end > 0:
        got = _loads(s[:end + 1] + "]")
        if isinstance(got, list):
            return got
        end = s.rfind("}", 0, end)
    return None


def extract_json(text: str | None, max_starts: int = 32):
    """First JSON value (object or list) in a model reply: fenced or bare, with prose around it
    (bracketed prose such as "[m/s]" is skipped), trailing commas, Python literals, single quotes,
    or a list truncated by max_tokens. Tries the first `max_starts` brackets. None if none."""
    if not isinstance(text, str) or not text.strip():
        return None
    text = _THINK.sub("", text).strip()
    candidates = [m.group(1).strip() for m in _FENCE.finditer(text) if m.group(1).strip()] + [text]
    for cand in candidates:
        got = _loads(cand)
        if isinstance(got, (dict, list)):
            return got
        for i in [i for i, c in enumerate(cand) if c in "{["][:max_starts]:
            sub = _balanced(cand, i)
            if sub is not None:
                got = _loads(sub)
                if isinstance(got, (dict, list)):
                    return got
            elif cand[i] == "[":
                got = _truncated_list(cand[i:])
                if got:
                    return got
    return None


# --------------------------------------------------------------------------- rule-based parsing

_NUMS = r"(\d+(?:\.\d+)?)"
_SIZE_WORDS = ("diameter", "height", "length", "width", "thickness", "wingspan", "breadth", "calibre",
               "caliber", "radius", "depth", "size", "tall", "long", "wide")
_TYPOS = {"velolicty": "velocity", "diasplacement": "displacement", "acceleraton": "acceleration",
          "centeral": "central", "？": "?", "’": "'"}
_SI_UNIT = {"L": "m", "V": "m/s", "A": "m/s^2"}


def _clean(text: str) -> str:
    text = str(text or "")
    for a, b in _TYPOS.items():
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip()


def _unit_dim(unit: str) -> str | None:
    cu = canonical_unit(unit or "")
    return _UNITS[cu][1] if cu in _UNITS else None


def _kind_from_words(text: str, dim: str | None = None) -> str:
    t = text.lower()
    if re.search(r"accel|\bacc\b|gravit|free.?fall", t):
        kind = "acceleration"
    elif re.search(r"total distance|distance travel|path length|distance covered", t):
        kind = "path_length"
    elif "displacement" in t:
        kind = "displacement"
    elif re.search(r"veloc|speed", t):
        kind = "speed"
    elif "distance" in t and "camera" in t:
        kind = "camera_distance"
    elif "distance" in t:
        kind = "distance"
    elif any(re.search(rf"\b{w}", t) for w in _SIZE_WORDS):
        kind = "size"
    else:
        kind = {"V": "speed", "A": "acceleration", "L": "size"}.get(dim or "", "other")
    if dim and KIND_DIM.get(kind) != dim:  # the unit decides the dimension
        kind = {"V": "speed", "A": "acceleration"}.get(dim, kind if KIND_DIM.get(kind) == "L" else "size")
    return kind


def _dimension(text: str) -> str:
    t = text.lower()
    for w in _SIZE_WORDS:
        if re.search(rf"\b{w}", t):
            return {"tall": "height", "long": "length", "wide": "width", "caliber": "calibre"}.get(w, w)
    return ""


def _singular_phrase(s: str) -> str:
    """'black road signs' -> 'black road sign', 'black cars in the roundabout' -> 'black car in the roundabout'."""
    m = re.search(r"\s+(?:in|on|at|near|of|with)\s+", s)
    if m:
        return _singular_phrase(s[:m.start()]) + s[m.start():]
    words = s.split()
    if words and len(words[-1]) > 3 and words[-1].lower().endswith("s") and not words[-1].lower().endswith("ss"):
        words[-1] = words[-1][:-2] if words[-1].lower().endswith(("ches", "shes", "xes")) else words[-1][:-1]
    return " ".join(words)


def _strip_article(s: str) -> str:
    s = re.sub(r"^\s*(?:the|a|an)\s+", "", s.strip(" ,.;:?"), flags=re.IGNORECASE)
    return s.strip(" ,.;:?")


_SEP = r"(?:=|:|~|≈|\bis\b|\bare\b|\b(?:of\s+)?(?:about|approx(?:imately|\.)?|around))\s*$"


def _unit_values(text: str) -> list[tuple[re.Match, float, str]]:
    """(match, value, canonical unit) of every number with a length / speed / acceleration unit."""
    out = []
    for m in _ANS_RE.finditer(text):
        cu = canonical_unit(m.group(2)) if m.group(2) else None
        if cu not in _UNITS or not re.search(r"\d", m.group(1)):
            continue
        try:
            v = abs(_to_float(m.group(1)))
        except ValueError:
            continue
        if math.isfinite(v) and v > 0:
            out.append((m, v, cu))
    return out


def _bare_value(text: str) -> tuple[int, int, float, bool] | None:
    """Unitless value (start, end, value, ambiguous) after the last "=" / "~" that does not assign a
    time ("t=1.5"); ambiguous when more non-time numbers follow it or there is no such sign."""
    signs = [m for m in re.finditer(r"[=~≈]", text)]
    sign = next((m for m in reversed(signs) if not re.search(r"\bt\s*$", text[:m.start()], re.IGNORECASE)),
                signs[-1] if signs else None)
    start = sign.end() if sign else 0
    nums = [m for m in _ANS_RE.finditer(text, start) if re.search(r"\d", m.group(1))
            and not re.search(r"\bt\s*=\s*$", text[:m.start()], re.IGNORECASE)
            and not re.match(r"\s*s(?:ec(?:ond)?s?)?\b", text[m.end():], re.IGNORECASE)]
    for k, m in enumerate(nums):
        try:
            v = abs(_to_float(m.group(1)))
        except ValueError:
            continue
        if math.isfinite(v) and v > 0:
            return m.start(), m.end(), v, sign is None or len(nums) > k + 1
    return None


def parse_prior_text(prior: str) -> dict:
    """Rule-based reading of a prior string ("billiard ball diameter = 57.2mm", "t=1.5, ball
    acceleration = 3.0m/s^2", "pedestrian walking speed ~1.1 m/s", "velocity of the soccer ball at
    1.5s = 5.21", "speed of the car = 3 m/s (t = 2 s)"): kind, value_si (unitless values are taken as
    SI), objects, dimension, time, axis. The value is the first number with a unit right after "=",
    ":", "~", "is" ... (else the first number with a unit, else a unitless one after the last "=");
    `ambiguous` when the text holds other candidate values, which are listed in `values_si` as
    (SI value, dimension or "")."""
    text = _clean(prior)
    cands = _unit_values(text)
    pick = next((c for c in cands if re.search(_SEP, text[:c[0].start()], re.IGNORECASE)), cands[0] if cands else None)
    values = [(v * _UNITS[u][0], _UNITS[u][1]) for _, v, u in cands]
    value, unit, ambiguous = None, "", True
    if pick is not None:
        m, value, unit = pick
        start, end = m.start(), m.end()
        ambiguous = len({round(v, 12) for v, _ in values}) > 1
    elif (bare := _bare_value(text)) is not None:
        start, end, value, ambiguous = bare
        values.append((value, ""))
    else:
        start = end = len(text)
    lhs = re.sub(_SEP, "", text[:start], flags=re.IGNORECASE).strip()
    rest = text[end:]
    dim = _UNITS[unit][1] if unit in _UNITS else None
    kind = _kind_from_words(lhs, dim)
    value_si = value * (_UNITS[unit][0] if unit in _UNITS else 1.0) if value is not None else None
    tpat = (r"\bt\s*=\s*" + _NUMS, r"\bat\s+(?:time\s+)?(?:t\s*=\s*)?" + _NUMS + r"\s*s\b")
    tm = next((m for part in (lhs, rest) for pat in tpat if (m := re.search(pat, part, re.IGNORECASE))), None)
    gravity = bool(re.search(r"gravit|free.?fall|\bg\s*$", lhs, re.IGNORECASE))
    name = re.sub(r"\bt\s*=\s*[\d.]+\s*s?\s*,?|\bat\s+(?:time\s+)?[\d.]+\s*s\b", " ", lhs, flags=re.IGNORECASE)
    words = r"accelerations?|acc|velocity|velocities|speed|gravity|gravitational|" + "|".join(_SIZE_WORDS)
    name = re.sub(rf"\b(?:{words})\b", " ", name, flags=re.IGNORECASE)
    name = re.sub(r"^\s*(?:of\s+)?(?:the\s+)?|\s+of\s*$", "", re.sub(r"\s+", " ", name).strip(), flags=re.IGNORECASE)
    name = re.sub(r"^(?:of\s+)", "", _strip_article(name), flags=re.IGNORECASE)
    if kind == "speed" and re.fullmatch(r"(?:walking|walk)?", name, re.IGNORECASE):
        name = "walking person"
    name = re.sub(r"\s+walking$|'s$", "", name, flags=re.IGNORECASE)
    return {"kind": kind, "value_si": value_si, "unit": unit, "objects": [] if gravity or not name else [name],
            "dimension": _dimension(lhs) if KIND_DIM.get(kind) == "L" else "",
            "time": float(tm.group(1)) if tm else None, "axis": "vertical" if gravity else "any",
            "gravity": gravity, "ambiguous": ambiguous, "values_si": values}


_OBJ_END = (r"(?=\s+at\s+(?:time\s+)?\d|\s+in\s+(?:\d|meters?|metres?|centimet|millimet|cm\b|mm\b|m\b|km|m/s)"
            r"|\s+(?:between|from)\s+\d|\s+during\b|\s*,|\s*\?|\s*$)")


def parse_question_text(question: str) -> dict:
    """Rule-based target quantity: kind, objects, dimension, time, window, axis, unit."""
    q = _clean(question)
    unit = question_unit_full(q) or question_unit(q)
    bare = re.sub(r"\([^()]*\)", " ", re.sub(r"\([^()]*\)", " ", q))  # "(the distance from ...)" is a gloss
    kind = _kind_from_words(bare, _unit_dim(unit))
    window = None
    wm = re.search(r"(?:between|from|in)\s+" + _NUMS + r"\s*s?(?:ec(?:ond)?s?)?\s+(?:and|to|-)\s+" + _NUMS + r"\s*s",
                   q, re.IGNORECASE)
    if wm and float(wm.group(2)) > float(wm.group(1)):
        window = [float(wm.group(1)), float(wm.group(2))]
    time = None
    tm = (re.search(r"\b(?:at|when)\s+(?:time\s+)?(?:t\s*=\s*)?" + _NUMS + r"\s*s\b", q, re.IGNORECASE)
          or re.search(r"\bt\s*=\s*" + _NUMS, q))
    if tm and window is None:
        time = float(tm.group(1))
    elif window is None and re.search(r"\binitial", q, re.IGNORECASE):
        time = 0.0
    elif window is None and re.search(r"\bfinal|\bat the end\b", q, re.IGNORECASE):
        time = math.inf
    axis = "horizontal" if re.search(r"horizontal", q, re.IGNORECASE) else (
        "vertical" if re.search(r"\bvertical", q, re.IGNORECASE) and kind != "size" else "any")
    objects: list[str] = []
    if kind == "distance":
        two = re.search(r"between\s+(?:the\s+)?two\s+(.+?)" + _OBJ_END, q, re.IGNORECASE)
        m = (re.search(r"between\s+(.+?)\s+and\s+(.+?)" + _OBJ_END, q, re.IGNORECASE)
             or re.search(r"from\s+(.+?)\s+to\s+(.+?)" + _OBJ_END, q, re.IGNORECASE))
        if two:  # "between the two black cars": two instances of one name
            objects = [_singular_phrase(_strip_article(two.group(1)))] * 2
        elif m:
            objects = [_strip_article(m.group(1)), _strip_article(m.group(2))]
    if not objects:
        quantity = r"(?:average\s+|initial\s+|final\s+|total\s+)?(?:veloc|speed|accel|displacement|distance|" + \
            "|".join(_SIZE_WORDS) + ")"
        m = re.search(r"([\w-]+(?:\s+[\w-]+){0,4})'s\s+" + quantity, q, re.IGNORECASE)
        name = _strip_article(re.sub(r"^(?:what|how)\s+(?:is|are|was|were)\s+", "", m.group(1), flags=re.I)) if m else ""
        if not name:
            m = re.search(r"\b(?:of|by)\s+(.+?)" + _OBJ_END, q, re.IGNORECASE)
            name = _strip_article(m.group(1)) if m else ""
        objects = [name]
    objects = [o for o in objects if o]
    return {"kind": kind, "objects": objects, "dimension": _dimension(q) if kind == "size" else "",
            "time": time, "window": window, "axis": axis, "unit": unit}


def parse_depth(depth_info: str) -> list[DepthEntry]:
    """One DepthEntry per "distance_<object>_camera = <d> m" line, with "t=<s>s" when given."""
    out = []
    for line in re.split(r"[\n;]+", str(depth_info or "")):
        m = re.search(r"distance_?(.*?)\s*[=:]\s*" + _NUMS + r"\s*(mm|cm|km|m)?\b", line, re.IGNORECASE)
        if not m:
            continue
        name = re.sub(r"_?(?:and_)?camera\s*$", "", m.group(1).strip(), flags=re.IGNORECASE)
        name = re.sub(r"\s+", " ", name.replace("_", " ")).strip()
        scale = _UNITS.get((m.group(3) or "m").lower(), (1.0, "L"))[0]
        tm = re.search(r"\bt\s*=\s*" + _NUMS, line[:m.start()] + " ")
        out.append(DepthEntry(object=name, distance_m=float(m.group(2)) * scale,
                              time=float(tm.group(1)) if tm else None))
    return out


def _is_3d(row) -> bool:
    return str(getattr(row, "video_type", ""))[1:2] == "3"


def _row_unit(row) -> str:
    """The question's unit: the full reading of its text (rates spelled out), else the row's
    target_unit column (qp.data.target_unit)."""
    u = getattr(row, "target_unit", None)
    u = u if isinstance(u, str) and u else question_unit(str(row.question))
    return question_unit_full(_clean(row.question)) or u


def answer_unit(row) -> str:
    """Unit to read a direct answer in: the question's, else (no unit stated, e.g. "What is the
    orbital diameter of the Io model?") the SI unit of the asked kind, as qp.geometry answers."""
    return _row_unit(row) or _SI_UNIT.get(KIND_DIM.get(parse_question_text(row.question)["kind"], ""), "")


def rule_spec(row) -> QuestionSpec:
    """Spec from regexes only (fallback when the model's JSON is unusable)."""
    t, p = parse_question_text(row.question), parse_prior_text(row.prior)
    moving = KIND_DIM.get(t["kind"]) != "L" or t["kind"] in ("displacement", "path_length")
    objects = p["objects"] or (t["objects"][:1] if p["gravity"] and moving else [])  # else: identified on video
    target = Quantity(kind=t["kind"], objects=t["objects"], dimension=t["dimension"], time=t["time"],
                      window=t["window"], axis=t["axis"], unit=_row_unit(row) or t["unit"])
    prior = Quantity(kind=p["kind"], objects=objects, dimension=p["dimension"], time=p["time"],
                     axis=p["axis"], value_si=p["value_si"])
    return QuestionSpec(qid=int(row.qid), target=target, prior=prior, depth=parse_depth(row.depth_info),
                        is_3d=_is_3d(row), notes="rule-based")


# --------------------------------------------------------------------------- model specs

SPEC_SYSTEM = """\
You convert one QuantiPhy question into a JSON measurement spec. A question states one known \
physical quantity of an object in a video (the prior) and asks for another quantity (the target) \
in a stated unit. Output ONLY one JSON object:
{"target": Q, "prior": Q, "notes": "..."} where Q = {"kind", "objects", "dimension", "time", \
"window", "axis", "value_si", "unit"}.
- kind: "size" (extent of one object: length, height, width, diameter, wingspan, thickness ...), \
"distance" (between two objects or points at one time), "displacement" (straight-line distance an \
object moves between two times), "path_length" (distance travelled along the path), "speed" \
(velocity magnitude at a time or averaged over a window), "acceleration", "camera_distance" \
(object-to-camera distance), "other".
- objects: short noun phrases naming the object(s) as they look in the video, e.g. ["white car"]; \
two entries for a distance. For a gravity prior ("gravity acc = 9.8m/s^2") name the object that \
falls or flies under gravity if the question reveals it, else ["falling object"].
- dimension: for a size, the measured dimension ("length", "height", "width", "diameter", ...); else "".
- time: instant in seconds ("at 1.5s", "t=1.5"); "initial" -> 0; "final" -> 1e9 (last frame); else null.
- window: [t0, t1] in seconds for averages / displacements over a stated time range; else null.
- axis: "horizontal" or "vertical" when stated (a gravity prior is "vertical"); else "any".
- value_si: prior only, the known value in SI units (m, m/s, m/s^2), e.g. 57.2mm -> 0.0572; null for the target.
- unit: target only, the unit asked for ("m", "cm", "m/s", "cm/s", "m/s^2", ...); "" for the prior.
- notes: typos or ambiguities, "" if none."""

_FEWSHOT = [
    ("speed of the bird =6m/s", "", "What is the length of the bird in meters?",
     {"target": {"kind": "size", "objects": ["bird"], "dimension": "length", "time": None, "window": None,
                 "axis": "any", "value_si": None, "unit": "m"},
      "prior": {"kind": "speed", "objects": ["bird"], "dimension": "", "time": None, "window": None,
                "axis": "any", "value_si": 6.0, "unit": ""}, "notes": ""}),
    ("t=1.0, acceleration of the cart = 2.5m/s^2", "t=1s, distance_cart_camera = 3.2m",
     "What is the cart's velocity at 2s in cm/s?",
     {"target": {"kind": "speed", "objects": ["cart"], "dimension": "", "time": 2.0, "window": None,
                 "axis": "any", "value_si": None, "unit": "cm/s"},
      "prior": {"kind": "acceleration", "objects": ["cart"], "dimension": "", "time": 1.0, "window": None,
                "axis": "any", "value_si": 2.5, "unit": ""}, "notes": ""}),
    ("width of the door = 90cm", "", "What is the distance between the cat and the dog at the end in meters?",
     {"target": {"kind": "distance", "objects": ["cat", "dog"], "dimension": "", "time": 1e9, "window": None,
                 "axis": "any", "value_si": None, "unit": "m"},
      "prior": {"kind": "size", "objects": ["door"], "dimension": "width", "time": None, "window": None,
                "axis": "any", "value_si": 0.9, "unit": ""}, "notes": ""}),
    ("gravity acc = 9.8m/s^2", "", "What is the average horizontal speed of the stone between 0.5s and 1.5s in m/s?",
     {"target": {"kind": "speed", "objects": ["stone"], "dimension": "", "time": None, "window": [0.5, 1.5],
                 "axis": "horizontal", "value_si": None, "unit": "m/s"},
      "prior": {"kind": "acceleration", "objects": ["stone"], "dimension": "", "time": None, "window": None,
                "axis": "vertical", "value_si": 9.8, "unit": ""}, "notes": ""}),
]

_NUM_OR_NULL = {"anyOf": [{"type": "number"}, {"type": "null"}]}
_Q_SCHEMA = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": list(KINDS)},
        "objects": {"type": "array", "items": {"type": "string"}},
        "dimension": {"type": "string"},
        "time": _NUM_OR_NULL,
        "window": {"anyOf": [{"type": "array", "items": {"type": "number"}}, {"type": "null"}]},
        "axis": {"type": "string", "enum": list(AXES)},
        "value_si": _NUM_OR_NULL,
        "unit": {"type": "string"},
    },
    "required": ["kind", "objects", "dimension", "time", "window", "axis", "value_si", "unit"],
}
SPEC_SCHEMA = {"type": "object", "properties": {"target": _Q_SCHEMA, "prior": _Q_SCHEMA, "notes": {"type": "string"}},
               "required": ["target", "prior", "notes"]}


def _spec_user(prior: str, depth: str, question: str) -> str:
    return (f"Prior: {str(prior).strip()}\nDepth info: {str(depth).strip() or 'none (2D video)'}\n"
            f"Question: {str(question).strip()}")


def spec_request(row, temperature: float = 0.0, seed: int | None = None, guided: bool = True) -> Request:
    msgs: list[dict] = [{"role": "system", "content": SPEC_SYSTEM}]
    for prior, depth, question, out in _FEWSHOT:
        msgs.append({"role": "user", "content": _spec_user(prior, depth, question)})
        msgs.append({"role": "assistant", "content": json.dumps(out)})
    msgs.append({"role": "user", "content": _spec_user(row.prior, row.depth_info, row.question)})
    return Request(messages=msgs, max_tokens=400, temperature=temperature, seed=seed,
                   json_schema=SPEC_SCHEMA if guided else None)


_KIND_SYN = {"velocity": "speed", "average_speed": "speed", "average speed": "speed", "length": "size",
             "height": "size", "width": "size", "diameter": "size", "extent": "size", "dimension": "size",
             "distance_travelled": "path_length", "distance_traveled": "path_length", "path": "path_length",
             "accel": "acceleration", "depth": "camera_distance"}


def _num(x) -> float | None:
    if isinstance(x, str):
        x = x.strip().lower().rstrip("s").strip()
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _time(x) -> float | None:
    if isinstance(x, str) and re.search(r"final|end|last", x, re.IGNORECASE):
        return math.inf
    if isinstance(x, str) and re.search(r"initial|start|begin", x, re.IGNORECASE):
        return 0.0
    v = _num(x)
    if v is None:
        return math.inf if isinstance(x, (int, float)) and x == math.inf else None
    return math.inf if v >= 1e6 else (v if v >= 0 else None)


def _quantity(d, flags: list[str], who: str) -> Quantity | None:
    if not isinstance(d, dict):
        return None
    kind = str(d.get("kind") or "").strip().lower().replace("-", "_")
    kind = _KIND_SYN.get(kind, kind)
    if kind not in KINDS:
        flags.append(f"{who}_kind_invalid")
        kind = ""
    objs = d.get("objects")
    objs = [objs] if isinstance(objs, str) else objs if isinstance(objs, list) else []
    window = d.get("window")
    if isinstance(window, (list, tuple)) and len(window) == 2 and all(_time(v) is not None for v in window):
        window = [float(_time(window[0])), float(_time(window[1]))]
        window = window if window[1] > window[0] and math.isfinite(window[1]) else None
    else:
        window = None
    axis = str(d.get("axis") or "any").lower()
    axis = {"x": "horizontal", "y": "vertical"}.get(axis, axis)
    return Quantity(kind=kind, objects=[str(o).strip() for o in objs if str(o).strip()],
                    dimension=str(d.get("dimension") or ""), time=_time(d.get("time")), window=window,
                    axis=axis if axis in AXES else "any", value_si=_num(d.get("value_si")),
                    unit=str(d.get("unit") or ""))


def validate_spec(parsed, row) -> tuple[QuestionSpec | None, list[str]]:
    """Model JSON -> QuestionSpec, repaired with the rule-based reading of the same text: the prior
    value from the prior string (unless the string holds several candidate values and the model
    picked one of them), depth from depth_info, the unit from the question, and kinds / objects /
    times where the model's are missing or inconsistent (each repair is flagged).
    Returns (None, flags) when the JSON has no usable target and prior (retry)."""
    flags: list[str] = []
    if not isinstance(parsed, dict):
        return None, ["no_json"]
    target, prior = _quantity(parsed.get("target"), flags, "target"), _quantity(parsed.get("prior"), flags, "prior")
    if target is None or prior is None:
        return None, flags + ["missing_target_or_prior"]
    if not target.kind and not prior.kind:
        return None, flags
    rt, rp = parse_question_text(row.question), parse_prior_text(row.prior)

    unit = _row_unit(row) or canonical_unit(target.unit) or ""
    target.unit, target.value_si = unit, None
    dim = _unit_dim(unit)
    if not target.kind or (dim and KIND_DIM.get(target.kind) != dim):
        flags.append("target_kind_from_rules")
        target.kind = rt["kind"]
    if target.kind != "camera_distance" and not target.objects:
        flags.append("target_objects_from_rules")
        target.objects = rt["objects"]
    if target.kind == "distance" and len(target.objects) < 2 and len(rt["objects"]) >= 2:
        flags.append("target_objects_from_rules")
        target.objects = rt["objects"]
    if target.kind == "distance" and len(target.objects) < 2 and rt["kind"] in ("path_length", "displacement", "size"):
        flags.append("target_kind_from_rules")   # one object: travelled / displaced / extent, not a gap
        target.kind = rt["kind"]
    if target.time is None and target.window is None and (rt["time"] is not None or rt["window"] is not None):
        flags.append("target_time_from_rules")
        target.time, target.window = rt["time"], rt["window"]
    if target.kind == "size" and not target.dimension:
        target.dimension = rt["dimension"]

    prior.unit = ""
    pdim = _UNITS[rp["unit"]][1] if rp["unit"] in _UNITS else None
    if not prior.kind or (pdim and KIND_DIM.get(prior.kind) != pdim):
        flags.append("prior_kind_from_rules")
        prior.kind = rp["kind"]
    if rp["gravity"]:
        prior.kind, prior.axis = "acceleration", "vertical"
    model_v = prior.value_si if prior.value_si is not None and prior.value_si > 0 else None
    keep = model_v is not None and rp["ambiguous"] and any(   # the model picked another value of the text
        abs(model_v - v) <= 1e-3 * v and d in ("", KIND_DIM.get(prior.kind)) for v, d in rp["values_si"])
    if rp["value_si"] is not None and not keep:
        if model_v is None or abs(model_v - rp["value_si"]) > 1e-3 * rp["value_si"]:
            flags.append("prior_value_from_text")
        prior.value_si = rp["value_si"]
    elif rp["value_si"] is None and model_v is None:
        flags.append("no_prior_value")
    if not prior.objects and rp["objects"]:
        flags.append("prior_objects_from_rules")
        prior.objects = rp["objects"]
    if prior.time is None and rp["time"] is not None:
        prior.time = rp["time"]
    spec = QuestionSpec(qid=int(row.qid), target=target, prior=prior, depth=parse_depth(row.depth_info),
                        is_3d=_is_3d(row), notes=str(parsed.get("notes") or ""))
    return spec, flags


# --------------------------------------------------------------------------- grounding

GROUND_PROMPT = "Locate the {name} in the image, output its bbox coordinates using JSON format."
GROUND_ALL_PROMPT = ('Locate every instance that belongs to the following categories: "{name}". '
                     "Report bbox coordinates in JSON format.")
EXTENT_PROMPT = ("Point to the two ends of the {dim} of the {name} in the image, output their point coordinates "
                 'in JSON format like this: [{{"point_2d": [x, y], "label": "end 1"}}, '
                 '{{"point_2d": [x, y], "label": "end 2"}}]')
IDENTIFY_PROMPT = ("Which object in this video is falling or flying through the air under gravity (free fall or "
                   "projectile motion)? Answer with a short noun phrase only, for example: red ball.")
_GENERIC = re.compile(r"^(?:|g|gravity.*|.*\bgravit.*|camera|object|objects?|falling object|object in free fall|"
                      r"free fall|projectile|unknown|none|n/?a|scene)$", re.IGNORECASE)
_BOX_RE = re.compile(r"bbox(?:_2d)?\"?\s*[:=]\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]")
_PT_RE = re.compile(r"point(?:_2d)?\"?\s*[:=]\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]")


def groundable(name: str) -> bool:
    return not _GENERIC.match(str(name or "").strip())


def _nums(v, n: int) -> list[float] | None:
    if isinstance(v, (list, tuple)) and len(v) == n and all(_num(x) is not None for x in v):
        return [float(_num(x)) for x in v]
    return None


def parse_grounding(text: str | None) -> list[dict]:
    """[{"box": [x1, y1, x2, y2] | None, "point": [x, y] | None, "label": str}] in model coordinates."""
    data = extract_json(text)
    items = data if isinstance(data, list) else [data] if isinstance(data, dict) else []
    if _nums(items, 4):
        items = [{"bbox_2d": items}]
    out = []
    for it in items:
        if isinstance(it, dict):
            box = _nums(it.get("bbox_2d", it.get("bbox", it.get("box"))), 4)
            pt = _nums(it.get("point_2d", it.get("point")), 2)
            if box or pt:
                out.append({"box": box, "point": pt, "label": str(it.get("label", ""))})
        elif _nums(it, 4):
            out.append({"box": _nums(it, 4), "point": None, "label": ""})
        elif _nums(it, 2):
            out.append({"box": None, "point": _nums(it, 2), "label": ""})
    if not out and isinstance(text, str):   # unparsable JSON: regex, skipping malformed numbers ("[-, -]")
        out = [{"box": b, "point": None, "label": ""} for m in _BOX_RE.finditer(text) if (b := _nums(m.groups(), 4))]
        out += [{"box": None, "point": p, "label": ""} for m in _PT_RE.finditer(text) if (p := _nums(m.groups(), 2))]
    return out


def _centre(c: dict) -> np.ndarray:
    return np.array([(c["box"][0] + c["box"][2]) / 2, (c["box"][1] + c["box"][3]) / 2]) if c.get("box") \
        else np.array(c["point"], float)


def pick_continuous(cands_by_frame: dict[int, list[dict]]) -> dict[int, tuple[dict, int]]:
    """One candidate per frame: the first one on the first frame, then the one nearest the previous
    pick (keeps the same instance when several objects match the name). {idx: (cand, n_cands)}."""
    out, prev = {}, None
    for idx in sorted(cands_by_frame):
        cands = cands_by_frame[idx]
        if not cands:
            continue
        c = cands[0] if prev is None else min(cands, key=lambda c: float(np.linalg.norm(_centre(c) - prev)))
        prev = _centre(c)
        out[idx] = (c, len(cands))
    return out


def annotate_frames(n_total: int, fps: float, times: list[float], n_uniform: int = 16, max_frames: int = 40,
                    offsets: tuple[float, ...] = (0.0, -0.1, 0.1, -0.2, 0.2)) -> list[int]:
    """`n_uniform` uniform frames plus frames at each mentioned time + offset (exact times first),
    up to `max_frames` in total (the Claude pipeline's selection, with the uniform frames kept)."""
    last = max(n_total - 1, 0)
    chosen = set(uniform_indices(n_total, n_uniform))
    for off in offsets:
        for t in times:
            if len(chosen) >= max_frames:
                return sorted(chosen)
            chosen.add(int(min(max(round((t + off) * fps), 0), last)))
    return sorted(chosen)


def roles_for(spec: QuestionSpec) -> list[tuple[str, str]]:
    """(role, object name) pairs to ground for one question."""
    out = []
    for role, q in (("prior", spec.prior), ("target", spec.target)):
        if q.kind == "camera_distance":
            continue
        names = [n for n in q.objects if groundable(n)]
        if names:
            out.append((role, names[0]))
        if q.kind == "distance" and len(names) > 1:
            out.append((role + "2", names[1]))
    return out


def is_gravity(spec: QuestionSpec, prior_text: str = "") -> bool:
    return spec.prior.kind == "acceleration" and bool(
        re.search(r"grav|free.?fall", prior_text or "", re.IGNORECASE)
        or any(re.search(r"grav", o, re.IGNORECASE) for o in spec.prior.objects))


_NUMBERING = re.compile(r"\s*(?:#\s*\d+|\(\d+\)|\b\d+|\bno\.\s*\d+)$", re.IGNORECASE)


def _key(name: str) -> str:
    """Object key: case/space-folded ("Black  Car 2" -> "black car 2"; "car 1" and "car 2" stay apart)."""
    return re.sub(r"\s+", " ", str(name).strip().casefold())


def _base(name: str) -> str:
    """Name without trailing numbering ("black car 2" -> "black car"): decides whether a quantity's
    two objects are two instances of one name."""
    k = re.sub(r"\s+", " ", str(name).strip())
    return _NUMBERING.sub("", k) or k


def pick_pair(cands_by_frame: dict[int, list[dict]], k: int = 6) -> tuple[dict, dict]:
    """Two instances of one name ("the two black cars"): from the first frame with two candidates
    (A = leftmost), each frame assigns the two candidates nearest the previous A / B positions."""
    a, b, pa, pb = {}, {}, None, None
    for idx in sorted(cands_by_frame):
        cands = cands_by_frame[idx][:k]
        if pa is None:
            if len(cands) < 2:
                continue
            ca, cb = sorted(cands[:2], key=lambda c: _centre(c)[0])
        elif len(cands) >= 2:
            ca, cb = min(((x, y) for x in cands for y in cands if x is not y),
                         key=lambda xy: float(np.linalg.norm(_centre(xy[0]) - pa) + np.linalg.norm(_centre(xy[1]) - pb)))
        elif cands:
            c = cands[0]
            if np.linalg.norm(_centre(c) - pa) <= np.linalg.norm(_centre(c) - pb):
                a[idx], pa = (c, 1), _centre(c)
            else:
                b[idx], pb = (c, 1), _centre(c)
            continue
        else:
            continue
        a[idx], b[idx], pa, pb = (ca, len(cands)), (cb, len(cands)), _centre(ca), _centre(cb)
    return a, b


def _ground_request(img, name: str, every: bool = False) -> Request:
    text = (GROUND_ALL_PROMPT if every else GROUND_PROMPT).format(name=name)
    return Request(messages=[{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": text}]}],
                   images=[img], max_tokens=384 if every else 256)


def _extent_request(img, name: str, dim: str) -> Request:
    return Request(messages=[{"role": "user", "content": [
        {"type": "image"}, {"type": "text", "text": EXTENT_PROMPT.format(name=name, dim=dim or "length")}]}],
        images=[img], max_tokens=128)


# --------------------------------------------------------------------------- runner

def direct_request(row, frames: np.ndarray, meta: dict, duration_s: float, max_tokens: int = 64) -> Request:
    """Official starter-kit zero-shot prompt (qp.prompts "direct": system prompt, clip sentence with
    fps / duration / frame count, prior + depth context, question, closing instruction)."""
    system, text = prompts.build("direct", row, len(set(meta["frames_indices"])), duration_s)
    return Request(messages=[{"role": "system", "content": system},
                             {"role": "user", "content": [{"type": "video"}, {"type": "text", "text": text}]}],
                   video=(frames, meta), max_tokens=max_tokens)


def _rows(rows) -> list:
    return list(rows.itertuples(index=False)) if hasattr(rows, "itertuples") else list(rows)


class QwenVL:
    """Qwen3-VL tasks over one backend. `backend` is "vllm", "hf" or any object with
    generate(list[Request]) -> list[str] (tests use a fake); real backends load lazily."""

    def __init__(self, model: str = DEFAULT_MODEL, backend="vllm", coord_mode: str = "rel1000",
                 source: str = SOURCE, **backend_kw):
        self.model, self.coord_mode, self.source = MODELS.get(model, model), coord_mode, source
        self._be = None if isinstance(backend, str) else backend
        self._backend_name, self._backend_kw = backend, backend_kw

    @property
    def backend(self):
        if self._be is None:
            self._be = make_backend(self._backend_name, self.model, **self._backend_kw)
        return self._be

    def generate(self, reqs: list[Request]) -> list[str | None]:
        """Backend replies; None marks a failed request (never cached as an answer)."""
        return list(self.backend.generate(reqs)) if reqs else []

    # ----------------------------------------------------------------- (a) specs
    def parse_specs(self, rows, retries: int = 2, guided: bool = True) -> dict[int, dict]:
        """{qid: {"spec", "flags", "raw", "attempts", "source"}}; greedy first, then `retries` sampled
        attempts for replies without usable JSON, then the rule-based spec (flag "rule_fallback").
        When every attempt failed in the backend (reply None) the rule spec also carries "error", so
        callers can use it now but do not cache it."""
        pending, raw, out = _rows(rows), {}, {}
        for attempt in range(retries + 1):
            if not pending:
                break
            reqs = [spec_request(r, 0.0 if attempt == 0 else 0.7, attempt or None, guided) for r in pending]
            nxt = []
            for r, text in zip(pending, self.generate(reqs)):
                qid = int(r.qid)
                raw.setdefault(qid, []).append(text)
                spec, flags = validate_spec(extract_json(text), r)
                if spec is None:
                    nxt.append(r)
                else:
                    out[qid] = {"spec": spec, "flags": flags, "raw": raw[qid], "attempts": attempt + 1,
                                "source": self.model}
            pending = nxt
        for r in pending:
            qid = int(r.qid)
            out[qid] = {"spec": rule_spec(r), "flags": ["rule_fallback"], "raw": raw.get(qid, []),
                        "attempts": retries + 1, "source": "rules"}
            if all(t is None for t in out[qid]["raw"]):
                out[qid]["error"] = "generation failed"
        return out

    # ----------------------------------------------------------------- (b) tracks
    def _identify(self, groups: list, specs: dict[int, QuestionSpec],
                  n_frames: int = 8) -> tuple[dict[str, str], set[str]]:
        """({video_id: name of the object under gravity}, video ids whose request failed) for videos
        with a gravity prior and no groundable prior object."""
        need = []
        for rows in groups:
            rs = _rows(rows)
            if any(int(r.qid) in specs and is_gravity(specs[int(r.qid)], r.prior)
                   and not any(groundable(o) for o in specs[int(r.qid)].prior.objects) for r in rs):
                need.append(rs[0])
        reqs = []
        for r in need:
            frames, meta = video_input(r.video_path, video_fps(r.fps, r.video_path)[0], n_frames, 448 * 448)
            reqs.append(Request(messages=[{"role": "user", "content": [
                {"type": "video"}, {"type": "text", "text": IDENTIFY_PROMPT}]}], video=(frames, meta), max_tokens=16))
        out, failed = {}, set()
        for r, text in zip(need, self.generate(reqs)):
            if text is None:
                failed.add(str(r.video_id))
                continue
            lines = str(text).strip().splitlines()
            name = re.sub(r"^(?:the|a|an)\s+", "", lines[0] if lines else "", flags=re.IGNORECASE).strip(" .\"'")
            if name and groundable(name) and len(name) < 60:
                out[str(r.video_id)] = name
        return out, failed

    def annotate_videos(self, groups: list, specs: dict[int, QuestionSpec], n_uniform: int = 16,
                        max_frames: int = 40, extents: bool = False, n_extent: int = 6) -> dict[str, dict]:
        """Ground every object named in the specs of each video on its selected frames (one request
        per frame x object, shared image first so prefix caching reuses it) and build RoleTracks per
        question. Returns {video_id: record} with meta, per-object obs + raw replies, tracks by qid;
        a video with a failed request (backend reply None) gets {"video_id", "error"} only, so it is
        not cached and is retried."""
        found, failed = self._identify(groups, specs)
        plans, reqs, where = [], [], []
        for rows in groups:
            rs = _rows(rows)
            first = rs[0]
            vid, path = str(first.video_id), str(first.video_path)
            fps = video_fps(first.fps, path)[0]   # dataset fps; the container's if missing (as Track A)
            n_total, W, H = video_info(path)
            texts = [t for r in rs for t in (r.question, r.prior, r.depth_info)]
            idxs = annotate_frames(n_total, fps, mentioned_times(texts), n_uniform, max_frames)
            frames = read_rgb(path, idxs)
            idxs = sorted(frames)
            H, W = frames[idxs[0]].shape[:2]
            roles, objects, dims = {}, {}, {}   # roles: qid -> [(role, name, obs key)]
            for r in rs:
                spec = specs.get(int(r.qid))
                if spec is None:
                    continue
                pairs = roles_for(spec)
                if vid in found and is_gravity(spec, r.prior) and not any(p[0] == "prior" for p in pairs):
                    pairs.append(("prior", found[vid]))
                keyed = dict(pairs)
                roles[int(r.qid)] = []
                for role, name in pairs:
                    twin = keyed.get(role[:-1] if role.endswith("2") else role + "2")
                    if twin is not None and _key(_base(twin)) == _key(_base(name)):   # two instances of one name
                        k = _key(_base(name)) + " [pair]"
                        objects.setdefault(k, (_base(name), True))
                        roles[int(r.qid)].append((role, name, k + ("#2" if role.endswith("2") else "#1")))
                        continue
                    k = _key(name)
                    objects.setdefault(k, (name, False))
                    roles[int(r.qid)].append((role, name, k))
                    q = spec.prior if role.startswith("prior") else spec.target
                    if q.kind == "size":
                        dims.setdefault(k, q.dimension or "length")
            imgs = {i: to_image(frames[i]) for i in idxs}
            ext_idx = set(uniform_indices(len(idxs), n_extent))
            for k, (name, every) in objects.items():
                for i in idxs:
                    reqs.append(_ground_request(imgs[i], name, every))
                    where.append((len(plans), k, i, "box"))
                    if extents and k in dims and idxs.index(i) in ext_idx:
                        reqs.append(_extent_request(imgs[i], name, dims[k]))
                        where.append((len(plans), k, i, "extent"))
            plans.append({"rows": rs, "vid": vid, "fps": fps, "size": (W, H), "n_total": n_total, "idxs": idxs,
                          "roles": roles, "objects": objects,
                          "sent": {i: imgs[i].size for i in idxs}})
        replies = self.generate(reqs)
        got: dict[tuple[int, str], dict] = {}
        n_failed = [0] * len(plans)
        for (p, k, i, what), text in zip(where, replies):
            if text is None:
                n_failed[p] += 1
            got.setdefault((p, k), {"box": {}, "extent": {}})[what][i] = text
        out = {}
        for n, plan in enumerate(plans):
            vid, bad = plan["vid"], n_failed[n] + (plan["vid"] in failed)
            total = sum(w[0] == n for w in where) + (vid in failed)
            out[vid] = ({"video_id": vid, "error": f"{bad} of {total} requests failed"} if bad
                        else self._record(n, plan, got, found.get(vid)))
        return out

    def _record(self, n: int, plan: dict, got: dict, identified: str | None) -> dict:
        size, fps = plan["size"], plan["fps"]
        objs = {}

        def to_obs(picked: dict) -> dict[int, Obs]:
            out = {}
            for i, (c, n_c) in picked.items():
                sent = plan["sent"][i]
                out[i] = Obs(t=i / fps, box=box_to_pixels(c["box"], size, sent, self.coord_mode) if c["box"] else None,
                             point=to_pixels(c["point"], size, sent, self.coord_mode) if c["point"] and not c["box"]
                             else None, score=round(1.0 / n_c, 3))
            return out

        for k, (name, every) in plan["objects"].items():
            rep = got.get((n, k), {"box": {}, "extent": {}})
            cands = {i: parse_grounding(t) for i, t in rep["box"].items()}
            raw = {"replies": {str(i): t for i, t in rep["box"].items()},
                   "extent_replies": {str(i): t for i, t in rep["extent"].items()}}
            if every:
                for tag, picked in zip(("#1", "#2"), pick_pair(cands)):
                    obs = to_obs(picked)
                    objs[k + tag] = {"name": name, "obs": [asdict(obs[i]) for i in sorted(obs)], **raw}
                continue
            obs = to_obs(pick_continuous(cands))
            for i, text in rep["extent"].items():
                pts = [c["point"] for c in parse_grounding(text) if c["point"]]
                if len(pts) >= 2:
                    ext = [to_pixels(pts[0], size, plan["sent"][i], self.coord_mode),
                           to_pixels(pts[1], size, plan["sent"][i], self.coord_mode)]
                    obs.setdefault(i, Obs(t=i / fps)).extent = ext
            objs[k] = {"name": name, "obs": [asdict(obs[i]) for i in sorted(obs)], **raw}
        tracks = {}
        for qid, pairs in plan["roles"].items():
            tracks[str(qid)] = [RoleTrack(role=role, object=name, source=self.source,
                                          obs=[Obs(**o) for o in objs[k]["obs"]]).to_dict()
                                for role, name, k in pairs]
        meta = {"video_id": plan["vid"], "fps": fps, "image_size": list(size), "n_frames_total": plan["n_total"],
                "frames": plan["idxs"], "model": self.model, "coord_mode": self.coord_mode}
        return {"video_id": plan["vid"], "meta": meta, "identified_prior_object": identified,
                "objects": objs, "tracks": tracks}

    # ----------------------------------------------------------------- (c) direct
    def direct_answer(self, groups: list, n_frames: int = 32, max_pixels: int = FRAME_PIXELS,
                      max_tokens: int = 64) -> dict[int, dict]:
        """Zero-shot answers (official starter-kit prompt + clip sentence), one request per question
        with the video's uniform frames; {qid: {"reply", "value", "n_frames", "frames"}}, plus "error"
        for a failed request (not cached). A question without a unit is read in SI (answer_unit)."""
        reqs, rows = [], []
        for g in groups:
            rs = _rows(g)
            path = str(rs[0].video_path)
            fps = video_fps(rs[0].fps, path)[0]
            frames, meta = video_input(path, fps, n_frames, max_pixels)
            duration = video_info(path)[0] / fps
            for r in rs:
                reqs.append(direct_request(r, frames, meta, duration, max_tokens))
                rows.append((r, meta))
        out = {}
        for (r, meta), text in zip(rows, self.generate(reqs)):
            v = parse_answer(text, answer_unit(r))
            out[int(r.qid)] = {"reply": text, "value": v if math.isfinite(v) and v > 0 else None,
                               "n_frames": len(set(meta["frames_indices"])), "frames": sorted(set(meta["frames_indices"])),
                               "model": self.model}
            if text is None:
                out[int(r.qid)]["error"] = "generation failed"
        return out


def tracks_from_record(rec: dict, qid: int) -> list[RoleTrack]:
    return [RoleTrack.from_dict(t) for t in rec.get("tracks", {}).get(str(qid), [])]
