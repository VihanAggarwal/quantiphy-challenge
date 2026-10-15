# simulation_0083 — notes

Scene: a fixed camera looks straight down at a uniform grey ground. There are two identical pickup-like cars, one yellow and one black-and-white.
The yellow car drives left at y~416. The black-and-white car drives right, centred at y~540, which is the image centre row.
Video: 1920x1080, 72 frames at 24 fps. Frames 0 and 1 are identical. From frame 1 onward both cars move at a constant velocity, about 10.06 px/frame (yellow) and 14.07 px/frame (black-and-white).
I took t = frame_index / fps, so 1.0 s is frame 24 and 2.0 s is frame 48.

## Method
- Segmentation: luma/saturation thresholds, then closing and hole filling to get per-frame silhouettes (masks.json). For sub-pixel edges I used 50 % crossings (R-B chroma for the yellow car, luma for the black-and-white car). I fitted a linear motion over frames 14-71.
- Perspective: the camera points straight down, and parallax is visible. The rear face of each car shows when the car is off-centre, and the projected length grows from 269 to 275 px as the car moves outward.
  Velocities of the tracked features give relative heights (z/H):
  - wheels: 9.96 px/frame
  - rear-bottom edge: 9.99
  - front-top edge: 10.06
  - mirrors: 10.10
  - deck: 10.16

  This gives H roughly 45 m and an HFOV of about 50 degrees.
- Projected length at the front-top height = 268.4 px. I measured it in the frame where each car's rear crosses the image centre, which removes the rear-height dependence: yellow 268.6, black-and-white 268.2.
  The scale at that height is Sa = 47.34 px/m from the prior of 5.67 m. Speeds and X positions computed from the front-top edge do not depend on the absolute heights.
- The black-and-white car is the same model as the yellow car. At mirrored offsets from the image centre, their projected lengths agree to within 0.1 px (270.26/270.15 and 275.11/274.98). Their mirror-to-mirror widths are both 116 px, and their parallax ratios match. So its length is 5.67 m.
- Width: the mirror-to-mirror span is 116.09 px, measured on the black-and-white car (dark mirrors, luma edges). Mirrors sit about 0.43 % of H higher than the front-top edge, so Sm = 47.55 px/m and W = 2.44 m. This assumes the bounding box includes the mirrors. Body-only width would be about 2.05-2.1 m.
- Distance: origin taken as the box centre. dX = (xFront_bw - xFront_y)/Sa - L. dY = 123.85 px / Sm = 2.605 m.
  - At frame 24: dX = 10.01 m, D = 10.35 m. If 1.0 s were frame 23 instead, D = 9.86.
  - At frame 48: dX = 22.25 m, D = 22.40 m. If 2.0 s were frame 47 instead, D = 21.89.
- Speeds come from the front-top edge velocity × 24 / Sa (constant velocity):
  - yellow: 5.10 m/s
  - black-and-white: 7.13 m/s

  Speeds from the mirror features agree with these.

## Answers and confidence
- 95 yellow width: 2.442 m. Medium confidence; it depends on whether the bounding box includes the mirrors.
- 96 black-and-white length: 5.67 m. High confidence (identical model).
- 97 black-and-white width: 2.442 m. Medium confidence (same caveat about the mirrors).
- 98 distance at 1.0 s: 10.35 m. Medium-high confidence; one frame of timing offset changes it by 5 %.
- 99 distance at 2.0 s: 22.40 m. High confidence.
- 100 yellow speed: 5.10 m/s. High confidence.
- 101 black-and-white speed: 7.13 m/s. High confidence.
