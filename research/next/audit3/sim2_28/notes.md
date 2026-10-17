# Audit sim2_28: notes

Inputs: research/next/audit3/inputs/sim2_28.json, which has 56 rows, 48 of them scored. Only the listed agent_notes were read.
The notes for the segmented internet clips and for simulation_0128_segmented do not exist on disk.
Scripts are in `scripts/` (OpenCV reads frames inside the scripts, and no frame stacks were saved). Every crop listed here was viewed.

## Family consistency (step 1)
- **simulation_0164 family: 0162 and 0163.** Both clips state ball diameter = 0.21 m, and the ball measures 78.5 px in 0162 and 79.2 px in 0163, so the scale is consistent.
  The two takes show different motions: 0162 accelerates toward a terminal speed, and 0163 decelerates into the pins. They share no motion values.
- **simulation_0128 and 0128_segmented.** The ball gives a = 609.3 px/s^2 in both clips, so s = 0.01608 m/px in both. Both clips answer 0.375 for the ball diameter, which is consistent.
  The SAM mask in the segmented twin drops the forks and leaves holes in the cab. This is a segmentation artefact, not the GT object, so it has no effect on q296, which is asked on the original clip.
- **internet_0015 family: 0001_seg and 0002_seg.** The camera and highway are identical: the lane-marking rows are the same within 1 px in both clips, and the lane is about 106 px.
  The current answers in both clips use the same scale (about 0.0331 m/px, so a lane of about 110 px) and the same time convention: fps 30 applied to the 24-fps SAM frames. The family is internally consistent.
- The other families are single clips.

## Agent notes skim (step 2)
- **simulation_0090.** The notes give the small bird's body length as **0.532 m**, but the current answer for q145 is **0.94**. The current value does not match the agent's own measurement.
  It would also make the "small bird" larger than the big bird (0.867 m).
- **Low-confidence or definitional rows:**
  - q143: frame convention.
  - q320: toast "length". The horizontal extent gives 0.120 m and the vertical gives 0.148 m.
  - q323: frame convention.
  - q332/q333/q334: which depth plane the bird is in.
  - q338: the ceiling is sloped. It is 2.64-2.70 m at the back wall and about 3.25-3.4 m at the man's depth. 3.3 is a hedge.
  - q279/q280: whether the deck is included.
  - q296: whether the forks are included.

  None of these has two agreeing routes that differ from the current answer by 15% or more.

## Quick check of every scored row (step 3)
| qid | clip | quantity | current | quick check (route) | verdict |
|---|---|---|---|---|---|
| 142 | 0090 | eagle speed | 17.98 | edges 156.3/95.66 px/f x 11 = 17.97 | ok |
| 143 | 0090 | bird separation at 0.3 s | 2.31 | f7: bbox-mid 478.5 px = 2.29; darkness centroid 476.6 px = 2.28 (f8 would give 2.59) | ok |
| 144 | 0090 | eagle length | 0.867 | 180-182 px x 0.004792 = 0.867 | ok |
| **145** | 0090 | small bird length | **0.94** | **R1: diff-mask bbox 110-113 px x 0.004794 = 0.53-0.54; R2: darkness column extent median 110 px, template speed 95.67 px/f, so 0.527** | **FIX to 0.532** |
| 211 | 0105 | ice cube height | 0.381 | top-edge fit a = 681.5 px/s^2, so 0.01438 m/px; 26.5-27 px gives 0.381-0.388 | ok |
| 212 | 0105 | cup+plate height | 1.434 | rows 974-1073, 100 px, gives 1.438 | ok |
| 213 | 0105 | cup+plate width | 2.675 | x 451-636, 186 px, gives 2.675 | ok |
| 214 | 0105 | cube velocity at 1 s | 9.74 | f24 backward difference 28 px gives 9.66 | ok |
| 278 | 0125 | plant height | 1.38 | 151 px x 0.00908 = 1.37 (person 5.60 px/f) | ok |
| 279 | 0125 | house height | 7.85 | 886 px gives 7.83 (front) to 8.05 (person scale) | ok |
| 280 | 0125 | house width | 6.83 | 773 px gives 6.83 (front) to 7.02 (person scale) | ok |
| 281 | 0125 | person height | 1.92 | 209-210 px gives 1.90 | ok |
| 295 | 0128 | ball diameter | 0.375 | a = 609.3 px/s^2 (both clips); 22 px (mask) to 23.8 px (coverage) gives 0.354-0.383 | ok |
| 296 | 0128 | forklift length | 6.57 | 414 px with forks gives 6.66 | ok (forks assumed part of the object) |
| 297 | 0128 | forklift height | 3.85 | 242 px gives 3.89 | ok |
| 1845 | 0128_seg | ball diameter | 0.375 | same as 295 | ok |
| 311 | 0132 | apple diameter | 0.099 | flight fit a = 6355 px/s^2, so 0.001542 m/px; 63-64 px gives 0.097-0.099 | ok |
| 312 | 0132 | table height | 0.984 | 640 px drop at constant depth gives 0.987 | ok |
| 313 | 0132 | horizontal speed | 0.664 | 431.5 px/s gives 0.665 | ok |
| 314 | 0132 | horizontal distance | 0.297 | 193.6 px gives 0.299 | ok |
| 320 | 0134 | toast length | 0.1204 | 195 px gives 0.114 (naive) to 0.120; the vertical 239 px would give 0.148 | ok (definitional ambiguity) |
| 321 | 0134 | toaster length | 0.2804 | 456-462 px gives 0.268-0.280 | ok |
| 322 | 0134 | toast peak rise | 0.1336 | template track 216.5 px gives 0.127-0.134 | ok |
| 323 | 0134 | toast acceleration at 1.75 s | 8.793 | f42: speed 24.0 vs 48.6 px/f, a difference of 24.6 px/f^2, gives 8.3-8.74 | ok |
| 331 | 0137 | flight path length | 15.1 | 9.146 x 99/60 = 15.09 (px path 19.78 px/f, constant) | ok |
| 332 | 0137 | house length | 6.1 | eave 846 px x 0.00772 = 6.53 (2D, front plane) | ok (7%) |
| 333 | 0137 | house height | 3.47 | 461 px gives 3.56 | ok |
| 334 | 0137 | bird to roof at 1 s | 3.2 | bird y 125.5, ridge 522: 396.5 px gives 3.06 | ok |
| 335 | 0142 | man height | 1.8 | stated fact, not changed (486 px x 0.003732 = 1.81, consistent) | fixed by rule |
| 336 | 0142 | distance walked | 5.6 | 18.9 px/f x 79 = 1493 px, gives 5.57 | ok |
| 337 | 0142 | tile side | 0.6 | floor-line VP fan, delta-a about 0.45 x camera height 1.347 m, gives about 0.60 | ok |
| 338 | 0142 | floor to ceiling | 3.3 | sloped ceiling: 2.64 m at the back wall, about 3.25 m at the man's depth (13.6 deg slope) | ok (hedge) |
| 377 | 0162 | v(1 s) | 1.041 | poly4-6 backward difference 16.1-16.2 px/f gives 1.034-1.041 | ok |
| 378 | 0162 | a(1 s) | 0.716 | 0.47-0.49 px/f^2 gives 0.72-0.76 | ok |
| 379 | 0162 | v(2 s) | 1.535 | 23.86-23.95 px/f gives 1.532-1.538 | ok |
| 380 | 0162 | a(2 s) | 0.33 | 0.211-0.217 px/f^2 gives 0.325-0.335 | ok |
| 2950 | inet0002_seg | red car length | 6.0 | 184-187 px x 0.0345 = 6.35-6.45 | ok (6%) |
| 2951 | inet0002_seg | red car width | 2.15 | 60-69 px gives 2.07-2.38 | ok |
| 2952 | inet0002_seg | red car speed | 29.0 | 35.5 px per unique frame; see the time-base note | ok (hedge) |
| 2961 | inet0008_seg | sailboat average speed | 4.1 | 34.0 px/s x 12/99.5 = 4.10 | ok |
| 2962 | inet0008_seg | speedboat average speed | 30.0 | 2D: 216 px/s (segmented part) gives 26.0; full crossing in the original, 244 px/s, gives 29.4 | ok |
| 2963 | inet0008_seg | speedboat length | 5.21 | 41-47 px gives 4.9-5.6 | ok |
| 2978 | inet0021_seg | airplane average speed | 65.0 | camera-corrected track with per-frame scale from its own length (69-88 px): 73 m/s | ok (11%, below threshold) |
| 2979 | inet0021_seg | plane to roof at 0 s | 72.0 | vertical gap 127 px x 40/70 = 72.6 | ok |
| 2980 | inet0021_seg | displacement 0-2 s | 128.0 | 271.5 px (camera-corrected) with per-frame scale: 144 m | ok (11%, below threshold) |

The unscored rows 381-385 (0163) and 2947-2949 (inet0001_seg) were checked only for family consistency.

## Fix
- **q145 (simulation_0090, small-bird body length): 0.94 -> 0.532.**
  - **Route 1:** the background-difference bbox horizontal extent is 110-113 px, stable over frames 3-18. The scale comes from the leading and trailing edge speed of the small bird, 95.65 px/frame: 11/(95.65 x 24) = 0.004792 m/px. This gives 0.53-0.54 m.
  - **Route 2:** the extent from a sky-darkness column threshold has a median of 110 px. The speed from template matching over 9 frames (one flap period) is 95.67 px/f, correlation 0.99. This gives 0.527 m.
  - **Why the current value is wrong:** 0.94 m would need a 196 px extent at the clip's own scale. The small bird never exceeds 113 px.
    The value contradicts the clip agent's own measurement (0.532), and it would make the "small bird" longer than the eagle (0.867 m, 181 px).

## Caveats (no change proposed)
- **Internet time base.** internet_0001 and 0002 are about 20-fps originals (20.6 and 19.6 fps, with uniform motion steps). SAM2 resampled them to 24 fps by duplicating frames.
  The rows nonetheless say fps = 30. For q2952 the red-car speed comes out at:
  - 24.2 m/s on the video clock;
  - 30.4 m/s with fps 30 applied to the SAM frames;
  - 36.6 m/s with fps 30 applied to the original frames.

  The current 29.0 sits between these and is within about 20% of every convention. Keep it.
- **internet_0008.** The speedboat is closer than the sailboat: its waterline is about 96 px below the horizon against about 77 px for the sailboat. A depth-aware scale would give about 21 m/s and 4.0 m.
  The internet labels are probably 2D human annotations, so the 2D values are kept. The sun moves about 3.8x faster than real time, so the footage is probably sped up. That does not change video-time labels.
- **internet_0021.** The plane grows from 69 to 88 px, because it is approaching on the landing path. The answer depends on the scale convention: about 82 m/s with the scale at t = 0, and about 70 m/s with no camera correction.
  The current 65/128 are 11-13% below my best route, which is under the 15% threshold.
