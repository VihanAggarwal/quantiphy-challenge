# simulation_0263 (A2SS, top-down 2D view, 2560x1440, 24 fps, 72 frames)
Spacecraft seen from above, starts at rest on the right and accelerates leftward along x (constant acceleration).
Track: right (rear) edge of dark mask (g<110) per frame; quadratic fit x(t) = -259.45 t^2 - 0.69 t + 2391.8 (resid 0.36 px)
-> a = 518.9 px/s^2 (left edge 512, centroid 520). Prior a = 4 m/s^2 -> scale 0.007709 m/px.
Shadow (intensity ~110-118, offset up-left) excluded with threshold g<100 (craft body 45-82); overlay checked.
Length: 765-789 px over frames (perspective/parallax drift), use ~778 px -> 6.00 m. Width: 366 px -> 2.82 m.
Speeds (backward diff of fitted track): v(0.5) = 249.3 px/s -> 1.92 m/s; v(1.0) = 508.8 px/s -> 3.92 m/s
(consistent with v = a t from rest).
Confidence: speeds high; length/width medium-high (shadow/edge choice ~ +-3%).
