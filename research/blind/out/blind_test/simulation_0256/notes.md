# simulation_0256 (S2SS, 2D, 24 fps, 41 frames)
Tennis ball enters frame 5 and rolls left to right along y~363 px, decelerating. Static camera, plain background.
- Track: HSV saturation mask centroid per frame (frames 6-39). Quadratic fit residual rms 0.18 px.
- Diameter in px: half-max saturation profiles 32.7 (vert) / 33.8 (horiz). Half-max contour eq-diam is about 31.9 (underestimates by about 1 px); min-enclosing circle 34.7. The ball looks slightly bigger near the image edges (off-axis stretch). Used D = 33.2 px, so 0.17/33.2 = 0.00512 m/px.
- Speed (backward difference of fitted track): 1423 / 1313 / 1202 px/s at t = 0.5 / 1 / 1.5 s, giving 7.29 / 6.72 / 6.15 m/s.
- Acceleration: constant deceleration of 221.6 px/s^2 (cubic fit gives 228 / 221 / 213), giving 1.13 m/s^2 at all three times.
Confidence: medium-high. The main error is the px diameter (about 3%).
