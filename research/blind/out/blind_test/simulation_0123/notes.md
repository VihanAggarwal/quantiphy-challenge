# simulation_0123 — bathroom vanity, top-down view, blue cup rolls left->right

## Scale
- Rolling cup tracked by cyan threshold over all 72 frames (frames 0/1 identical). x(t) linear: 14.537 px/frame
  (residual ~0.2 px), y constant 587.0 -> 348.885 px/s. Prior 0.338 m/s -> s = 9.688e-4 m/px.
- Camera is near-orthographic: the drains of the two identical sinks are offset +54.4/+51.0 px from the sink centres
  (perspective factor rim->drain k = 0.9967), faucet handles project exactly over the sink centres, and the
  holder cup's base ring is offset only ~1.4 px from its rim. Height differences of a few cm are negligible (<1%).

## Measurements (half-max edges on Y / saturation profiles; line fits for the towel)
- 265 rolling-cup length (along the axis, image y): 77.6 px (sat 77.7, Y 77.5, constant over frames) -> 0.0752 m
- 266 rolling-cup diameter: slight taper 42.3 -> 45.3 px (Y) / 41.7 -> 44.2 (sat); max (rim) about 45.0 px -> 0.0436 m
- 267 green toothbrush: axis at 44.6 deg, head tip t=-67 to handle end t=+45.4 -> 112.4 px -> 0.1089 m
- 268 holder cup rim diameter: circle fit 44.7 px (pixel-centre contour, so +1), plus half-max profiles 45.7/46.3/46.2 -> 45.8 px -> 0.0444 m
  (about the same as the rolling cup's rim, so probably the same model)
- 269/270 largest (bottom) towel: line fit to the outer edges, rotated -25.3 deg. Short-edge separation 372.3 px.
  Long-edge separation 184.1 px; the upper edge has a dark shading band, so it could be ~2 px more.
  -> L 0.361 m (answered 0.363), W 0.179 m

## Caveats and confidence
- If the ground truth were the world axis-aligned box of the rotated objects (not their own dimensions), the towel would be
  0.402 x 0.315 m and the toothbrush about 0.085 m. I chose the object's own dimensions; the length answer is nudged slightly upward.
- Confidence: 265 high, 266 medium-high, 267 high, 268 medium-high, 269 medium-high, 270 medium (AABB convention risk).
