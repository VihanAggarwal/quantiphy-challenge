"""Code-as-World-VL-9B direct answers with the authors' QuantiPhy recipe (open weights, Track B).

    from qp.open.caw import CAW
    caw = CAW()                                    # vLLM, as the authors run it; backend="hf" = fallback
    answers = caw.direct_answer([rows_of_one_video, ...])     # {qid: {"reply", "value", ...}}

Adapted from MirroS-Lab/Code-as-World (https://github.com/MirroS-Lab/Code-as-World, commit 1353bf07,
code_as_world/evaluation.py and templates/quantiphy_video.jinja), Apache License 2.0. Changed: the text
side is re-implemented without jinja2 / vLLM imports; each video is read once and reused for its
questions; replies are parsed with qp.parse.parse_answer (unit conversion) next to the authors'
first-number parser; a second short-clip retry (see read_video); an optional transformers fallback
whose token layout follows kuotunyu/quantiphy-geo-vlm methods/caw (MIT). See THIRD_PARTY_NOTICES.md.

The authors' recipe (vLLM 0.19.1, transformers 5.11.0, qwen-vl-utils 0.0.14, decord 0.6.0):
  system prompt  the starter-kit zero-shot prompt joined into one line (SYSTEM_PROMPT)
  user turn      [video] " Given that <prior>. [depth sentence] <question>\\n\\nPlease answer ... needed."
  chat template  the checkpoint's (== their qwen3_5_no_think.jinja; sha256 checked), thinking off
  video          fetch_video with decord, nframes 16, min_pixels 0, max_pixels 262144; a clip shorter
                 than 16 frames is retried with its length; timestamps from the dataset fps
  decoding       bf16, seed 1, temperature 0.01, top_p 0.001 (= greedy), at most 512 new tokens,
                 max_model_len 4608, logit bias -100 on <|image_pad|> / <|video_pad|>
Colab: pip install "vllm==0.19.1" "transformers==5.11.0" "qwen-vl-utils==0.0.14" "decord==0.6.0"
"""

from __future__ import annotations

import hashlib
import math
import os
import re
from typing import Any

from qp.parse import parse_answer

AUTHORS_REPO = "https://github.com/MirroS-Lab/Code-as-World"
AUTHORS_COMMIT = "1353bf07d24e5463caff92ce23ffd34d03984831"
MODEL_ID = "MirroS-Lab/Code-as-World-VL-9B"        # Apache-2.0, fine-tuned from Qwen/Qwen3.5-9B
MODEL_REVISION = "46b111c53f5680eb12c63a7391e5c690d1e14ab1"  # pinned by kuotunyu/quantiphy-geo-vlm
SOURCE = "caw9b"

# evaluation.py L24-30
SYSTEM_PROMPT = (
    "You are an expert video analyst specializing in physics measurements. "
    "Analyze the video frames carefully and provide ONLY the numerical answer with units. "
    "No explanation or reasoning needed. Format your response as: [value] [unit]. "
    "Example: 2.5 cm. Be as accurate as possible with measurements and calculations. "
    "Please give me an estimated answer even if you are not sure."
)
DEPTH_PREFIX = ("Additionally, you have the following information about the distance between the objects "
                "in the video and the shooting camera:")                                  # L69-72
ANSWER_SUFFIX = "\n\nPlease answer the question with numbers and units ONLY. No explanation needed."  # .jinja
CHAT_TEMPLATE_SHA256 = "22e67fd2f9b2fc41a36bc509c7aa87a96963dd76e7eb84977d907672d540355b"  # qwen3_5_no_think.jinja
MAX_PROMPT_LENGTH, MAX_RESPONSE_LENGTH = 4096, 512                                         # L37-57
MAX_MODEL_LEN = MAX_PROMPT_LENGTH + MAX_RESPONSE_LENGTH
VIDEO_NFRAMES, VIDEO_TIMESTAMP_FPS, VIDEO_FPS = 16, 24.0, 2.0
MIN_PIXELS, MAX_PIXELS, SEED = 0, 262144, 1
SAMPLING_CONFIG = {"temperature": 0.01, "top_p": 0.001, "top_k": -1, "min_p": 0.0, "presence_penalty": 0.0,
                   "repetition_penalty": 1.0, "max_tokens": MAX_RESPONSE_LENGTH, "n": 1}
ENGINE_CONFIG = {"dtype": "bfloat16", "seed": SEED, "max_model_len": MAX_MODEL_LEN, "tensor_parallel_size": 1,
                 "max_num_batched_tokens": 8192, "max_num_seqs": 128, "enforce_eager": False,
                 "disable_custom_all_reduce": True, "enable_chunked_prefill": True, "mm_processor_cache_gb": 0,
                 "trust_remote_code": True, "skip_tokenizer_init": False}
NUMBER_PATTERN = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")                              # L60
NFRAMES_INTERVAL_PATTERN = re.compile(r"nframes should in interval \[(\d+), (\d+)\], but got (\d+)")
_GIVEN_THAT_RE_TEMPLATE = r"^\s*Given\s+that\s+{}\s*[,.;:]\s*"                                # L68
_META_KEYS = {"total_num_frames", "fps", "width", "height", "duration", "video_backend", "frames_indices"}
VIDEO_PLACEHOLDER = "<|vision_start|><|video_pad|><|vision_end|>"


# --------------------------------------------------------------------------- text side (CPU)

def clean_text(value: Any) -> str:
    """_clean_text: None / 'nan' / 'none' -> ''."""
    text = "" if value is None else str(value).strip()
    return "" if text.lower() in {"nan", "none"} else text


def positive_float(value: Any) -> float | None:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def normalise_question(value: Any) -> str:
    q = clean_text(value).replace("？", "?")
    return q if not q or q[-1] in ".!?" else q + "?"


def content(row) -> str:
    """_content_from_record: 'Given that <prior>. [depth sentence] <question>'."""
    prior, question = clean_text(row.prior), clean_text(row.question)
    if prior and question:
        stripped = re.sub(_GIVEN_THAT_RE_TEMPLATE.format(re.escape(prior)), "", question, count=1,
                          flags=re.IGNORECASE).strip()
        if stripped != question and stripped[:1].islower():
            stripped = stripped[:1].upper() + stripped[1:]
        question = stripped
    question = normalise_question(question)
    parts = [f"Given that {prior}."] if prior else []
    depth = clean_text(getattr(row, "depth_info", ""))
    if depth:
        parts.append(f"{DEPTH_PREFIX} {depth}")
    prefix = " ".join(parts).rstrip()
    if prefix and prefix[-1] not in ".!?":
        prefix += "."
    return f"{prefix} {question}".strip() if prefix else question


def format_prompt(row) -> str:
    """templates/quantiphy_video.jinja after .strip(): '<video> {{ content | trim }}' + the closing line."""
    return f"<video> {content(row).strip()}{ANSWER_SUFFIX}"


def build_messages(row) -> list[dict]:
    """_build_prompt_ids messages: system string + [video, text] user turn (_message_content)."""
    parts: list[dict] = []
    for i, text in enumerate(format_prompt(row).split("<video>")):
        if i:
            parts.append({"type": "video"})
        if text:
            parts.append({"type": "text", "text": text})
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": parts}]


def strip_answer_tags(value: Any) -> str:
    text = str(value or "")
    m = re.search(r"<answer>(.*?)</answer>", text, flags=re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def parse_prediction(value: Any) -> float | None:
    """The authors' parser (_parse_prediction): first number, no unit handling."""
    found = NUMBER_PATTERN.findall(strip_answer_tags(value))
    try:
        return float(found[0]) if found else None
    except ValueError:
        return None


def parse(reply: str | None, unit: str) -> dict:
    """value: qp.parse.parse_answer (converts e.g. '150 cm' for a question in m), else |authors' number|;
    None when neither gives a finite non-zero number."""
    ours, authors = parse_answer(strip_answer_tags(reply), unit), parse_prediction(reply)
    value = ours if math.isfinite(ours) and ours > 0 else (
        abs(authors) if authors is not None and math.isfinite(authors) and authors != 0 else None)
    return {"value": value, "authors_value": authors, "parse_answer": ours if math.isfinite(ours) else None}


def retry_nframes(message: str) -> int | None:
    """_process_video's retry: frame count to ask for after a too-short-clip ValueError, or None."""
    m = NFRAMES_INTERVAL_PATTERN.search(message)
    if m is None:
        return None
    lo, hi, requested = (int(v) for v in m.groups())
    return None if requested <= hi or hi < lo else hi


def calculate_timestamps(indices: list[int], fps: float, merge: int = 2) -> list[float]:
    """Mean time of the first and last frame of each temporal group (indices padded with the last)."""
    idx = list(indices)
    if len(idx) % merge:
        idx += [idx[-1]] * (merge - len(idx) % merge)
    ts = [i / fps for i in idx]
    return [(ts[i] + ts[i + merge - 1]) / 2 for i in range(0, len(ts), merge)]


def expand_video_tokens(ids: list[int], grid_thw, timestamps: list[float], encode, start: int, pad: int,
                        end: int, merge: int = 2) -> list[int]:
    """Replace the one <|vision_start|><|video_pad|><|vision_end|> triple the way vLLM does for
    Qwen3-VL-style models: per temporal group '<t seconds>' + start + pad * (h*w/merge^2) + end."""
    triple = [start, pad, end]
    hits = [i for i in range(len(ids) - 2) if ids[i:i + 3] == triple]
    if len(hits) != 1:
        raise ValueError(f"expected one video placeholder, found {len(hits)}")
    t, h, w = (int(x) for x in grid_thw)
    if len(timestamps) != t:
        raise ValueError(f"{len(timestamps)} timestamps for {t} temporal groups")
    repl: list[int] = []
    for ts in timestamps:
        repl += list(encode(f"<{ts:.1f} seconds>")) + [start] + [pad] * (h * w // merge ** 2) + [end]
    return ids[:hits[0]] + repl + ids[hits[0] + 3:]


# --------------------------------------------------------------------------- video (qwen-vl-utils)

def read_video(path: str) -> tuple[Any, dict, float, str | None]:
    """_process_video: fetch_video with the authors' settings -> (frames, metadata, sample_fps, deviation).
    A clip shorter than 16 frames is retried with its length (authors); qwen-vl-utils rounds that to an
    even count, which fails again for 4k+3 frames, so a second retry asks for the largest even count."""
    os.environ.setdefault("FORCE_QWENVL_VIDEO_READER", "decord")   # read when qwen_vl_utils is imported
    from qwen_vl_utils.vision_process import fetch_video
    if not os.path.isfile(path):
        raise FileNotFoundError(f"video not found: {path}")
    info = {"video": path, "min_pixels": MIN_PIXELS, "max_pixels": MAX_PIXELS, "video_fps": VIDEO_FPS,
            "nframes": VIDEO_NFRAMES}
    deviation = None
    for attempt in range(3):
        try:
            (video, meta), sample_fps = fetch_video(info, return_video_sample_fps=True, return_video_metadata=True)
            return video, dict(meta or {}), float(sample_fps), deviation
        except ValueError as e:
            n = retry_nframes(str(e)) if attempt == 0 else None
            if n is None and attempt == 1 and NFRAMES_INTERVAL_PATTERN.search(str(e)):
                n = int(NFRAMES_INTERVAL_PATTERN.search(str(e)).group(2)) // 2 * 2
                deviation = f"second short-clip retry with nframes={n}"
            if not n:
                raise
            info["nframes"] = n
    raise RuntimeError("unreachable")


def video_input(video, raw_meta: dict, sample_fps: float, table_fps) -> tuple[tuple, dict]:
    """_video_input: ((frames, metadata), mm_processor_kwargs); timestamps use the dataset fps."""
    ts_fps = positive_float(table_fps) or VIDEO_TIMESTAMP_FPS
    meta = {k: v for k, v in raw_meta.items() if k in _META_KEYS}
    n = int(video.shape[0]) if hasattr(video, "shape") else len(video)
    fi = meta.get("frames_indices")
    fi = fi.detach().cpu().tolist() if hasattr(fi, "detach") else (list(fi) if fi is not None else None)
    meta["frames_indices"] = [int(i) for i in fi] if fi and len(fi) == n else list(range(n))
    meta["fps"] = float(ts_fps or sample_fps or 24.0)
    meta["total_num_frames"] = int(meta.get("total_num_frames", n))
    return (video, meta), {"fps": ts_fps, "do_sample_frames": False}


# --------------------------------------------------------------------------- runner

def _rows(rows) -> list:
    return list(rows.itertuples(index=False)) if hasattr(rows, "itertuples") else list(rows)


def _ensure_vocab_size(model: str, revision: str | None) -> None:
    """evaluation.py _ensure_vocab_size: expose text_config.vocab_size on the config class for vLLM."""
    from transformers import AutoConfig
    config = AutoConfig.from_pretrained(model, revision=revision, trust_remote_code=True)
    text = getattr(config, "text_config", None)
    if not hasattr(config, "vocab_size") and text is not None and hasattr(text, "vocab_size"):
        if not hasattr(config.__class__, "vocab_size"):
            setattr(config.__class__, "vocab_size", property(lambda self: getattr(self.text_config, "vocab_size", None)))


class CAW:
    """Code-as-World-VL-9B. backend "vllm" (the authors' engine settings; gpu_memory_utilization None =
    theirs, 0.5, on a GPU of 60 GiB or more, else 0.9 so the 17.5 GiB of weights leave room for the KV
    cache), "hf" (transformers generate, greedy, batch 1) or a fake object with generate(items) ->
    list[str] for tests, where each item is (row, prompt_ids, (frames, metadata), processor kwargs)."""

    def __init__(self, model: str = MODEL_ID, revision: str | None = MODEL_REVISION, backend="vllm",
                 gpu_memory_utilization: float | None = None, chat_template: str | None = None, **engine_kw):
        self.model, self.revision = model, revision
        self.gpu_memory_utilization, self.engine_kw = gpu_memory_utilization, engine_kw
        self.chat_template = chat_template
        self._fake = None if isinstance(backend, str) else backend
        self.backend_name = backend if isinstance(backend, str) else "fake"
        self._tok = self._proc = self._llm = self._hf = None
        self.template_ok: bool | None = None

    # ----------------------------------------------------------------- loading
    def _tools(self):
        if self._tok is None:
            from transformers import AutoProcessor, AutoTokenizer
            kw = {"trust_remote_code": True, "use_fast": True, "revision": self.revision}
            tok, proc = AutoTokenizer.from_pretrained(self.model, **kw), AutoProcessor.from_pretrained(self.model, **kw)
            template = open(self.chat_template, encoding="utf-8").read() if self.chat_template else proc.chat_template
            self.template_ok = hashlib.sha256(template.encode("utf-8")).hexdigest() == CHAT_TEMPLATE_SHA256
            if not self.template_ok:
                print("warning: chat template differs from the authors' qwen3_5_no_think.jinja "
                      "(pass chat_template=<their file> to use theirs)")
            tok.chat_template = proc.chat_template = template
            if tok.pad_token_id is None:
                tok.pad_token = tok.eos_token
            self._tok, self._proc = tok, proc
        return self._tok, self._proc

    def prompt_ids(self, row) -> list[int]:
        tok, proc = self._tools()
        text = proc.apply_chat_template(build_messages(row), add_generation_prompt=True, tokenize=False,
                                        enable_thinking=False)
        return tok.encode(text, add_special_tokens=False)[:MAX_PROMPT_LENGTH]

    def _logit_bias(self) -> dict[int, float]:
        tok, proc = self._tools()
        ids = [tok.convert_tokens_to_ids(getattr(proc, a)) for a in ("image_token", "video_token")
               if getattr(proc, a, None)]
        return {i: -100.0 for i in ids if isinstance(i, int) and i >= 0}

    def _engine(self):
        if self._llm is None:
            import torch
            from vllm import LLM
            _ensure_vocab_size(self.model, self.revision)
            util = self.gpu_memory_utilization
            if util is None:
                util = 0.5 if torch.cuda.get_device_properties(0).total_memory >= 60 * 2**30 else 0.9
            self._llm = LLM(model=self.model, revision=self.revision, gpu_memory_utilization=util,
                            **{**ENGINE_CONFIG, **self.engine_kw})
        return self._llm

    # ----------------------------------------------------------------- generation
    def _generate_vllm(self, items: list) -> list[str | None]:
        from vllm import SamplingParams
        sampling = SamplingParams(**SAMPLING_CONFIG, seed=SEED, detokenize=True, logit_bias=self._logit_bias() or None)
        inputs = [{"prompt_token_ids": ids, "multi_modal_data": {"video": [video]}, "mm_processor_kwargs": pkw}
                  for _, ids, video, pkw in items]
        return [o.outputs[0].text if o.outputs else None for o in self._engine().generate(inputs, sampling)]

    def _generate_hf(self, items: list) -> list[str]:
        import torch
        from transformers import AutoModelForImageTextToText, LogitsProcessor, LogitsProcessorList
        from transformers.video_utils import VideoMetadata
        tok, proc = self._tools()
        if self._hf is None:
            self._hf = AutoModelForImageTextToText.from_pretrained(
                self.model, revision=self.revision, dtype=torch.bfloat16, attn_implementation="sdpa",
                device_map="auto", trust_remote_code=True).eval()
        bias = self._logit_bias()

        class Bias(LogitsProcessor):
            def __call__(self, input_ids, scores):
                scores = scores.clone()
                for i, b in bias.items():
                    scores[:, i] += b
                return scores

        start, pad, end, eos = tok.convert_tokens_to_ids(["<|vision_start|>", "<|video_pad|>", "<|vision_end|>",
                                                          "<|im_end|>"])
        image_pad = tok.convert_tokens_to_ids("<|image_pad|>")
        merge = int(getattr(getattr(proc, "video_processor", None), "merge_size", 2) or 2)
        cache: dict[int, tuple] = {}
        out = []
        for _, ids, (video, meta), pkw in items:
            key = id(video)
            if key not in cache:
                px = proc(text=VIDEO_PLACEHOLDER, videos=[[video]], video_metadata=[[VideoMetadata(**meta)]],
                          return_tensors="pt", **pkw)
                cache[key] = (px["pixel_values_videos"], px["video_grid_thw"])
            pv, grid = cache[key]
            full = expand_video_tokens(ids, grid[0].tolist(), calculate_timestamps(meta["frames_indices"], meta["fps"]),
                                       lambda s: tok.encode(s, add_special_tokens=False), start, pad, end, merge)
            dev = self._hf.device
            x = torch.tensor([full], device=dev)
            types = torch.tensor([[2 if t == pad else 1 if t == image_pad else 0 for t in full]], device=dev)
            with torch.inference_mode():
                gen = self._hf.generate(input_ids=x, attention_mask=torch.ones_like(x), mm_token_type_ids=types,
                                        pixel_values_videos=pv.to(dev), video_grid_thw=grid.to(dev), do_sample=False,
                                        max_new_tokens=max(1, min(MAX_RESPONSE_LENGTH, MAX_MODEL_LEN - len(full))),
                                        eos_token_id=eos, pad_token_id=tok.pad_token_id,
                                        logits_processor=LogitsProcessorList([Bias()]))
            out.append(tok.decode(gen[0, len(full):].tolist(), skip_special_tokens=True))
        return out

    def generate(self, items: list) -> list[str | None]:
        if not items:
            return []
        if self._fake is not None:
            return list(self._fake.generate(items))
        return self._generate_vllm(items) if self.backend_name == "vllm" else self._generate_hf(items)

    # ----------------------------------------------------------------- task
    def direct_answer(self, groups: list, **_) -> dict[int, dict]:
        """One reply per question; each video is decoded once (qwen-vl-utils) for all its questions.
        {qid: {"reply", "value", "authors_value", "parse_answer", "n_frames", "frames", "deviation"}},
        plus "error" when the engine returned no output (not cached). Replies are read in the
        question's unit, or in SI when it states none (qp.open.qwen_vl.answer_unit)."""
        from qp.open.qwen_vl import answer_unit
        items, info, out = [], [], {}
        for g in groups:
            rs = _rows(g)
            try:
                video, raw_meta, sample_fps, deviation = self.read(str(rs[0].video_path))
            except Exception as e:  # noqa: BLE001 - recorded per question, no answer for this video
                for r in rs:
                    out[int(r.qid)] = {"reply": None, "value": None, "error": f"{type(e).__name__}: {e}"}
                continue
            vin, pkw = video_input(video, raw_meta, sample_fps, rs[0].fps)
            for r in rs:
                items.append((r, self.prompt_ids(r), vin, pkw))
                info.append((r, vin[1], deviation))
        for (r, meta, deviation), text in zip(info, self.generate(items)):
            out[int(r.qid)] = {"reply": text, **parse(text, answer_unit(r)), "n_frames": len(meta["frames_indices"]),
                               "frames": meta["frames_indices"], "deviation": deviation, "model": self.model,
                               "recipe": f"{AUTHORS_REPO}@{AUTHORS_COMMIT[:8]}"}
            if text is None:
                out[int(r.qid)]["error"] = "generation failed"
        return out

    def read(self, path: str):
        """Video decode hook (tests replace it to run without qwen-vl-utils)."""
        return read_video(path)
