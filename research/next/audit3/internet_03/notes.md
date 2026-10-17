# Audit internet_03: internet_0034, internet_0071, internet_0059, internet_0066

Result: all 28 scored rows checked, and **no fixes are proposed**. Every quick check is within 11% of the current
answer, and no row comes near the rule for a fix (two routes within 8% of each other, and the current answer at least
15% away from both).

The scripts are in `scripts/` (OpenCV only; the frames are read inside the scripts). The crops I looked at are in this
folder.

## Family / consistency table

| clip | prior | scale used by agent | my check of scale |
|---|---|---|---|
| internet_0034 | toilet-paper roll "size" = 100 mm | roll axial width 588 px @4K = 294 px @1080p -> 29.4 px/cm | gradient edges at f52/f58: W = 292-295 px @1080p |
| internet_0071 | toilet-paper width = 10 cm | roll width 295 px @1080p -> 29.5 px/cm | same |
| internet_0059 | g = 9.8 | parabola a = 4970 px/s^2 -> 0.1972 cm/px (single 2D scale) | 4966 px/s^2 (same); depth-aware fit gives ball D = 24.9 cm |
| internet_0066 | g = 9.8 (unusable: camera looks straight down, ball rolls on floor) | assumed basketball 24 cm / 263 px | court line 51 px = 5.08 cm (2 in) -> ball 25.8 cm at floor scale, 23.3-24.2 cm after ball-centre height correction (camera height 1.2-1.6 m) |

- **0034 and 0071 are the same file** (identical md5). Both use the same roll-width scale, so the family is consistent.
  The 0034 prior "size = 100 mm" is the axial width; the diameter is about 11.8 cm, which agrees with 0071's 11.9 cm.
- The 0034/0071 file has a 24.1 fps container (60 frames, 2.49 s), but the dataset fps is 30. Following the
  project convention (t = frame / dataset fps), all times are taken at 30 fps, as both agents did. If the labels used
  container time instead, the 0034/0071 motion answers would change by 8-30%. This cannot be resolved without labels,
  so it is noted only.
- 0059 and 0066 are separate families but both contain a basketball: 22.9 cm and 24.0 cm. Both are plausible
  (a size-7 ball is 23.9-24.3 cm).

## Rows checked (scored)

| qid | clip | question | current | quick check (route) | diff | action |
|---|---|---|---|---|---|---|
| 3026 | 0034 | displacement 0.5-1.73 s (cm) | 12.9 | 12.98 (LK feature track + similarity transform of roll centre, f15 (1357.9,659.1) -> f51.9 (976,691.6) = 383 px / 29.5) | +1% | keep |
| 3027 | 0034 | speed 0.5-1.73 s (cm/s) | 10.5 | 10.55 (383 px / 1.23 s) | 0% | keep |
| 3028 | 0034 | thumbnail width (cm) | 1.55 | 1.66-1.81 (nail outline about 106 px @4K at f52 = 1.81 cm at roll scale; the thumb is about 6 cm in front of the roll axis, so ~1.66 after depth correction) | +7..+17% | keep (the nail boundary is uncertain and the depth-corrected value is within 7%) |
| 3264 | 0071 | roll diameter (cm) | 11.9 | 11.83 / 11.92 (gradient edges: H 348-349 px vs W 292-295 px at f52/f58) | -1% | keep |
| 3265 | 0071 | holder length (cm) | 14.0 | 13.8 (arm x 760-1168 at f15) | -1% | keep |
| 3266 | 0071 | wall tile length (cm) | 27.3 | 27.3 (middle-course grouts at 499 / 1304 = 805 px). The top and bottom courses measure 775 px on the left and 815 px on the right, so the camera is slightly yawed. | 0% | keep* |
| 3267 | 0071 | wall tile height (cm) | 18.5 | 18.2 (row grouts 340/886 on the right, 343/870 on the left; about 536 px at the holder) | -2% | keep* |
| 3268 | 0071 | velocity at 0.50 s (cm/s) | 19.0 | 17.5-17.8 (roll-centre track: 17.3-17.5 px/frame at f15; the roll decelerates fast here, with frame steps 24, 20, 18, 17, 14) | -7% | keep |
| 3269 | 0071 | velocity at 1.00 s (cm/s) | 10.7 | 10.5 (10.35 px/frame at f30) | -2% | keep |
| 3270 | 0071 | average velocity 0.5-1.5 s (cm/s) | 10.7 | 10.95 (f15 -> f45 = 322.9 px) | +2% | keep |
| 3180 | 0059 | ball diameter (cm) | 22.9 | 24.9 (depth-aware g-fit in ball-diameter units, D = 0.249 m, sub-ranges 0.242-0.262); 25.4 with a constant scale x 129 px (50% edge crossing) | +9% | keep (<15%) |
| 3181 | 0059 | middle poster length (cm) | 74.9 | 79.4 (380 px x 0.209 cm/px from a wall-outlet plate) | +6% | keep |
| 3182 | 0059 | left poster height (cm) | 77.1 | 81.5 (390 px x 0.209) | +6% | keep |
| 3183 | 0059 | right poster height (cm) | 33.9 | 35.9 (172 px x 0.209) | +6% | keep |
| 3184 | 0059 | left edge of left poster to right edge of right poster (cm) | 191.9 | 203.6 (974 px x 0.209) | +6% | keep |
| 3185 | 0059 | velocity at 2.50 s (m/s) | 3.19 | 2.98 depth-aware (D 0.249) / 3.15 at constant scale | -7% / -1% | keep |
| 3186 | 0059 | velocity at 3.00 s (m/s) | 4.33 | 4.41 depth-aware / 4.33 at constant scale | +2% | keep |
| 3187 | 0059 | average velocity 2.5-3.2 s (m/s) | 3.43 | 3.42 / 3.43 | 0% | keep |
| 3188 | 0059 | displacement 2.5-3.0 s (m) | 1.49 | 1.45 / 1.49 | -3% | keep |
| 3229 | 0066 | ball diameter (cm) | 24.0 | 23.3-24.2 (court line 51 px = 5.08 cm, ball vertical extent 259-264 px, corrected for ball-centre height) | -1% | keep |
| 3230 | 0066 | velocity at 1.80 s (m/s) | 2.42 | 2.34-2.52 (colour-midpoint track 90.6 px/frame; background-difference centroid 85.5 px/frame; scale 24 cm / 259-263 px) | ±4% | keep |
| 3231 | 0066 | velocity at 1.90 s | 2.41 | 2.34-2.52 | ±4% | keep |
| 3232 | 0066 | velocity at 2.00 s | 2.39 | 2.34-2.52 | ±4% | keep |
| 3233 | 0066 | velocity at 2.10 s | 2.38 | 2.34-2.52 | ±4% | keep |
| 3234 | 0066 | velocity at 2.20 s | 2.37 | 2.34-2.52 | ±4% | keep |
| 3235 | 0066 | displacement 1.7-1.8 s (m) | 0.243 | 0.234-0.252 (3 frames x 85.5-90.6 px) | ±4% | keep |
| 3236 | 0066 | displacement 1.8-1.9 s | 0.241 | same | ±4% | keep |
| 3237 | 0066 | displacement 1.9-2.0 s | 0.240 | same | ±4% | keep |
| 3238 | 0066 | displacement 2.0-2.1 s | 0.239 | same | ±4% | keep |

\* The tiles in 0071 are on the wall, which is several cm behind the roll axis. The measured 805 x 536 px has a 1.50
ratio, so the tiles may be 30 x 20 cm. In that case the wall scale is about 26.6 px/cm and the true tile size is about
10% above the current answers. This is not confirmed by an independent reference at wall depth, and it is below the
15% threshold, so the rows are not changed.

## Method notes per clip

- **0034/0071**: The camera is static (phase correlation on the tile band shows 0 px shift).
  - Track: pyramidal LK features on the roll, with skin pixels removed by a saturation mask. A RANSAC similarity
    transform is fitted per frame pair and applied to the roll centre, because the roll is tilting at f8-f20.
  - Positions (1080p): f14 1375.8, f15 1357.9, f16 1341.2, f30 1200.0, f45 1035.5, f52 975.4.
  - The 0071 agent's v(0.5 s) of 19.0 used a texture point at f13-f17 (23, 20, 17, 13 px steps). My centre track gives
    about 17.5 cm/s. That is a 7% difference, so the row is kept.
- **0059**: The handheld camera drifts by up to 20 px. I removed this by phase correlation on the poster region.
  - The ball is segmented by background difference. Its blur-free diameter is measured perpendicular to the velocity
    at the 50% edge crossing. It shrinks from 136 px at f66 to 124 px at f90-97, so the ball recedes toward the wall
    by about 9%. This is why the single-scale acceleration falls from 5240 px/s^2 (f66-81) to 4720 px/s^2 (f81-97).
  - Depth-aware fit: Y/d(t) is fitted with a quadratic, giving a = 39.3 diameters/s^2, so D = 9.8 / 39.3 = 0.249 m.
  - The agent's ball diameter (116 px colour-mask minor axis) is about 8% small. Its velocities are within 7% of mine.
  - Wall scale: a standard US duplex outlet plate (4.5 x 2.75 in) below the posters measures 54.5 x 33.5 px, which
    gives 0.209 cm/px. The ball's scale at its farthest point is 0.203 cm/px, a lower bound for the wall.
  - Both say the posters are about 4-6% larger than the current answers, which used the ball's average scale. That is
    below the threshold, so they are kept.
- **0066**: The camera looks straight down at the gym floor. Jitter is under 5 px and was compensated.
  - The ball's vertical extent (no blur in that direction) is 257-264 px. Court lines (maroon and blue) measure
    50-52 px wide; at 2 in that gives 0.0996 cm/px at the floor.
  - The ball-size route and the court-line route agree within about 3% on diameter and speed. The g prior cannot set
    the scale here, because the ball moves only in the floor plane.

## Fixes

None.
