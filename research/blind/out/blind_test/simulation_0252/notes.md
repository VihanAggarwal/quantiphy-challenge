# simulation_0252 (S2SS, 24 fps, 41 frames = 1.71 s)
Method: ball rolls left->right at constant image row (y~385), constant depth (planar 2D).
- Track: background subtraction vs frame 0 (thr 25), blob centroid (ball+shadow, rigid) frames 6-40.
  Quadratic fit x(t) rms 0.48 px: pixel speed 1342/1228/1114/1001 px/s at 0.5/1/1.5/2 s,
  constant deceleration ~228 px/s^2. Backward-difference offset +4.7 px/s.
- Scale: ball diameter measured on contrast-enhanced 5x crops: 68-72 px (horizontal ~71, vertical ~68) -> 70 px,
  0.344/70 = 0.004914 m/px.
- Answers: 6.62, 6.06, 5.50 m/s; t=2 s is beyond video end (1.67 s) -> extrapolated with constant deceleration: 4.94.
Confidence: 851-853 medium-high (scale uncertainty ~3%); 854 medium (extrapolation).
