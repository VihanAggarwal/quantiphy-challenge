# VERIFY: trackb_next (Track B RUN_PRESET "ctx"), reported verdict INCONCLUSIVE

Verifier: independent re-run on 2026-10-14/15, CPU only, no API calls, no GPU. No agent file was changed. All
re-runs used copies of the scripts in the verifier's scratch directory (ROOT patched to the repo), so the agent's logs
and CSVs were not overwritten.

## Verdict
**INCONCLUSIVE confirmed.** The GPU run has not happened, so nothing can PASS or FAIL yet. The diagnosis reproduces
exactly. The code runs end to end on CPU with a mock model. There is no leakage. **But criterion 4 of the
pre-registered kill test cannot fail as it is written** (see issue 1). Fix it before the run's outputs arrive.

## 1. Reproduction (all match)
| command (verifier copy) | result |
|---|---|
| `diagnose.py` | log and `diag_rows.csv` **byte-identical** to the agent's (members, 2x2 swap QQ .507 / QC .733 / CQ .507 / CC .730, spec agreement 97-100%) |
| `diag_px.py`, `diag_mix_cvq.py`, `diag_hires.py` | logs and row CSVs byte-identical (cvq .554 -> cvqP+cT .671; full-res qwen_geo_raw .556, cvq_geo_raw .572 on 131 q) |
| `diag_boot.py` | identical: tracks +.226 [+.159, +.305]; spec -.000 [-.004, +.003]; cvq target +.116 [+.051, +.175]; prior +.032 [-.007, +.081] |
| `dry_run.py --out <scratch>` (replay) | ta .715, tacx .706, cvqcx .638, ta_direct .766 (as reported). Replay ta geo_value vs Claude-track CC: within 1% on 155 of 156 finite rows, 3 rows missing in both, 1 row 3% off. This matches the claim "157/159". |
| `pytest research/trackb_next/test_ctx.py` | 25 passed |
| `pytest tests/ research/trackb_next/test_ctx.py` | **682 passed** (185 s) |
| `evaluate_ctx.py --root <replay>` | runs; ref cvq_geo macro .5584, size/dist .4900 (n 100) |
| `evaluate_ctx.py --root <replay val + fake test> --lovo` | runs; old-4 LOVO reproduces **.5793** (= research/trackb_v5/l5_lovo.log) |
| Expected-gain upper bound | the gains by size/distance rows recompute to +.107 on all 3289 test rows. The agent's +.103 is on scored rows. The arithmetic is consistent. |

## 2. Pre-registration and rules
- The kill test is fixed in RESULT.md, and the run has produced no outputs, so no threshold could have been fit to
  them. The diagnosis used validation labels plus Claude Track A tracks only as a yardstick. Nothing from it enters a
  Track B answer, file or parameter.
- No leakage: `qp/open/{ctx_annot,run_ctx,ctx_merge}.py` and notebook section 13d read only open-model outputs.
  `run_ctx` drops the `answer` column before building prompts, and the Claude records (`runs/val_hr_v1_high`) are not
  referenced. The Claude annotation appears only in `diagnose.py` / `diag_*.py` and in the `dry_run.py` mock, whose
  outputs go to scratch. No test labels. Cost $0.
- No candidate file exists (`submissions/trackB_cand_ctx.csv` is absent), which is correct for INCONCLUSIVE.

## 3. Issues (fix 1-3 BEFORE evaluating the run; tightening a bar before data exists is legitimate)
1. **Criterion 4 cannot fail.** `evaluate_ctx.lovo()` compares v3's old-4 search (.5793) against a pool of
   **old-4 + cvq_geo** + new methods. With **no new method at all** (`lovo(root, [])`) it prints
   `v3's search (old 4) 0.5793; with cvq + new methods 0.5974; criterion 4 MET`. cvq_geo alone clears the +.010 bar
   by +.018. As written, criterion 4 does not test what the new methods add to the median ensemble, so the
   decision reduces to criteria 1-3 (false-PASS risk).
   Fix: the baseline should be the same search on the pool without the new methods (old 4 + cvq_geo, k <= 4:
   **.5974**), so the bar becomes >= **.6074**.
2. **Criterion 3 passes when there is no data.** If `test/<method>` is missing, or no fact row changes,
   `fact_changed = 0` and the criterion prints "Y". The criterion should require test coverage (for example >= 90% of
   the 136 fact rows answered).
3. **Fallback can change silently.** If `outputs/trackb_v1/{val,test}/caw/caw.csv` is missing on Drive, ctx_merge
   falls back to `ta/direct.csv` and `cvqcx` is skipped. The method is then no longer the pre-declared
   "CaW fallback" one. Check the `ctx_merge ... fallback <path>` line in colab.log before scoring.
4. Resolution confound (small, not one-directional). In criterion 4 the old members' validation values come from the
   480p validation run, while the new methods use val_hires. The new methods' validation CaW fallback is also the
   480p CaW. On the test set everything is full resolution. `diag_hires.py` shows mixed effects on 131 q: qwen_geo
   +.034, CaW -.033, cvq_geo -.004.
5. Mild design-on-validation. The prompt's generic segment list ("a part, a gap, the extent of a path, the spacing of
   marks") mirrors the diagnosed validation failures (orbit diameter, ruler graduation, floor tiles). It contains no
   per-row content and no labels, so it is acceptable. But validation gains on those clips may be slightly
   optimistic. The facts criterion and LOVO partly guard against this.
6. Possible false negative: `cvqcx_geo` (trackb_v1 SAM 2 motion + cx targets) is the variant closest to the diagnosed
   oracle (cvq prior + better target, .671). It is not in PRIMARY, so it cannot trigger a PASS; it only enters the
   criterion-4 pool. Consider declaring it now, before the run.
7. Process: the agent added three NEW files under `qp/open/` and edited `notebooks/`. The task's hard rule says
   "do not modify qp/". No existing qp/ or scripts/ file was changed (checked with `git show --stat f4f7341`), and
   the Colab clone needs the files there, but this deviation should be visible to the user. Note also that these
   files are already in commit f4f7341 on `main` (committed from the parent session, not by this lever's run), so
   step 0 of RUN_INSTRUCTIONS.md may already be done.
8. The +.02 central estimate (30% recovery x 60% surviving the median) is a guess with no measurement behind it.
   Count nothing until the run passes the corrected kill test.
