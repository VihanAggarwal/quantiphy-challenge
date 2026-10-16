"""Parse the agent's self-reported confidence per answered question from notes.md.

Heuristic: every occurrence of an answered qid (as a whole number, also inside "1407/1408" or "720-723" ranges) opens a
segment that runs to the next qid occurrence or the end of the line; the first confidence phrase in the segment is that
qid's confidence. A line whose qids carry no phrase of their own inherits a phrase that appears later on the same line
(e.g. "410 = 0.2, 412 = 0.36 ... Confidence is low."), else the next non-empty line if it starts with "Confidence"/"conf".
Levels: guess 0, very low 0.5, low 1, low-medium 2, medium 3, medium-high 4, high 5.

    from conf import confidence; confidence(Path('/tmp/blind_test/simulation_0172'))  -> {qid: level}
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PHR = [
    (r"\bguess(?:ed|work)?\b", 0.0),
    (r"\bvery[ -]low\b", 0.5),
    (r"\b(?:low[ -/]+(?:to[ -])?med(?:ium)?|med(?:ium)?[ -/]+(?:to[ -])?low)\b", 2.0),
    (r"\b(?:med(?:ium)?[ -/]+(?:to[ -])?high|high[ -/]+(?:to[ -])?med(?:ium)?)\b", 4.0),
    (r"\blow\b", 1.0),
    (r"\bmed(?:ium)?\b", 3.0),
    (r"\bhigh\b", 5.0),
]
CONF_CTX = re.compile(r"conf|confidence|certain|\(|:|;|-", re.I)


def level(seg: str):
    """first confidence phrase in seg, only if the segment talks about confidence or uses the terse '(medium)' style"""
    s = seg.lower()
    best = None
    for pat, lv in PHR:
        m = re.search(pat, s)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), lv, m.group(0))
    if best is None:
        return None
    pos, lv, word = best
    # avoid "high" in "high-res", "low" in "low frame rate" etc.: require a confidence cue nearby or a bracket/colon form
    ctx = s[max(0, pos - 40): pos + len(word) + 25]
    if not re.search(r"conf|confiden|certain|\(\s*" + re.escape(word) + r"|[:|]\s*" + re.escape(word) + r"|" + re.escape(word) + r"\s*[);.,|(]|"
                     + re.escape(word) + r"\s*$", ctx):
        return None
    if re.search(re.escape(word) + r"[- ](?:res|resolution|frame|speed|value|end|side|precision|poly|contrast|pass)", s[pos:pos + 30]):
        return None
    return lv


def qid_positions(line: str, qids: set[int]):
    out = []
    for m in re.finditer(r"(?<![\d.])(\d{1,4})(?:\s*[-–/]\s*(\d{1,4}))?(?![\d.])", line):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else None
        if b is not None and a in qids and b in qids and b > a and b - a < 12 and "/" not in m.group(0):
            ids = [q for q in range(a, b + 1) if q in qids]
        else:
            ids = [q for q in ([a] + ([b] if b is not None else [])) if q in qids]
        if ids:
            out.append((m.start(), m.end(), ids))
    return out


def confidence(vd: Path) -> dict[int, float]:
    f, a = vd / "notes.md", vd / "answers.json"
    if not f.exists() or not a.exists():
        return {}
    try:
        qids = {int(k) for k in json.loads(a.read_text())}
    except Exception:
        return {}
    lines = [x for x in f.read_text().splitlines()]
    res: dict[int, float] = {}
    for li, line in enumerate(lines):
        pos = qid_positions(line, qids)
        if not pos:
            continue
        pending = []
        for j, (s, e, ids) in enumerate(pos):
            end = pos[j + 1][0] if j + 1 < len(pos) else len(line)
            lv = level(line[e:end])
            if lv is None:
                pending += ids
            else:
                for q in ids + pending:
                    res.setdefault(q, lv)
                pending = []
        if pending:
            # continuation lines (indented, no qid of their own) or a following "Confidence ..." line
            for nxt in lines[li + 1: li + 4]:
                if not nxt.strip():
                    continue
                if qid_positions(nxt, qids):
                    break
                cont = nxt.startswith((" ", "\t")) or re.match(r"\s*[-*]?\s*(?:conf|confidence)", nxt, re.I)
                if not cont:
                    break
                lv = level(nxt)
                if lv is not None:
                    for q in pending:
                        res.setdefault(q, lv)
                    break
    # fallback: the answer value as printed in the notes, then the first confidence phrase after it on that line
    try:
        ans = json.loads(a.read_text())
    except Exception:
        ans = {}
    text = "\n".join(lines)
    for k, x in ans.items():
        q = int(k)
        if q in res:
            continue
        try:
            xv = float(x)
        except (TypeError, ValueError):
            continue
        forms = {repr(xv), str(x), f"{abs(xv):g}", f"{abs(xv):.2f}", f"{abs(xv):.1f}", f"{abs(xv):.3f}"}
        for fm in sorted(forms, key=len, reverse=True):
            fm = fm.rstrip("0").rstrip(".") if "." in fm else fm
            if len(fm) < 2 and abs(xv) >= 1:
                continue
            for m in re.finditer(r"(?<![\d.])" + re.escape(fm) + r"(?![\d])", text):
                eol = text.find("\n", m.end())
                seg = text[m.end(): eol if eol >= 0 else len(text)]
                lv = level(seg[:90])
                if lv is not None:
                    res[q] = lv
                    break
            if q in res:
                break
    return res


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        print(p, confidence(Path(p)))
