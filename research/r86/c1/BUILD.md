# C1 micro bundle (PLAN.md item A2), Track A

Built 2026-10-14 by `research/r86/c1/build_c1.py`. Nothing was uploaded or committed. No files in `qp/` or `scripts/` were changed.

- **Base:** `submissions/trackA_combo3_on_combo2.csv` (combo3)
- **Output:** `submissions/trackA_cand_C1_on_combo3.csv`, written through `scripts/make_submission.py`
- **Logs:** `research/r86/c1/changes_C1.csv` (one line per row, with the reason) and `research/r86/c1/cap_clips.csv` (one line per pooled clip)

## What changed vs combo3

45 rows were set and 39 of them changed value. In 6 rows (the 3-row clips) the clip median is the row's own value, so the row keeps its value. All 45 rows are scored: none of them is a validation-overlap row. Every other row is identical to combo3, value for value.

| Component | Source | S2 | D2 | S3 | D3 | Set | Moved |
|---|---|---|---|---|---|---|---|
| B_fact | `r86/dsc` lever B: stated size facts. The 0012(+seg) bird length is set to 0010's prior of 1.19 m, and its wingspan is scaled by the same factor. The dragon length in 0282/0302/0309 is set to 0283's prior of 0.75 m. | | 5 | | 2 | 7 | 7 |
| C_readme | `r86/dsc` lever C: the small-bird length in 0088/0090/0091 is set to 0089's prior of 0.94 m. | | 3 | | | 3 | 3 |
| D_depthid | `r86/dsc` lever D: 0026(+seg) has a human depth track (114.8319/114.8356 m) identical to 0025's, which states 1.3 m/s. | | | 2 | | 2 | 2 |
| AUD_0020 | `loss_audit.md` §8.4: the whole simulation_0020 clip is rescaled so the person is 1.8 m tall, a factor of 1.8/9.4417 = 0.1906 on rows 8, 9 and 10. | | 3 | | | 3 | 3 |
| AUD_CAP | `loss_audit.md` §8.4: S2 sim constant-acceleration pooling. Each timed acceleration takes the clip median when it lies within ±20% of that median. Clips are the ones the audit names: 0223, 0224(+seg), 0253, 0254, 0255(+seg), 0256, 0234, 0235. | 30 | | | | 30 | 24 |
| **Total** | | **30 (24 moved)** | **11** | **2** | **2** | **45** | **39** |

These were deliberately **not applied**: all 22 A_qpool rows and all 7 E_kin rows in `r86/dsc/changes_famcons.csv`, as PLAN §2 A2 and §4 require. The build asserts that none of those rows was touched. Against the dsc candidate `cand_famcons_on_combo3.csv`, C1 differs on exactly 56 rows: those 29, plus the 27 audit rows that moved.

## Where each answer comes from (no labels)

- **Fact values** (1.19, 0.75, 0.94 and 1.3) are parsed in the script from the `prior` column of the test inputs (simulation_0010, 0283, 0089 and 0025).
  - The 0025/0026 depth-track identity is also checked in the script, from `depth_info`.
  - The script recomputes these values itself and asserts that they match the dsc log to rtol 1e-12.
- **Wingspan and the 0020 rows:** combo3 answers times a same-clip scale factor. The 1.8 m adult height is a fixed a-priori constant.
- **AUD_CAP:** the median of the clip's own combo3 answers.
- **Validation and test labels:** no test label exists here. The validation split is read only for its `(video_id, question)` keys, to flag overlap rows in the log; its answer column is never selected.
- **Track:** this is a Track A file only, and nothing here goes into Track B.

## Commands

```
.venv/bin/python research/r86/c1/build_c1.py
.venv/bin/python scripts/make_submission.py submissions/trackA_cand_C1_on_combo3.csv <scratch>/c1_recheck.csv   # byte-identical to the output
```

## Checks run

- **Inside `build_c1.py`:**
  - The base ids match `load_test()`.
  - Each fact value is parsed from the test priors and equals the expected value.
  - The 0025/0026 human depth tracks are identical.
  - The 12 fact rows match `changes_famcons.csv` exactly, in both old and new values.
  - No A_qpool or E_kin row was touched.
  - No row outside the change log moved.
  - All 3289 values are finite and > 0.
  - `make_submission.py` passed, and its re-read equals the built values.
- **Separate re-check:**
  - `make_submission.py` was re-run on the output, and the result is byte-identical (`cmp`).
  - Every column other than `parsed_value` is identical to combo3.
  - 39 rows changed vs combo3: S2 24, D2 11, S3 2, D3 2.
  - In combo3, none of the 45 rows was already a fact row. Their provenance is: rule>physb2 30, rule<=physb2 11, dmed 2, raw 2.

## Caveats for the read (PLAN A2: read per category vs combo3, and revert a category if it drops)

- **The expected effect is about +.001 overall, so only a drop is readable.** D2, S3 and D3 each have under 12 changed rows. S2's 24 moved rows move by a median of 2.2% and a maximum of 24.6%.
- **AUD_CAP confidence is low:**
  - 0253 (5.36 to 4.68) and 0254 (5.97 to 4.86) fall steadily with time, which may be real deceleration (audit note).
  - simulation_0223 at 1.5 s is a borderline member (0.803 of the clip median) and moves ×1.246, the largest S2 move.
  - If S2 drops, revert all of S2. Do not drop single rows on the basis of the read.
- **AUD_CAP covers only the audit's named clips.** Applied generically, the same rule would also take in 0153(+seg) (car), 0229/0230 (paper airplane) and 0163 (overlap, already equal). The audit did not list those clips, so they are left as in combo3.
- **D2 holds four components** (B_fact 5, C_readme 3, AUD_0020 3). A D2 drop cannot be split among them without another slot. The C_readme moves (about ×1.8, lower confidence per dsc) are the most likely cause.
- **Overlap with A1 (Sol blend):** the fact rows (B, C, D) are disjoint from A1. The 24 AUD_CAP S2 rows and the 3 AUD_0020 D2 rows are non-fact rows that A1 would also cover. A1 must therefore be built on top of C1, and the blend then either applies to the C1 values or skips these 27 rows, so that "upload 3 minus upload 2" isolates A1.

## Per-row change list

| qid | video | cat | component | old | new | new/old |
|---|---|---|---|---|---|---|
| 6 | simulation_0012 | D2 | B_fact | 2.0227 | 1.1900 | 0.588 |
| 7 | simulation_0012 | D2 | B_fact | 3.7971 | 2.2339 | 0.588 |
| 1649 | simulation_0012_segmented | D2 | B_fact | 1.9602 | 1.1900 | 0.607 |
| 1650 | simulation_0012_segmented | D2 | B_fact | 3.7615 | 2.2835 | 0.607 |
| 992 | simulation_0282 | D2 | B_fact | 0.8404 | 0.7500 | 0.892 |
| 1469 | simulation_0302 | D3 | B_fact | 0.6200 | 0.7500 | 1.210 |
| 1486 | simulation_0309 | D3 | B_fact | 0.6200 | 0.7500 | 1.210 |
| 134 | simulation_0088 | D2 | C_readme | 0.5321 | 0.9400 | 1.766 |
| 145 | simulation_0090 | D2 | C_readme | 0.5221 | 0.9400 | 1.800 |
| 149 | simulation_0091 | D2 | C_readme | 0.5181 | 0.9400 | 1.814 |
| 1115 | simulation_0026 | S3 | D_depthid | 0.4400 | 1.3000 | 2.955 |
| 1689 | simulation_0026_segmented | S3 | D_depthid | 0.4600 | 1.3000 | 2.826 |
| 8 | simulation_0020 | D2 | AUD_0020 | 9.4417 | 1.8000 | 0.191 |
| 9 | simulation_0020 | D2 | AUD_0020 | 5.2561 | 1.0021 | 0.191 |
| 10 | simulation_0020 | D2 | AUD_0020 | 1.3935 | 0.2657 | 0.191 |
| 684 | simulation_0223 | S2 | AUD_CAP | 0.7123 | 0.7123 | 1.000 (no move) |
| 686 | simulation_0223 | S2 | AUD_CAP | 0.7126 | 0.7123 | 1.000 |
| 688 | simulation_0223 | S2 | AUD_CAP | 0.5718 | 0.7123 | 1.246 |
| 691 | simulation_0224 | S2 | AUD_CAP | 1.0067 | 0.9956 | 0.989 |
| 693 | simulation_0224 | S2 | AUD_CAP | 0.9956 | 0.9956 | 1.000 (no move) |
| 695 | simulation_0224 | S2 | AUD_CAP | 0.9845 | 0.9956 | 1.011 |
| 1945 | simulation_0224_segmented | S2 | AUD_CAP | 0.8865 | 0.8375 | 0.945 |
| 1947 | simulation_0224_segmented | S2 | AUD_CAP | 0.8375 | 0.8375 | 1.000 (no move) |
| 1949 | simulation_0224_segmented | S2 | AUD_CAP | 0.7855 | 0.8375 | 1.066 |
| 859 | simulation_0253 | S2 | AUD_CAP | 5.2540 | 5.0879 | 0.968 |
| 860 | simulation_0253 | S2 | AUD_CAP | 5.3634 | 5.0879 | 0.949 |
| 861 | simulation_0253 | S2 | AUD_CAP | 4.9217 | 5.0879 | 1.034 |
| 862 | simulation_0253 | S2 | AUD_CAP | 4.6829 | 5.0879 | 1.086 |
| 867 | simulation_0254 | S2 | AUD_CAP | 5.9733 | 5.4867 | 0.919 |
| 868 | simulation_0254 | S2 | AUD_CAP | 5.7865 | 5.4867 | 0.948 |
| 869 | simulation_0254 | S2 | AUD_CAP | 5.1870 | 5.4867 | 1.058 |
| 870 | simulation_0254 | S2 | AUD_CAP | 4.8606 | 5.4867 | 1.129 |
| 874 | simulation_0255 | S2 | AUD_CAP | 1.0343 | 1.0257 | 0.992 |
| 875 | simulation_0255 | S2 | AUD_CAP | 1.0257 | 1.0257 | 1.000 (no move) |
| 876 | simulation_0255 | S2 | AUD_CAP | 1.0169 | 1.0257 | 1.009 |
| 2003 | simulation_0255_segmented | S2 | AUD_CAP | 1.0699 | 1.0520 | 0.983 |
| 2004 | simulation_0255_segmented | S2 | AUD_CAP | 1.0520 | 1.0520 | 1.000 (no move) |
| 2005 | simulation_0255_segmented | S2 | AUD_CAP | 1.0342 | 1.0520 | 1.017 |
| 880 | simulation_0256 | S2 | AUD_CAP | 1.1644 | 1.1644 | 1.000 (no move) |
| 881 | simulation_0256 | S2 | AUD_CAP | 1.1449 | 1.1644 | 1.017 |
| 882 | simulation_0256 | S2 | AUD_CAP | 1.1651 | 1.1644 | 0.999 |
| 765 | simulation_0234 | S2 | AUD_CAP | 2.4544 | 2.4107 | 0.982 |
| 767 | simulation_0234 | S2 | AUD_CAP | 2.3671 | 2.4107 | 1.018 |
| 773 | simulation_0235 | S2 | AUD_CAP | 2.3701 | 2.4229 | 1.022 |
| 775 | simulation_0235 | S2 | AUD_CAP | 2.4758 | 2.4229 | 0.979 |
