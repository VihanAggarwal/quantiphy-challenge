# simulation_0093 (S2MX, 24 fps, 38 frames, 1920x1080)
Scene: A320 (Air China) moving left at a constant ~40.41 px/frame, Cybertruck moving right at a constant ~20.09 px/frame. Plain grey background, static camera. Frames 0 and 1 are identical.
Method: median background, then abs-diff masks, then subpixel edges by coverage sums (seg.py, cov.py, plane.py, tail.py).
- Car silhouette length: 90.97 px at frame 0 (fully left of centre). Width grows with offset at slope 0.0139, and the left/right edge speed ratio (19.95 vs 20.23) independently gives W/Z = 0.0139, so this is perspective.
  Perspective-free car length fL/Z is 89.2-90.3 px. Used 90.3, a hedge toward 91.1, the value that would make the speeds round (30/60 m/s).
- Plane nose-to-tail-cone length: 606.8 px. The nose and tail cone lie on the centreline, so there is no end-face effect. The near horizontal-stabiliser tip pokes past the tail when the plane is right of centre, so the tail cone was measured separately.
- Plane height: 180.5 px from fin top to near-engine bottom, minus 0.6 px of perspective, giving 179.9 px.
- Car height: 30.11 px raw, about 28.95 px after the near-tyre and far-roof perspective correction. Near and far engines sit at the same image height, so the camera is roughly level and the horizon is about y=540.
- Depth ambiguity: with the same depth assumed, the plane comes out at 38.1-38.6 m. A real A320 is 37.57 m, which would also give exactly 60 m/s. Used 38.0 m as a hedge, so the plane scale is 38.0/606.8 m/px.
Answers: car height 1.82 m (med), plane length 38.0 m (med-high), plane height 11.27 m (med), plane speed 60.7 m/s (med-high), car speed 30.2 m/s (high).
