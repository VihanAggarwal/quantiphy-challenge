# VERIFY: splinefit (global penalised-spline derivative estimator, 2D geometry)

Verifier verdict: **FAIL confirmed**. The numbers reproduce exactly, the kill test was applied as written, and I found no
leakage. A false negative cannot be ruled out entirely, but it is bounded at about +.002 overall, with no label-free sign of one.

## 1. Reproduction (free replays only; no API calls)
I copied spline.py, replay.py and evaluate.py into a scratch directory. The only edit was ROOT, set to the repo path, so the
agent's out/ was not overwritten. Then I ran:
```
ENV: ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=<scratch>/ledger.jsonl   (ledger stayed empty)
replay.py --split val_hires --run val_hr_v1_high   -> replaced 17, fallback 0, glock 1 (9 s)
replay.py --split test --run test_v1_high_854      -> replaced 475, fallback 23, glock 54 (2 min)
replay.py --split val_hires --run val_hr_v2_high ; --split val --run val_opus_{high,med,xhigh}
evaluate.py --secondary <the four secondary tables>
```
- The replay tables match the agent's out/*.csv on parsed_value, geo_value, direct_value, method and flags, on every one
  of 345 validation rows and 8710 test rows.
- My evaluate.py log is byte-identical to out/eval_primary.txt, and eval_rows.csv is identical (52 rows).
- combo3 holds the routed base value on 742 of 1163 D2 rows and 310 of 579 S2 rows, as claimed.
- Expected-gain arithmetic checks out. h025: 71 x .040 / 2212 + 55 x 0 / 4548 = +.00128. gcv: 52 x (-.0889) / 2212 +
  55 x (-.025) / 4548 = -.00239.

## 2. Kill test and how it was applied
- The thresholds (mean >= +.010, clip-CI lower bound > 0, no category loss, expected overall >= +.002, no negative source)
  match the template other levers used (aabb, gates, depthpro). They do not look chosen after seeing labels.
- I cannot prove from file times that the test was written first: RESULT.md was rewritten at 21:31, after evaluation.
  The replay outputs contain no labels, and evaluate.py, the only code that reads labels, was written at 21:29, after the replays.
- The change of h-grid from 0.15/0.40 to 0.10/0.25 is disclosed and was label-free. I checked the 21% figure: the transfer
  1/(1 + (0.8)^6) gives a 21% speed shrink at 2 rad/s with h = 0.40.
- The verdicts are applied correctly. h025 fails (b), with CI [-.0125, +.050], and (d), at +.0013. gcv, h010 and gcv_glock
  fail every criterion.

## 3. Leakage and rules
- Labels are read only inside evaluate.py, for scoring. There is no per-row selection and no candidate file
  (none exists in submissions/).
- No file in qp/ or scripts/ is newer than the Gemini blueprint (21:14). No keys appear in research/splinefit/.
  There was no paid spend, and Track B was not involved.

## 4. Checks for a false negative
- **The implementation is correct.** The B-spline pieces and derivatives check out by hand. The penalty
  sum (D3 c)^2 / D^5 equals the integral of f'''^2 exactly. On a noiseless projectile every mode returns the exact v and a,
  including at the track end. The monkeypatch reaches the scored code path: _measure looks up _motion at call time, and
  build_results imports `solve` inside the function, so the gravity-lock context is live (54 locks on test).
- **Power is low, but the possible gain is bounded.** There are only 13-14 affected held-out rows from 8 clips. 7 of h025's
  10 validation rows come from simulation_0171, whose labels are inconsistent. At h025's CI upper bound (+.05 per row) the
  expected gain is 71 x .05 / 2212 + 55 x .05 / 4548 = **+.0022 at most**. That is roughly the bar, and far from the +.04 the
  0.86 goal needs.
- **A label-free direction check on the test rows h025 changes shows no sign of a hidden gain.** h025's geometry moves
  toward Claude's independent direct answer in only 44% of S2 rows (n = 71) and 40% of D2 rows (n = 55). For gcv and h010 the
  S2 share is 62%. This is a weak proxy.
- **The scope is narrower than Gemini's proposal, and the narrowing is justified.** Gemini proposed a 3D world-coordinate
  spline with Depth Pro and a D3-lab gravity lock. The agent tested only 2D:
  - 3D non-lab answers and lab motion answers are routed to direct answers.
  - Lab static answers see the prior only through the f MAP. CAM_SIG_LOG_F = .05 against PRIOR_SIG_LOG = .20 gives a prior
    weight of 25 / 425, about 6%, which I checked in qp/geometry.py.
  - Gravity priors (untimed acceleration) are already fitted with one parabola over the free-flight span, which in effect is
    a locked constant acceleration.
- **One minor reporting inaccuracy.** RESULT.md presents more-than-20% moves as a GCV risk. h025 has as many: 9 S2 and 6 D2
  combo3 rows move by more than 20% (S2 down to x0.40 of the old value, D2 down to x0.23). This weakens the "h025 is the only
  defensible variant" remark further and supports not uploading it.
- **Not run.** The pre-registered secondary D2-vs-S2 cross-prior check was skipped. Given the bound above, it could not
  change the verdict.
