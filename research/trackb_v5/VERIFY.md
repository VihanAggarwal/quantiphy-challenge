# VERIFY: Track B v5 (lever "trackb_free"), independent check 2026-10-14

Verdict: **PASS confirmed, with caveats.** Every reported number reproduces exactly. Both candidate files rebuild
byte for byte. No leakage was found. L1 is a clean pre-registered pass. L2' is a post-hoc restriction (disclosed),
and its D3 part has weak support. The expected-gain arithmetic is correct, but the central +.008 is optimistic;
about +.005 (range ~0 to +.011) is more realistic.

## What I re-ran (CPU only, free; writes redirected to my scratchpad, no agent file modified)
| command | reported | reproduced |
|---|---|---|
| `research/trackb_v4/eval_sets.py` | v3cat +rules .6227 | .6227 (S2 .575 D2 .586 S3 .693 D3 .636) |
| `levers_a.py` L1 | .6291, +.0064 [.000,+.017], 8 rows +1.10, test S3 142, factor med 1.18 | identical (factor median 1.183) |
| `levers_a.py` L2 all members | .6246, +.0020 [-.004,+.010], 24 rows +0.40 | identical |
| `levers_a.py` L3 | .6180, -.0047, 59 rows -0.70 | identical |
| `run_l2q.py` L2' | .6264, +.0037 [.000,+.011], 16 rows +0.70 | identical |
| `l2_check.py qwen cvq cv` | qwen +.041 (\|.\| .055); cvq +.148; cv +.139 | identical (54 clips, 334 q) |
| `LN._fit("qwen")` (OUT -> scratch) | sigma_zb .02, gap 1.68 | sigma_zb .02, sigma_zL .02, gap 1.675 |
| `report.py` (incl. eval_l6s) | main .6334 +.0107 [.000,+.024]; plus .6381 +.0155 [+.003,+.031] | identical; L6s-b .6274, facts 17 rows .841->.894 |
| `build_v5.py` (main / plus / --no-l2q --no-l1) | | main and plus byte-identical to `submissions/trackB_cand_v5*.csv`; v3 rebuild 0/3289 rows differ (max rel diff 9e-16) |
| `make_submission.py` round trip | | both pass (3289 rows, template order, finite, > 0) |
| l5_lovo.log | 8-method LOVO .5779 vs old-4 .5793 | log consistent with the code (cache read, not recomputed) |

## Pre-registration audit
- From the worker transcript (wf_c8cc6551-c3e/agent-af1c00f351889cbe7): RESULT.md with the kill tests was written at 22:25:10.
  levers_a.py was created at 22:25:35, after that. The pre-registration section in the final RESULT.md is identical to that first
  write (diff: one blank line). The L6s/L7 addendum was appended at 22:40:58, before eval_l7, as claimed.
- L1: rules 1-2 hold and its lever-specific check holds (gap 1.675 >= 1). The validation part was not blind (disclosed).
- L2': this is a post-hoc variant. The pre-registered L2 (all geometry members) failed its label-free check because of the
  cv/cvq members, and the restriction to Qwen was chosen after the per-source check and the L2 validation split had been
  seen (disclosed). L6s, also post-hoc, was moved to the secondary candidate; L2' was not, so the two are handled
  inconsistently. It is still defensible: (a) in D3 the only geometry member is qwen_geo, so L2' and L2 are identical in
  D3, and all of L2''s validation gain is in D3; (b) the excluded part (cv_geo -> cv_fov in S3) fails the label-free check,
  so the subset was chosen by a test-input check, not per row by labels; (c) read literally, rules 1-3 would pass full L2
  as well (24 validation rows, so rule 3 does not apply).
- The bootstrap bar (lower bound > -0.010) is lenient. Both L1 and L2' get lower bound = 0.000 only because each gain sits
  in one clip (L1: captured_0034as +1.1; L2': captured_0013 +0.7). Removing those two clips leaves a delta of exactly +.0000.

## Leakage / clean-input checks
- Validation rows go into the rules table without answers (`harness.Data`: `val.drop(columns=["answer"])`). In the
  candidates, 22 (main) and 33 (plus) changed rows overlap validation, and none equals a validation label.
- Main changes only lab rows: S3 233 / D3 228 in total, 221 / 218 scored. It changes 0 stated rows (facts / motionfam /
  freefall / labfacts).
- No closed-model output is used. `emulate.py` loads the Claude-track fit_noise.json at import, but `LN.factors`
  overrides sigma_zb and sigma_zL (both .02, fitted on Qwen tracks + test priors). sigma_px 2.0 and SIGMA_A .15 are a-priori
  constants. The L4 values (`changes_ffbd.csv` column `new`) are a*(t_k - t0 - 1/(2 fps)) from stated priors and
  background-subtraction t0. The `old` column there holds Track A answers but is not used.
- Gray areas, not answer leakage:
  - The lab camera constant (LAB_FOV_DEG 84, f = 722 px) was set from "GT-implied 76-90 deg on 6 val videos"
    (qp/claude_annotate.py). Those are exactly the 6 validation lab clips (0013, 0021x, 0027s, 0034as, 0041x, 0061).
    It is one global, pre-existing constant, but it means the L2' validation gain on captured_0013 is in-sample.
  - `research/labnoise/common.py` BALL_D holds Table 6 sizes, used only to put balls into classes. sigma_zb = sigma_zL
    in this run, so the classes have no effect on any value.

## Extra held-out check I added (label-free, test inputs only)
The 15 D3 lab rows whose answers come from the `labfacts` rule are exactly known: prop sizes stated in another lab event,
covering 5 scenes (0008, 0009, 0018, 0052, 0053), each with s/x renders. Scored on the member alone:
- qwen_geo (solved f): mean item .693, median log(pred/stated) -.003, median |.| .221.
- qwen_fov (fixed f, the L2' member): mean item .693, median log ratio +.128, median |.| .172.
So the fixed-f Qwen member is no better here, and it reads about 13% high. That would fail the pre-registered L2 bias
bound of +-0.10 if the bound were applied to D3. L2' raises the D3 lab size rows by a median factor of 1.13 (118 rows) and
distances by 1.22 (44 rows). In the full median only 1 of the 15 rows moves (24.0 -> 24.6, item 1.0 -> 0.9). This does
not refute L2' (5 correlated scenes; the one validation clip, captured_0013, wanted larger values), but the sign of the
D3 gain is uncertain.

## Expected gain
The arithmetic is correct: S3 140 x .05..14 / (4 x 538) = +.003..+.009; D3 218 x .03..10 / (4 x 933) = +.002..+.006.
- L1 (S3) rests on the Track A leaderboard analogue (+.015 S3, 148 rows x1.17), which is solid. Track B answers are
  noisier, so the gain per row is probably nearer the low end: about +.002..+.006 overall.
- L2' D3: about -.002..+.005 (see the extra check above).
- Realistic main total: about +.005 (0..+.011), i.e. Track B about .621 -> .626, not .629.

## FAIL / INCONCLUSIVE levers: false-negative risk
- L2, L3, L5: no bug found. L3 pools on top of the preset's own `pool` rule (double pooling). L5's LOVO is
  noise-limited but built correctly.
- L6: the failure comes from one internet twin (internet_0019, a SAM 2 demo cut-out). The simulation-twin part (L6s) is
  plausibly real (facts 17 rows +.053/row) and is already in the secondary candidate, so the remaining hidden gain is small.
- L4 and L7: untestable. Track A shows L7 at about +.001, so nothing material is lost.

Side note for the orchestrator: qp/mra.py THRESHOLDS = (.1,...,.9,.95), not the {.5,...,.95} in the task text. All numbers
here use qp.mra, which matches the leaderboard closely (v3: validation .6227 vs leaderboard .621).
