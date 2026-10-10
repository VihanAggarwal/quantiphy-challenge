# QuantiPhy Challenge (NeurIPS 2026)

Our entry for the [QuantiPhy Challenge](https://quantiphy.stanford.edu/competition/index.html):
given a short video, one known physical quantity (the *prior*, e.g. `speed of the bird = 6 m/s`)
and, for 3D scenes, camera distances, estimate an object's size, distance, speed or acceleration.

- **Deadline:** 2026-10-23 23:59 AoE · **3 scored uploads/day**
- **Tracks:** A = any model (incl. closed APIs) · B = open-weight only
- **Metric:** MRA. Each answer scores the fraction of 10 relative-error tolerances it meets
  (<90%, <80%, …, <10%, <5%); averaged within S2/D2/S3/D3 (prior static/dynamic × 2D/3D video),
  then over the four. A 50% error is worth 0.4, 10% is 0.9, under 5% is 1.0. Blank/zero scores 0.

## Leaderboard (official test set, 3,289 questions)

| Submission | Track | MRA | S2 | D2 | S3 | D3 | Date |
|---|---|---|---|---|---|---|---|
| `submissions/trackA_opus55_high_v2.csv` (Claude Opus 5.5 high, 854 px, geometry + direct) | A | **0.763** | .801 | .810 | .703 | .738 | 2026-10-09 |
| `submissions/trackA_probe2_geo_nonlab3d.csv` (v2 with geometry on 3D non-lab) | A | 0.737 | .798 | .810 | .673 | .668 | 2026-10-09 |
| `submissions/trackA_probe3_s2maxext_d2denseoff_labdirect.csv` (S2 longest-extent prior, D2 dense off, direct on lab 3D) | A | **0.764** | .803 | .810 | .715 | .727 | 2026-10-09 |

Public leaderboard snapshot 2026-10-09 16:48 UTC (before our uploads): Track A 1st 0.842, 2nd 0.835, 3rd 0.825,
about ten teams at 0.80-0.81, 20th 0.769; Track B 1st 0.803, 2nd 0.772, 3rd 0.756. Probes 4-6 and two diagnostic
uploads are described in [research/PROBES.md](research/PROBES.md).

Validation (480p, 159 questions) over-predicted D2 (.916 vs .810) and S3 (.784 vs .703) and
under-predicted S2 (.709 vs .801): its categories have only 32-47 questions each.
Probe 2 confirms Claude's direct estimate beats geometry on 3D non-lab videos (S3 -.030, D3 -.070 with geometry).
Probe 3: longest-extent S2 priors +.002, dense motion off on D2 +.000, direct answers on lab 3D +.012 on S3 but -.011 on D3.
`submissions/trackA_v3_best_per_category.csv` takes each category's best measured rows (S2 and S3 from probe 3, D2 and D3 from v2): expected ~.767.

## Results so far (validation, 159 questions)

| Pipeline | MRA | S2 | D2 | S3 | D3 | Cost |
|---|---|---|---|---|---|---|
| Official GPT-5.1 zero-shot baseline | 0.486 | | | | | |
| Track A: Claude Opus 5.5, medium effort | 0.766 | .709 | .951 | .709 | .694 | $1.52 |
| Track A: Claude Opus 5.5, high effort | **0.782** | .706 | .916 | .784 | .723 | $1.87 |
| Track A: agentic tool loop (full-res, medium) | 0.743 | .663 | .943 | .705 | .660 | $8.69 |

Numbers above as recorded when each run was made. With the current code (geometry with the ICI velocity
window, `qp.refine` at the 480p scale, dense motion tracks by default) high effort replays at 0.781
(`--dense off`: 0.783), and on the full-resolution copies (480p records rescaled, what the 854 px test run
sees) at 0.784; the run x dense-variant table and the test-submission steps are in
[docs/TRACK_A.md](docs/TRACK_A.md).

About 8% of validation labels contradict their own video or each other (listed in `qp/combine.py`
and the analysis notes); excluding them, high effort scores ~0.81. Projected test MRA from the
validation per-source rates and the test mix: ~0.80.

## How it works (Track A)

1. **One request per video** (`qp/claude_annotate.py`, `scripts/run_claude.py`): frames (16 uniform +
   frames at every mentioned time) and all the video's questions go to Claude Opus 5.5, which returns
   per question a structured spec (what to measure), pixel annotations (extent endpoints, motion
   points, boxes per frame) and its own direct estimate. Batch API (50% off), structured outputs.
2. **Local post-steps** (`run_claude.post_steps`, no API cost): optical-flow refinement of motion-prior
   tracks (`qp/refine.py`), then dense per-frame tracks for motion quantities (`qp/dense_track.py`,
   `--dense motion`, the default; see [docs/TRACK_A.md](docs/TRACK_A.md)).
3. **Geometry in code** (`qp/geometry.py`): the prior sets the metric scale (2D: metres per pixel;
   3D: pinhole camera with the focal length solved from the prior and the lab rig's ~84° FOV as a
   prior), motion from polynomial fits over time, units converted to the asked unit.
4. **Answer selection** (`qp/combine.py`): geometry unless implausible, far from the direct estimate,
   or a 3D solve that had to assume the target's depth (then Claude's direct estimate).
5. Spend is capped by `qp/budget.py`: every request is held at its worst case until its usage is
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

Details, costs per run and the measured dense-tracking table: [docs/TRACK_A.md](docs/TRACK_A.md).
