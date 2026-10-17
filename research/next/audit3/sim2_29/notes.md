# Audit sim2_29: notes

Input: research/next/audit3/inputs/sim2_29.json (51 rows, 40 scored). Scripts are in scripts/. Each one reads frames with
OpenCV inside the script and writes no frame stacks. The only image files are a few small crops and montages.

## Step 1: family consistency

- **simulation_0193 / 0194 (Jupiter and Callisto; same prior, 0.627 m/s).** My own Callisto orbit track gives R = 414.1 px
  and 61.06 px/s in both clips, so the scale is 0.01027 m/px in each. Orbital diameter is 8.50 in both clips (current
  8.5186 / 8.53). Callisto diameter is 0.1202 / 0.116 and Jupiter is 1.7459 / 1.71; these agree within 4%. Consistent.
- **simulation_0282 (prior speed 1.29 m/s, top-down) and simulation_0283 (prior length 0.75 m, side view, snowy cliff).**
  These are two separate harness families, but they show the same dragon asset. The values match each other:
  - 0283's speed answer of 1.29 was measured independently (505 px = 0.75 m, then 35-36 px/frame).
  - 0282's length of 0.75 lies inside my measured x extent of 478-521 px × 1.552e-3 = 0.74-0.81 m.
  - Consistent.
- **Other families.** All other families have a single clip in this item, so no cross-clip check is possible.

## Step 2: agent notes

I read every listed notes file. The two internet_*_segmented notes files do not exist (no agent notes), so I measured
those clips myself. Points to note:

- **0020.** Gravity cannot be used for scale: the ball motion is keyframed. The early drop is about 0.9-1.2 px/f² and
  eases out. The bounce is about 11-16 px/f², and the flight is about 0.19 px/f². The absolute scale is therefore
  unverifiable.
  - Q9: the agent's notes say they submitted 123 m/s, but the current answer is 1.002. The ball is exactly at rest in
    frames 0-1 (my own track: frames 0 and 1 are both at (751.8, 691.3), with first motion at frame 2). The GT at
    t = 0 cannot be determined. Left unchanged.
- **0106.** The current Q215 (1.7393) is not the agent's answer (1.60). It is close to the agent's scenario A
  (same-size viruses, right one closer, 1.746). Scenario B (same depth, same 3D speed) gives 1.5667.
  - My quick check: the pixel speeds at the start are equal (L 11.5 and R 11.7 px/frame over frames 1-3).
  - From one camera, A and B cannot be told apart by motion; only the "touching at t = 0" design argument favours B.
  - The current answer differs from B by 11%, which is below the 15% threshold. No fix.
- **0111, Q226 (bridge width).** This is a hedge, 6.6 m: about 6.9 m if the bridge is in the same plane as the water,
  about 5.8 m if the deck height is corrected. The deck height cannot be observed. No second route; left unchanged.
- **0298, Q1035 (truck width).** 3.37 m includes the mirrors (188 px). The body alone (156-160 px) gives 2.8-2.86 m.
  This is a question of interpretation, with no second route.

## Step 3: quick check of every scored row

| qid | clip | quantity | current | quick check (route) | diff | verdict |
|---|---|---|---|---|---|---|
| 8 | 0020 | person height | 1.78 | scale not recoverable (gravity is keyframed: early drop gives ~1.8-2.4 m, other cues 1.4-2.1 m) | n/a | keep |
| 9 | 0020 | ball v at 0.0 s | 1.002 | ball at rest in frames 0-1 (physical value ≈ 0) | n/a | keep (GT undeterminable) |
| 10 | 0020 | ball diameter | 0.30 | 33 px / person 211.5 px, depth ratio 1.06, consistent with row 8 | 0% (relative) | keep |
| 73 | 0078 | black speed 1 s | 1.0 | blob-centroid ratio 0.767 × 1.3 = 0.997 | 0% | keep |
| 74 | 0078 | distance 1 s | 5.3 | 1401 px / (14.45 px/f × 24) × 1.3 = 5.25 | 1% | keep |
| 75 | 0078 | distance 2 s | 3.03 | 825 px → 3.09 | 2% | keep |
| 208 | 0104 | phone diagonal | 0.204 | 566 px × 3.472e-4 (24.0 px/f lift) = 0.197 | 4% | keep |
| 209 | 0104 | gray cone diameter | 0.115 | top pad 317 px = 0.110 / collar 344 px = 0.119 | ≤4% | keep |
| 210 | 0104 | extension 0.5 s | 0.095 | 264 px (lift starts at frame 1) = 0.0917 | 4% | keep |
| 215 | 0106 | left v 1 s | 1.7393 | B: 1.5667; A: 1.746 | 11% / 0.4% | keep (below threshold) |
| 216 | 0106 | distance 1 s | 4.37 | same-depth geometry 4.39 | 0.5% | keep |
| 217 | 0106 | distance 2 s | 7.06 | 7.10 | 0.6% | keep |
| 224 | 0111 | boat length | 3.58 | 236-240 px × 0.01523 (5.47 px/f) = 3.60-3.66 | 1-2% | keep |
| 225 | 0111 | boat width | 1.29 | 85 px → 1.29 | 0% | keep |
| 226 | 0111 | bridge width | 6.6 | same plane 6.9; deck-corrected ~5.8 | ±5-14% | keep (hedge) |
| 231 | 0113 | ring speed | 0.131 | 0.4016 px/f × 24 / 73.5 px = 0.131 | 0% | keep |
| 232 | 0113 | pool side | 6.2 | 458 px / 73.5 = 6.23 | 0.5% | keep |
| 264 | 0122 | sword length | 0.944 | pommel accel route 0.945; tip-only accel 0.998 (perspective-biased) | 0-6% | keep |
| 308 | 0131 | balloon width | 14.87 | 356 px × 0.04198 (mean of top/bottom slopes) = 14.95 | 0.5% | keep |
| 309 | 0131 | balloon height | 19.51 | 468 px raw × 0.04198 = 19.65 | 0.7% | keep |
| 490 | 0194 | Callisto orbit diameter | 8.53 | 8.50 | 0.3% | keep |
| 491 | 0194 | Callisto diameter | 0.116 | threshold-area equivalent diameter 12.0-12.4 px = 0.123-0.127 (agent's half-max 11.3 px) | 6-9% | keep |
| 492 | 0194 | Jupiter diameter | 1.71 | 163-168 px half-max = 1.68-1.72 | ≤2% | keep |
| 647 | 0220 | parking long side | 5.79 | 1124.5 px × h/(875-550), h = 0.004012 × 417 = 1.673 → 5.81 | 0.3% | keep |
| 648 | 0220 | robot height | 1.24 | 306 px × 0.004012 = 1.23 | 1% | keep |
| 992 | 0282 | dragon length | 0.75 | 478-521 px × 1.552e-3 = 0.74-0.81; sibling prior 0.75 | ≤8% | keep |
| 993 | 0282 | wingspan | 1.58 | max vertical extent 1035 px = 1.61 (glide pose 900 px = 1.40) | 2% | keep |
| 994 | 0282 | displacement 0.5-1 s | 0.645 | 34.6 px/f × 12 × 1.552e-3 = 0.644 | 0% | keep |
| 995 | 0283 | speed 1 s | 1.29 | 34.4-36.1 px/f × 24 × 1.485e-3 = 1.23-1.29 | ≤5% | keep |
| 996 | 0283 | displacement 0.5-1 s | 0.65 | 0.63-0.65 | ≤3% | keep |
| 1033 | 0297 | displacement 0.5-1 s | 0.875 | 1.75 × 0.5 (lateral motion at constant speed, as the agent verified) | 0% | keep |
| 1034 | 0298 | truck length | 9.47 | 534 px × 0.01789 (26.05 px/f) = 9.55 | 1% | keep |
| 1035 | 0298 | truck width | 3.37 | 188 px incl. mirrors = 3.36 (body only 2.8-2.86) | 0% / 16% | keep (interpretation) |
| 1036 | 0298 | displacement 0.5-1 s | 5.59 | 26.05 × 12 × 0.01789 = 5.59 | 0% | keep |
| 2964 | i0010_seg | shooter height (cm) | 173.8 | 112-113 px × 24/(15.4-16.5 px ball) = 163-176 | ≤6% | keep |
| 2965 | i0010_seg | ball v at 2.00 s (cm/s) | 552.3 | parabola-fit 313 px/s × 1.45-1.56 cm/px (ball size) = 455-488; gravity scale 1.632 cm/px gives 511 | 12-18% (ball scale) / 8% (gravity) | keep: routes disagree by 5-12% |
| 2981 | i0025_seg | canoe length | 9.7 | 233 px × 1.75 m / (36-38 px boatman, hunched; ~40 px upright) = 10.2-11.3 | 5-14% | keep (watch) |
| 2982 | i0025_seg | average speed | 0.73 | 15.6 px/s × 0.044-0.047 = 0.68-0.74 | ≤7% | keep |
| 2983 | i0025_seg | displacement first 5 s | 3.6 | 74-78 px × 0.044-0.047 = 3.3-3.6 | ≤9% | keep |

### Rows needing an in-depth second route (quick check ≥15% off)

- **2965 (internet_0010_segmented, ball velocity at 2.00 s).**
  - Route 1, ball-size scale: the ball measures 15.4 px (coverage-weighted) to 16.5 px (blob equivalent diameter), with
    no motion elongation (w ≈ h). The parabola fit over frames 48-83 (rms 1.4/2.1 px) gives
    v(f60) = (9.56, -4.18) px/f = 313 px/s, which gives 455-488 cm/s.
  - Route 2, gravity: the vertical acceleration is 0.667 px/f², so 980 cm/s² gives 1.632 cm/px and 511 cm/s.
  - The two routes disagree by 5-12% and do not meet the 8% agreement rule. The current 552 is only 8% above route 2.
  - No fix. If anyone hedges later, a value near 490-500 sits within 5% of both routes.
- **2981 (canoe length).** This one is only 14% at most and was not flagged. Note that the current answers for the canoe
  are not internally consistent. Length 9.7 implies 0.0416 m/px (boatman about 42 px). Speed 0.73 and displacement 3.6
  imply 0.047 m/px (boatman about 37 px, which matches my measured 36-38 px). Below threshold, so I left it unchanged.

## Fixes

None. No row meets all three conditions: two independent routes within 8%, the current answer at least 15% away, and a
concrete error that can be named.
