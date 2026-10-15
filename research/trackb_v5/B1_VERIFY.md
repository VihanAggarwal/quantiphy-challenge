# VERIFY: Track B candidate B1 (`submissions/trackB_cand_B1.csv`), independent check 2026-10-15

**Verdict: PASS.** I rebuilt B1 from its written component definitions with my own code, which does not import
`build_b1.py`. The result equals the submitted file on all 3289 rows (max relative difference 1.7e-13).

- Every row count and attribution that was claimed reproduces exactly.
- The file passes `scripts/make_submission.py`.
- No validation label reaches any test answer, and neither does any closed-model answer value.

The issues listed at the end do not block the upload.

The scripts and logs are in `research/trackb_v5/B1_verify/`. I did not modify any builder file, `qp/` or `scripts/`,
and I committed nothing.

## 1. Reproduction

| check | result |
|---|---|
| `build_b1.py` into a scratch path | byte-identical to `submissions/trackB_cand_B1.csv` (same md5) |
| `build_v5.py` main / `--l6s --l4` | byte-identical to `trackB_cand_v5.csv` / `trackB_cand_v5plus.csv` |
| `build_v5.py --no-l2q --no-l1` | 0 of 3289 rows differ from the uploaded v3 (max relative difference 9e-16) |
| `build_b1.py --decompose --val` | log identical to `B1_build.log` (apart from the paths); `B1_rows.csv` byte-identical |
| `check_b1.py` re-run | identical to `B1_checks.log`, except it now finds 97 Track A files instead of 95: two were added since (`trackA_cand_C1_solblend_on_combo3.csv`, `trackA_cand_solblend_on_combo3.csv`). It still finds 26 rows, all explained. |
| **independent rebuild** (`B1_verify/indep_b1.py`) | **0 of 3289 rows differ** |

What `indep_b1.py` does:
- It reads the 8 open member CSVs itself and asserts that they equal the harness table.
- It re-implements each component from the description in B1_BUILD.md:
  - the S2 cell routing (cell = category|source|unit kind, as in `pseudo_tb.py`) with the S2 fallback set;
  - L2' as qwen_geo -> qwen_fov in S3/D3;
  - L6s restricted to D2, from `build_v5.l6s_values`;
  - preset "trackb", taken from `qp.postprocess.PRESETS`;
  - L1, restricted to S3 and to rows not set by a stated-fact rule;
  - L4, recomputed from fps, the question time, the stated acceleration and `fall_t0.csv`. It asserts these equal
    the `new` column of `changes_ffbd.csv`;
  - the clamp, with its own regex loop.
- Component sizes: 552 routed + 27 fallback S2 rows, 0 empty routed rows, L6s 276, L1 145, L4 21, and clamp 47 rows
  (44 car width, 3 person height).

## 2. Rows changed vs v3, per category (`B1_verify/analyze.log`)

All rows / scored rows; a scored row is not a validation-overlap question.

| | S2 | D2 | S3 | D3 | total |
|---|---|---|---|---|---|
| B1 vs v3 (claimed) | 498/476 | 380/377 | 253/240 | 291/279 | 1422/1372 |
| B1 vs v3 (re-derived) | 498/476 | 380/377 | 253/240 | 291/279 | 1422/1372 |

**Leave-one-out attribution, scored rows:** identical to the claim.
- s2route: S2 473, D2 25, S3 15, D3 19
- l6s: S2 13, D2 335, S3 1, D3 33
- l4: D2 21
- l2q: S3 156, D3 218
- l1: S3 138
- clamp: S2 7, D2 18, S3 4, D3 16

Attribution coverage:
- Every changed row is attributed to at least one component (0 unattributed).
- The `components` column of `B1_rows.csv` matches my attribution row for row.
- The changed set in `B1_rows.csv` is exactly my 1422 rows.

**Spill-over reproduces:**
- S2 routing: 66 rows outside S2 (63 scored): D2 25, S3 17, D3 24. Plus 2 S2 rows that change only through pooling.
- L6s: 52 rows outside D2 (D3 38, S2 13, S3 1), plus 80 D2 rows that change only through pooling.
- L2': 0.

`B1_spillover.csv` (200 lines, 192 distinct qids) equals my spill-over set, and every one of those rows changes in B1.

**Other row checks:**
- S3/D3 lab rows: all 791 equal `trackB_cand_v5.csv`. The only non-lab differences from v5 are 20 S3 and 63 D3 rows,
  which are spill-over and clamp rows.
- Stated rows: the 166 rows set by facts / motionfam / freefall / labfacts change 0 times, and so do the 129
  `fact_labels.csv` rows. The stated set is the same in the base build and in B1.
- `--keep S2,D2,S3`: D3 rows equal v3 exactly and all other rows equal B1. The row-by-row revert works.

## 3. Submission format

`scripts/make_submission.py` passes on the file itself:
- 3289 rows in template order, with the template's columns;
- every value finite and > 0, and the ids unique;
- the round trip leaves every value unchanged;
- the non-value columns are identical to the uploaded v3 file.

## 4. Leakage and clean inputs

- **Validation labels do not reach test answers.** I rebuilt B1 with every validation answer replaced by random
  numbers. I patched `qp.data.load_validation` before loading, and confirmed the patch took effect. The result still
  differs on 0 rows.
- **Validation-overlap rows:** B1 changes 50 of the 131 overlap rows. None equals its validation label, and none is
  scored.
- **Files opened by my rebuild** (audit hook, 636 data files, listed in `B1_verify/indep_files_opened.txt`):
  - the test parquet, the validation csv (read but without effect, see the first bullet) and the template;
  - the open member CSVs in `/tmp/claude-0/tb3/x/trackb_v1/{test,val}/{caw,cv,cvq,qwen,qwen35,gemma4}`. The configs
    name Qwen3-VL-32B-Instruct-FP8, Qwen3.5-27B, gemma-4-31B-it and sam2.1-hiera-large + Grounding DINO;
  - 592 Qwen spec JSONs;
  - `trackb_dense/out` re-solved geometry, `out_test_cvq_seg.csv` and the model-free `_postprocess_cache`;
  - the two routing files (member names only), `changes_ffbd.csv` and `fall_t0.csv`;
  - `labtracks_test_qwen.pkl`, plus `fit_noise.json` (loaded when `emulate.py` is imported);
  - v3 and B1, which are read only for the comparison.

  None of these is a Track A, Claude, Sol, Argon, Gemini or GPT answer file. There were no subprocesses.
- **`labtracks_test_qwen.pkl` (the L1 input)** rebuilds from the Qwen annotate JSONs with
  `labnoise_open.build_tracks` (cache redirected to scratch). All 806 records are identical.
- **L1 factors** are unchanged in each of these cases:
  - the Track A `fit_noise.json` sigmas are set to NaN;
  - the Table 6 `BALL_D` table is emptied;
  - every ball is forced into the large class.

  In all three, 199 factors differ from 1, so no Table 6 size and no Track A fit reaches an answer. The reason is
  that sigma_zb = sigma_zL = 0.02 makes the ball class irrelevant.
- **Routing selection is reproducible from pseudo-labels alone.** Re-running the `dump.py` selection gives all 7 S2
  cells, their n_fit values and the S2 fallback set exactly. The selection uses only Track A combo2 test predictions
  on test rows of non-validation videos, and validation video ids only (no answers). This is development-time
  selection of member names, which the FAQ allows if disclosed, and B1_BUILD.md discloses it.
- **Closed-model answer values (`B1_verify/closed_scan.log`).** I scanned 113 files, a wider set than check_b1:
  - `submissions/trackA_*`, `research/r86/plan86/*`;
  - `runs/test_*/test.csv`, including the Claude test runs and Sol `test_sol_high`, both `parsed_value` and
    `direct_value`;
  - every research CSV whose path names a closed model.

  26 of the 1422 changed rows equal a closed value for the same question. These are the same 26 rows that check_b1
  reports:
  - 21 are the L4 formula; Track A's ffbd candidate uses the same model-free formula;
  - 2 are the clamp bound 2.3;
  - 3 are the row's own open member value (qwen_direct/qwen35 10, qwen35 10.8, caw 6.7).

  None is unexplained. Because my audited rebuild reproduces B1 exactly from open inputs, no closed value can be in
  the answers.

## 5. Validation (scoring only)

The `--val` numbers reproduce:
- v3 .6227 -> B1 .6458 (+.0231, clip bootstrap 90% [-.0000, +.0432]);
- S2 .575 -> .619, D2 .5865 -> .5946, S3 .693 -> .721, D3 .636 -> .649.

The clamp range claims check out:
- Stated test person heights in priors are 1.63-1.87 m.
- Validation labels are 1.61-1.87 m for person height and 1.86-2.21 m for car width.
- No test prior states a car width.

## 6. Issues (none blocking)

1. **Clamp direction wording.** "41 go down and 6 go up" is relative to v3. Relative to the value before the clamp it
   is 43 down and 4 up. The row set (47 rows) is correct either way.
2. **Clamp coverage gap.** This is a design observation, not a build defect: the regex is guard_tb.py's, as specified.
   - `width of the (?:\w+ )?car` allows only one word before "car". So 19 car-width questions with longer
     descriptions ("turning yellow car", "black and white car", "grey and red car", "dark green car") are not
     clamped.
   - All 19 sit at an implausible 3.57-5.82 m in B1.
   - One of them, qid 45 (S2, simulation_0071), was 2.15 m in v3. B1 moves it to 3.57 m through routing plus pooling.
   - Widening the regex (for example `(?:\w+ ){0,3}`) would be an a-priori fix. It would need its own read and
     disclosure, and it is not in B1.
3. **Git.** Commit `7849ad2` ("Track B B1 bundle build ... verification in progress", 00:38 UTC) contains the 8 B1
   files.
   - It was made from the lead session (same Claude-Session id) after the builder finished (B1_BUILD.md 00:17), so
     the builder's "nothing committed" was true for the builder.
   - The committed CSV is identical to the working file.
4. **Rounding.** The ALL bootstrap lower bound is -0.0000 (printed as .000 in B1_BUILD.md).
5. **Disclosed gray areas, confirmed and unchanged:**
   - The S2 routing is in-sample with respect to Track A pseudo-labels on the same test rows, so its fact-row read
     (.800 -> .856) is not independent.
   - `guard_tb.py` printed a comparison with Track A while the clamp was developed.
   - The S3 read mixes L2' (156 scored rows) and L1 (138), plus spill-over.
   - L6s and L2' were chosen post hoc.

**Expected gain:** I agree with the central +.015 (+.007 to +.025) and with treating validation's +.023 as optimistic.
The per-category kill thresholds in B1_BUILD.md (S2 .559, D2 .664, S3 .621, D3 .642) equal PLAN.md's (v3 + .001).

## Commands (CPU only, outputs to scratch)

```
.venv/bin/python research/trackb_v5/build_b1.py --out <scratch>/B1_rebuild.csv
.venv/bin/python research/trackb_v5/build_b1.py --out <scratch>/B1_dec.csv --rows <scratch>/rows.csv --decompose --val
.venv/bin/python research/trackb_v5/build_v5.py --out <scratch>/v5.csv            # and --l6s --l4 / --no-l2q --no-l1
.venv/bin/python research/trackb_v5/check_b1.py submissions/trackB_cand_B1.csv
.venv/bin/python research/trackb_v5/build_b1.py --out <scratch>/B1_keep3.csv --keep S2,D2,S3
.venv/bin/python scripts/make_submission.py submissions/trackB_cand_B1.csv <scratch>/B1_resub.csv
.venv/bin/python research/trackb_v5/B1_verify/indep_b1.py --audit --out <scratch>/indep_B1.csv
.venv/bin/python research/trackb_v5/B1_verify/indep_b1.py --scramble-val
.venv/bin/python research/trackb_v5/B1_verify/analyze.py
.venv/bin/python research/trackb_v5/B1_verify/closed_scan.py
.venv/bin/python research/trackb_v5/B1_verify/l1_routing_checks.py
.venv/bin/python research/trackb_v5/B1_verify/clamp_check.py
.venv/bin/python research/trackb_v5/B1_verify/labtracks_check.py <scratch dir>
```
