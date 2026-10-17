# 0037 motion re-measure (independent second measurer, r2motion)

I did not read research/next/labaudit*/0037/ notes. The shared file `0037/remeasure.md` already existed, so I wrote
these notes here instead of overwriting it. I accidentally wrote 12 frame PNGs into `0037/m2/` (another
measurer's folder) and deleted them right away. I did not open any of that folder's files.

## Scene
Ping-pong ball (prior: 4 cm) thrown from the person's hand near the cup. It bounces left along the far part of
the table and comes toward the camera. Apex frames: video 15, 24, 32-33, 39-40, 47. It touches the table about
4 times. The touch near video 19-20 is hidden behind the card tower. The one near video 36 (capture 37) falls in
the dropped frame, and the ball is behind or through the glass jar there.
Renders s and x are the same footage composited, and their ball tracks agree to within 1 px.

## Clock
The video has 49 frames at 24 fps. A uniform 25 to 24 retime gives cap(n) = round(25n/24), so the capture
frames dropped are 12 and 37.
- Check 1: the ball x-step from video 35 to 36 is 38 px, against about 14 px for its neighbours. That is a
  double step.
- Check 2: the person's optical flow from video 11 to 12 is 0.81, against 0.24 and 0.41 for its neighbours.
  That is also a double step.
So t=1.0 s is capture 25 = video 24, and its forward step is video 25. t=1.4 s is capture 35 = video 34, and
its forward step is video 35.

## Method
- track.py: blob track (difference from the median background, white mask). alpha.py: alpha-weighted
  centroids in a, s and x. The three agree to within about 1-2 px except at frame 35, where the ball is
  over the jar lid.
- bounces.py: fits a pixel parabola to each arc. Pixel g-acceleration in px/frame²: B 10.5, C 10.4, D 12.9,
  E 13.1. Bounce captures: 29.21, 37.75, 45.47.
- globalfit.py: global 3D piecewise-ballistic fit with g = 9.81, f = 711 and bounces on a common plane.
  It fits the camera pitch and roll, the bounce times and the per-arc horizontal velocity.
  - Option `card`: the table height comes from the credit card's ToF (0.679 m at px (561,540)).
  - Option `tof`: anchors the ball's surface range to 1.055 m at capture 25.
- Unanchored check: the gravity-scaled fit alone gives a ball surface range of 1.051-1.060 m at capture 25.
  The given ToF value is 1.055 m, so f = 711 and the clock mapping hold.
- Second depth route: apparent size (blur-perpendicular width and alpha area). It gives a range ratio of
  0.87-0.90 between capture 33.5 and capture 25, against 0.90-0.91 in the model.

## Results (renders share labels, so the same value goes to a, s and x)
| qid | clip | t | label-style | physical | notes |
|---|---|---|---|---|---|
| 2685, 2691, 2697 | a, s, x | 1.0 s | **63 cm/s** | ~64-65 | Lateral step 14.5 px at 1.055 m = 2.15 cm/frame. Radial step -1.2 to -1.45 cm/frame (model and size routes). Per-arc fits give 61.7-65.3; the shared-velocity fit (worse rms, 1.25 px) gives 55.6-57.5. |
| 2686, 2692, 2698 | a, s, x | 1.4 s | **95 cm/s** | ~100-101 | Vertical speed at capture 35.5 = g·2.1 frames = 0.83 m/s, from bounce timing alone, which is robust. Horizontal speed is 0.52-0.63 m/s. Label-style depends on where the frame-35 click falls on the blurred streak over the jar lid: 81 at the bright centroid (485,395), 94 at (484,399), 102 at the model position (480.7,399.9), 107 at the streak-extent midpoint (482.4,403.5). |

Caveat: one frame of ToF noise of about 1 cm in the radial step would push the label-style speed up by
about 3-5 cm/s.
