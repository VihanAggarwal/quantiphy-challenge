# Global spline derivative estimator for 2D geometry (Gemini's proposal) — research/splinefit/

## PRE-REGISTERED KILL TEST (written 2026-10-14 before any evaluation on labels or stated facts)

Hypothesis: replacing qp.geometry's LOCAL derivative estimators (speed at t = ICI local polynomial of
half-width 0.12-0.5 s; acceleration at t = widest local polynomial of degree < 4) with a GLOBAL robust
penalised spline of the whole track (cubic B-splines, exact jerk penalty lam * int f'''^2, Huber IRLS on
residuals standardised by their robust scale) improves the 2D geometry answers, both where the PRIOR is a
speed/acceleration at a time (D2: it sets the image scale) and where the TARGET is one (S2 motion).

Variants, fixed before evaluation (`spline.py`):
- `gcv`: lam per track by generalised cross-validation over h in geomspace(0.03, 3, 25) s (lam = rho h^6);
- `h010`: fixed equivalent-kernel time scale h = 0.10 s;
- `h025`: fixed h = 0.25 s;
- `gcv_glock`: `gcv` + gravity lock (2D gravity prior: speed at t of the falling prior track inside its free-flight
  span takes its vertical velocity from that one parabola, i.e. vertical acceleration locked to the prior's).
(h = 0.15 / 0.40 were replaced by 0.10 / 0.25 after a label-free synthetic check: h = 0.40 s shrinks speeds on a
2 rad/s circle by 21%. Huber weights enter the weighted obs density so they do not add smoothing.)
Only the VALUE of a speed / acceleration at a time changes; the original _motion runs first, so failures, prior
noise checks and all other quantity kinds are unchanged.

Held-out rows (no test labels; parameters fixed):
1. Validation labels: run `val_hr_v1_high` (the test configuration: Opus high, 854 px), split val_hires, 2D questions
   (S2/D2), annotations as in the submission (refine off + dense motion).
2. Stated-fact rows on test: qp.postprocess "facts" rule applied rows (the stated value is exact), 2D rows only,
   replayed from `test_v1_high_854` with the same annotations. A fact row that is also a validation question is
   counted once (validation).
"Routed answer" = what the current submission (combo3) uses on those rows: run_claude.build_results' choice
(geometry unless rejected), then S2 simulation(+segmented) motion targets -> geometric mean of geometry and Claude's
direct answer (U2 / combo3), S2 internet -> direct (unaffected), D2 -> geometry.
AFFECTED rows = routed answer changes by |log(new/old)| > 0.005 (smaller changes cannot move an MRA threshold in
practice).

PASS for a variant iff ALL of:
 (a) mean item-MRA change (new - old) on the pooled affected rows (1 + 2) >= +0.010;
 (b) clip-bootstrap (2000 resamples of base clips, segmented twin = its original) 90% CI lower bound > 0;
 (c) no category (S2, D2) with a net negative item-score sum on its pooled affected rows;
 (d) expected overall gain >= +0.002, = sum over categories of (combo3 rows the candidate changes by > 0.5%) x
     (that category's mean item gain on the pooled affected rows) / (4 x scored N_cat) (S2 553, D2 1137);
 (e) neither source (validation, facts) has a negative mean change on its affected rows.
If several variants pass, the one with the largest pooled mean gain is taken (4 variants tried: noted as a
multiple-comparison caveat). If PASS: candidate on combo3 for the passing categories only, with merge_skip.py.
Secondary (not part of the test): the same on the other cached validation runs (val_hr_v2_high, val_opus_high,
val_opus_med, val_opus_xhigh, ...), and the D2-vs-S2 cross-prior consistency on test (same object, same question,
independent size-prior answer).

---------------------------------------------------------------------------------------------------------------
## RESULTS (run after the pre-registration above)

### Verdict: FAIL for all four variants. No candidate file built.

### What was run (no API calls, no paid spend; free replays of cached Claude records)
```
# spline module + monkeypatch of qp.geometry._motion (qp/ untouched): research/splinefit/spline.py
# synthetic, label-free sanity check (projectile / circle / jerk ramp, 100 draws each): scratch synth.py
ENV='ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=<scratchpad>/splinefit/ledger.jsonl'
$ENV .venv/bin/python research/splinefit/replay.py --split val_hires --run val_hr_v1_high      # primary val
$ENV .venv/bin/python research/splinefit/replay.py --split test --run test_v1_high_854         # test 2D (1742 q)
$ENV .venv/bin/python research/splinefit/replay.py --split val_hires --run val_hr_v2_high      # secondary
$ENV .venv/bin/python research/splinefit/replay.py --split val --run val_opus_{high,med,xhigh} # secondary
.venv/bin/python research/splinefit/evaluate.py --secondary out/val_hires_val_hr_v2_high.csv,out/val_val_opus_{high,med,xhigh}.csv
```
Outputs: `out/eval_primary.txt` (full log), `out/eval_rows.csv` (every affected held-out row, old/new/label/score).

Reproduction checks (before any labels were read): validation replay base == cached `val_hires.csv` geometry 159/159;
test replay base S2 == `runs/test_v1_high_854/test.csv` 579/579; combo3 holds the replayed refine-off D2
geometry on 742/1163 D2 rows and the routed S2 value (gm for sim motion, direct for internet) on 310/579 S2 rows.
Replacements: 475 timed speed/acceleration measurements on test 2D (23 fallbacks: < 6 obs or < 0.2 s span),
gravity lock 54; only 17 on the 69 validation 2D questions (most D2 priors are untimed: path / duration or the
parabolic-span acceleration, which the lever does not touch).

### Pre-registered test (affected = routed answer moves > 0.5%)
| variant | val (n, delta) | facts (n, delta) | POOLED n / clips | pooled delta [90% clip CI] | S2 item sum | D2 item sum | combo3 rows S2/D2 | exp. overall | verdict |
|---|---|---|---|---|---|---|---|---|---|
| gcv | 9, -.100 | 4, .000 | 13 / 8 | **-.069** [-.340, +.100] | -0.80 | -0.10 | 52 / 55 | -.0024 | FAIL (a,b,c,d,e) |
| h010 | 9, -.022 | 4, -.025 | 13 / 7 | **-.023** [-.054, .000] | -0.10 | -0.20 | 53 / 45 | -.0009 | FAIL (a,b,c,d,e) |
| h025 | 10, +.020 | 4, +.050 | 14 / 8 | **+.029** [-.013, +.050] | +0.40 | 0.00 | 71 / 55 | +.0013 | FAIL (b, d) |
| gcv_glock | 8, -.113 | 4, .000 | 12 / 7 | **-.075** [-.378, +.107] | -0.80 | -0.10 | 52 / 56 | -.0025 | FAIL (a,b,c,d,e) |

Only 28 stated-fact rows fall in 2D test clips (D2 19, S2 9; 6 more are validation questions, counted there), and
just 4 of them move by > 0.5% under any variant (moves of 0.7-2%, item changes of +-0.1).

Secondary validation runs (same 24 clips, other Claude tracks; delta on affected rows):
| run | gcv | h010 | h025 | gcv_glock |
|---|---|---|---|---|
| val_hr_v2_high | -.100 (n 11) | +.010 | +.109 | -.110 |
| val_opus_high | -.150 (n 10) | +.010 | +.022 | -.146 |
| val_opus_med | -.189 (n 9) | +.009 | +.010 | -.170 |
| val_opus_xhigh | -.178 (n 9) | .000 | +.033 | -.178 |

### Reading
- **The derivative estimator is not where the 2D errors are.** On test the spline moves only ~100 combo3 rows by
  > 0.5% (median |change| ~2%, median ratio 0.99: slightly lower speeds). The held-out affected rows are dominated
  by gross misses whose errors (log error 0.6-1.2 in simulation_0171) are track/label problems that no smoother
  fixes: 7 of the 10 validation h025 rows are simulation_0171 (the clip with non-monotone astronaut labels).
- **GCV fails**: on the sparse Claude tracks it under-smooths and blows up at a track end (simulation_0163 qid 399:
  0.376 -> 0.944, label 0.359). It is worse on every replicate (-.10 to -.19 per affected row). On test it moves
  9 S2 and 7 D2 rows by > 20% (max x2.47, min x0.16): a high-risk change with no evidence behind it.
- **Gravity lock** changes almost nothing beyond gcv (1 validation measurement); its rows inherit gcv's loss.
- **h025** is the only variant with a positive sign, and it is positive on all five validation runs. But these are
  the same 3-4 clips, mostly 0171's gross misses (e.g. 0.0 -> 0.2 on a 2.4x miss). The pooled CI includes 0, and
  even taken at face value (+.029 per affected row on ~126 combo3 rows) it is worth +.0013 overall, below the
  +.002 bar. The ICI local estimator already adapts its window, which leaves a global smoother little to gain.
- Relation to earlier results: this agrees with kinematic answer smoothing (+-.003) and Blender label emulation
  (S2 -.002, D2 0). The 2D motion pipeline is limited by the tracks and the labels, not by the differentiation.

### Not done / follow-ups
- No candidate: the kill test failed, so nothing goes onto combo3.
- If someone wants to spend one upload on it anyway, h025 is the only defensible variant (S2 71 + D2 55 rows,
  expected ~+.001 at best, roughly 50/50 to read as 0 on the leaderboard). We do not recommend it.
- The pre-registered secondary D2-vs-S2 cross-prior consistency check was NOT run. Every variant had already failed
  the primary test, and only 3 combo3 rows with a static target move at all (D2 priors are mostly untimed), so it
  could not change the verdict.
- No temporary frames or large files were written (out/ is 1.4 MB, mostly the test replay table).
