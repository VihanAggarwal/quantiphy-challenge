# Fixed confidence gates: geometry vs Claude's direct answer per row (Gemini's "uncertainty-aware meta-router")

Directory: `research/gates/`. Free replay of cached Claude runs only (no API calls). Written 2026-10-14.

## PRE-REGISTRATION (written before any held-out evaluation was run)

### Hypothesis
Learned per-question routers lost .017-.047 under leave-one-video-out (too many fitted parameters on 24 videos).
A small number of FIXED, physically motivated gates, using only input-time signals, might still capture part of the
+.031 best-of oracle: trust geometry where its own measurement is stable and well conditioned and Claude's direct
answers are unstable; hedge geometry with the direct answer where the geometry's own pixel measurement is noisy.

### Signals (all from test inputs and cached runs; no labels)
Runs: a = `runs/test_v1_high_854` (all rows), b = `runs/test_3dnl_v1_high_b`, c = `runs/test_3dnl_v2_high`
(3D non-lab only). 3D non-lab geometry per run = `research/simfov/out/replay.csv` `geo_old` (f solved from the
prior; carries `sens_old` = |d ln prior / d ln f|, `fov_old`, `method_old`, `flags_old`).
- `dmed`, `gmed`: log-median over runs of the direct / geometry answers.
- `R_dir`, `R_geo`: max - min of log(answer) over the 3 runs (run disagreement).
- `gd` = |log(geo / direct)|.
- Track uncertainty from Claude's own pixel track of run a (no refinement, no dense tracking), per role
  (target, prior), `u` = relative standard error of the measured quantity:
  size / extent: coefficient of variation of the extent length over its observations (>= 3 obs, else unknown);
  speed at a time: s.e.(v)/|v| of qp.geometry's local fit (+-0.5 s); acceleration at a time: s.e.(a)/|a| of the
  local fit (half-width 0.75 s, degree <= 4); speed / acceleration without a time (or with a window): the same
  ratio from one degree-2 fit over the window or the whole track; displacement / path length: sqrt(2) x residual
  sigma / |displacement|. Two-object distances: unknown. `u_geo` = sqrt(u_target^2 + u_prior^2), unknown terms = 0
  (so only a MEASURED instability can fire a gate), capped at 1.
- Geometry flags of run a: `time_outside_track` (asked time outside the tracked span, clamped),
  `window_extrapolated`, `gravity_from_target_track`.

### Gate rules and thresholds (fixed a priori; no fitting)
**G3D (primary)** - 3D non-lab rows (S3/D3, simulation and segmented), default = `dmed` (Claude direct, median of 3).
Fire when ALL of:
1. 3 valid direct answers and 3 valid geometry answers;
2. geometry well conditioned in every run: `method_old == 3d_focal_from_prior`, `sens_old >= 0.3`, no assumed-depth
   flag (qp.combine.ASSUMED_FLAGS) in `flags_old`, solved horizontal FOV `fov_old` within [8, 105] deg (the range of
   the simulation cameras);
3. geometry agrees across the 3 independent annotations: `R_geo <= 0.10`;
4. Claude's direct answers disagree: `R_dir >= 0.20`;
5. the geometry's own track noise is small: `u_geo <= 0.10`.
Action: `gm(dmed, gmed)` (geometric mean; a hedge, not a full switch).

**G2D (primary)** - 2D rows whose routed answer is geometry (S2 static, D2 all), default = geometry
(D2: refine-off / dense-off geometry as in the submission, replayed from run a's records; S2 static: run a's geometry).
Fire when ALL of:
1. valid geometry and direct answers;
2. `gd >= 0.10` (otherwise a switch hardly moves the answer);
3. the geometry's own measurement is unstable: `u_geo >= 0.15` OR a flag in {time_outside_track,
   window_extrapolated, gravity_from_target_track}.
Action: `gm(geometry, direct)`.

No lab gate: there are no exactly-known stated-fact rows in lab clips in the held-out harness, only 35 validation
lab rows (19 static), and the leaderboard showed S3 lab static -> direct at -.074 per row (U4); lab is left as is.
Secondary variants (reported only, never used for the verdict or the candidate): G3D with action `gmed` (full
switch); G3D without condition 4; G2D with action `direct`.

### Evaluation
Held-out rows: (1) validation labels of the identical test questions (`research/gates/evalsets.py`, val), and (2)
the exactly-known stated-fact rows on test (qp.postprocess "facts" rule; label = stated value), with the validation
label taken where a row is in both. Labels are read only for scoring; never written into an answer.
Base on held-out rows = the pre-rule routed pipeline answer (3D non-lab: `dmed`; 2D: geometry as above).
Score = qp.mra.item_scores. Report per gate: number of held-out rows gated, mean item delta (gated - base) on those
rows, clip bootstrap 90% CI (clips = video_id without `_segmented`, 4000 resamples, seed 0), per category.

### Kill test (pass bar), per primary gate
PASS only if ALL of:
- >= 10 held-out rows gated (else INCONCLUSIVE);
- mean item delta on gated held-out rows >= +0.010 and its clip-bootstrap 90% CI lower bound > 0;
- expected overall gain >= +0.002, computed as sum over categories of (candidate rows changed in scored test rows of
  that category) x (pooled mean item delta on held-out gated rows) / (4 x N_cat), N = S2 553, D2 1137, S3 538,
  D3 933;
- no category loss: the per-category mean delta on held-out gated rows is >= 0 for every category with >= 3
  held-out gated rows.
Candidate (only for a passing gate): combo3 rows that still hold the raw routed value (3D non-lab: combo3 == dmed;
2D: combo3 == the routed geometry, rtol 1e-6) get the gated value; family / fact / rule rows are never touched;
built with `research/merge/merge_skip.py` on `submissions/trackA_combo3_on_combo2.csv`.

---
(Everything below this line was written after the evaluation ran.)

## Stage 1 result (pre-registered gates as written above)
`.venv/bin/python research/gates/evaluate.py` (output: `research/gates/out/evaluate.txt`):
| gate | fires on test (all / eligible scored rows) | held-out rows gated | delta on gated held-out rows | verdict |
|---|---|---|---|---|
| G3D (primary) | 29 / 10 (D3 7, S3 3) | 4 (facts, 2 clips) | +0.000 | INCONCLUSIVE (n < 10); cannot reach +.002 overall with 10 rows |
| G2D (primary) | 11 / 9 (D2 9) | 0 | - | INCONCLUSIVE (n = 0); cannot reach +.002 overall with 9 rows |
| G3D_full (secondary) | 29 / 10 | 4 | -0.100 | - |
| G3D_no4 (secondary: no direct-spread condition) | 232 / 52 (D3 27, S3 25) | 71 (9 val, 62 facts; 18 clips) | +0.0028, 90% CI [-0.005, +0.011] | below the +.01 bar; exp. overall +0.0001 |
The conjunction of five conditions is too narrow: Claude's extents rarely vary across frames (median extent CV 0),
and the 3 geometry runs rarely agree within 10% while the 3 direct runs disagree by >= 20%. As pre-registered,
neither primary gate can pass (both would need >= ~40 rows at +.1 per row).

## STAGE 2 PRE-REGISTRATION (written after stage 1, before any stage-2 evaluation)
Stage 1 showed only that the gates were too narrow (fire counts are test-input facts, not labels). Seen from labels
so far: only the stage-1 numbers above (4 G3D rows, 71 G3D_no4 rows, their per-clip deltas). Stage 2 widens the
gates using input-only coverage, fixes everything below before running, and is evaluated once.
**G3D-2**: 3D non-lab; geometry well conditioned in all 3 runs (as in G3D condition 2); `R_geo <= 0.15`;
`u_geo <= 0.15`; and `R_dir >= R_geo` (Claude's direct answers are less consistent across runs than the geometry is).
Action `gm(dmed, gmed)`.
**G2D-2**: 2D rows routed to geometry; `gd >= 0.10`; `u_geo >= 0.05` (about the 90th percentile of 2D u_geo on
test inputs) or an instability flag. Action `gm(geometry, direct)`.
**GLAB-2**: S3 lab static rows (routed to geometry, lab camera FOV); `gd >= 0.10`; `u_geo >= 0.15` or an
instability flag. Action `gm(geometry, direct)`. Validation labels only (no lab facts).
Same kill test as stage 1 (n >= 10 held-out gated rows; delta >= +.010 with 90% CI lower bound > 0; expected
overall >= +.002; no category loss), per gate. Two stage-level caveats are part of the verdict: (1) stage 2 is a
second look, so a pass is weaker evidence than a stage-1 pass; (2) a PASS still needs a leaderboard check before it
is merged into a final submission.
Diagnostic (reported, never used to build a candidate): on held-out rows, mean item delta of gm / full switch vs the
routed default, by terciles of each signal (3D non-lab: R_dir, R_geo, u_geo, wellcond, gd; 2D: gd, u_geo), to show
whether any input-time signal carries routing information at all.

## Stage 2 result
`.venv/bin/python research/gates/evaluate2.py` (output: `research/gates/out/evaluate2.txt`):
| gate | fires on test (all / eligible scored) | held-out gated | delta on gated held-out rows (clip bootstrap 90%) | exp. overall | verdict |
|---|---|---|---|---|---|
| G3D-2 | 185 / 48 (D3 28, S3 20) | 51 (4 val, 47 facts; 18 clips) | +0.0059 [-0.0036, +0.0156]; D3 +.0056 (36), S3 +.0067 (15) | +0.0001 | FAIL |
| G2D-2 | 41 / 20 (D2 20) | 1 | -0.100 | -0.0004 | INCONCLUSIVE |
| GLAB-2 | 4 / 0 | 0 | - | 0 | INCONCLUSIVE |
Even taken at face value, G3D-2 is worth +.0001 overall: only 48 scored 3D non-lab rows still hold the raw
direct median (the rest already carry family facts, K scale, pooling), and +.006 per row on 48 rows is nothing.

## Diagnostics: do the input-time signals carry routing information? (held-out rows, no fitting)
3D non-lab (145 held-out rows: direct median .792, gm(direct, geometry) .746, geometry .683). Mean item delta vs
the direct median, by tercile of each signal:
| signal | low tercile: gm / geometry | mid | high |
|---|---|---|---|
| R_dir (direct spread over 3 runs) | -.018 / -.049 | -.062 / -.162 | -.060 / -.119 |
| R_geo (geometry spread over 3 runs) | +.004 / +.002 | -.029 / -.081 | -.117 / -.252 |
| u_geo (track noise) | -.043 / -.073 | .000 / -.015 | -.098 / -.242 |
| gd (geometry vs direct disagreement) | +.002 / +.002 | -.008 / -.023 | -.135 / -.310 |
| well conditioned in all 3 runs (113 rows) vs not (32) | -.027 / -.076 vs -.119 / -.228 | | |
- The premise "Claude's direct answer is unstable -> trust geometry" is refuted: where the 3 direct runs disagree most,
  geometry still loses (-.06 as gm, -.12 as a full switch). Direct-run spread marks hard questions, not questions
  where geometry is better.
- Geometry stability signals (low R_geo, low gd) only find rows where geometry ~= direct (delta ~0): when geometry
  is consistent it agrees with Claude, so switching gains nothing; when it disagrees it is usually the one that is
  wrong. No tercile of any signal shows geometry or the blend ahead by more than +.004.
2D (80 held-out rows, geometry .866): where geometry and direct disagree, geometry wins (gd .05-.10: direct -.117;
.10-.25: -.100; > .25: -.171, 19 rows); on rows with the noisiest tracks (u_geo > .05, 15 rows) direct still loses
-.140. So "geometry track unstable -> direct" is refuted in 2D as well. (Side note, small: on the 10 held-out S2
simulation motion rows where they disagree (3 clips), geometry .58 > gm .49 > direct .43, against the leaderboard's
+.005 for S2 sim motion -> gm on 225 scored rows; the leaderboard is the stronger evidence, no action.)

## Verdict: FAIL (no candidate built)
- Stage 1 (pre-registered gates): both primary gates INCONCLUSIVE by the n >= 10 rule and unable to reach +.002 by
  construction (29 / 11 rows fire on all of test, 10 / 9 eligible scored rows).
- Stage 2 (widened, re-registered): G3D-2 FAIL (+.006 on 51 held-out rows, CI includes 0, +.0001 overall); G2D-2 and
  GLAB-2 INCONCLUSIVE (1 and 0 held-out rows) and worth < .0005 overall even if right.
- The diagnostics explain why: none of the physically motivated confidence signals (3-run agreement of direct or
  geometry answers, track extent / motion-fit noise, f conditioning, geometry/direct disagreement) separates the rows
  where the other method is better. This matches the earlier finding that learned routers lose under LOVO: the
  +.031 oracle is not reachable with input-time signals of this kind. Do not spend uploads on gating.
- Expected overall gain of the lever: ~0 (G3D-2 at face value +.0001).

## Commands (all free; no API calls)
```
.venv/bin/python research/gates/base_table.py      # per-row table: combo3, runs a/b/c geo/direct  -> out/base.csv
.venv/bin/python research/gates/evalsets.py        # held-out labels: 131 val + 129 facts rows      -> out/evalsets.csv
ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=<scratch>/ledger.jsonl \
  .venv/bin/python research/gates/features.py      # refine-off replay + track signals (4m41s CPU) -> out/features.csv
.venv/bin/python research/gates/evaluate.py        # stage 1 -> out/evaluate.txt
.venv/bin/python research/gates/evaluate2.py       # stage 2 + diagnostics -> out/evaluate2.txt, out/gated2.csv
```
Notes: 3D non-lab geometry per run comes from `research/simfov/out/replay.csv` (`geo_old`; within a median 0.2-0.7%
of the run CSVs' geo_value). The D2 geometry of the submission chain is not exactly reproducible from one replay
(24-30% of D2 rows equal either replay exactly, 85% within 5%), so 2D candidate eligibility used exact equality with
either replay; irrelevant here since no gate passed. Held-out = 131 validation rows (identical test questions) +
129 stated-fact rows (6 in both, validation label kept); labels were used only for scoring.
