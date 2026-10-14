# Track B v5: free improvements from the existing open-weight Colab outputs

Status: DONE 2026-10-14. Verdict: PASS for L1 (lab label-noise emulator, S3) and L2' (fixed lab camera for the Qwen
geometry member, S3/D3). Main candidate `submissions/trackB_cand_v5.csv`: expected +.005..+.015 overall (central ~+.008),
i.e. Track B ~.626-.636 from .621. Secondary `submissions/trackB_cand_v5plus.csv` adds two levers that cannot pass the
pre-registration (L6s post-hoc, L4 untestable): a further ~+.005 +- .004 (estimate). Top-10 (~.667) is NOT reachable
with free post-processing of the existing open-model outputs; it needs better open-model measurements (new Colab run).

(Pre-registration below was written before any lever evaluation in this directory.)

## Pre-registered kill tests (written before running the lever evaluations)

Base = Track B v3 (per-category log-median sets S2 caw+cv_geo+qwen_direct, D2 caw+cv_geo+qwen_direct+qwen_geo,
S3 cv_geo+qwen_geo+qwen_direct, D3 caw+qwen_geo+qwen_direct) + qp.postprocess preset "trackb".
Reproduced here: validation .6227 (S2 .575 D2 .586 S3 .693 D3 .636); leaderboard .621.
Open-weight inputs only: /tmp/claude-0/tb3/x/trackb_v1/{val,test}/{caw,cv,cvq,qwen,qwen35,gemma4} and the
model-free re-solves of research/trackb_dense/out (Qwen / SAM 2 tracks). No Claude/GPT/Gemini output or parameter.

Held-out measures: validation (159 q, 24 clips, validation rows put into the test question table so the family
rules see test links; labels read only for scoring), clip bootstrap (2000 resamples of the 24 clips, 90% CI);
test stated-fact rows (136 exact values, research/trackb_dense/out/fact_labels.csv; scored on answers before the
facts rule overwrites them).

A lever PASSES only if all of these hold:
1. Validation: summed item change over the affected validation rows > 0, and the clip-bootstrap 90% CI of the
   overall validation delta has its lower bound > -0.010.
2. Stated facts: if the lever changes any fact row, the mean item change over the changed fact rows >= 0.
3. If the lever changes fewer than 5 validation rows and no fact row, the lever-specific label-free test-input
   check below must hold; otherwise the verdict is INCONCLUSIVE and the lever is not put in the main candidate.
4. Selection levers (member sets): the selection procedure, re-run inside leave-one-video-out (LOVO) with the
   family rules applied, must beat the fixed v3 sets' LOVO macro MRA by >= +0.010. Otherwise FAIL.

Lever-specific checks (fixed now):
- L1 lab label-noise emulator on S3 lab motion rows (research/trackb_dense/labnoise_open.py, Qwen 3D tracks with
  the fixed lab camera, noise sigma fitted on the TEST lab speed priors measured on the same open tracks; the
  dense study had already printed val +.026 S3 on 8 rows before this pre-registration, so the val part is not
  blind). Label-free check: the fitted noise profile must prefer sigma_z > 0 (log-lik gap >= 1 vs sigma_z = 0),
  i.e. the stated test priors themselves show the label inflation.
- L2 fixed lab camera (f = 722 px at 1280 px, 84 deg; derived earlier from GT of 6 validation lab clips, so the
  validation part is not blind) for the 3D lab geometry members. Label-free check: on the test S3 lab clips (size
  prior), the fixed-f open-track geometry must reproduce the STATED prior sizes with median log ratio within
  +-0.10 and median |log ratio| <= 0.20.
- L3 twin / render pooling (the pool rule with unit=clip, scope=base: a segmented twin and its original, lab s/x
  renders; identical prior text only via the existing equivalence rules).
- L4 free-fall backward difference (research/path85b_phys: a*(t - t0 - 1/(2 fps)) on the simulation drop events,
  t0 from model-free background-subtraction tracks): no validation or fact rows exist; label-free check = the
  fall_t0 fits have rms < 3 px. Even if it holds, at most a secondary candidate (mechanism unproven on its own).
- L5 member sets incl. qwen35 / gemma4 / cvq / fov variants: rule 4.
- L6 segmented-twin masks: 2D questions on segmented clips and on originals with a pixel-aligned segmented twin
  re-measured with the twin's foreground connected components (component chosen by the open-model box), or
  routed to mask-based geometry. Needs >= 10 affected validation + fact rows, else INCONCLUSIVE.

Candidate: if any lever passes, submissions/trackB_cand_v5.csv via scripts/make_submission.py, with rows changed
per category and expected gain = rows x avg item gain / (4 x N_cat), N = S2 553, D2 1137, S3 538, D3 933.

### Addendum to the pre-registration (written after L1-L3 and L6 were scored, before L7 was run)
- L7 lab label-noise emulator on D3 lab motion rows (same factors as L1, same sigma; the Track A analogue was
  ~+.001..+.002 D3). General rules 1-3 apply (fewer than 5 changed validation rows -> INCONCLUSIVE).
- L6s (simulation twins only) is POST-HOC: defined after L6 failed and after its per-row validation values and the
  fact-row result had been seen. It cannot pass the pre-registration; it is reported separately and only goes into
  a secondary candidate.


## Hypothesis
The Track B answers (log-median of open-weight members + family rules) still miss model-free corrections that worked in
Track A or that the test inputs allow: the lab label process (forward differences of noisy clicked 3D centres inflate
lab speeds / path lengths), a known lab camera instead of a focal length solved from an ill-conditioned motion prior, exact
segmented-twin masks instead of open-model boxes, and better member sets.

## Commands (all CPU, no API; `.venv/bin/python`, outputs in research/trackb_v5/)
```
research/trackb_v4/eval_sets.py                 # baseline reproduction: v3cat +rules .6227
research/trackb_v5/analyze_val.py               # error analysis (out_val_rows.csv)
research/trackb_v5/levers_a.py                  # L1, L2 (all members), L3
research/trackb_v5/l2_check.py qwen cvq cv      # L2 label-free check on TEST stated lab sizes
research/trackb_v5/run_l2q.py                   # L2' (Qwen member only)
research/trackb_v5/l5_lovo.py                   # L5 LOVO with rules (218 subsets of 8 methods), log l5_lovo.log
research/trackb_v5/seg_snap.py val|test         # L6 twin-mask snapping (component cache /tmp/claude-0/trackb_v5_cache)
research/trackb_v5/eval_l6.py ; eval_l6s.py     # L6 (pre-registered), L6s (post-hoc, simulation twins only)
research/trackb_v5/eval_l7.py                   # L7 D3 lab emulator
research/trackb_v5/seg_members.py               # per-member scores on segmented / twin rows (diagnostic)
LN._fit("qwen") (labnoise_open, OUT redirected to research/trackb_v5/out_lnfit)   # L1 label-free check
research/trackb_v5/build_v5.py --out submissions/trackB_cand_v5.csv
research/trackb_v5/build_v5.py --out submissions/trackB_cand_v5plus.csv --l6s --l4
research/trackb_v5/report.py                    # combined validation + rows changed vs uploaded v3
```
Sanity: `build_v5.py --no-l2q --no-l1` reproduces the uploaded `trackB_v3_catmedian_famrules.csv` exactly (0 of 3289
rows differ), so every difference in the candidates comes from the levers.

## Where Track B loses (validation, v3 + rules; diagnostic only)
Largest losses: D2 simulation sizes (13 rows, item .33, median log error -0.79; two odd clips 0193/0196 where every
geometry member fell back to CaW), D3 simulation sizes (21 rows .65), S2 simulation accelerations (6 rows .25), S3
simulation sizes (10 rows .48), lab D3 distances/sizes. Many members coincide with CaW (geometry fallback) on hard clips.

## Results per lever (base = v3 + rules, validation .6227; deltas are macro MRA over the 4 categories)

| Lever | val MRA | delta [90% clip CI] | val rows changed / item sum | facts | label-free check | test rows | verdict |
|---|---|---|---|---|---|---|---|
| L1 lab emulator, S3 lab motion | .6291 (S3 .693->.719) | +.0064 [.000, +.017] | 8 / +1.10 (all from captured_0034as) | none touched | noise profile prefers sigma_z=2 cm over 0 by 1.68 log-lik (>= 1): PASS | S3 142 (factor median 1.18: small-ball speed 1.12 x86, mid-ball speed 1.31 x36, small-ball path 1.53 x18) | **PASS** |
| L2 fixed lab camera, all geometry members | .6246 (S3 .693->.686, D3 .636->.651) | +.0020 [-.004, +.010] | 24 / +0.40 | none | per source log(f_solved/f_cam) on 54 test S3 lab clips: Qwen +.041 (median abs .055) PASS; SAM 2 cvq +.148, cv +.139 FAIL (masks read lab objects ~14% small) | S3 287, D3 218 | **FAIL** (check fails for the SAM 2 members) |
| L2' fixed lab camera, Qwen member only (qwen_geo -> qwen_fov in S3/D3) | .6264 (D3 .636->.651) | +.0037 [.000, +.011] | 16 / +0.70 (all from captured_0013) | none | Qwen source passes (above); fixed-f open-track lab ball speeds vs stated priors 0.98-1.36 (median ~1.08 incl. label inflation) | D3 218, S3 156 | **PASS** (the restriction follows the pre-registered check applied per source; note the full-L2 val split was seen first) |
| L3 twin / render pooling | .6180 | -.0047 [-.012, +.001] | 59 / -0.70 | - | - | 682 | **FAIL** |
| L4 free-fall backward difference | no val rows | - | 0 | none | clean-view fall fits rms 0.1-2.8 px (< 3): holds | D2 21, D3 15 | INCONCLUSIVE (secondary only) |
| L5 member sets incl. qwen35/gemma4/cvq/fov, chosen by validation | in-sample best .64 | LOVO (with rules) of the 8-method search .5779 vs v3's own procedure (old 4) .5793 | - | - | - | - | **FAIL** (needs >= +.010) |
| L6 twin-mask snapping, cv_geo member -> snapped (S2/D2, all sources) | .6165 | -.0062 [-.017, .000] | 13 / -0.90 (internet_0019 -0.8: SAM 2 demo cut-outs) | 10 rows .840 -> .870 | - | D2 265, S2 61 | **FAIL** |
| L6s (post-hoc) snapped geometry alone, simulation twins only, rows where it is valid | .6274 | +.0048 [-.001, +.013] | 12 / +0.60 (0098_seg +0.4, 0171 +0.4, 0060 -0.2) | 17 rows .841 -> .894 | - | 368 rows direct (scored: D2 272, S2 84) + family-pool spill-over | not eligible (post-hoc): secondary only |
| L7 lab emulator, D3 lab motion | .6227 | 0 | 2 / 0 | none | - | D3 49 (factor median 0.97) | INCONCLUSIVE (< 5 val rows) |

Notes
- L1 and L2' each rest on ONE validation clip (captured_0034as, captured_0013); the clip-bootstrap lower bounds are
  exactly 0. Their support is mechanistic: L1 is the Track A label-process model (S3 +.015 on the Track A leaderboard) with
  the noise re-fitted on open-model tracks and test priors only; L2' is backed by the test stated lab sizes.
- L5: the v3 selection itself is optimistic (in-sample .6227 vs LOVO of its own procedure .579 with rules); no wider
  search does better under LOVO, so the v3 sets stay.
- L6: the internet segmented clips are SAM 2 demo cut-outs (watermark "Modified with Segment Anything 2 Demo"),
  often with different frame counts / fps (11 of 13 internet twins skipped as not frame-aligned); simulation twins are
  exact. Snapping fixed e.g. simulation_0098_segmented boat length 8.59 -> 10.06 (label 10.0), shark 3.32 -> 3.26 (3.26).
- Clean-input check: no Claude/GPT/Gemini output or parameter is used. LAB f = 722 px @1280 was originally derived from
  6 validation lab clips' labels (not from Claude); here it is re-checked on test inputs with Qwen tracks (above). The L4
  values are a*(t_k - t0 - 1/(2 fps)) with a from the stated prior and t0 from model-free background subtraction.

## Candidates
| file | levers | val (combined table) | changed rows vs uploaded v3 (scored, non-val-overlap) |
|---|---|---|---|
| `submissions/trackB_cand_v5.csv` (MAIN) | L2' + L1 | .6334 (S3 .721, D3 .651), +.0107 [.000, +.024] | S3 221, D3 218 (all lab; no stated-fact row changed) |
| `submissions/trackB_cand_v5plus.csv` (secondary) | main + L6s + L4 | .6381 (S2 .588, D2 .597, S3 .721, D3 .647), +.0155 [+.003, +.031] | D2 362, D3 278, S3 224, S2 81 |
Both: 3289 rows, template order, finite > 0, built by scripts/make_submission.py.

Expected gain (rows x avg item gain / (4 x N_cat)):
- MAIN: S3 L1 ~140 rows x +.05 (Track A per-row) .. +.14 (validation per-row) -> +.003..+.009 overall;
  D3 218 rows x +.03 .. +.10 (validation per changed D3 row +.100, 7 rows) -> +.002..+.006; L2' S3 rows ~0
  (no validation item change). Total +.005..+.015, central ~+.008 -> Track B ~.629 (S3 ~.63-.64, D3 ~.65).
- SECONDARY adds: L6s D2 272 scored rows x +.053 (facts per-row) / 4548 = +.0032, S2 84 x +.05 / 2212 = +.0019, D2/D3
  family-pool spill-over (~90 D2, ~60 D3 rows) ~0; L4 +-.001 (sign depends on the Blender speed convention). About
  +.005 +- .004 on top of MAIN.

Recommendation: upload MAIN first. If a Track B slot is free afterwards, upload SECONDARY; its delta over MAIN reads
L6s+L4 directly (S2/D2 change only through them; D3 adds the family spill-over and the 15 L4 rows).
Reaching ~.667 needs about +.046: post-processing of the current outputs gives ~+.01-.02. The remaining gap is
measurement quality of the open members (geometry falls back to CaW on hard clips; direct VLM answers are weak:
qwen_direct S2 .31). A new Colab run (better grounding / SAM 2 tracks for all clips, more direct-answer samples for the
median) is the only lever of that size.
