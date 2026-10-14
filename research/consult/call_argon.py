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
    body, srcs, u, finish = "", [], None, None
    # Batch API: the job runs on Google's side and we poll, so no long-lived HTTP connection (the proxy drops them).
    job = client.batches.create(model=MODEL, src=[types.InlinedRequest(contents=text, config=cfg)],
                                config={"display_name": f"argon_{out_path.stem}"})
    print("batch", job.name, flush=True)
    while True:
        job = client.batches.get(name=job.name)
        st = job.state.name if job.state else ""
        if st in ("JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"):
            break
        time.sleep(30)
    print("state", st, flush=True)
    if st != "JOB_STATE_SUCCEEDED":
        raise SystemExit(f"batch ended {st}: {job.error}")
    ir = job.dest.inlined_responses[0]
    if ir.error:
        raise SystemExit(f"request error: {ir.error}")
    r = ir.response
    body, u = r.text or "", r.usage_metadata
    for c in (r.candidates or []):
        finish = c.finish_reason
        for g in (getattr(getattr(c, "grounding_metadata", None), "grounding_chunks", None) or []):
            if getattr(g, "web", None) is not None:
                srcs.append(f"- {g.web.title}: {g.web.uri}")
    p, o, th = (u.prompt_token_count or 0, u.candidates_token_count or 0, u.thoughts_token_count or 0) if u else (0, 0, 0)
    usd = (p * PIN + (o + th) * POUT) / 1e6
    with LEDGER.open("a") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "run": f"argon_{out_path.stem}",
                            "model": MODEL, "video": "", "prompt": p, "output": o, "thoughts": th,
                            "usd": round(usd, 6)}) + "\n")
    if srcs:
        body += "\n\n## Grounding sources (returned by the API)\n" + "\n".join(dict.fromkeys(srcs))
    out_path.write_text(body)
    print(f"done in {time.time() - t0:.0f}s: prompt {p}, output {o}, thoughts {th}, ${usd:.3f}; "
          f"finish={finish}; wrote {out_path}")


if __name__ == "__main__":
    main()
