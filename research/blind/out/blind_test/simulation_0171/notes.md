# simulation_0171: astronaut bounding across a lunar surface (S2SS, 24 fps, 80 frames, 2304x1296)

## Setup
- The camera is static: the median background is clean. One astronaut, seen side-on, moves left to right on a path parallel to the image plane.
  The backpack's vertical pixel extent stays at 195-196 px over frames 0-54 and reaches about 199 px at the end, so depth is roughly constant.
  I used a 2D planar model.
- The pelvis track comes from frame-to-frame ECC (Euclidean: rotation plus translation) on the rigid backpack and helmet region
  (ecc.py). The pelvis is placed at an offset r0=(27,110) px from the backpack centre, rotated with the measured torso pitch.
  The torso pitches about 12 deg over frames 0-24; the pitch is confirmed by the angle of the backpack's rear edge.
  Variants with other regions and offsets (r0 from (20,95) to (32,122)) change the speeds by 1% or less.
- The animation is stitched from segments. The velocity jumps at frames 15, 30 and 61, so all smoothing stays inside a segment:
  0-14, 15-29, 30-60, 61-79.

## Scale
- The prior is height 2.2 m. The pixel height is ambiguous:
  - The astronaut's AABB height in the frame-0 pose is about 338 px.
  - The estimated standing or rest-pose height is about 355-365 px (353 px at frame 76 with bent knee and leaning torso; at most 368 px with a pointed foot).
- I used a hedge of H = 350 px, giving 0.006286 m/px. That is within about 3.5% of both hypotheses.

## Measurements (pelvis, px/frame)
| t (frame) | speed px/f | dS/dt px/f^2 (backward-of-backward, S'(k-1)) |
|---|---|---|
| 0.5 s (12) | 11.13 (range 11.0-11.28) | about -0.06 (smoothed -0.06 to -0.09; raw +0.03 to +0.07) |
| 1 s (24) | 35.6 (range 35.56-35.68) | about -0.10 (range -0.05 to -0.14); S'(k-0.5) is about -0.36 and S'(k) about -0.62 |
| 2 s (48) | 15.03 | about +-0.015 (near zero) |
| 3 s (72) | 9.40 (range 9.34-9.49) | about -0.04 (range 0 to -0.08) |

## Answers
- Speeds: 409 = 1.679, 411 = 5.371, 413 = 2.267, 415 = 1.418 m/s. Confidence is medium-high: the main risk is the definition of the scale (±4%).
- Accelerations (magnitudes): 410 = 0.199, 412 = 0.362, 414 = 0.054, 416 = 0.145 m/s^2. Confidence is low.
  All four asked times fall where the speed is nearly stationary, so the true values are small and depend on the difference convention.
