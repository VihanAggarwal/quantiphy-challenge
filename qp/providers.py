"""Minimal multimodal clients behind one call: ask(system, frames, text) -> reply text.

Model ids are passed on the command line; the Anthropic default is the latest Opus.
Each client retries transient errors with exponential backoff.
"""

from __future__ import annotations

import base64
import os
import time

from .frames import Frame

DEFAULT_MODELS = {"anthropic": "claude-opus-5-5"}


def _frame_label(f: Frame) -> str:
    return f"Frame {f.index} at t={f.time_s:.3f}s ({f.width}x{f.height} px):"


class Client:
    def __init__(self, provider: str, model: str | None, max_tokens: int = 4096):
        self.provider, self.max_tokens = provider, max_tokens
        self.model = model or DEFAULT_MODELS.get(provider)
        if not self.model:
            raise SystemExit(f"--model is required for provider {provider!r}")
        if provider == "anthropic":
            import anthropic
            self._c = anthropic.Anthropic()
        elif provider == "openai":
            import openai
            self._c = openai.OpenAI()
        elif provider == "gemini":
            from google import genai
            self._c = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        else:
            raise ValueError(f"unknown provider {provider!r}")

    def ask(self, system: str, frames: list[Frame], text: str, retries: int = 5) -> str:
        for attempt in range(retries + 1):
            try:
                return getattr(self, f"_{self.provider}")(system, frames, text)
            except Exception as e:  # noqa: BLE001 - provider SDKs raise many types
                if attempt == retries:
                    raise
                wait = 2 ** attempt * 2
                print(f"  {type(e).__name__}: {e} -- retrying in {wait}s")
                time.sleep(wait)
        raise AssertionError("unreachable")

    def _anthropic(self, system, frames, text):
        content = []
        for f in frames:
            content.append({"type": "text", "text": _frame_label(f)})
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                        "data": f.jpeg_b64}})
        content.append({"type": "text", "text": text})
        msg = self._c.messages.create(model=self.model, max_tokens=self.max_tokens, system=system,
                                      messages=[{"role": "user", "content": content}])
        return "".join(b.text for b in msg.content if b.type == "text")

    def _openai(self, system, frames, text):
        content = []
        for f in frames:
            content.append({"type": "text", "text": _frame_label(f)})
            content.append({"type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{f.jpeg_b64}", "detail": "high"}})
        content.append({"type": "text", "text": text})
        r = self._c.chat.completions.create(
            model=self.model, max_completion_tokens=self.max_tokens,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": content}])
        return r.choices[0].message.content or ""

    def _gemini(self, system, frames, text):
        from google.genai import types
        parts = []
        for f in frames:
            parts.append(_frame_label(f))
            parts.append(types.Part.from_bytes(data=base64.b64decode(f.jpeg_b64), mime_type="image/jpeg"))
        parts.append(text)
        r = self._c.models.generate_content(
            model=self.model, contents=parts,
            config=types.GenerateContentConfig(system_instruction=system))
        return r.text or ""
