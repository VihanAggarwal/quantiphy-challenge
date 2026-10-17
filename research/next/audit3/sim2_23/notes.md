# Audit sim2_23 (Track A, 2D Blender sims): notes

Inputs: research/next/audit3/inputs/sim2_23.json. There are 44 rows and all of them are scored.
Families:
- 0145 + 0145_segmented (rocket)
- 0223 (xiangqi)
- 0135 + 0136 (kitchen cup)
- 0294 + 0295 + 0296 (butterfly)
- 0204 (falling magnifying glass)
- 0112 + 0112_segmented (car on bridge)

Scripts are in `scripts/` (OpenCV frame reads only; no frame stacks were saved). The small track tables are in `*.txt`.

## Family structure findings
- **Butterfly:** 0294 and 0295 are the same footage with a different background. Their per-frame bg-diff bboxes are identical (bg_0294.txt vs bg_0295.txt), so 1026 and 1028 should be equal, and so should 1027 and 1029. 0296 is a top-down camera of the same flight (flap period of about 21 frames in all three clips).
  - The wing span is consistent across views. 0296 open span is 255-265 px × 8.57e-4 = 0.22 m. In 0294, the raised-wing height above the body is about 264 px × 4.29e-4 = 0.113 m, which is about half the span. So the speed-derived scales of the two cameras agree.
- **Kitchen:** 0135 (level front view) and 0136 (top-down) show the same roll take. The cup moves fast, decelerates, then rolls at constant speed after about frame 30 in both clips.
  - Fitting the 0135 centroid against the 0136 centroid gives a slope of 1.10-1.12 px/px, which matches the prior scale ratio 133/118.5 = 1.122. The best fit needs a time offset of about 0.5-1 frame between the clips.
  - That offset plus smoothing explains the 0.54 vs 0.585 split at 1 s (8%). This is below threshold, so there is no fix.
- **Rocket and car:** the segmented twins share all answers with their originals. The segmented frames were used for the quick checks.

## Row table (quick check = one fast independent route on the frames)
| qid | clip | quantity | current | quick check | diff | verdict |
|---|---|---|---|---|---|---|
| 227 | 0112 | bridge thickness | 0.71 | 76.5 px; 0.796 at car-centreline scale, 0.705 with the agent's reflection depth ratio 0.885 | in range | keep (depth ratio not independently verifiable; range 0.69-0.80) |
| 228/1813 | 0112(+seg) | car height | 1.325 | roof 412-413 to contact 538 = 125.5-127.6 px × 0.010408 = 1.31-1.33 | <2% | keep |
| 229/1814 | 0112(+seg) | wheel dia | 0.653 | tyre 67-70 px × 0.00981 (near-side scale) = 0.66-0.69 | ≤6% | keep |
| 230/1815 | 0112(+seg) | car length | 4.31 | silhouette 421 px / silhouette speed 27.18 px/f × 0.2775 m/f = 4.30 | <1% | keep |
| 324 | 0135 | toaster length | 0.296 | 0136 top-down 434 px at cup scale = 0.319, which becomes ~0.30 after the toaster-top height correction (camera ~1.6-2 m above counter) | ~2-8% | keep |
| 325 | 0135 | outlet height | 0.0569 | 73 px × hc/(891.75-540) = 7.83e-4, giving 0.057 | <1% | keep |
| 326 | 0135 | cup v @1 s | 0.5395 | 0136 route 0.585; frame offset of ~0.5-1 f between clips | 8% | keep |
| 327 | 0135 | cup v @2.25 s | 0.4255 | constant phase: 0136 gives 25.0 px/f × 7.342e-4 × 24 = 0.44 | 3% | keep |
| 328 | 0136 | toaster length | 0.319 | 0135 route 0.296 | 7.5% | keep |
| 329 | 0136 | cup v @1 s | 0.585 | own centroid backward difference 33.3 px/f = 0.587; 0135 route 0.54 | ≤8% | keep |
| 330 | 0136 | cup v @2.25 s | 0.437 | 24.8-25.2 px/f = 0.437-0.444 | <2% | keep |
| 339/1849 | 0145(+seg) | tire dia | 1.196 | 100 px × 2.9/(226..236) × 0.978 = 1.20-1.255 | ≤5% | keep |
| 340/1850 | 0145(+seg) | avg speed | 11.97 | smoothstep model from own track: 1131 px / 28 f gives 11.9; constant-accel model gives 11.0 | ≤8% | keep |
| 341/1851 | 0145(+seg) | v @1 s | 18.85 | tail quadratic fit, frames 13-25: 62.8 px/f gives 18.5 (L=236 px) / 19.3 (L=226 px) | ≤3% | keep |
| 342/1852 | 0145(+seg) | a @1 s | 13.45 | tail quadratic 1.95 px/f² gives 13.8-14.4; cubic fits 1.1-1.8 px/f² (model dependent) | ≤7% | keep |
| 539 | 0204 | table length | 2.29 | table top width at the glass contact row 1018: 1526 + 3.72·71 = 1790 px × 1.312e-3 = 2.35 | 2.5% | keep |
| 540 | 0204 | typewriter length | 0.412 | 313 px × 1.28-1.31e-3 = 0.40-0.41 | ≤3% | keep |
| 541 | 0204 | typewriter height | 0.224 | 169 px × 1.29-1.31e-3 = 0.218-0.222 | ≤3% | keep |
| 542 | 0204 | letter length | 0.259 | 198 px; at row 995 the depth scale is 1.378e-3, giving 0.273 | 5% | keep |
| 543-545 | 0204 | glass v @0.125/0.25/0.333 | 1.044/2.264/3.084 | own centroid track: 2nd difference 13.0 px/f²; backward differences 33.0/71.2/96.9 px/f give 1.036/2.235/3.04 | ≤1.5% | keep |
| 681/682 | 0223 | board L/W | 1.173/1.069 | orange rim x 448-1486 = 1037 px, y 72.5-1018.5 = 946 px, at 0.097/86 m/px (general bbox 86-87 px): 1.17/1.07 | <1% | keep |
| 683/685/687 | 0223 | v @0.5/1/1.5 s | 0.335/0.689/1.033 | own track (duplicate frames 9/11/18/20/28/34 belong to the later index, verified by quadratic prediction); cubic fit gives 12.31/25.39/37.91 px/f = 0.334/0.689/1.029 | <1% | keep |
| 684/686/688 | 0223 | a @0.5/1/1.5 s | 0.715/0.70/0.685 | quadratic 1.076 px/f² = 0.70; cubic 0.727/0.696/0.665 | ≤3% | keep |
| **1026** | 0294 | wing length | **0.20** | raised-wing extent 388-395 px × 0.32/(31.07×24) = 0.166-0.170 | **+18-20%** | **FIX → 0.167** |
| 1027 | 0294 | displacement 0.5-1 s | 0.157 | 12 f × 31.07 px × 4.29e-4 = 0.160 | 2% | keep |
| 1028 | 0295 | wing length | 0.182 | same footage as 0294, so 0.167 | +9% | keep (below the 15% rule; see note) |
| 1029 | 0295 | displacement | 0.16 | 0.160 | 0% | keep |
| 1030 | 0296 | wing span | 0.224 | 255-265 px × 8.57e-4 = 0.219-0.227 | ≤2% | keep |
| 1031 | 0296 | wing length | 0.166 | open-wing body-axis extent 190-197 px × 8.57e-4 = 0.163-0.169 | <2% | keep |
| 1032 | 0296 | displacement | 0.16 | 12 × 15.55 px × 8.57e-4 = 0.160 | 0% | keep |

## Fix
### qid 1026 (simulation_0294, wing length): 0.20 → 0.167
**Route 1 (own clip):**
- The pixel speed comes from same-phase centroid displacement of the bg-diff mask. Lags 20, 21, 22 and 42 give 31.07 ± 0.2 px/frame. The 0294/0295 agents found 30.6-31.3.
- That gives a scale of 4.29e-4 m/px at the body depth.
- The wings rotate about the body axis, so their front-back extent is invariant. It is measured cleanly when both wings are fully raised into the body's vertical plane (frames 9, 29-32 and 51, at three image positions): 388-395 px.
- Result: 0.166-0.170 m.

**Route 2 (sibling camera 0296, top-down):**
- The scale comes from the same speed prior: 15.4-15.7 px/frame, or 8.49-8.66e-4 m/px.
- The open-wing extent along the body axis is 190-197 px (full-res bg-diff, plus a visual check of the frame-40 crop).
- Result: 0.160-0.171 m, centre 0.166.

**Why the current value is wrong:**
- The 0294 agent took about 470 px from "flat wings 420-513 px".
- When the wings are flat, the near and far wing are about ±0.11 m off the body plane. The near wing is magnified, and near/far parallax grows toward the image edges. Measured flat-wing widths: 423-433 px near the centre (frames 19-21 and 40-42) and 516-524 px at x≈370 (frames 61-63).
- So the flat-wing horizontal extent overstates the wing length by 9-35%.
- The raised-wing extent is consistent everywhere (388-411 px) and agrees with the independent top-down clip.

## Notes (no change proposed)
- **1028 (0295, 0.182)** is the identical footage of 0294. Family consistency points to 0.167, but the 9% difference is below the 15% rule. The agent used a flat-wing frame-41 width (422 px), which carries the same near-wing magnification bias.
- **0135/0136 cup speed at 1 s** (0.54 vs 0.585): the clips are the same take, but there is a ~0.5-1 frame timing offset between them, and the speed changes ~5%/frame at t=1 s. Both values are within 8% of each other, so I made no change.
- **0136 agent's toaster remark:** it said "toaster further back → underestimated". For a top-down camera the toaster top is closer to the camera than the cup axis, so 0.319 is, if anything, slightly high. The 0135 value of 0.296 is consistent after correction. No change.
- **227 bridge thickness** relies on the agent's water-reflection depth ratio (0.885). I could not verify it independently; the plausible range is 0.69-0.80.
