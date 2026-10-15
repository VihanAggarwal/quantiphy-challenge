# internet_0042 — top-down drone view of a suspension bridge (2160x3840, 44 frames, 30 fps)

Camera: road-surface phase correlation shows < 0.5 px/frame drift (static enough).
Both cars drive downward (front at the bottom of the frame); the white car (Volvo-like SUV) enters at the top, and the black estate/MPV leaves at the bottom.

Perspective: the camera is a few degrees off nadir. The road widens from 1310 px (y=150) to 1463 px (y=3650), and the barrier
joint spacing grows from 192 to 240 px, so s_v is proportional to s_h^2 (a clean planar tilt). Relief displacement is
also visible. The white car's apparent length shrinks from 453 to 432 px as it nears the nadir, and the black car's grows
from 445 to 485 px as it moves away. So pixel ratios depend on the frame. The answers below hedge between a naive single-scale
pixel ratio (most likely how the GT was made) and a perspective/relief-corrected estimate.

Key pixel measurements:
- White car length: 453 (frames 11-16), 448 (fr 21), 432 (fr 43). Body width 175 px; 199 px with mirrors.
- Black car length: 445 (fr 0), 468 (fr 10), 485 (fr 20). Body width about 170 px; 207 px with mirrors.
- Road (inner barrier to inner barrier): 1368 px at the middle row (1310-1463). Bridge outer edges: 1555 px at the middle row (1487-1660); the bridge/road ratio is 1.136 at every row.
- White car front bumper moves from y=147 (fr 0) to 1497 (fr 43), 1350 px in 43 frames (942 px/s). Its centre from fr 11 to 43 moves 32.5 px/frame.

Scale: 4.572/(432..456 px) = 0.0100-0.0106 m/px. The naive centre is about 0.0103.

| qid | quantity | naive range | physical (corrected) | answer | confidence |
|---|---|---|---|---|---|
| 3060 | white car width | 1.78-1.85 (body), 2.05 (mirrors) | ~1.87-2.0 | 1.86 | medium |
| 3061 | black car width | 1.73-1.80 (body), 2.1 (mirrors) | ~1.67-1.79 | 1.76 | medium |
| 3062 | black car length | 4.5-5.0 (frame dependent) | ~4.2-4.5 | 4.68 | low |
| 3063 | road width | 13.5-14.4 | ~14.6-15.7 | 14.5 | medium |
| 3064 | bridge width | 15.3-16.4 | ~16.6-17.8 | 16.5 | medium |
| 3065 | white car avg speed | 9.6-10.0 m/s | ~10.8-11.6 | 10.1 | medium |
