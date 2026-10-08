"""Turn a free-text model reply into one positive number in the question's unit."""

from __future__ import annotations

import math
import re

# Scale of each unit relative to SI (m, m/s, m/s^2), and its dimension.
_UNITS = {
    "mm": (1e-3, "L"), "cm": (1e-2, "L"), "m": (1.0, "L"), "km": (1e3, "L"),
    "mm/s": (1e-3, "V"), "cm/s": (1e-2, "V"), "m/s": (1.0, "V"), "km/s": (1e3, "V"),
    "km/h": (1 / 3.6, "V"),
    "mm/s^2": (1e-3, "A"), "cm/s^2": (1e-2, "A"), "m/s^2": (1.0, "A"), "km/s^2": (1e3, "A"),
}

_NUM = r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)?(?:\.\d+)?(?:\s*[eE][-+]?\d+|\s*[x×]\s*10\^?\s*[-+]?\d+)?"
_UNIT = (r"km/h|kph|[ckm]?m\s*/\s*s(?:\s*(?:\^\s*2|²|2))?|"
         r"(?:kilo|centi|milli)?met(?:er|re)s?(?:\s*(?:per|/)\s*sec(?:ond)?s?(?:\s*(?:squared|\^\s*2|²))?)?|"
         r"[ckm]?m")
_ANS_RE = re.compile(r"(?<![\w.])(" + _NUM + r")\s*(" + _UNIT + r")?(?![A-Za-z])", re.IGNORECASE)
_FINAL_RE = re.compile(r"final answer\s*[:=]?\s*(.+)", re.IGNORECASE)


def canonical_unit(unit: str) -> str | None:
    u = unit.lower().replace(" ", "").replace("²", "^2")
    if u in ("kph", "km/h"):
        return "km/h"
    m = re.fullmatch(r"(kilo|centi|milli)?met(?:er|re)s?(per|/)?(sec(?:ond)?s?)?(squared|\^2)?", u)
    if m:
        base = {"kilo": "k", "centi": "c", "milli": "m"}.get(m.group(1) or "", "") + "m"
        if m.group(3):
            return base + ("/s^2" if m.group(4) else "/s")
        return base
    m = re.fullmatch(r"([ckm]?m)(/s)?(\^2|2)?", u)
    if m:
        return m.group(1) + (m.group(2) or "") + ("^2" if m.group(2) and m.group(3) else "")
    return u if u in _UNITS else None


def _to_float(s: str) -> float:
    s = s.replace(",", "").replace(" ", "")
    m = re.fullmatch(r"(.+?)[x×]10\^?([-+]?\d+)", s)
    return float(m.group(1)) * 10 ** int(m.group(2)) if m else float(s)


def parse_answer(text: str | None, target_unit: str = "") -> float:
    """First number in the reply (after 'Final answer:' if present), converted to
    `target_unit` when the reply names a different unit of the same dimension.
    Returns NaN when no usable number is found."""
    if not isinstance(text, str):
        return math.nan
    finals = _FINAL_RE.findall(text)
    if finals:
        text = finals[-1]
    for m in _ANS_RE.finditer(text):
        if not re.search(r"\d", m.group(1)):
            continue
        try:
            v = abs(_to_float(m.group(1)))
        except ValueError:
            continue
        if not math.isfinite(v):
            continue
        reply, target = canonical_unit(m.group(2) or ""), canonical_unit(target_unit or "")
        if reply in _UNITS and target in _UNITS and _UNITS[reply][1] == _UNITS[target][1]:
            v *= _UNITS[reply][0] / _UNITS[target][0]
        return v
    return math.nan


_PER_S = r"\s*(?:/|per)\s*s(?:ec(?:ond)?s?)?"
_Q_UNIT_RE = re.compile(
    r"\bin\s+(?:units?\s+of\s+)?(?:(km\s*/\s*h|kph|(?:km|kilomet(?:er|re)s?)\s+per\s+hour)"
    rf"|((?:kilo|centi|milli)?met(?:er|re)s?|[ckm]?m)({_PER_S}(\s*(?:\^\s*2|²|2|squared)|{_PER_S})?)?)(?![\w/^])",
    re.IGNORECASE)


def question_unit_full(question: str) -> str:
    """Unit asked by the question (last "in <unit>"), canonical, including spelled-out rates
    ("in meters per second", "in cm per second", "in m/s2", "in meters per second squared") that
    a plain 'in <unit>' match reads as a length. "" if none."""
    unit = ""
    for m in _Q_UNIT_RE.finditer(str(question or "")):
        if m.group(1):
            unit = "km/h"
            continue
        base = canonical_unit(m.group(2)) or ""
        cu = base + ("/s^2" if m.group(4) else "/s" if m.group(3) else "")
        unit = cu if cu in _UNITS else unit
    return unit
