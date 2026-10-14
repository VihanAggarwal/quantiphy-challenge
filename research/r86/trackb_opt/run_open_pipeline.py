"""Run the unchanged Track A v1 pipeline (scripts/run_claude.py: request, records, post-steps, geometry,
combine) with an open-weight model behind an OpenAI-compatible endpoint (open_client.OpenCompatClient).

    OPEN_BASE_URL=http://localhost:8000/v1 OPEN_MODEL=Qwen/Qwen3.8-27B-FP8 \
      .venv/bin/python research/r86/trackb_opt/run_open_pipeline.py --split val --name val_q38_v1 \
      --effort medium --frames 16 --max-frames 32 --max-side 854 --workers 16 [--coords rel1000]

All run_claude.py flags pass through; --model defaults to $OPEN_MODEL and --local-estimate is forced. The
Claude ledger is never touched: QP_LEDGER points at <runs>/<name>/open_ledger.jsonl with a huge cap and the
model is priced at 0. Output: <runs>/<name>/<split>.csv (id, parsed_value, geo_value, direct_value, method ...)
-> score with scripts/score.py (val) or feed the Track B builder / qp.postprocess preset "trackb" (test).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    coords = "auto"
    if "--coords" in argv:
        i = argv.index("--coords")
        coords = argv[i + 1]
        del argv[i:i + 2]
    model = os.environ.get("OPEN_MODEL", "")
    if "--model" not in argv:
        argv += ["--model", model]
    else:
        model = argv[argv.index("--model") + 1]
    if "--local-estimate" not in argv:
        argv.append("--local-estimate")
    name = argv[argv.index("--name") + 1]
    runs = Path(os.environ.get("QP_RUNS") or ROOT / "runs")
    (runs / name).mkdir(parents=True, exist_ok=True)
    os.environ["QP_LEDGER"] = str(runs / name / "open_ledger.jsonl")
    os.environ["QP_BUDGET_USD"] = "1e12"
    os.environ.setdefault("ANTHROPIC_API_KEY", "")

    from qp import budget
    budget.PRICES[model] = {"input": 0.0, "output": 0.0, "cache_write_5m": 0.0, "cache_write_1h": 0.0,
                            "cache_read": 0.0}
    import run_claude
    from open_client import OpenCompatClient
    return run_claude.main(argv, client=OpenCompatClient(model=model, coords=coords))


if __name__ == "__main__":
    main()
