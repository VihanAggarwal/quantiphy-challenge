# simulation_0254 (S2SS, 24 fps, 60 frames, 1920x1080)
Scene: side (2D) view of a ~44 deg incline; tennis ball rolls down it, enters frame at frame 18 (top edge), reaches floor ~frame 47, then rolls on floor at ~7.1 m/s.
Ball NOT visible at t=0.5 s (frame 12) -> extrapolated.
- Tracking: HSV yellow threshold, connected components (track.py -> trk.txt).
- Diameter: ~25 px (half-max of bg-diff, slow frames & floor frames 24.7-25.7 px). Scale 0.17/25 = 0.0068 m/px.
- Path length vs time on slope (frames 19-46) fits a quadratic with 1 cm residual: a = 719.5 px/s^2 = 4.89 m/s^2.
- Physics check: rolling solid sphere a = 5/7 g sin(44.2 deg) = 4.886 m/s^2 -> implied diameter 25.03 px. Scale confirmed.
- Speeds = backward-difference convention: v(t - 1/48) from the fit (v = 4.89 t + 1.65 m/s).
Answers: v(0.5)=4.00 (extrapolated, medium confidence: assumes constant accel on slope before entering frame),
v(1)=6.44, v(1.5)=8.89, v(1.75)=10.11 (high), a=4.89 at all asked times (high; ball on slope until ~1.96 s).
