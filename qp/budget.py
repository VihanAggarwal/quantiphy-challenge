"""Spend ledger with a hard cap for paid API calls.

The ledger is budget/ledger.jsonl: append-only JSON lines, committed to git so the running
total survives container resets (it holds token counts and ids only, never secrets).

    {"type": "usage", "ts", "run", "model", "mode": "sync"|"batch", "id", "input_tokens",
     "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "usd", ...}
    {"type": "hold", "id": <batch id>, "usd": <worst case>, ...}  submitted batch, not yet collected
    {"type": "release", "id": <batch id>}                        batch collected (its usage lines are in)

A hold should be the batch's worst case (input + max_tokens output), so committed() is a true
upper bound on what the ledger's requests can cost; extra hold fields (split, custom ids, settings)
let a runner find and collect a batch after its own state files are lost.

committed() = recorded usage + open holds + in-process reservations; check() refuses any new
spend that would push it past the cap (env QP_BUDGET_USD, default 200). The ledger path can be
overridden with env QP_LEDGER (tests).
"""

from __future__ import annotations

import fcntl
import json
import os
import threading
import warnings
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "budget" / "ledger.jsonl"
DEFAULT_CAP_USD = 200.0
BATCH_DISCOUNT = 0.5

# USD per million tokens. Cache writes: 5-minute TTL (1.25x input) / 1-hour TTL (2x input).
PRICES = {
    "claude-opus-5-5": {"input": 4.0, "output": 20.0, "cache_write_5m": 5.0, "cache_write_1h": 8.0,
                        "cache_read": 0.20},
    "claude-fable-5-1": {"input": 10.0, "output": 50.0, "cache_write_5m": 12.5, "cache_write_1h": 20.0,
                         "cache_read": 0.25},
}

_lock = threading.Lock()
_reserved = 0.0


class BudgetExceeded(RuntimeError):
    pass


def ledger_path() -> Path:
    return Path(os.environ.get("QP_LEDGER", DEFAULT_LEDGER))


def cap() -> float:
    return float(os.environ.get("QP_BUDGET_USD", DEFAULT_CAP_USD))


def _get(usage: Any, key: str) -> Any:
    return usage.get(key) if isinstance(usage, dict) else getattr(usage, key, None)


def usage_dict(usage: Any) -> dict:
    """Token counts from an SDK Usage object or a dict (missing -> 0)."""
    out = {k: int(_get(usage, k) or 0) for k in
           ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}
    cc = _get(usage, "cache_creation")
    if cc is not None:
        out["cache_creation_1h_input_tokens"] = int(_get(cc, "ephemeral_1h_input_tokens") or 0)
    return out


def _prices(model: str) -> dict:
    if model in PRICES:
        return PRICES[model]
    warnings.warn(f"no price for {model!r}; using the most expensive known model's prices")
    return max(PRICES.values(), key=lambda p: p["output"])


def price(usage: Any, model: str = "claude-opus-5-5", batch: bool = False) -> float:
    """USD cost of one response's usage (Message Batches: 50% off every token type)."""
    u, p = usage_dict(usage), _prices(model)
    w1h = u.get("cache_creation_1h_input_tokens", 0)
    w5m = u["cache_creation_input_tokens"] - w1h
    usd = (u["input_tokens"] * p["input"] + u["output_tokens"] * p["output"]
           + w5m * p["cache_write_5m"] + w1h * p["cache_write_1h"]
           + u["cache_read_input_tokens"] * p["cache_read"]) / 1e6
    return usd * (BATCH_DISCOUNT if batch else 1.0)


def estimate_usd(input_tokens: float, output_tokens: float, model: str = "claude-opus-5-5",
                 batch: bool = False) -> float:
    return price({"input_tokens": input_tokens, "output_tokens": output_tokens}, model, batch)


def entries(path: Path | None = None) -> list[dict]:
    path = path or ledger_path()
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def spent(path: Path | None = None) -> float:
    """USD of all recorded usage."""
    return sum(float(e.get("usd", 0.0)) for e in entries(path) if e.get("type", "usage") == "usage")


def open_holds(path: Path | None = None) -> dict[str, float]:
    holds: dict[str, float] = {}
    for e in entries(path):
        if e.get("type") == "hold":
            holds[e["id"]] = float(e["usd"])
        elif e.get("type") == "release":
            holds.pop(e["id"], None)
    return holds


def committed(path: Path | None = None) -> float:
    """Recorded usage + estimates of submitted-but-uncollected batches + in-flight reservations."""
    return spent(path) + sum(open_holds(path).values()) + _reserved


def check(estimate_usd: float, path: Path | None = None) -> float:
    """Raise BudgetExceeded if committed() + estimate exceeds the cap; return the headroom left."""
    total, limit = committed(path), cap()
    if total + estimate_usd > limit:
        raise BudgetExceeded(f"estimate ${estimate_usd:.2f} + committed ${total:.2f} "
                             f"exceeds the cap ${limit:.2f} (QP_BUDGET_USD)")
    return limit - total - estimate_usd


@contextmanager
def reserve(estimate_usd: float, path: Path | None = None) -> Iterator[None]:
    """Hold `estimate_usd` against the cap while a request is in flight (call record() inside)."""
    global _reserved
    with _lock:
        check(estimate_usd, path)
        _reserved += estimate_usd
    try:
        yield
    finally:
        with _lock:
            _reserved -= estimate_usd


def _append(entry: dict, path: Path | None = None) -> dict:
    path = path or ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, sort_keys=True) + "\n"
    with _lock, path.open("a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)  # other processes appending to the same ledger
        try:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
    return entry


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def record(run: str, model: str, mode: str, request_id: str, usage: Any, usd: float | None = None,
           path: Path | None = None, **extra: Any) -> dict:
    """Append one response's usage and cost; returns the ledger entry."""
    if mode not in ("sync", "batch"):
        raise ValueError(f"mode must be 'sync' or 'batch', got {mode!r}")
    u = usage_dict(usage)
    usd = price(u, model, batch=mode == "batch") if usd is None else usd
    return _append({"type": "usage", "ts": _now(), "run": run, "model": model, "mode": mode,
                    "id": request_id, **u, "usd": round(usd, 6), **extra}, path)


def hold(run: str, batch_id: str, estimate_usd: float, path: Path | None = None, **extra: Any) -> dict:
    """Count `estimate_usd` against the cap until release(batch_id); `extra` is stored with it."""
    return _append({"type": "hold", "ts": _now(), "run": run, "id": batch_id,
                    "usd": round(estimate_usd, 6), **extra}, path)


def release(batch_id: str, path: Path | None = None) -> dict:
    return _append({"type": "release", "ts": _now(), "id": batch_id}, path)
