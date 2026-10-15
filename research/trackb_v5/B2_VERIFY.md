# VERIFY: Track B probe B2route and candidate B1clamp, independent check 2026-10-15

Files checked: `submissions/trackB_probe_B2route.csv` and `submissions/trackB_cand_B1clamp.csv`, built by
`research/trackb_v5/build_b2.py` (B2_BUILD.md).

**Verdict: PASS for both files.**
- Both rebuild byte for byte from `build_b2.py`.
- My own rebuild, which imports neither `build_b1.py` nor `build_b2.py`, equals both files on all 3289 rows.
- Every row count and attribution in B2_BUILD.md reproduces.
- Both files pass `scripts/make_submission.py`, and the round trip leaves the values unchanged.
- No validation label and no Track A value reaches any answer.

The issues in section 8 do not block the uploads. Two of them affect how the D3 and S3 reads should be interpreted
(8.1 and 8.2).

The scripts and logs are in `research/trackb_v5/B2_verify/`. I did not modify `qp/`, `scripts/`, `build_b1.py`,
`build_b2.py` or any other existing file, made no paid call, and committed nothing. `git diff HEAD` is empty. The only
untracked files are the B2 build's, plus this file and `B2_verify/`.

## 1. Reproduction

| check | result |
|---|---|
| `build_b2.py --out <scratch>` (B2route defaults) | byte-identical to `trackB_probe_B2route.csv` (md5 aa7893d5...) |
| `build_b2.py --route S2 --clamp wide` | byte-identical to `trackB_cand_B1clamp.csv` (md5 372a8020...) |
| `build_b2.py --route S2 --clamp b1` and `build_b1.py` | both byte-identical to `trackB_cand_B1.csv` (md5 86a48519...) |
| `build_b2.py ... --rows --decompose --val` (both files) | logs identical to `B2_build.log` / `B1clamp_build.log` (apart from paths and stderr warnings); `B2_rows.csv` and `B1clamp_rows.csv` byte-identical; the internal "route S2 + clamp b1 == B1" assertion passes |
| `check_b2.py` re-run (`B2_verify/check_b2_rerun.log`) | identical to `B2_checks.log`, except for the builder's trailing "exit 0" line |
| **independent rebuild** (`B2_verify/indep_b2.py`) | **0 of 3289 rows differ** for B1, B2route and B1clamp (max relative difference 1.2e-13 / 1.7e-13); the base with v3 sets reproduces the uploaded v3 (0 rows) |

These rebuilds use the current `build_b2.py`, which already has `--keep-ref`. That confirms the builder's note that
the outputs did not change when the option was added.

What `indep_b2.py` does. It starts from the same shared base as `B1_verify/indep_b1.py`: the `harness.Data` member
table, `qp.postprocess` preset "trackb" and `build_v5.l6s_values`. Then:
- It reads the 8 open member CSVs itself, asserts that they equal the harness table, and asserts that qwen_fov differs
  from qwen_geo only on lab rows.
- It re-implements the routing from B2_BUILD.md:
  - every row of a routed category gets the category fallback set;
  - each cell of `routing_base8_min25_k2.csv` gets its listed set;
  - an empty row falls back to the fallback set, then to the B1 set;
  - L2' is applied inside S3/D3 routed and fallback sets.
- L6s overrides on D2, then the rules run, then L1 (S3, not stated), then L4 (recomputed from fps, the question time,
  the stated g and `fall_t0.csv`, and asserted equal to `changes_ffbd.csv`), then the clamp.
- The wide car-width clamp is my own token parser, written from the B2_BUILD.md spec rather than from build_b2's
  regex. Over all 3289 test questions it selects exactly the same rows as the builder's regex (0 disagreements).

## 2. Rows changed per category (from the files; all / scored)

| | S2 | D2 | S3 | D3 | total |
|---|---|---|---|---|---|
| B2route vs B1 (claimed) | 17/16 | 856/836 | 462/430 | 832/798 | 2167 |
| B2route vs B1 (re-derived) | 17/16 | 856/836 | 462/430 | 832/798 | 2167 |
| B2route vs v3 | 498/476 | 1057/1034 | 482/450 | 832/798 | |
| B1clamp vs B1 (claimed = re-derived) | 5/5 | 6/6 | 1/1 | 7/7 | 19 |
| B1clamp vs v3 | 498/476 | 381/378 | 253/240 | 291/279 | |

**Leave-one-out attribution (scored rows), re-derived; identical to the claim:**

| | own only | own + other | other only | interaction only | raw unchanged (pool spill) |
|---|---|---|---|---|---|
| S2 | 0 | 0 | 14 | 2 (qids 12, 1746) | 16 |
| D2 | 722 | 102 | 12 | 0 | 98 |
| S3 | 384 | 43 | 3 | 0 | 2 |
| D3 | 637 | 153 | 8 | 0 | 12 |

Rows touched by another category's routing, scored:
- S2: D2 6, S3 6, D3 7.
- D2: S3 8, D3 113.
- S3: D2 2, D3 45.
- D3: D2 85, S3 81.

Each category added alone to B1, all / scored: identical to the claim.
- route D2: S2 4, D2 838/818, D3 73.
- route S3: S2 10/9, D2 3, S3 456/424, D3 76/72.
- route D3: S2 9, D2 136, S3 42/40, D3 824/790.

**Qids 12 and 1746 (correction to B2_BUILD.md).** B2_BUILD.md says they change "only when two categories are routed
together". That is not what happens:
- Routing S3 alone or D3 alone (on top of B1) already gives exactly the B2route values, 12.592 and 8.991, against
  8.129 in B1. Routing D2 alone leaves them at B1.
- The two causes are redundant, so leaving one category out cannot undo the change, and leave-one-out labels the rows
  "interaction only".
- The counts are right; only the explanation is wrong (see 8.5).

**Builder row files:**
- `B2_rows.csv`: the changed set equals my 2167 rows. The `attribution`, `raw_changed` and `spill` columns and the new
  values match mine row for row.
- The `new_winner` totals reproduce: D2 441 cell / 20 fallback / 381 pool / 8 L6s / 6 clamp; S3 246 / 24 / 59 / 133 L1;
  D3 589 / 8 / 232 / 3 clamp; S2 5 cell / 12 pool.
- The "pool rule" winners are exactly the changed rows where the pool rule applied and no later step touched the row.
- `B2_spillover.csv`: 419 rows. They equal my set of changed rows that are either raw-unchanged or touched by another
  category's routing.
- `B1clamp_rows.csv`: equals my 19 rows.

## 3. Components inside B2route (all claims reproduce)

**Routing:**
- Cell row counts match B2_BUILD.md:
  - D2: 169 / 47 / 138 / 32 / 590 / 158;
  - S3: 179 / 143 / 38 / 91 / 55;
  - D3: 350 / 101 / 72 / 330 / 90.
- Fallback rows:
  - D2 29 (simulation A 10, lab L 9, lab V 6, segmentation A 3, internet A 1);
  - S3 72 (segmentation V 27, simulation A 23, lab A 12, segmentation A 10);
  - D3 26 (segmentation V 14, lab A 6, simulation A 5, segmentation A 1).
- 0 routed rows were empty, and 0 fell back to the B1 set.

**L2':**
- qwen_fov differs from qwen_geo on 757 rows, all of them lab (S3 319, D3 438).
- In B2route all 319 S3 rows still use qwen_fov: lab L 170, lab V 143, lab A 6 (fallback).
- 0 D3 rows use it. In B1 all 438 D3 lab rows used it.

**L6s:**
- 276 D2 rows.
- The routed set underneath is cvq_geo alone on 253 of them: segmentation L 118, simulation L 113, simulation V 22.
- The other 23 are segmentation V rows with the set cvq_geo+qwen_geo.

**L1:** 143 rows in B2route vs 145 in B1, with 142 in both.
- Rows 2379, 2540 and 2666 drop out. `labnoise_open.factors` sets a factor within 3% of 1 to exactly 1.
- Row 2624 is new.

**L4:** 21 rows, final values equal to B1.

**Stated:** the same 166-row set as B1, with 0 values changed. 0 of the 129 `fact_labels.csv` rows change, in either
file.

**Clamp (B1 regex):** 30 rows (car width 18, person height 12).
- 21 rows are clamped in both B1 and B2route.
- 26 B1-only rows are all car widths, now in range at 1.800-2.207 m.
- 9 rows are newly clamped: 8, 2266, 2271, 2276, 2293, 2312, 2331, 2973 and 3151. Their post-rule values:

| rows | video | post-rule | clamped to | raw source |
|---|---|---|---|---|
| 8 | simulation_0020 | 12.94 m | 2.0 m | D2 sim L cvq_geo |
| 2266, 2271, 2276 | captured_0015, 0015s, 0015x | 310-318 cm | 200 cm | D2 lab fallback |
| 2293, 2312, 2331 | captured_0018, 0018s, 0018x | 128 cm | 150 cm | D3 lab L cvq_geo+qwen35 |
| 2973 | internet_0019_segmented | 143.9 cm | 150 cm | |
| 3151 | internet_0055 | 2.007 m | 2.0 m | |

**Alternatives (not uploaded), re-derived:**
- `--no-l2q-route`: exactly the 319 S3 lab rows differ (302 scored), and nothing else.
- Routing wins over L6s (no L6s): raw differs on D2 275/271 rows. Final differs on D2 337, S2 11, S3 1 and D3 41 rows.

**Revert:** `--keep S2,D2,S3`, rebuilt independently and also taken from the builder's output, gives D3 equal to B1 and
every other row equal to B2route. The two versions are identical.

## 4. B1clamp

- **The 19 changed rows:** 35, 42, 45, 58, 90, 97, 105, 273, 293, 1286, 1299, 1312, 1324, 1337, 1354, 1366, 1769, 1781
  and 1840.
  - By category: S2 5, D2 6, S3 1, D3 7.
  - All are scored, and all are set to exactly 2.3 m, down from B1 values of 3.573 / 4.126 / 5.461 / 5.823 m.
  - In total 66 rows are clamped: 63 car width and 3 person height (B1's 47 plus these 19).
- **Rows the wide regex adds:** 19 rows, with the phrases turning yellow car 13, black and white car 3, grey and red
  car 2, dark green car 1.
  - None of them contains "toy", and none is a stated row.
- **Not matched:** 9 of the 81 "width ... car" questions, the same 9 that B2_BUILD.md lists:
  - road 400 and 1396;
  - "(from the left wheel to the right wheel)" 1456, 1466, 1496;
  - lettering 1533;
  - "width, in meters, of the blue car" 1536, 1541, 2011.
- **Validation:** 0 rows change.
- **Expected gain:** I checked the +.004 arithmetic. An answer of 2.3 m scores .5 / .7 / 1.0 for a true width of
  1.8 / 2.0 / 2.2 m, against about 0 now.
- **The same 19 rows in B2route** sit at 1.953-7.478 m:
  - The D3 and S3 turning-yellow-car rows are routed to 1.953 m, which is in range.
  - The S2 rows 42, 45, 58 and the D2 row 35 sit at 5.19-5.32 m.
  - Wording correction: those S2/D2 rows were pooled with the D3 0062-0067 rows in B1. In B2route they are no longer
    pooled and keep their own cvq_geo / L6s raw values. "Pooled with the D3 rows, they move to 5.2 m" in B2_BUILD.md
    describes the same change loosely.

## 5. Submission format

- `scripts/make_submission.py` passes on both files.
- 3289 rows in template order, with the template's columns. The non-value columns are identical to the template and
  to B1.
- Every value is finite and > 0, and the ids are unique.
- The round trip leaves every value bit-identical.

## 6. Leakage and clean inputs

**Files opened by my rebuild.** Under an audit hook it opened 640 data files, with no subprocess
(`B2_verify/indep_files_opened.txt`):
- the test parquet, the validation csv and the template;
- the open member CSVs and 592 Qwen spec JSONs under `/tmp/claude-0/tb3/x/trackb_v1`;
- `trackb_dense/out` re-solved geometry, `out_test_cvq_seg.csv` and the `_postprocess_cache`;
- the two routing files, `changes_ffbd.csv`, `fall_t0.csv`, `labtracks_test_qwen.pkl` and `fit_noise.json`;
- 4 Track B submission files (v3, B1, B2route, B1clamp), read only for the comparison.

None of these is a Track A, Claude, Sol, Argon, Gemini or GPT answer file. The builder's own audit (check_b2 re-run)
gives the same picture: 639 files, and the only subprocess is `make_submission.py`.

**Validation labels do not reach test answers.**
- I rebuilt all three files with every validation answer replaced by random numbers (`--scramble-val`). I patched
  `qp.data.load_validation` before loading, and checked that 0 of 159 labels in `harness.Data` were left unchanged.
- All three files still differ on 0 rows (`B2_verify/scramble.log`).

**Validation-overlap rows (unscored).**
- B2route changes 87 of the 131 overlap rows; B1clamp changes 0.
- One B2route row, qid 1077 (simulation_0015, bench seat height), equals its validation label of 0.45 m. This is a
  coincidence:
  - 0.45 is the round direct answer of four open members (caw, qwen_direct, qwen35, gemma4);
  - the routed S3 sim L set (qwen_direct+gemma4) returns it;
  - the row is not scored, and the scramble test rules out a label path.

**Track A answer values** (`B2_verify/closed_scan.log`). Each match is explained using the independent rebuild:
- **Scan 1, check_b1 style** (parsed_value of 99 files: `submissions/trackA_*` and `research/r86/plan86/trackA_*`):
  - B2route: 12 of its 2167 changed rows equal a Track A value. These are the same 12 that check_b2 reports
    (1153, 1210, 1319, 1342, 1348, 1636, 1641, 1730, 1735, 1763, 1774, 1898). Each is the row's own round open direct
    answer (1.75, 0.15, 3.5, 1.8, 0.45, 0.6 or 3.2 from qwen35 / gemma4 / qwen_direct / caw).
  - B1clamp: 0.
- **Scan 2, wider** (all numeric columns of 109 files: the above, `runs/test_*` Claude and Sol test runs including
  direct_value, and every research CSV whose path names a closed model; files must cover at least 300 test qids):
  - B2route: 15 rows. The 12 above plus 1224, 1267 and 1465, all of them own open round direct answers (0.15, 1.8,
    4.5).
  - B1clamp: 1 row, 1354, which is the clamp bound 2.3.
  - Unexplained: none.
- Since the audited rebuild reproduces both files exactly from open inputs, no closed value can be in the answers.

**Routing provenance** (`B2_verify/routing_check.log`).
- Re-running the `pseudo_tb.py` / `dump.py` selection reproduces every one of the 23 cells (member set and n_fit) and
  all 4 category fallback sets exactly. The settings are k = 1-2 for cells and 1-4 for fallbacks, with cells of at least
  25 fit rows.
- The selection uses only Track A combo2 test predictions on test rows of non-validation videos. From the validation set
  it uses video ids only, not answers.
- This is development-time selection of member names, which the FAQ allows if disclosed. B2_BUILD.md's updated
  disclosure note covers routing in all four categories and the clamp widening.
- Track A values are read only by this verifier script. Nothing in it writes an answer.

## 7. Validation (scoring only)

`--val` reproduces exactly:

| build | MRA | S2 | D2 | S3 | D3 | clip bootstrap delta vs B1 [90%] |
|---|---|---|---|---|---|---|
| B1 | .6458 | .6187 | .5946 | .7209 | .6489 | |
| B1 + route D2 | .6424 | .6187 | .5811 | .7209 | .6489 | -.0034 [-.009, +.006] |
| B1 + route S3 | .6491 | .6250 | .5946 | .7279 | .6489 | +.0033 [-.008, +.012] |
| B1 + route D3 | .6366 | .6187 | .5946 | .7116 | .6213 | -.0092 [-.031, +.019] |
| B2route | .6371 | .6250 | .5811 | .7209 | .6213 | -.0087 [-.036, +.023] |
| no L2' in routed sets | .6371 | | | | | -.0087 [-.035, +.022] |
| no L6s | .6381 | | | | .6255 | -.0077 [-.035, +.024] |
| B1clamp | .6458 | | | | | 0 (0 rows) |

**Stated-fact rows**, raw values before the facts rule (values stated in the test priors, not test labels): D2 8 rows
.787 -> .950, S3 12 rows .692 -> .817, D3 50 rows .788 -> .762. All reproduce.

**Kill thresholds:** B1 + .001 gives D2 .677, S3 .640 and D3 .653, against the B1 reads .676 / .639 / .652.

## 8. Issues (none blocking)

1. **The D3 read mixes the routing with dropping L2' on lab rows.**
   - 410 of the 798 changed scored D3 rows are lab rows. In B1 all of them used qwen_fov (L2'), the fix that was part of
     B1's D3 gain of +.011 (218 scored D3 rows in the B1 attribution).
   - The D3 lab routed sets (cvq_geo+qwen35, cv_geo+gemma4) and the fallback set have no Qwen geometry member, so L2'
     disappears on all 438 D3 lab rows.
   - So a D3 fail cannot be pinned on the routing itself: losing L2' could explain part of it.
   - Pseudo-label agreement points the same way, as development-time information only: on D3 lab L, the best 1-2 member
     set with qwen_fov allowed as a 9th candidate is qwen_direct+qwen_fov at .666, vs .658 for the routed set.
   - If D3 fails, a non-lab-only D3 routing would separate the two effects. build_b2.py has no option for this today.
2. **The S3 read includes D3 spill-over that was negative on validation.**
   - D3 routing touches 45 scored S3 rows.
   - On validation, route D3 alone lowers S3 by .0093 (.7209 -> .7116). Route S3 alone raises it by .0070, and in the
     full build the two cancel: S3 = .7209, the same as B1.
   - So B2route's S3 read probably understates S3 routing on its own. If S3 misses .640 narrowly, `--route S2,S3` (the
     builder's own suggestion) is the clean read.
3. **L2' inside the routed S3 lab sets is an interpretation, and both readings look equally good.**
   - Pseudo-label agreement: S3 lab L .745 with qwen_geo vs .735 with qwen_fov; S3 lab V .729 vs .741.
   - Validation is identical.
   - The builder's choice (319 rows on qwen_fov) is consistent with how B1 treats L2', as a fix to the member, and it is
     disclosed in B2_BUILD.md.
   - The table lists qwen_geo, so the disclosure should keep the note that the lab Qwen member is re-solved with the
     fixed camera.
4. **B2route makes larger moves.**
   - 569 of the 836 changed scored D2 rows take a single-member answer (cvq_geo alone), so no median protects them.
     Row 8 (a person height of 12.94 m) is caught only because the clamp covers person heights.
   - Scored rows that move by more than 2x vs B1: D2 74 (8.9%), D3 126 (15.8%), S3 29 (6.7%), S2 0.
   - Expect a noisy read. This is information, not a defect.
5. **Two explanations in B2_BUILD.md are wrong or loose; the counts are right.**
   - S2 qids 12 and 1746 do not need two categories routed together: S3 routing alone or D3 routing alone moves them to
     the same values (section 2). For the S2 read this means these 2 rows move if either S3 or D3 routing is kept in a
     `--route` rebuild. The `--keep` revert keeps B2route's S2 values whatever is reverted.
   - "Pooled with the D3 0062-0067 rows, they move from 3.57 to 5.19-5.31 m" is loose. The S2 rows 42, 45 and 58 are no
     longer pooled in B2route and take their own raw cvq_geo values (section 4).
6. **Disk space.** The root filesystem is at 99% (about 640 MB free). Other processes hold about 2.6 GB in `/tmp/blind`
   and about 2.8 GB in `/tmp/pip-unpack-*`.
   - One of my `make_submission.py` round trips into scratch failed with ENOSPC, and passed on retry.
   - The submission files were not affected: the md5s are unchanged.
7. **Process note (mine).** A shell-variable slip briefly wrote three verifier outputs (B1/B2 rebuild CSVs and logs) to
   `/`. I moved them to scratch at once. No repository file was touched.

## Commands (CPU only, outputs to scratch)

```
.venv/bin/python research/trackb_v5/build_b2.py --out <s>/B2route.csv
.venv/bin/python research/trackb_v5/build_b2.py --out <s>/B1clamp.csv --route S2 --clamp wide
.venv/bin/python research/trackb_v5/build_b2.py --out <s>/B1_via_b2.csv --route S2 --clamp b1
.venv/bin/python research/trackb_v5/build_b1.py --out <s>/B1_via_b1.csv
.venv/bin/python research/trackb_v5/build_b2.py --out <s>/B2_keep3.csv --keep S2,D2,S3
.venv/bin/python research/trackb_v5/build_b2.py --out <s>/B2_dec.csv --rows <s>/B2_rows.csv --decompose --val
.venv/bin/python research/trackb_v5/build_b2.py --out <s>/B1c_dec.csv --route S2 --clamp wide --rows <s>/B1clamp_rows.csv --decompose --val
.venv/bin/python research/trackb_v5/check_b2.py submissions/trackB_probe_B2route.csv submissions/trackB_cand_B1clamp.csv
.venv/bin/python scripts/make_submission.py submissions/<file>.csv <s>/resub_<file>.csv
.venv/bin/python research/trackb_v5/B2_verify/indep_b2.py --audit --outdir <s>/indep
.venv/bin/python research/trackb_v5/B2_verify/indep_b2.py --scramble-val --outdir <s>/scr
.venv/bin/python research/trackb_v5/B2_verify/analyze_b2.py <s>
.venv/bin/python research/trackb_v5/B2_verify/closed_scan_b2.py
.venv/bin/python research/trackb_v5/B2_verify/routing_check_b2.py
```
