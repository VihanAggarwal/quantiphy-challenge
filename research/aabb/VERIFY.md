# Independent verification of the aabb lever (2026-10-14)

Verdict: **FAIL confirmed** under the pre-registered kill test. All reported numbers reproduce exactly. I found no
leakage or rule violation. The false-negative risk is moderate for the narrow claim that "the block does nothing for
size rows" and low for the claim that "there is no material leaderboard gain". Details follow.

## What I re-ran (free only, no API calls)
Environment for all runs: `ANTHROPIC_API_KEY="" ANTHROPIC_BASE_URL="http://127.0.0.1:9" QP_LEDGER=<scratch>`.
- `.venv/bin/python research/aabb/run_pilot.py --score`: output is **byte-identical** to the scoring part of `run.log`
  (aabb .8269, hr_v1 .7942, delta +.0327 [-.0370, +.1062], clips better 3/6, KILL TEST: FAIL; 3-run +.0135; 4-run +.0058).
- `.venv/bin/python research/aabb/null_check.py`: byte-identical to `null_check.txt`.
- `.venv/bin/python research/aabb/step1_bias.py`: byte-identical to `step1_bias.txt`.
- I re-parsed the saved raw responses in `out/*.json` with `ca.parse_json` + `ca.to_annotations`. All 52 direct
  answers match the stored `direct` dicts. The same parse of the comparator runs' raw records (v1, v2, opus; 92
  simulation rows each) reproduces their CSV `direct_value` exactly, so the comparison is like for like.
- Request parity: the pilot's `meta` (frames, scale, image size, questions, prompt_version) is identical to the
  `val_hr_v1_high` record for the clip I checked (simulation_0300). The comparator config is frames 16 / max 32 / v1 /
  max_side 2576. The only differences are the appended CONVENTION block and sync instead of batch mode.
- Spend: the ledger has 6 `aabb_pilot` usage lines totalling $2.7099 (matching out/*.json). The global usage total
  is $152.07.

## Checks
1. **Numbers reproduce:** yes, exactly (above).
2. **Kill test:** PASS needs both (1) a delta of at least +.015 and (2) more than half of the changed clips
   improving. The result is +.0327 with 3 of 6 clips better, so FAIL is applied correctly. The bar is not looser
   than Argon's own proposal (+.025 on validation plus a stated-facts check). I cannot independently verify the
   pre-registration timing from the files: RESULT.md was last modified at 22:03, after the run (21:51), and the
   repo commit e750d03 (22:57) contains everything at once. I see no sign that the main bar was tuned after the fact.
3. **Leakage:** none. Validation labels are used only to score. Step 1(b) uses the sanctioned test "facts" (priors
   stated in other clips), not test labels. The convention text is a generic hypothesis and has no per-row values.
   No test answers were produced and no candidate CSV exists. Track B is not involved. No API keys appear in the
   files.
4. Not applicable (FAIL, no candidate).
5. **False-negative analysis.** These are my own extra computations, not pre-registered:
   - Condition 2 counted simulation_0170, a clip of pure speed and acceleration rows with no size rows, which
     contributed the largest loss (-.113). A size convention block cannot plausibly help those rows, so this
     design leans toward a false negative. On the **30 size rows only**:
     - aabb - hr_v1: +.080 [-.004, +.162], 3 of 5 clips better. This would pass both conditions.
     - aabb - mean(v1, v2, opus): +.073 [+.013, +.120], 4 of 5 clips better.
     - Without 0009: +.058 [.000, +.113], 3 of 4 clips.
     - Without 0009 and the lane row: +.035 [.000, +.071], 3 of 4 clips.
     So a modest single-run size-row edge survives the agent's exclusions. Part of it is height inflation in 0060
     (car, pedestrian), which the stated test facts suggest would not transfer, since heights there already read
     +4.7% high.
   - The **mechanism guard as pre-registered** (mean shift on all length/width rows vs all height rows) is actually
     *satisfied*: +0.171 (17 rows) vs +0.080 (11 rows) in `run.log`. The statement "the mechanism guard also fails"
     depends on a post-hoc exclusion of 0009 and the lane row. RESULT.md states that exclusion openly, and the guard
     only matters after a PASS, so the verdict does not change. It is still a wording issue.
   - **Deployment-relevant effect** (aabb as an extra ensemble member, size rows):
     - 4-run median - 3-run median: +.020 [+.005, +.042], 3 of 3 changed clips.
     - Without 0009: +.008.
     - Upper bound: if +.02 held on all 498 test 3D simulation size rows, the gain would be about S3 .0011 + D3 .0020
       = **+.003 overall**. The realistic gain is lower, because:
       - many of those rows are already exact stated facts;
       - the test runs use 854 px, not the pilot's 2576 px;
       - the height inflation would not carry over.
     - Cost: about $12.5 at test settings, against roughly $48 of budget left.
   - The pilot tested a simplified version of Argon Idea 4: a convention text block, not the structured
     yaw/L:W:H output with a solver. It also skipped Argon's stated-facts arm. Step 1 still bounds any AABB effect
     to about 5% on vehicle lengths, so neither variant has a large ceiling.

## Bottom line
FAIL stands. A real size-row prompt effect cannot be excluded at n=5 clips. Its leaderboard value is at most about
+.003 for about $12.5, below what validation can resolve, and it may be partly a general size inflation that would
not transfer to test. I agree with not building a candidate.
