# QuantiPhy Challenge (NeurIPS 2026)

Our entry for the [QuantiPhy Challenge](https://quantiphy.stanford.edu/competition/index.html):
given a short video, one known physical quantity (the *prior*, e.g. `speed of the bird = 6 m/s`)
and, for 3D scenes, camera distances, estimate an object's size, distance, speed or acceleration.

- **Deadline:** 2026-10-23 23:59 AoE · **3 scored uploads/day**
- **Tracks:** A = any model (incl. closed APIs) · B = open-weight only
- **Metric:** MRA. Each answer scores the fraction of 10 relative-error tolerances it meets
  (<90%, <80%, …, <10%, <5%); averaged within S2/D2/S3/D3 (prior static/dynamic × 2D/3D video),
  then over the four. A 50% error is worth 0.4, 10% is 0.9, under 5% is 1.0. Blank/zero scores 0.

## Results so far (validation, 159 questions)

| Pipeline | MRA | S2 | D2 | S3 | D3 | Cost |
|---|---|---|---|---|---|---|
| Official GPT-5.1 zero-shot baseline | 0.486 | | | | | |
| Track A: Claude Opus 5.5, medium effort | 0.766 | .709 | .951 | .709 | .694 | $1.52 |
| Track A: Claude Opus 5.5, high effort | **0.782** | .706 | .916 | .784 | .723 | $1.87 |
| Track A: agentic tool loop (full-res, medium) | 0.743 | .663 | .943 | .705 | .660 | $8.69 |

About 8% of validation labels contradict their own video or each other (listed in `qp/combine.py`
and the analysis notes); excluding them, high effort scores ~0.81. Projected test MRA from the
validation per-source rates and the test mix: ~0.80.

## How it works (Track A)

1. **One request per video** (`qp/claude_annotate.py`, `scripts/run_claude.py`): frames (16 uniform +
   frames at every mentioned time) and all the video's questions go to Claude Opus 5.5, which returns
   per question a structured spec (what to measure), pixel annotations (extent endpoints, motion
   points, boxes per frame) and its own direct estimate. Batch API (50% off), structured outputs.
2. **Geometry in code** (`qp/geometry.py`): the prior sets the metric scale (2D: metres per pixel;
   3D: pinhole camera with the focal length solved from the prior and the lab rig's ~84° FOV as a
   prior), motion from polynomial fits over time, units converted to the asked unit.
3. **Answer selection** (`qp/combine.py`): geometry unless implausible, far from the direct estimate,
   or a 3D solve that had to assume the target's depth (then Claude's direct estimate).
4. Spend is capped by `qp/budget.py`: every request is held at its worst case until its usage is
   recorded in `budget/ledger.jsonl` (committed, so resets never re-buy paid work).

Track B (open weights, Colab GPU): `notebooks/colab_pipeline.ipynb` — Qwen3-VL specs/grounding/direct
answers, Code-as-World-VL-9B direct answers, Grounding DINO + SAM 2 tracks, the same geometry solver.

## Layout

| Path | What |
|---|---|
| `qp/spec.py` | Shared contract: QuestionSpec, RoleTrack/Obs (pixel tracks), Answer |
| `qp/data.py` | Loaders: `val` (480p), `val_hires` (validation questions on the full-res test copies), `test` |
| `qp/mra.py` | MRA, exact parity with the official `evaluator.py` (tested) |
| `qp/geometry.py` | Pixel measurements + prior → answer (2D scale, 3D pinhole, looming, endpoint depths) |
| `qp/claude_annotate.py`, `scripts/run_claude.py` | Track A batch pipeline |
| `qp/combine.py`, `scripts/combine_runs.py` | Answer selection; multi-run medians |
| `qp/refine.py`, `qp/dense_track.py`, `scripts/dense_tracks.py` | Optical-flow / dense CPU tracking from Claude's boxes |
| `qp/claude_verify.py`, `qp/claude_agent.py` | Verification pass; agentic tool loop (experimental) |
| `qp/open/` | Track B: Qwen3-VL, Code-as-World, Grounding DINO/OWLv2 + SAM 2 |
| `scripts/make_submission.py` | Fill the official template and validate it for upload |

## Quick start

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
python scripts/download_data.py          # Hugging Face datasets + submission template -> data/
cp .env.example .env                     # ANTHROPIC_API_KEY=...
pytest -q

# validation (cached records replay for free; new runs are paid)
python scripts/run_claude.py --split val --name val_opus_high --effort high --mode batch
# test + submission
python scripts/run_claude.py --split test --name test_v1_high_854 --effort high --prompt-version v1 \
    --max-side 854 --mode batch --chunk-videos 20 --est-output-per-question 1200
python scripts/make_submission.py runs/test_v1_high_854/test.csv submissions/test_v1_high_854.csv
```
