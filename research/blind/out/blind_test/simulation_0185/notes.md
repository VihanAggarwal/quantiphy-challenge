# simulation_0185 — gift box falls onto a ramp and slides down it (2D planar view, 1920x1080, 24 fps, 40 frames)

## Tracking
- Median background over all 40 frames, then a diff mask, then the convex hull of the white box body. Frames 0-8: vertical free fall (cx ~497 constant). Frame ~9: lands on the ramp. After that it slides along a 28.5 deg image-plane incline. The box keeps a constant 28.5 deg roll and does not rotate.
- Video frame 38 is a duplicate of 37, and frame 39 jumps two frames. This does not affect any asked time (frames <= 36).
- Free fall: per-frame displacements 1.9, 6.5, 10.2, 14.2, 17.9, 22.2, 26.0 px, so a = 3.98 px/frame^2 (quadratic-fit residual < 0.4 px). The box starts from rest at frame 0 (first step = 0.5a).
- Slide: quadratic fit of arc length over frames 10-37 gives a = 1.298 px/frame^2 (hull, rect and mask tracks agree).
- Consistency check: a_slide/a_fall = 0.326 against prior/g = 3.18/9.81 = 0.324. So the scale from the prior (0.00425 m/px) and the scale from gravity (0.00427 m/px) agree within 0.7%. The motion is in a plane parallel to the image at constant depth. Scale used: 0.00426 m/px.

## Answers
- 446, accel 0-0.3 s: free fall, so the true value is g = 9.81 in Blender units (measured 9.75). Interval or difference conventions can give 8.9-9.4 (e.g. (v(7)-0)/0.3 = 8.86, mean per-frame a with a half-step first frame = 9.11, linear fit = 9.40). Hedged answer: 9.4. Confidence medium.
- 447, v(1 s), frame 24: backward-difference speed of 746-755 px/s, giving 3.17-3.21 m/s. Answer 3.17, leaning slightly toward the frame-23 alternative (3.07). Confidence high.
- 448, v(1.5 s), frame 36: 1110-1120 px/s, giving 4.71-4.77 m/s. Answer 4.73. Check: v24 + 0.5 s x 3.18 = 4.78. Confidence high.
- Sizes. The box is a near-cube. Front face is about 90-93 px each side, so 0.38-0.39 m at centre depth after the perspective correction (side-face parallax k ~ 0.04). The cube is rolled 28.5 deg.
  - World AABB X: 120-126 px front-face extent, so 0.50-0.52 m.
  - World AABB Z: 0.515 m for the body only, 0.60-0.61 m including the bow (bow top 142-143 px above the lowest corner).
  - Local (unrotated) dims: 0.385 m, or about 0.55 m height with the bow.
- 449, length: world AABB X, answer 0.50. Confidence medium (0.39 if local dims were used).
- 450, height: hedged answer 0.585, between world AABB with bow (0.605), world body only (0.515) and local with bow (0.55). Confidence medium-low.
