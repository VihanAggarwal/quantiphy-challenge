# VERIFY: gates lever (independent verifier, 2026-10-14)

Verdict of the verifier: **FAIL confirmed**. The numbers reproduce exactly, there is no leakage, and no bug or setup
problem could have hidden a gain that reaches the +.002 bar.

## What I ran (free replay only, scratch copies; the agent's files were not touched)
I copied the five scripts to a scratch dir, pointed ROOT at the repo and the output at scratch, and ran:
```
.venv/bin/python <scratch>/base_table.py      # base.csv: identical to research/gates/out/base.csv (DataFrame.equals)
.venv/bin/python <scratch>/evalsets.py        # evalsets.csv: identical (131 val + 129 facts, 6 overlap)
ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=<scratch>/ledger.jsonl \
  .venv/bin/python <scratch>/features.py      # features.csv: identical, 3289 x 30; no ledger file written (no API calls)
.venv/bin/python <scratch>/evaluate.py        # byte-identical to out/evaluate.txt
.venv/bin/python <scratch>/evaluate2.py       # byte-identical to out/evaluate2.txt
```
Key lines reproduced: G3D 29 fired / 10 eligible / 4 held-out, delta 0.0 (INCONCLUSIVE); G2D 11 / 9 / 0 (INCONCLUSIVE);
G3D_no4 71 held-out +0.0028 [-0.0053, +0.0106]; G3D-2 185 / 48 (D3 28, S3 20) / 51 held-out (4 val, 47 facts,
18 clips), +0.0059 [-0.0036, +0.0156], D3 +.0056 (36), S3 +.0067 (15), exp. overall +0.0001 -> FAIL;
G2D-2 41 / 20 / 1 held-out (-0.1); GLAB-2 4 / 0 / 0. Diagnostics: 3D non-lab 145 rows direct .792 / gm .746 /
geometry .683; 2D 80 rows geometry .866 with all tercile and bin tables as in RESULT.md.

## Checks
1. **Reproduction**: exact (see above).
2. **Pre-registration / honest application**: the thresholds in evaluate.py and evaluate2.py match the registered
   text exactly (G3D: 3 valid runs, 3d_focal_from_prior, sens >= .3, no ASSUMED_FLAGS, FOV 8-105, R_geo <= .10,
   R_dir >= .20, u_geo <= .10; G2D: gd >= .10 and u_geo >= .15 or flag; G3D-2 / G2D-2 / GLAB-2 as written). The
   kill test is applied by code as registered. I could not verify the timing independently: the repo has no git, and
   RESULT.md was last written at 22:17, after evaluate2.txt. Stage 2 was designed after the stage-1 held-out output,
   including the G3D_no4 secondary. The agent disclosed this and treated stage 2 as a weaker second look. The stage-2
   G2D threshold (u_geo .05) matches the input-only 90th percentile I measured (2D test u_geo p90 = .043). Since the
   verdict is FAIL, the post-hoc stage carries no risk.
3. **Leakage**: labels are read only in evalsets.csv and used only inside item_scores. No answer is written: no
   submission file was created and features.py uses no labels. Nothing touches Track B. Candidate eligibility
   excludes validation-overlap rows. item_scores(pred, gt) is called with the arguments in the right order.
4. **Candidate**: none built (correct for a FAIL).
5. **False-negative risk: low.**
   - The geometry used (simfov `geo_old`) is the best of the simfov geometry variants. In
     research/simfov/out/evaluate.txt, all variants lose to dmed by .155 to .207 on validation, so a weak geometry
     choice is not hiding a gain.
   - The u_geo feature uses `_local` correctly (f[4] = residual sigma, f[6] = per-unit-sigma s.e. lever).
   - Ceiling check (my own computation). Even a perfect per-row oracle cannot reach the +.002 bar:
     - 3D non-lab: on the 145 held-out rows, best-of(dmed, geometry) is +.0186 per row and best-of(dmed, gm) is
       +.0152 per row. The eligible pool is 239 scored rows still holding dmed in combo3 (D3 121, S3 118), so the
       perfect-router ceiling is about +.0016 overall (geometry) or +.0013 (gm).
     - 2D routed-geometry rows (S2 static, D2): on the 56 held-out rows, best-of(geometry, direct) is +.0107 per
       row. The eligible pool is 508 rows (D2 440, S2 68), so the ceiling is about +.0014 overall.
   - These oracles are measured on held-out rows, so treat them as order-of-magnitude bounds. They agree with the
     agent's conclusion.

## Issues (minor, do not change the verdict)
- RESULT.md and the follow-ups say "only 48 scored 3D non-lab rows still hold the raw direct median". That is wrong
  as a general statement: 48 is only the G3D-2-fired subset. There are 239 such scored rows (D3 121, S3 118). The
  stated consequence, "caps any 3D router at about +.001", is still roughly right (+.0013 to +.0016 by the held-out
  oracle above), because the per-row oracle gain is small.
- out/gated.csv, which evaluate.py writes, is not in out/ (it was probably deleted to save disk). This is harmless:
  it is regenerated on re-run.
- Pre-registration timing cannot be verified (no git, and RESULT.md was rewritten at the end).
