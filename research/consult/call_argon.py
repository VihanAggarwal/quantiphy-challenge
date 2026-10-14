"""Send a research prompt (+ attached context files) to Gemini 4 Argon with Google Search grounding; save the answer.
Budget-guarded on budget/ledger_gemini.jsonl (cap $15). Argon's price is not published where we could check: priced
at a cautious $5 / $40 per MTok (input / output incl. thinking).

    .venv/bin/python research/consult/call_argon.py PROMPT.md OUT.md [ATTACH ...]
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "budget" / "ledger_gemini.jsonl"
MODEL, PIN, POUT, CAP, MAX_OUT = "gemini-4-argon", 5.0, 40.0, 15.0, 32768


def main():
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    from google import genai
    from google.genai import types
    prompt_path, out_path, attach = Path(sys.argv[1]), Path(sys.argv[2]), [Path(p) for p in sys.argv[3:]]
    text = prompt_path.read_text()
    text = text.split("\n---\n", 1)[1] if "\n---\n" in text else text      # only the part below the line
    for a in attach:
        text += f"\n\n===== ATTACHED FILE: {a.name} =====\n{a.read_text()}"
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=types.HttpOptions(timeout=1_800_000))
    n_in = client.models.count_tokens(model=MODEL, contents=text).total_tokens
    spent = sum(json.loads(l).get("usd", 0) for l in LEDGER.read_text().splitlines() if l.strip())
    worst = (n_in * PIN + MAX_OUT * POUT) / 1e6 + 0.5          # + grounding queries
    print(f"input {n_in} tokens; ledger ${spent:.2f}; worst case ${worst:.2f}", flush=True)
    if spent + worst > CAP:
        raise SystemExit("over the Gemini cap")
    cfg = types.GenerateContentConfig(max_output_tokens=MAX_OUT,
                                      thinking_config=types.ThinkingConfig(thinking_level="high"),
                                      tools=[types.Tool(google_search=types.GoogleSearch())])
    t0 = time.time()
    r = client.models.generate_content(model=MODEL, contents=text, config=cfg)
    u = r.usage_metadata
    p, o, th = u.prompt_token_count or 0, u.candidates_token_count or 0, u.thoughts_token_count or 0
    usd = (p * PIN + (o + th) * POUT) / 1e6
    with LEDGER.open("a") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "run": f"argon_{out_path.stem}",
                            "model": MODEL, "video": "", "prompt": p, "output": o, "thoughts": th,
                            "usd": round(usd, 6)}) + "\n")
    body = r.text or ""
    gm = getattr(r.candidates[0], "grounding_metadata", None) if r.candidates else None
    srcs = []
    for ch in (getattr(gm, "grounding_chunks", None) or []):
        w = getattr(ch, "web", None)
        if w is not None:
            srcs.append(f"- {w.title}: {w.uri}")
    if srcs:
        body += "\n\n## Grounding sources (returned by the API)\n" + "\n".join(dict.fromkeys(srcs))
    out_path.write_text(body)
    print(f"done in {time.time() - t0:.0f}s: prompt {p}, output {o}, thoughts {th}, ${usd:.3f}; "
          f"finish={r.candidates[0].finish_reason if r.candidates else None}; wrote {out_path}")


if __name__ == "__main__":
    main()
