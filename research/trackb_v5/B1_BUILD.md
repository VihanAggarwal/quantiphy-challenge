# Track B candidate B1: build log (2026-10-15)

This is `research/r86/PLAN.md` section 2 item B1 and section 3 step 1: one upload, read per category.

- **File:** `submissions/trackB_cand_B1.csv`. It has 3289 rows in template order, every value finite and > 0, and it
  passes `scripts/make_submission.py`.
- **Base:** the uploaded `submissions/trackB_v3_catmedian_famrules.csv` (leaderboard .621: S2 .558, D2 .663,
  S3 .620, D3 .641).
- **Inputs:** open-weight outputs, model-free code and test inputs only. No Track A answer value enters any answer
  (checks 1 and 2 below).

## What I changed

New files (I did not modify anything in `qp/`, `scripts/`, `build_v5.py` or any other existing file, and I did not
commit):

| file | content |
|---|---|
| `research/trackb_v5/build_b1.py` | the builder: v5 pipeline + S2 routing + D2-only L6s/L4 + restricted clamp; `--keep` reverts categories to v3; `--decompose`, `--val` |
| `research/trackb_v5/check_b1.py` | audit and value checks (below) |
| `submissions/trackB_cand_B1.csv` | the candidate |
| `research/trackb_v5/B1_rows.csv` | every changed row (1422): v3 / B1 value, raw changed, per-component spill-over flags, leave-one-out attribution |
| `research/trackb_v5/B1_spillover.csv` | the pool-rule spill-over rows (200), by source component |
| `research/trackb_v5/B1_build.log`, `B1_checks.log` | console output of the two commands |

## Recipe (one component per category)

| category | B1 content | source |
|---|---|---|
| S2 | Pseudo-label routing, S2 only. Per-cell log-median sets from `research/r86/intel_tb_pseudolabel/routing_base8_min25_k2.csv` (7 S2 cells, 552 of the 579 test S2 rows). The other 27 rows (internet / segmentation accelerations) use the S2 fallback set `cvq_geo + qwen_geo + qwen35` (`fallback_category_sets.json`). | the S2-only salvage (`skeptic/subsetcats.py`) |
| D2 | v5plus L6s (snapped twin-mask cvq geometry on simulation twins, applied before the rules), D2 rows only (276 rows), plus v5plus L4 (free-fall backward difference), D2 rows only (21 rows) | `build_v5.l6s_values`, `research/path85b_phys/changes_ffbd.csv` column `new` |
| S3 | v5 MAIN: L2' (`qwen_geo` -> `qwen_fov`) and L1 (lab label-noise emulator, 145 lab motion rows, stated rows excluded) | `build_v5.py` |
| D3 | v5 MAIN L2' (`qwen_geo` -> `qwen_fov`) | `build_v5.py` |
| all | Clamp, applied after the rules: car width to [1.5, 2.3] m and person height to [1.50, 2.00] m. It uses the regexes of `research/r86/pp_strategy/guard_tb.py`, cut down to these two classes (no car length, car height, wheels or balls). | a-priori ranges |

Clamp details:
- Rows are skipped if the question or prior contains "toy", or if a stated-fact rule (facts, motionfam, freefall,
  labfacts) set the row.
- On test, both skips affect 0 rows. 56 test questions mention "toy", but none is a car-width or person-height question.
- The clamp changes 47 rows: 44 car widths and 3 person heights. 41 go down and 6 go up.
- Check of the ranges against test inputs and validation labels: stated test person heights are 1.63-1.87 m (no car
  width is stated). Validation labels are 1.61-1.87 m for person height and 1.86-2.21 m for car width. All are inside
  the ranges.

Pipeline order, as in `build_v5.py`: raw (sets / routing / L6s), then `qp.postprocess` preset "trackb" on the whole
test table, then L1, then L4, then the clamp, then `--keep`, then `make_submission.py`.

Interpretations I made, all within PLAN.md:
- **S3 includes L2' as well as L1.** v5 MAIN applies L2' in S3, and PLAN section 5 says "v5 S3/D3 lab". The S3 and D3
  lab rows equal `trackB_cand_v5.csv` exactly (0 differ).
- **L6s and L4 are restricted to D2.** v5plus also put L6s on S2 rows and L4 on 15 D3 rows. I left those out, so that
  S2 reads the routing and D3 reads L2'.
- **Fallback for an empty routed row.** A routed S2 row with no finite member falls back to the S2 fallback set, then to
  the v3 set. This touched 0 rows.

## Rows changed vs v3 (all rows / scored rows; scored = not a validation-overlap question)

| | S2 | D2 | S3 | D3 | total |
|---|---|---|---|---|---|
| **B1 vs v3** | **498 / 476** | **380 / 377** | **253 / 240** | **291 / 279** | 1422 / 1372 |
| s2route | 495 / 473 | 27 / 25 | 16 / 15 | 19 / 19 | |
| l6s (D2) | 13 / 13 | 338 / 335 | 1 / 1 | 33 / 33 | |
| l4 (D2) | 0 | 21 / 21 | 0 | 0 | |
| l2q (L2') | 0 | 0 | 164 / 156 | 228 / 218 | |
| l1 | 0 | 0 | 145 / 138 | 0 | |
| clamp | 7 / 7 | 18 / 18 | 4 / 4 | 18 / 16 | |

How the per-component rows are counted:
- They are leave-one-out attributions inside B1: a row counts for component k if B1 differs from B1 without k.
- A row can count for two components: 45 rows count for s2route and l6s, 76 for l2q and l1, and 4 for s2route and clamp.
- Every changed row is attributed to at least one component.

Each component added to v3 on its own:

| alone | S2 | D2 | S3 | D3 |
|---|---|---|---|---|
| s2route | 496/474 | 25/23 | 17/16 | 24/24 |
| l6s | 13/13 | 344/341 | 1/1 | 38/38 |
| l4 | 0 | 21/21 | 0 | 0 |
| l2q | 0 | 0 | 164/156 | 228/218 |
| l1 | 0 | 0 | 149/142 | 0 |
| clamp | 3/3 | 18/18 | 4/4 | 18/16 |

## Pool-rule spill-over

These are rows whose raw value is unchanged but whose final value changes, through the "trackb" pool rule (one vote
per base clip, 1.6x own-vote guard). They are listed in `research/trackb_v5/B1_spillover.csv`.
- **S2 routing:** 66 rows outside S2 (63 scored): D2 25, S3 17, D3 24. This is the "about 60" that PLAN.md
  anticipated. Another 2 S2 rows change only through pooling. The source clips are simulation families (0058-0067
  cars, 0068/0073/0084 cars, 0098/0101-0103 + twins, 0022/0026/0034/0036/0043 + twins, 0024/0031/0039/0042 + twins,
  0074, 0144, 0164).
- **L6s (D2):** 52 rows outside D2: D3 38, S2 13, S3 1. Another 80 D2 rows change only through pooling.
- **L2':** 0. Lab rows do not pool with other categories.
- All 200 spill-over rows also differ in B1.
- Inside B1, 144 changed rows have an unchanged raw value and are not post-step-only rows: D2 78 (l6s) + 3 (s2route);
  D3 26 (l6s) + 12 (s2route) + 7 (both); S3 15 (s2route) + 1 (both); S2 2 (s2route).
- Consequence for the reads: each category's read includes these spill-over rows. D3, for example, is L2' on 218
  scored rows, plus 33 l6s rows, 19 s2route rows and 16 clamp rows.

## Validation

These numbers use the combined table: validation questions are put into the test table without answers, and the labels
are read only to score. No row was set or selected by them.

| build | MRA | S2 | D2 | S3 | D3 | clip bootstrap delta [90%] |
|---|---|---|---|---|---|---|
| v3 | .6227 | .5750 | .5865 | .6930 | .6362 | |
| + l2q | .6264 | .5750 | .5865 | .6930 | .6511 | +.0037 [.000, +.011] |
| + s2route | .6336 | .6187 | .5865 | .6930 | .6362 | +.0109 [-.008, +.025] |
| + l6s (D2 only) | .6243 | .5750 | .5973 | .6930 | .6319 | +.0016 [-.002, +.008] |
| + l1 | .6291 | .5750 | .5865 | .7186 | .6362 | +.0064 [.000, +.017] |
| + l4 | .6227 | | | | | 0 (no validation rows) |
| + clamp | .6232 | .5750 | .5865 | .6930 | .6383 | +.0005 [.000, +.001] |
| **B1** | **.6458** | **.6187** | **.5946** | **.7209** | **.6489** | **+.0231 [.000, +.043]**, 51 rows changed |

Caveats:
- The L1, L2' and L6s validation numbers are not blind (see RESULT.md and VERIFY.md).
- The routing table was chosen without validation labels. Restricting it to S2, however, followed the skeptics'
  validation reads.
- The L6s spill-over into D3 reads -.004 on validation.
- Stated-fact rows (test priors) are scored on the raw answers before the facts rule:
  - s2route: 9 rows, .800 -> .856. This is in-sample for the routing fit, which used these test rows.
  - l6s: 11 D2 rows, .882 -> .982.
  - l2q: 0 rows.

## Expected gain and per-category kill test

- **Expected gain:** +.015 overall (+.007 to +.025), per PLAN.md, so about .636. Validation reads +.023, which is
  optimistic for the reasons above.
- **Kill test, per category, after the upload:** keep a category only if its read is >= its v3 score + .001, i.e.
  S2 >= .559, D2 >= .664, S3 >= .621, D3 >= .642.
- **Reverting a category:** rebuild with `--keep` set to the categories that passed. The others then take the uploaded
  v3 values row by row. For example, if D3 fails:
  `.venv/bin/python research/trackb_v5/build_b1.py --out submissions/trackB_cand_B1_keep.csv --keep S2,D2,S3`.
  Spill-over rows stay with the category they sit in, consistent with that category's read.

## Commands

```
.venv/bin/python research/trackb_v5/build_b1.py --out submissions/trackB_cand_B1.csv \
    --rows research/trackb_v5/B1_rows.csv --decompose --val          > research/trackb_v5/B1_build.log
.venv/bin/python research/trackb_v5/check_b1.py submissions/trackB_cand_B1.csv   > research/trackb_v5/B1_checks.log
```

`research/trackb_v5/B1_spillover.csv` was derived from `B1_rows.csv` (spill flags and attribution columns).

## Checks run (all pass)

1. **Reproduction.**
   - `build_v5.py` (main, `--l6s --l4`, `--no-l2q --no-l1`) rebuilt `trackB_cand_v5.csv`, `trackB_cand_v5plus.csv`
     and the uploaded v3 with 0 of 3289 rows different.
   - `build_b1.py` with no components rebuilds the uploaded v3 exactly (asserted in `--decompose`).
2. **Clean inputs.** `check_b1.py` re-runs the build under a Python audit hook and lists every file opened (636 data
   files) and every subprocess (only `scripts/make_submission.py`). None is a Track A, Claude, GPT, Gemini, Sol, Argon or
   Muse output. Three files touch Track A material, and each was checked:
   - `research/labnoise/out/fit_noise.json` (the Track A noise fit on Claude tracks) is loaded when `emulate.py` is
     imported. The L1 factors are identical with its sigmas replaced by NaN (199 factors), so it does not reach any
     answer.
   - `changes_ffbd.csv` holds Track A answers in its `old` column. Only `new` is used, and all 21 L4 values were
     recomputed from the stated acceleration, the question time, fps and the model-free t0.
   - The two pseudo-label routing files hold member names only (printed in the log).

   The remaining files are as follows:
   - `runs/_postprocess_cache` holds video-frame thumbnails and twin and fall caches (model-free).
   - The rest are the open-model member CSVs, Qwen specs and tracks, and the dataset and template.
3. **Values.** 26 of the 1422 changed rows equal a value in at least one of 95 Track A files. Each has an
   open-pipeline origin:
   - 21 are the L4 formula.
   - 2 are clamp bounds.
   - 3 are an open member's own answer: qid 2026 qwen_direct/qwen35 10, qid 2084 qwen35 10.8, qid 2141 caw 6.7.

   None is unexplained. **Confirmed: Track A was used only for routing selection (member names). No Track A answer value
   is in any Track B answer.**
4. **Stated facts.** 0 of 129 test stated-fact rows change their final answer vs v3.
5. **Submission.** `scripts/make_submission.py` passes, and a round trip leaves the values unchanged.
6. **Lab rows.** The S3/D3 lab rows equal v5 MAIN exactly. The non-lab S3 (20) and D3 (63) differences from v5 MAIN
   are the spill-over and clamp rows above.

## FAQ disclosure note (for the technical report, Open-Weight Track)

> **Use of Main Track outputs during Open-Weight development (FAQ section 09).** Our Open-Weight submission's S2
> (2D static) answers come from a log-median of open-weight members. The choice of which members to median in each
> cell (category x video source x unit kind) was made during development by comparing the open-weight members with
> our own Main Track (closed-API, Claude Opus) test predictions, which served as pseudo-labels. The comparison used test
> questions outside the validation videos and cells with at least 25 such questions, choosing among one- and
> two-member sets. The resulting table (`routing_base8_min25_k2.csv` and `fallback_category_sets.json`) contains member
> names only. A development script for the canonical-size clamp (`guard_tb.py`) also printed a comparison against
> Main Track predictions. The clamp classes and ranges in the submission are fixed world-knowledge ranges (car width
> 1.5-2.3 m, person height 1.50-2.00 m), checked against stated test priors and validation labels. At inference time the
> Open-Weight pipeline uses only publicly available weights (Qwen3-VL-32B-Instruct-FP8, Qwen3.5-27B, Gemma-4-31B-it, CaW, Grounding DINO, SAM 2.1) and
> model-free code on the test inputs. No closed-model output, parameter or answer value enters any Open-Weight answer.
> Validation labels were used only to score candidates and to choose among pre-registered levers, never to set an
> individual answer.
