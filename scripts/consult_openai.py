"""Ask an OpenAI model a text-only question (research consultation), budget-guarded on the OpenAI ledger.

    python scripts/consult_openai.py research/consult/brief_2026-10-11.md research/consult/astra_2026-10-11.md

Sends the prompt file as the user message, writes the reply to the output file, and appends the cost to
budget/ledger_openai.jsonl. Refuses when the ledger plus the request's worst case would exceed --cap-usd.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_openai_direct import LEDGER, PRICES, load_env, price, spent  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt_file")
    ap.add_argument("out_file")
    ap.add_argument("--model", default="gpt-6-astra")
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--max-output", type=int, default=30000)
    ap.add_argument("--cap-usd", type=float, default=45.0)
    args = ap.parse_args()
    load_env()

    prompt = Path(args.prompt_file).read_text()
    pin, _, pout = PRICES[args.model]
    worst = (len(prompt) / 3 * pin + args.max_output * pout) / 1e6
    print(f"ledger ${spent():.2f}, worst case ${worst:.2f}, cap ${args.cap_usd:.2f}")
    if spent() + worst > args.cap_usd:
        raise SystemExit("refused: would exceed the cap")

    import openai
    r = openai.OpenAI().responses.create(model=args.model, reasoning={"effort": args.effort},
                                         max_output_tokens=args.max_output,
                                         input=[{"role": "user", "content": prompt}])
    usd = price(args.model, r.usage)
    with LEDGER.open("a") as fh:
        fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "run": "consult",
                             "model": args.model, "video": Path(args.prompt_file).name, "id": r.id,
                             "input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens,
                             "usd": round(usd, 6)}) + "\n")
    Path(args.out_file).write_text(r.output_text or f"(no text; status {r.status})\n")
    print(f"{r.status}: {r.usage.input_tokens} in / {r.usage.output_tokens} out, ${usd:.3f}; "
          f"ledger ${spent():.2f}; wrote {args.out_file}")


if __name__ == "__main__":
    main()
