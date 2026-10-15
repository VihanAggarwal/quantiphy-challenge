# internet_0014 - top-down drone view of a football pitch, 2 players + ball (right penalty area)

## Scale
- Camera ~nadir, near-static (ECC affine drift <= 2.4 px / 0.1 deg over clip; all frames aligned to frame 0).
- Center circle fitted on white-line pixels: centre (941.4, 521.6), r = 117.0 px (ellipse axes 233.7/234.1 -> round, no tilt).
  Both penalty arcs also fit r = 117.1 / 117.0 px about the penalty spots -> confirms 117 px = 9.15 m -> 12.79 px/m.
  (Penalty box / goal area / goal width imply ~13.1-13.4 px/m if standard, but the prior defines the scale; arcs agree with circle.)
- Lens distortion negligible (goal lines straight to <0.6 px); left/right halves symmetric.

## Tracking
- Median background of aligned frames; player mask = |lum diff| strong (>28 brighter or < -42 darker, excludes grass-coloured shadows), ball excluded.
- Ball: brightest blob tracked frame by frame (kicked ~frame 172, rolls down-left, decelerating 43 -> 28 px/s, picked up ~frame 263).
- Player A (dark, starts near penalty spot at (1462.0,530.0)) chases and takes the ball; player B (orange) starts at (1406.7,520.0).
- Overlays checked visually at frames 0, 210, 240, 270.

## Answers
- 2070 initial distance: frame 0, 56.2 px -> 4.40 m (frames 0-4 mean gives 4.30). Confidence medium-high.
- 2071 player A to goal at 0 s: goal centre on goal line (1594.6, 520.5); 132.9 px -> 10.39 m (perpendicular 10.37). Confidence medium (definition of "goal").
- 2072 ball speed at 7.00 s (frame 210): linear fit 195-225 -> 1.108 px/frame -> 2.60 m/s (central diffs 2.58-2.63). Confidence high (scale-limited).
- 2073 player with ball avg velocity 8-9 s: displacement frame 240 (1430.6,630.0) -> 270 (1402.3,653.2) = 36.5 px -> 2.85 m/s (path length 2.92). Confidence medium-high.
- 2074 distance at 9.00 s: A (1402.3,653.2), B (1458.8,574.8): 96.6 px -> 7.56 m. Confidence medium-high.
