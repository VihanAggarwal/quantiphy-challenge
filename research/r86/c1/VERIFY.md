# VERIFY: C1 micro bundle (PLAN A2), independent check 2026-10-15

Verdict: **PASS.** `submissions/trackA_cand_C1_on_combo3.csv` equals the change set re-derived from the named
components. Only the 39 claimed rows differ from combo3 (S2 24 / D2 11 / S3 2 / D3 2), every other column is
identical, `make_submission.py` passes, and no label is used. All BUILD.md numbers reproduce. Three of the 30 AUD_CAP
rows, including the two largest S2 moves, are rows the audit's own computation would have left out (finding 1).

## What I re-ran (CPU only; writes went to the session scratchpad, no file of the build was modified)
| Check | Result |
|---|---|
| `build_c1.py` copy with only ROOT/OUTD/OUT redirected to scratch | CSV, `changes_C1.csv`, `cap_clips.csv` byte-identical (sha256 08b1d9c1...) |
| `r86/dsc/build_famcons.py` copy with OUTD redirected | `changes_famcons.csv` and `cand_famcons_on_combo3.csv` byte-identical to the tracked files |
| `research/r86/c1/verify_c1.py` (mine; own parsing from the raw parquet, not the builder's code) | 28/28 PASS, below |
| `scripts/make_submission.py` on the C1 file into scratch | "3289 rows, 761 KB, ready to upload"; output `cmp`-identical to the C1 file |
| `git status` | qp/, scripts/, combo3 and r86/dsc unchanged. Nothing committed. The C1 CSV is gitignored (`submissions/*.csv`) |

## Change set, re-derived independently (verify_c1.py)
- Ids, row order and columns match the template. The 9 non-value columns are string-identical to combo3. The string
  diff set equals the numeric diff set: **39 rows**.
- I found the rows from the test inputs, not from the builder's qid list:
  - B_fact: every "length of the dragon" row outside 0283 (exactly 992, 1469, 1486); the 0012(+seg) bird length and
    wingspan rows.
  - C_readme: every "length of the small bird" row outside 0089 (exactly 134, 145, 149).
  - D_depthid: the 0026(+seg) person-speed rows, after checking that both 0026 depth tracks give the same human track
    as 0025 (114.8319 / 114.8356).
  - AUD_0020: all 3 rows of simulation_0020.
  - AUD_CAP: every acceleration question in the 10 named clips. All of them parse as timed, so none was missed.
- The values come from the test priors (1.19, 0.75, 0.94, 1.3) plus the 1.8 m constant. C1 equals the re-derived
  values on all 45 rows (max rel diff 2e-16), and the rows that move are exactly the 39 that differ.
- Per category, moved/set (category row count): S2 24/30 (579), D2 11/11 (1163), S3 2/2 (578), D3 2/2 (969).
- The 12 fact rows equal the dsc B/C/D rows in both old and new values. The 22 A_qpool and 7 E_kin rows are unchanged
  vs combo3. C1 differs from the dsc candidate on exactly 56 rows (those 29 plus the 27 audit movers).
- AUD_CAP moves: median 2.2%, max 24.6%. The 6 rows that do not move are the middle rows of the six 3-row clips.

## Leakage and rules
- Validation is read for keys only (`usecols=[video_id, question]`; the label column is never loaded). None of the 45
  rows is one of the 128 test/validation overlap rows, and none of their video ids appears in validation.
- build_c1.py reads no label: it subsets `load_split("val_hires")` to the two key columns and never opens master.pkl.
  Its only constants are the four prior values (asserted against the parsed priors), 1.8 m, the 20% tolerance and the
  depth-track values (asserted from `depth_info`).
- No paper Table 6 size: C1 touches no lab row. Track A file only. No Track B file is written or affected.

## Findings for the read (beyond BUILD.md)
1. **AUD_CAP base, reconstructed exactly.**
   - The audit's "33 qualify, 23 move > 1%" reproduces exactly when its rule is run on all S2 sim clips using the
     **pre-combo3 routed answers** (`r_parsed_value`): the 10 named clips give 27 rows, plus 0153(+seg) and 0163.
   - On combo3 the named clips give 30 rows. The 3 extra rows were outside ±20% on the raw base: **688 (0223 1.5 s,
     ×1.246), 870 (0254 1.75 s, ×1.129), 859 (0253 0.5 s, ×0.968)**. Later combo3 rules moved them inside.
   - The build follows PLAN A2 as written (combo3 base, named clips, "~30 rows"), so this is not a defect.
   - The two largest S2 moves are exactly the rows the audit did not count. If a more conservative S2 is wanted,
     revert rows 688/870/859 to combo3: that leaves 27 rows set and 21 moved.
2. **C_readme puts the small bird above the big bird.**
   - In 0088/0090/0091 the small-bird length becomes 0.94 m, while the same clip's big-bird length stays at
     0.726/0.723/0.736 m. In 0089, which states the small bird, the big bird is 1.49 m.
   - So either those clips' whole size scale is about 2× too low (rows 132/144/148 then also miss and are left
     alone), or the transfer is wrong.
   - This supports BUILD.md's call that C_readme is the most likely cause of a D2 drop.
3. **S3 and D3 are clean single-component reads.**
   - S3 changes only D_depthid (2 rows, ×2.9). That fact (1.3, rule `motionfam`) is in the path85 facts log, but
     combo3 had declined it (prov `dmed`, 0.44/0.46).
   - BUILD.md's "none of the 45 was already a fact row" is true of the combo3 values.
   - D3 changes only the 0302/0309 dragon rows.
4. **Minor asymmetry in B_fact, as dsc specified.** The 0012 wingspan is rescaled with the bird-length factor. The
   0282 dragon wingspan (row 993) and displacement (row 994) are not rescaled by ×0.892.
5. **0020 sanity check.** After the rescale the ball diameter is 0.266 m (a basketball is about 0.24 m), which is
   consistent with the rescale. The implied gravity is no longer the stated 9.8 m/s²: the fix bets that the labels
   follow the asset scale, as the audit says.

## Commands
```
.venv/bin/python -I research/r86/c1/verify_c1.py          # 28 checks, prints OVERALL PASS; writes nothing
.venv/bin/python scripts/make_submission.py submissions/trackA_cand_C1_on_combo3.csv <scratch>/c1_mksub.csv
cmp <scratch>/c1_mksub.csv submissions/trackA_cand_C1_on_combo3.csv
```
