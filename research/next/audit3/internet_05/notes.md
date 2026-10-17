# Audit3 internet_05 (internet_0032, internet_0065, internet_0074)

Each family has only one clip, so a cross-clip family comparison was not possible. Every scored row (25) got
an independent quick check on the frames. Every row's quick check lands within 15% of the current answer, so no
in-depth re-measure was triggered and **no fixes are proposed**.

## Step 1/2: consistency and agent notes
- internet_0032 (boat, prior: boat length 3.5 m). The camera is static: phase correlation of the left treeline, the right
  treeline and the reeds between frames 0, 105 and 209 shifts by < 0.5 px and shows no zoom. The boat's pixel length grows
  from 213 px to 250 px while its image y and height stay constant, so it is turning toward broadside at fixed depth.
  The agent hedged the scale at L = 221 px, which is a reasonable choice. Accelerations were already marked low confidence.
- internet_0065 (basketball over a gym floor, top-down; prior g = 9.8). Gravity lies along the optical axis, so g cannot
  set the in-plane scale. The agent instead used a standard size-7 ball (23.9 cm), which is reasonable. The handheld
  tilt drift (about -0.5 px/frame in x and +2.7 px/frame in y) is small next to the ball's 96 px/frame.
- internet_0074 (pickleball, top-down drone; prior: court width 6.1 m). The container runs at 23.976 fps with every 5th
  frame of the 30 fps source dropped. My own ball track confirms this: every 4th step is twice as long, for example
  frames 19 to 20 move 79 px while the other steps move about 40 px. Real time is preserved, so using container
  timestamps is correct.

## Step 3: quick checks (my independent measurement)
| qid | quantity | current | quick check | route | diff |
|---|---|---|---|---|---|
| 3013 | boat d 0-2 s | 1.30 | 1.29 (L=221) / 1.33 (L0=213) / 1.29 (per-frame scale) | my dark-hull threshold bow/stern centre track, 9-frame smoothing | <=3% |
| 3014 | boat d 2-4.5 | 1.79 | 1.76-1.78 (L=221) / 1.82-1.85 (L0) / 1.68-1.71 (per-frame) | same | <=6% |
| 3015 | boat d 4.5-7 | 1.88 | 1.89-1.90 (L=221) / 1.97 (L0) / 1.74 (per-frame) | same | <=8% |
| 3016 | v 0-2 | 0.649 | 0.643 (0.61-0.667) | d/2 | 1% |
| 3017 | v 2-4.5 | 0.715 | 0.703-0.713 | d/2.5 | 1-2% |
| 3018 | v 4.5-7 | 0.753 | 0.757 | d/2.5 | 1% |
| 3019 | a1 | 0.026 | 0.027-0.031 (const scale); per-frame scale 0.014 | dv / 2.25 s | routes disagree, no fix |
| 3020 | a2 | 0.015 | 0.018 (30 fps) / 0.022 (29.85 fps); per-frame scale 0.009 | dv / 2.5 s | routes disagree, no fix |
| 3021 | a 0-7 | 0.020 | 0.024 (const scale); per-frame 0.010; quadratic fit (agent) 0.019 | dv / 4.75 s | routes disagree, no fix |
| 3221 | v(0.2 s) | 2.67 | 2.68 | background-subtracted ball blob (camera-compensated), 96.5 px/frame x 30 x 0.239/258 | <1% |
| 3222 | v(0.3) | 2.64 | 2.68 | same | 1.5% |
| 3223 | v(0.4) | 2.60 | 2.68 | same | 3% |
| 3224 | v(0.5) | 2.57 | 2.68 | same | 4% |
| 3225-3227 | disp. over 0.1 s | 0.265/0.262/0.258 | 0.268 | v x 0.1 | 1-4% |
| 3228 | ball diameter cm | 24.0 | 24 (standard ball). 2nd route: floor lines are 50 px = 5.08 cm (2 in), so 1.016 mm/px at floor; ball 258 px is 26.2 cm at floor scale, which is consistent with a 24 cm ball rolling about 0.12 m above the floor with the camera at about 1.5 m | floor-line scale | consistent |
| 3282 | court length | 13.4 | 13.38-13.44 | white line profile: width 908-915 px, length 2000-2007 px | <1% |
| 3283 | players at 0 s | 14.2 | 14.3 | body centres, 2128 px | 1% |
| 3284 | v ball 1.0 s | 8.5 | 8.6 | own HSV track frames 22-26 (5 source frames, 0.1668 s), 1281 px/s | 1.3% |
| 3285 | ball-net 1.0 s | 3.27 | 3.34 | ball y 1801, net cord rows 1296-1312 | 2% |
| 3286 | ball-nearest player 2.0 s | 2.85 | 2.91 (torso); 2.54 (feet) | ball (994, 838) vs player (1000, ~410) | 2% (torso) |
| 3287 | v ball 3.0 s | 8.2 | 8.24 | frames 70-74, 1226 px/s | <1% |
| 3288 | net length | 6.9 | 7.0 (posts at about 260-1300 px); 6.71 by the rules | post-to-post pixel span | 1.5% |
| 3289 | players at 4.5 s | 9.4 | 9.55 (hips) - 9.75 (heads) | body points | 2-4% |

## Fixes
None. No row's quick check differs from its current answer by >= 15%, except the boat accelerations. For those the
independent routes (constant scale vs per-frame scale, 30 vs 29.85 fps frame indexing) disagree with each other by far
more than 8%, so the fix criterion cannot be met.

## Disk
Only small downscaled JPG/PNG crops are kept in img/ (about 1.6 MB). No frame stacks were written.
