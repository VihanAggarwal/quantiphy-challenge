# internet_0058 - vertical basketball toss, slow camera tilt (~37 px over clip)
Method: HSV ball mask (hue wrap 160-180/0-9, S>110, V<150) -> per-frame centroid; camera shift by phase correlation of the upper frame (dy 0 -> -37 px), positions stabilized.
Scale: parabola fit of stabilized ball y over frames 23-63 (rms 1.5 px): a = 1998 px/s^2 -> 203.9 px/m (0.00491 m/px).
Cross-checks: ball diameter 48 px -> 0.235 m (basketball 0.24); backboard width 352 px -> 1.83 m at ~192 px/m (basket nearly at person depth).
Horizon from court-line vanishing point y~588 -> camera height 1.53 m; rim y~300 -> rim height 3.03 m (perspective), 2.95 m (planar from feet floor).
Answers:
- 3171 person height: cap top 569 to shoe bottom 901 = 332 px -> 1.63 m (medium-high)
- 3172 basket-floor: 3.0 m (high; planar 2.95, perspective 3.03, standard 3.05)
- 3173 v(1.00s): parabola 4.01, backward diff 4.15 -> 4.1 m/s (high)
- 3174 ball-floor 1.00s: ball centre y 206, floor at feet 893 -> 3.37 m (medium)
- 3175 ball-basket 1.00s: ball (1080,206) vs rim centre (881,295) = 218 px -> 1.07 m (medium)
- 3176 v(2.00s): parabola 5.79, backward diff 5.4-5.6 -> 5.7 m/s (high)
- 3177 ball-floor 2.00s: 2.48 m (medium)
- 3178 ball-floor 1.40s (near apex): 4.19 m (medium)
- 3179 avg speed 1.40-2.00s: 349.5 px in 0.6 s -> 2.86; free-fall check 2.94 -> 2.88 m/s (high)
