# Track A: producing a test submission

Track A answers every question in three steps:

1. Claude Opus 5.5 annotates each video in one request (`scripts/run_claude.py`). It returns the
   question specs, pixel tracks and its own direct answers. This step is paid and uses the Batch API.
2. Local CPU post-steps refine the tracks (`run_claude.post_steps`, no API cost), then `qp/geometry.py`
   solves each question.
3. `qp/combine.py` picks either the geometry answer or Claude's direct answer.

## The current best pipeline

| Setting | Value |
|---|---|
| Prompt | v1 |
| Effort | high |
| Frames | 16 uniform, plus frames at the mentioned times (32 at most) |
| Frame size | long edge capped at 854 px (`--max-side 854`), the size the prompt was validated at |
| Answer rule | `assumed_src` (default) |
| Post-steps | `qp.refine` (optical flow on motion-prior tracks), then `qp.dense_track` on the motion tracks (`--dense motion`, now the default) |

```bash
# 1. Annotate the test set (paid, batch, 50% off). A rerun resumes from batch.json and the ledger.
#    With the default $200 cap, videos wait until earlier batches are collected (see "Cost" below).
.venv/bin/python scripts/run_claude.py --split test --name test_v1_high_854 --effort high --prompt-version v1 \
    --max-side 854 --mode batch --chunk-videos 20 --est-output-per-question 1200

# 2. Re-score with the current code: the same command. Once every video is cached it sends nothing and
#    rewrites runs/test_v1_high_854/test.csv. It prints "post-steps: prior refinement on, dense tracking
#    motion"; dense results are cached under runs/_dense_cache/test. --dense off gives the annotator's
#    tracks only.
.venv/bin/python scripts/run_claude.py --split test --name test_v1_high_854 --effort high --prompt-version v1 \
    --max-side 854 --mode batch

# 3. Build the submission: fills the official template and checks ids, numbers and size.
.venv/bin/python scripts/make_submission.py runs/test_v1_high_854/test.csv submissions/test_v1_high_854.csv
```

The `test_v1_high_854` process that is running now was started at 13:03, before these changes. When it
finishes, its `test.csv` uses the code it loaded then: the old refine, no dense step, and the geometry
before ICI. Run step 2 again after it finishes. A replay must repeat the run's settings (model, effort,
frames, prompt version, max side), or it refuses to run. `--dense` and `--rule` change nothing on the API
side.

Combining runs (`scripts/combine_runs.py`, a median in log space) does not help. On validation, med +
high scores 0.779 and med + high + med2 scores 0.779, against 0.782 for high alone. So one high run is
the recommendation.

## Cost

### API cost per run

Measured on validation (24 videos, 159 questions), batch prices. The test-set column scales the cost
per question to 3289 questions on 568 videos.

| Run | Validation | Per question | Test set |
|---|---|---|---|
| v1 low (854 px) | $1.12 | $0.0070 | ~$23 |
| v1 medium (854 px) | $1.52 | $0.0095 | ~$31 |
| **v1 high (854 px)** | **$1.87** | **$0.0117** | **~$39** |
| v1 xhigh (854 px) | $4.72 | $0.0297 | ~$98 |
| v2 high (1280 px, 44 frames, full-res) | $4.36 | $0.0274 | ~$90 |
| agent loop, medium (full-res) | $8.69 | $0.055 | ~$180 |

The test run's own estimate at launch was $45.34, with 1200 output tokens per question.

The budget holds each batch at its worst case (input plus max_tokens) until the batch is collected. For
the whole test set that worst case is $205, above the $200 cap. The run therefore submits in waves: 359
of 568 videos are in flight, and 209 wait for holds to be released. Actual spend stays near the
estimate.

### CPU post-steps (4 cores, full-resolution copies)

| Step | Validation (24 videos) | Test set (568 videos) |
|---|---|---|
| `qp.refine` | ~1 min | ~25 min, recomputed on every replay |
| dense motion | ~1–1.5 min | ~35 min the first time; replays read the cache |

## Measured: dense variants on every cached run

### What was run

Each run was scored with `scripts/dense_tracks.py --what motion|size|both`. The "none" rows are
`run_claude.build_results` without the dense step. All rows use one frozen copy of the code: commit
d43d6e9, which includes the ICI geometry of 42a0314. The scratch scripts are in
`/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/integ/`, with outputs in
`out2/`.

| Group | Runs | Split |
|---|---|---|
| 480p | `val_opus_{low,med,med2,high,xhigh}` | `val`, prompt v1 |
| Simulated full-res (`sim_*`) | the same records, with the image size and scale set to the full-resolution copy | `val_hires` |
| Real full-res | `val_hr_v2_high` (v2, 1280 px) and `val_hr_agent_med` (agent loop) | `val_hires` |

The simulated full-res runs give the annotator the same view as `test_v1_high_854` (854 px frames
from full-res videos), while the tracking and geometry run on the full-res pixels.

### Columns

- **Δ** is the change in final MRA against the "none" row of the same run.
- **"none, old refine"** is the old `qp/refine.py`, before the change described under "Decisions".
- **MRA excl. suspect GT** leaves out the 12 suspect qids: 403, 2349, 2607, 3049, 3051, 1123, 1130,
  1354, 1355, 3054, 139 and 2276.
- **dense tracks** counts questions with at least one accepted dense track.

| run | variant | MRA | Δ | S2 | D2 | S3 | D3 | geo MRA | MRA excl. suspect GT | dense tracks |
|---|---|---|---|---|---|---|---|---|---|---|
| val_opus_low | none, old refine | 0.698 | +0.000 | 0.684 | 0.916 | 0.463 | 0.730 | 0.552 | 0.728 | 0 |
| val_opus_low | none | 0.698 |  | 0.684 | 0.916 | 0.463 | 0.730 | 0.552 | 0.728 | 0 |
| val_opus_low | **motion** | 0.699 | +0.001 | 0.697 | 0.911 | 0.458 | 0.730 | 0.554 | 0.733 | 62 |
| val_opus_low | size | 0.693 | -0.005 | 0.675 | 0.908 | 0.460 | 0.730 | 0.544 | 0.723 | 79 |
| val_opus_low | both | 0.694 | -0.004 | 0.684 | 0.908 | 0.453 | 0.730 | 0.546 | 0.727 | 103 |
| val_opus_med | none, old refine | 0.767 | +0.000 | 0.713 | 0.951 | 0.709 | 0.694 | 0.719 | 0.797 | 0 |
| val_opus_med | none | 0.767 |  | 0.713 | 0.951 | 0.709 | 0.694 | 0.719 | 0.797 | 0 |
| val_opus_med | **motion** | 0.768 | +0.001 | 0.716 | 0.954 | 0.709 | 0.694 | 0.716 | 0.799 | 66 |
| val_opus_med | size | 0.756 | -0.011 | 0.688 | 0.938 | 0.705 | 0.694 | 0.704 | 0.787 | 106 |
| val_opus_med | both | 0.758 | -0.009 | 0.694 | 0.941 | 0.705 | 0.694 | 0.702 | 0.788 | 129 |
| val_opus_med2 | none, old refine | 0.768 | +0.000 | 0.703 | 0.884 | 0.753 | 0.730 | 0.713 | 0.798 | 0 |
| val_opus_med2 | none | 0.768 |  | 0.703 | 0.884 | 0.753 | 0.730 | 0.713 | 0.798 | 0 |
| val_opus_med2 | **motion** | 0.774 | +0.007 | 0.725 | 0.884 | 0.753 | 0.734 | 0.713 | 0.804 | 63 |
| val_opus_med2 | size | 0.760 | -0.008 | 0.681 | 0.873 | 0.749 | 0.736 | 0.707 | 0.790 | 98 |
| val_opus_med2 | both | 0.767 | -0.000 | 0.706 | 0.873 | 0.749 | 0.740 | 0.707 | 0.796 | 124 |
| val_opus_high | none, old refine | 0.783 | +0.000 | 0.709 | 0.916 | 0.784 | 0.723 | 0.738 | 0.813 | 0 |
| val_opus_high | none | 0.783 |  | 0.709 | 0.916 | 0.784 | 0.723 | 0.738 | 0.813 | 0 |
| val_opus_high | **motion** | 0.781 | -0.002 | 0.725 | 0.916 | 0.758 | 0.726 | 0.734 | 0.810 | 73 |
| val_opus_high | size | 0.777 | -0.006 | 0.691 | 0.905 | 0.781 | 0.730 | 0.726 | 0.807 | 99 |
| val_opus_high | both | 0.775 | -0.009 | 0.703 | 0.905 | 0.758 | 0.732 | 0.721 | 0.803 | 122 |
| val_opus_xhigh | none, old refine | 0.657 | +0.000 | 0.672 | 0.838 | 0.793 | 0.326 | 0.614 | 0.679 | 0 |
| val_opus_xhigh | none | 0.657 |  | 0.672 | 0.838 | 0.793 | 0.326 | 0.614 | 0.679 | 0 |
| val_opus_xhigh | **motion** | 0.664 | +0.007 | 0.697 | 0.843 | 0.788 | 0.328 | 0.610 | 0.686 | 50 |
| val_opus_xhigh | size | 0.652 | -0.005 | 0.656 | 0.832 | 0.793 | 0.328 | 0.607 | 0.673 | 93 |
| val_opus_xhigh | both | 0.659 | +0.001 | 0.678 | 0.838 | 0.788 | 0.330 | 0.601 | 0.680 | 111 |
| sim_val_opus_low | none, old refine | 0.644 | -0.023 | 0.684 | 0.700 | 0.463 | 0.730 | 0.534 | 0.674 | 0 |
| sim_val_opus_low | none | 0.667 |  | 0.684 | 0.792 | 0.463 | 0.730 | 0.557 | 0.697 | 0 |
| sim_val_opus_low | **motion** | 0.702 | +0.035 | 0.712 | 0.905 | 0.458 | 0.732 | 0.557 | 0.731 | 63 |
| sim_val_opus_low | size | 0.655 | -0.012 | 0.666 | 0.768 | 0.458 | 0.730 | 0.543 | 0.686 | 83 |
| sim_val_opus_low | both | 0.693 | +0.026 | 0.703 | 0.884 | 0.453 | 0.732 | 0.546 | 0.721 | 108 |
| sim_val_opus_med | none, old refine | 0.745 | -0.022 | 0.713 | 0.865 | 0.709 | 0.694 | 0.698 | 0.776 | 0 |
| sim_val_opus_med | none | 0.767 |  | 0.713 | 0.954 | 0.709 | 0.694 | 0.719 | 0.798 | 0 |
| sim_val_opus_med | **motion** | 0.773 | +0.005 | 0.731 | 0.957 | 0.709 | 0.694 | 0.721 | 0.800 | 66 |
| sim_val_opus_med | size | 0.754 | -0.014 | 0.694 | 0.919 | 0.705 | 0.698 | 0.702 | 0.785 | 112 |
| sim_val_opus_med | both | 0.761 | -0.007 | 0.719 | 0.922 | 0.705 | 0.698 | 0.706 | 0.789 | 135 |
| sim_val_opus_med2 | none, old refine | 0.751 | -0.016 | 0.703 | 0.819 | 0.753 | 0.730 | 0.697 | 0.782 | 0 |
| sim_val_opus_med2 | none | 0.768 |  | 0.703 | 0.884 | 0.753 | 0.730 | 0.713 | 0.798 | 0 |
| sim_val_opus_med2 | **motion** | 0.779 | +0.011 | 0.741 | 0.884 | 0.753 | 0.736 | 0.715 | 0.804 | 64 |
| sim_val_opus_med2 | size | 0.759 | -0.008 | 0.697 | 0.862 | 0.749 | 0.730 | 0.705 | 0.789 | 103 |
| sim_val_opus_med2 | both | 0.770 | +0.003 | 0.734 | 0.862 | 0.749 | 0.736 | 0.706 | 0.797 | 129 |
| sim_val_opus_high | none, old refine | 0.763 | -0.021 | 0.709 | 0.835 | 0.784 | 0.723 | 0.718 | 0.793 | 0 |
| sim_val_opus_high | none | 0.784 |  | 0.709 | 0.919 | 0.784 | 0.723 | 0.739 | 0.814 | 0 |
| sim_val_opus_high | **motion** | 0.784 | +0.000 | 0.734 | 0.919 | 0.758 | 0.726 | 0.737 | 0.813 | 73 |
| sim_val_opus_high | size | 0.777 | -0.007 | 0.694 | 0.905 | 0.781 | 0.726 | 0.730 | 0.807 | 112 |
| sim_val_opus_high | both | 0.778 | -0.005 | 0.725 | 0.905 | 0.756 | 0.728 | 0.729 | 0.807 | 135 |
| sim_val_opus_xhigh | none, old refine | 0.659 | +0.000 | 0.672 | 0.846 | 0.793 | 0.326 | 0.616 | 0.681 | 0 |
| sim_val_opus_xhigh | none | 0.659 |  | 0.672 | 0.846 | 0.793 | 0.326 | 0.616 | 0.681 | 0 |
| sim_val_opus_xhigh | **motion** | 0.665 | +0.006 | 0.697 | 0.849 | 0.788 | 0.328 | 0.611 | 0.687 | 47 |
| sim_val_opus_xhigh | size | 0.655 | -0.004 | 0.659 | 0.843 | 0.793 | 0.326 | 0.613 | 0.676 | 97 |
| sim_val_opus_xhigh | both | 0.663 | +0.004 | 0.694 | 0.846 | 0.786 | 0.328 | 0.609 | 0.685 | 113 |
| val_hr_v2_high | none, old refine | 0.782 | +0.001 | 0.706 | 0.922 | 0.774 | 0.726 | 0.745 | 0.810 | 0 |
| val_hr_v2_high | none | 0.781 |  | 0.706 | 0.916 | 0.774 | 0.726 | 0.743 | 0.808 | 0 |
| val_hr_v2_high | **motion** | 0.782 | +0.002 | 0.706 | 0.916 | 0.779 | 0.728 | 0.736 | 0.809 | 91 |
| val_hr_v2_high | size | 0.779 | -0.002 | 0.688 | 0.927 | 0.774 | 0.726 | 0.740 | 0.807 | 108 |
| val_hr_v2_high | both | 0.780 | -0.001 | 0.694 | 0.922 | 0.779 | 0.726 | 0.733 | 0.807 | 142 |
| val_hr_agent_med | none | 0.743 |  | 0.666 | 0.941 | 0.702 | 0.664 | 0.730 | 0.775 | 0 |
| val_hr_agent_med | **motion** | 0.745 | +0.002 | 0.672 | 0.943 | 0.702 | 0.662 | 0.728 | 0.778 | 69 |
| val_hr_agent_med | size | 0.736 | -0.007 | 0.641 | 0.941 | 0.700 | 0.664 | 0.724 | 0.769 | 51 |
| val_hr_agent_med | both | 0.739 | -0.004 | 0.650 | 0.943 | 0.700 | 0.662 | 0.723 | 0.771 | 89 |

### Mean change by group

The confidence interval is a 90% interval from a video-level bootstrap (resampling videos, 2000
draws).

| Variant | Group | Mean Δ | Runs with Δ > 0 | 90% CI |
|---|---|---|---|---|
| motion | 480p (5 runs) | +0.003 | 4 of 5 | −0.004 .. +0.009 |
| motion | sim full-res (5 runs) | +0.012 | 5 of 5 | +0.000 .. +0.025 |
| motion | real full-res (2 runs) | +0.002 | 2 of 2 | −0.001 .. +0.005 |
| size | 480p | −0.007 | 0 of 5 | −0.015 .. −0.002 |
| size | sim full-res | −0.009 | 0 of 5 | −0.017 .. −0.003 |
| size | real full-res | −0.004 | 0 of 2 | −0.014 .. +0.003 |
| both | 480p | −0.004 | 1 of 5 | −0.015 .. +0.004 |
| both | sim full-res | +0.004 | 3 of 5 | −0.009 .. +0.020 |
| both | real full-res | −0.003 | 0 of 2 | −0.010 .. +0.004 |

The `val_opus_xhigh` D3 score of 0.326 comes from its records: 2 videos hit max_tokens and 1 is
partial. The questions a max_tokens response completed before the cut are now used
(`claude_annotate.salvage_questions`). This recovers 1 question for xhigh: simulation_0060 qid 1343. The
other cut-off record has no text. The record keeps its max_tokens status, so `--retry-failed` still
re-sends the video.

## Decisions

### Dense motion becomes the default (`--dense motion`)

The criterion was fixed before the full-res results were in. A variant becomes the default only if:

1. its mean Δ is above 0 in both the 480p and the simulated full-res groups;
2. Δ is above 0 in at least 4 of 5 runs in each group;
3. no run loses more than 0.01.

Motion meets all three. On 480p it gains +0.003 (4 of 5 runs), on simulated full-res +0.012 (5 of 5),
and on real full-res +0.002 (2 of 2); its worst run is −0.002. Size and both do not meet it.

The gain is small and mostly noise-level. The consistent part is S2, at +0.003 to +0.037 in every run:
in 2D, dense sub-pixel target tracks help the geometry fits. S3 loses 0.026 on the high runs, mostly
from qids 2721 and 2722: `path_length` on the rolling tennis balls of `captured_0034as`. The dense path
there is correct; the sparse track's ~55 cm was a fit artefact, and every speed in that clip is about
30% under the ground truth either way.

On simulated full-res, `sim_val_opus_low` gains +0.035. This comes from dense tracks replacing priors
that the geometry's noise floor fails to catch at full resolution (see "Open issues").

This changes replays. With default settings, `run_claude.py` on `val_opus_high` now prints 0.781 instead
of 0.783; it says so in a "post-steps" line, and `--dense off` restores the old numbers. Cached run CSVs
in `runs/` were not rewritten.

### Dense size and both stay off

Size is negative in every one of the 12 runs (−0.002 to −0.014). GrabCut-measured extents come out
smaller than Claude's on some size priors. On qids 2272–2275 they are about 5% short, where Claude's own
extents were within 1%. Those shorter priors scale every answer of the video.

### `qp/refine.py` now works at the 480p scale (resolution fix, not a dense variant)

The pixel thresholds of the optical-flow prior refinement (FB 1 px, LK window 21 px, deviation 30 px,
3 px grid) were set on 480p frames. On the full-resolution copies the refinement rejected 2 of the 9
accepted priors:

- `internet_0013`: `camera_not_static`;
- `simulation_0196`, a 2560² copy: forward-backward error above 1 px.

That cost about 0.02 on every simulated full-res run; see the "none, old refine" rows. Frames larger
than 480p are now tracked downscaled to a 480 px short side, and the path is mapped back to original
pixels (`WORK_SHORT`).

- **480p validation:** unchanged by construction, since every clip there has a 480 px short side.
- **Simulated full-res:** acceptance matches 480p exactly, recovering +0.016 to +0.023 per run.
- **Real `val_hr_v2_high`:** −0.001, because 2 more priors are accepted with neutral effect.

`tests/test_refine.py` has a 1280×960 test of the mapping.

## Contracts (checked across the three new modules)

- **Coordinates.** Every module writes RoleTrack/Obs in original video pixels, with t = frame / dataset
  fps:
  - `qp.claude_annotate` maps sent pixels back by `meta.scale`.
  - The agent's records use `scale` 1.0.
  - The verify pass maps crop pixels through each image label's formula.
  - `qp.dense_track` and `qp.refine` take and return original pixels.
- **Geometry and selection.** `run_claude.build_results`, `claude_verify.solve_question` and
  `select`, and `claude_agent.AgentSession.geometry` all call `qp.geometry.solve` the same way. Each
  passes `camera_fov_deg=LAB_FOV_DEG` only for 3D lab clips, and each selects through
  `qp.combine.choose(DEFAULT_RULE)` with the same `GEO_MAX_SI` guard.
- **Ledger.** Run, agent and verify requests all go through `qp.budget`: `reserve` at the worst case,
  `record` with run, split and video_id, and `hold`/`release` for batches. Agent and verify add a kind or
  turn field.
- **Agent tracking.** The agent's `track` tool really uses `qp.dense_track`: `dense_motion` between
  two or more anchors, and `track_pass` outward. A test now asserts `between_anchors == "dense_motion"`.
  In the real agent run `val_hr_agent_med`, 19 of 38 multi-anchor tracks used `dense_motion`, and the
  other 19 fell back to chained passes.
- **Verify input.** `scripts/dense_tracks.py --tracks-out` now writes the JSON that
  `scripts/run_claude_verify.py --dense` reads, so the verifier sees the same dense tracks.

## Open issues

- **Geometry noise floor at full resolution.** `PX_NOISE_FLOOR` (1 px) is in original pixels, but an
  annotator's ~1 px error is in the pixels it saw. With `--max-side 854` on a 1080p–4K video, the floor
  is 2–4.5 times too small, so a near-static prior passes `prior_motion_below_noise`.
  - Example: `internet_0013` in `sim_val_opus_low` has a pedestrian prior with 2 points 6 px apart at
    480p. Its 6 D2 answers go to 0, which is −0.031 MRA.
  - Proposed fix: `solve(..., seen_scale=meta["scale"])` with floor = PX_NOISE_FLOOR / seen_scale.
  - It was not applied here because `qp/geometry.py` was being edited in parallel (the ICI window).
- **Unverified videos in the verify pass.** `scripts/run_claude_verify.py` scores unverified videos
  with `run_claude.build_results` without the dense step, and passes no `--dense` tracks to them.
  Pass-1 numbers in a verify run can therefore differ slightly from the run's CSV.
- **Pending full-res runs.** `val_hr_v1_high` (v1 at native resolution), `val_hr_v2_med` and
  `val_v2_high` were still in their batches. To evaluate one when it lands, at no API cost:

  ```bash
  .venv/bin/python scripts/run_claude.py --split val_hires --name val_hr_v1_high --effort high --prompt-version v1   # replay
  for w in motion size both; do .venv/bin/python scripts/dense_tracks.py --name val_hr_v1_high --split val_hires --what $w; done
  ```

- **v2 versus v1 at full resolution.** On the real full-res run, v2 high (0.781–0.782) matches
  simulated v1 high at 854 px (0.784) within noise, at 2.3 times the cost. v1 at 854 px stays the test
  configuration until the v1 native-resolution run says otherwise.
