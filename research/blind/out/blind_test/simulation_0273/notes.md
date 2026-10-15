# simulation_0273 (A2SC, 2D planar, phoenix flying left, static camera, 2560x1440, 24 fps, 72 frames)

Method
- Background built from frame 0 (left part) + frame 71 (right part); mask by colour difference; per-frame bbox/centroid (ext.py, acc.py).
- Head+body template matching (tm.py) for valid stretches.
- Wing-flap cycle is ~24 frames, so pixel acceleration measured with phase-matched second differences x(k)-2x(k+24)+x(k+48), k=0..23:
  centroid 277, bbox-centre 284, xmin 288, xmax 280, template 279-285 px/s^2 -> a = 282 px/s^2 (constant).
- Phase-matched first differences give v(t) ~ a*t px/s (starts from rest at t=0).
- Scale: prior a = 2 m/s^2 -> 2/282 = 0.00709 m/px.

Answers
- 965 body length: horizontal bbox extent 551-633 px over the flap cycle, median ~598 px -> 4.24 m -> 4.25 m. Confidence medium (AABB definition / wing pose).
- 966 v(0.5s): uniform acceleration from rest, v = 2*t; backward diff gives 2*(t-1/48)=0.958; answer 0.98. Confidence high.
- 967 v(1.0s): 2.0 (backward diff 1.958); answer 1.98. Confidence high.
