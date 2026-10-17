# Audit internet_08 (clips internet_0040, 0072, 0049, 0050, 0073)

Result: **no fixes proposed.** All 28 scored rows were quick-checked. No quick check differs from the current answer by >= 15% in a way that two independent routes agree on.

## Clip / family facts established
- **internet_0040 and internet_0072 are the same footage.** Frame k of 0040 equals frame k+11 of 0072: mask centroid and bbox match to about 1 px for all 28 frames. The card has the same pixel size in both: about 428 x 290 px when still, with a mask long side of 421-431 px.
  - The 0072 prior gives length = 8.56 cm for the long (horizontal) side. That gives 0.0200-0.0203 cm/px.
  - The 0040 prior says "width = 83.98 mm". If it is applied to the horizontal side (423-428 px), the scale is 0.0196-0.0199 cm/px. This is within 2% of the twin, so the family is consistent with the current answers.
  - If 83.98 mm were applied to the vertical side, every 0040 answer would rise by 1.47x. That reading contradicts the twin's stated length of 8.56 cm.
- **Container fps cannot be trusted.** The identical 0040 and 0072 frames report 24.4 and 26.8 fps. I used the dataset's 30 fps throughout, as the original agents did.
- **0049 and 0050 show the same rider.** The person height comes out at 1.67-1.69 m in 0049 (prior 3.8 m/s) and 1.677 m in 0050 (prior 2.9 m/s). These are independent priors, so the agreement supports both scales.
- **0049 camera.** Phase-correlation drift is about 30 x 55 half-res px over the clip, and I tracked in stabilized coordinates.
  - The rider accelerates in pixel terms, from about 13 to 17 half-px/frame. Their pixel height stays constant at about 222 px including the wheels, so this is real acceleration and not a change in depth.
  - The linear-fit average is 467 half-px/s (displacement/T gives 460), so 122-123 half-px/m. The agent had 466 px/s and 122.7 px/m.
  - Hough floor seams give a vanishing point at (922, 584) half-res, with intersection IQR 579-590. This confirms the agent's horizon of about 585.
  - The camera height is c = (756-584)/122 = 1.41 m (agent: 1.385 m).
- **0050.** The rider centroid moves at 473.8 px/s (displacement/T gives 477.6) after stabilization, which gives 163.4 px/m. This matches the agent. Cap top 879 to soles 1153 is 274 px, so 1.677 m. The left board is 415-671 x 525-701 px and the left pole base is at y = 1154, both matching the agent.
- **0073.** Template tracking with the belt front frame (static) used to remove camera motion gives these relative speeds:
  - red package 58.5 px/s
  - middle box 58.7 px/s
  - blue bag 58.75 px/s

  Raw speeds are about 55 px/s, and the camera drifts at -3.6 px/s. The scale is 0.3/58.6 = 0.00512 m/px (agent: 0.00517).

## Rows checked (quick-check route; deviation from current)
| qid | clip | quantity | current | quick check | route | dev |
|---|---|---|---|---|---|---|
| 3051 | 0040 | card length cm | 8.4 | 8.56 (twin 0072 stated length, same card and same px size); px ratio with 53.98 mm on the short side: 7.97 | family transfer | 2% / 5% |
| 3052 | 0040 | displacement 0-0.73 s cm | 12.6 | 635-645 px (centroid / top-left, f0 to f22) x 0.0196-0.0203 = 12.4-13.1 | mask track | <4% |
| 3053 | 0040 | speed 0-0.73 s cm/s | 17.2 | 12.4-13.1 / 0.733 = 16.9-17.9; the path is nearly straight | same | <4% |
| 3271 | 0072 | card width cm | 5.87 | 8.56 x 290/427-430 = 5.78-5.81 (ISO would be 5.40) | minAreaRect, f28-38 | 1-2% |
| 3272 | 0072 | v(0.5 s) cm/s | 32.0 | f14-f16 central difference: 49.7 (centroid) / 50.1 (scale-aware template) px/frame, so 30.0-30.3; 31.4 at the card's own depth (template scale 0.96) | 2 tracks | 2-6% |
| 3273 | 0072 | v(1.0 s) cm/s | 7.6 | 12.1-13.0 px/frame, so 7.3-7.9 | centroid / top-left | <4% |
| 3274 | 0072 | a(0.5 s) cm/s^2 | 90 | linear fit of per-frame speeds: 4 points 94-98, 6 points 72-84, 8 points 68 | 2 tracks; window-dependent | within the band |
| 3110 | 0049 | rider height m | 1.68 | 206 px / 122.9 = 1.68; twin rider in 0050: 1.677 | speed fit + cross-clip | <1% |
| 3111 | 0049 | gray table height m | 0.79 | top 677, foot 788, h = c(1-(677-584)/(788-584)) = 0.75-0.77 | ground-plane | 3-5% |
| 3112 | 0049 | gray bench height m | 0.48 | top 717, ground 790, giving 0.50-0.51 | ground-plane | 4-6% |
| 3113 | 0049 | brown table height m | 0.79 | top front 675-680, ground 781-793, giving 0.73-0.77 | ground-plane | 3-8% |
| 3114 | 0049 | brown table length m | 2.4 | 834-1184 = 350 px at (784-584)/1.41 = 142 px/m, so 2.47 | ground-plane | 3% |
| 3115 | 0049 | canopy height m | 3.5 | pillar foot 797, top rafters 260, giving 3.49-3.55 (ignoring the overhang) | ground-plane | <2% |
| 3116 | 0049 | mid brown to gray table m | 5.3 | centre to centre 774 px at 137-142 px/m, so 5.45-5.62 (edge to edge would be about 3.4) | ground-plane | 3-6% |
| 3117 | 0050 | rider height m | 1.68 | 274 / 163.4 = 1.677 | own track | <1% |
| 3118 | 0050 | right stand height m | 4.0 | naive 4.01; perspective 4.00 (agent pixels) | agent px re-derived | <1% |
| 3119 | 0050 | left stand height m | 3.94 | (1154-525) / 163.4 = 3.85 naive; 4.03 perspective | own px | 2% |
| 3120 | 0050 | bird to ground m | 4.05 | bird sits on the left board top (feet at 522, centre at 504), giving 3.85-4.17 | own px | <5% |
| 3121 | 0050 | distance between stands m | 17.6 | pole to pole (2742 px) or board to board (3005 px) at own depths: 18.2; naive 16.8-18.4 | agent model | 3-5% |
| 3122 | 0050 | left board width m | 1.57 | 256 px, giving 1.567 (naive) / 1.584 (perspective) | own px | <1% |
| 3123 | 0050 | left board height m | 1.10 | 176 px, giving 1.08-1.09 | own px | 1-2% |
| 3275 | 0073 | blue to yellow bag m | 1.04 | centre to centre 200 px x 0.00512 = 1.02 (edge gap would be 0.20) | own px | 2% |
| 3276 | 0073 | red package width m | 0.481 | 92 px, giving 0.471 | crop at 1.5x | 2% |
| 3277 | 0073 | red package height m | 0.243 | 48 px, giving 0.246 | crop | 1% |
| 3278 | 0073 | middle box width m | 0.548 | 105-106 px, giving 0.54 | crop | 1-2% |
| 3279 | 0073 | middle box height m | 0.191 | 37 px, giving 0.189 | crop | 1% |
| 3280 | 0073 | red package to blue bag m | 1.984 | centre to centre 384 px, giving 1.97 (edge gap would be 1.36) | own px | 1% |
| 3281 | 0073 | blue bag displacement 2.0-3.5 s m | 0.45 | f60 to f105: 91.3 px relative to the frame, giving 0.467; red/box 86.6 px, giving 0.443; belt speed x 1.5 s = 0.45 | 2 tracks | <4% |

## Residual risks (not fixable under the two-route rule)
- **3051-3053: meaning of the 0040 prior.**
  - If the dataset applied 83.98 mm to the short side (a typo of 53.98 used literally), all three answers would be 1.47x larger.
  - The twin's stated 8.56 cm length argues against that reading. The current answers match the twin.
- **0049: perspective-corrected or single-scale GT.**
  - The current answers are perspective-corrected, as the audit instructions ask.
  - A naive single scale at the rider's depth would make the table and bench heights about 15-20% larger (gray table 0.90, middle brown table 0.98).
- **Distance-convention rows: centre to centre or edge to edge.** This affects 3116, 3275 and 3280, and both routes measure the same pixels. Centre to centre is kept.
- **3274: acceleration depends on the fitting window** (68-98 cm/s^2). The sign is also unknown (the card is decelerating). The current 90 sits inside the band.
