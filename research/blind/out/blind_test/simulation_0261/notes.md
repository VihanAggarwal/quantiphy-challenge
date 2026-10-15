# simulation_0261 (A2SS, 2D sim, 1080x1920, 24 fps, 50 frames)
Mug free-falls from rest at top (x~575 constant), lands ~frame 19, static afterwards.

## Tracking
Background = last frame (rows<1400) + first frame (rows>=1400); diff>12 mask, largest blob centroid per frame (track.py).
Quadratic fit of centroid y, frames 0-17: a = 5090 px/s^2 (rms 0.2 px; top/bottom edges give 5076/5121),
release t0 ~ -0.004 s, second differences constant (~8.85 px/frame^2) -> no perspective/tilt trend.
Scale = 9.8/5090 = 1.925 mm/px (mug falls at constant depth; body width 79 px at top and landed).

## Height (q917)
Body vertical extent at centre column = Hp + top/bottom ellipse half-axes (cylinder seen off-axis).
Frame 0: centre extent 111.5 px, ellipse half-axes ~12 + ~11.5 (from rim profile curvature) -> Hp ~87.5.
Landed frame 40: centre extent ~101, half-axes ~8.5 + 7.6 -> Hp ~85. Use 86.5 px -> 0.1665 m.
(diameter 79 px = 0.152 m, with handle 111 px = 0.214 m.) Confidence: medium (+-4%).

## Speeds (backward difference, frame = round(t*fps))
v_bd(n) = (5090*(n-0.5)/24 + 19) px/s * scale: n=5 -> 1.87, n=10 -> 3.92, n=15 -> 5.96 m/s
(raw diffs: 1.88, 3.92, 5.95). Continuous g*t alternative: 2.00, 3.96, 6.16; floor-frame alternative for 0.2/0.4: 1.47, 3.54.
Confidence: 0.625 s high; 0.4 s high-medium; 0.2 s medium (frame-convention ambiguity).
