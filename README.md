# QuantiPhy Challenge (NeurIPS 2026)

Our entry for the [QuantiPhy Challenge](https://quantiphy.stanford.edu/competition/index.html):
given a short video, one known physical quantity (the *prior*, e.g. `speed of the bird = 6 m/s`)
and, for 3D scenes, camera distances, estimate an object's size, speed or acceleration.

- **Deadline:** 2026-10-23 23:59 AoE · **3 scored uploads/day**
- **Tracks:** A = any model (incl. closed APIs) · B = open-weight only
- **Metric:** MRA. Each answer scores the fraction of 10 relative-error tolerances it meets
  (<90%, <80%, …, <10%, <5%); averaged within S2/D2/S3/D3 (prior kind × 2D/3D), then over the four.
  A 50% error is worth 0.4, 10% is 0.9, under 5% is 1.0. Blank/zero/non-numeric scores 0.

## Layout

| Path | What |
|---|---|
| `qp/data.py` | Loaders for validation (159 Qs, with answers), test (3,289 Qs) and the template |
| `qp/mra.py` | MRA, tested for exact parity with the official `evaluator.py` |
| `qp/frames.py` | Uniform frame sampling with timestamps; optional pixel-grid overlay |
| `qp/prompts.py` | `direct` (official zero-shot prompt) and `measure` (pixel-measure-then-scale) |
| `qp/parse.py` | Reply → number in the question's unit (handles cm↔m, km/h, ×10ⁿ) |
| `qp/providers.py` | Anthropic / OpenAI / Gemini clients behind one `ask()` |
| `scripts/run_vlm.py` | Run a model over a split; cached, resumable, parallel |
| `scripts/score.py` | Score runs on validation |
| `scripts/make_submission.py` | Fill the official template and check it before upload |

## Quick start

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env                                   # add API keys
git clone https://github.com/Paulineli/QuantiPhy external/QuantiPhy   # official evaluator (for tests)
python scripts/download_data.py                        # needs huggingface.co + quantiphy.stanford.edu
pytest -q

python scripts/run_vlm.py --split val --method measure --name opus_measure --limit 10   # probe
python scripts/run_vlm.py --split val --method measure --name opus_measure
python scripts/score.py runs/*/val.csv

python scripts/run_vlm.py --split test --method measure --name opus_measure
python scripts/make_submission.py runs/opus_measure/test.csv submissions/opus_measure.csv
```

## Plan

Reference points: GPT-5.1 zero-shot scores **0.486** on validation (official repo); the public
Track B entry [kuotunyu/quantiphy-geo-vlm](https://github.com/kuotunyu/quantiphy-geo-vlm) reached
**0.577** on test with OWLv2 detection + pixel geometry + Qwen3-VL / Code-as-World-VL-9B.

The paper's main finding is that VLMs ignore the stated prior and answer from world knowledge.
Every question is really *scale × pixel measurement*, so the plan is to make the pixel
measurement explicit:

1. **Baselines (Track A).** `direct` vs `measure` prompts on validation with Claude, GPT and
   Gemini; pick frame count and grid overlay.
2. **Measurement in code.** Have the VLM return pixel coordinates / boxes for the prior object
   and the target (JSON), then compute the answer in Python: metres-per-pixel from the prior,
   finite differences over timestamps for speed/acceleration, pinhole depth scaling in 3D.
   Add a detector/tracker (OWLv2 or SAM 2) for precise boxes over time.
3. **Arbitration / ensembling.** Geometric answer when tracking is confident, VLM answer
   otherwise; median across models; per-category routing chosen on validation.
4. **Track B** reuses steps 2–3 with open-weight VLMs (Qwen3-VL, Code-as-World-VL) on a GPU.

Validation is only 159 questions (~40 per category), so differences under ~0.03 MRA are noise;
use the daily test uploads to confirm anything that matters.
