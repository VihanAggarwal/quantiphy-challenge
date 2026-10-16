# Lab audit, family 0022 (captured_0022, 0022s, 0022x; one event, one label set)

Scripts (in `scripts/`): `extract.py` (frames and montages), `track2.py` (ball track by median-background difference),
`edges.py` (table edge lines and corners), `geom.py` (vanishing points, f check, plane normal), `traj.py` / `traj2.py` / `kin25.py`
(plane-based trajectory, stated-depth route, kinematics), `ballsize.py` (apparent ball size).
Images: `montage_{o,s,x}.png`, `median_*.png`, `corners_x30.png`, `crop_x_*.png`, `crop_ball_x*.png`, `frames/`.

## Scene
49 frames, 1280x720, 24 fps (2.04 s). One wooden table top (the lab table) is held slightly tilted toward the camera, with a person behind it.
A ping-pong ball sits at the far edge (u 437.6, v 380) until video frame 11. It starts rolling at frame 12, rolls straight toward the
near edge, and leaves the table at frames 45-46. The o, s and x renders have the same geometry: ball tracks agree within ~1 px.
The ball track shows one double step between video frames 35 and 36 (11.6 px against ~5.7 px, 3.5 cm against ~1.7 cm).
That is a dropped frame, consistent with a 25 fps capture resampled to 24 fps.
Mapping t to video frames by 24 fps (14.4/19.2/28.8/38.4) or by original 25 fps frames (14-15/19-20/29-30/38-39) changes nothing below.

## Geometry
- Table top corners (x render, fitted edge lines, residuals <1 px): FL (281.6,417.3), FR (600.0,361.9), NR (671.1,513.5), NL (224.7,613.9).
  The front-face thickness is excluded.
- The orthogonality of the two vanishing points gives f = 716 px (prior audits found 709-715). The plane normal is (-0.04, -0.87, -0.50).
- Scale route A: the ball-centre plane is anchored by the stated range at t = 0.6 (1.751 m), and the table is 2 cm below it.
  This gives a table top of 76.4 x 59.7 cm (f 711) or 75.9 x 59.7 (f 716). Anchoring at t = 0.8 gives the same.
  Anchoring at t = 1.2 gives 74.5 x 58.3.
- Scale route B: the earlier audits rectified the table to 76.0 x 60.3 cm. That agrees with route A within 1%, so the scale is confirmed.
- Consistency of the stated depths: the plane anchored at t = 0.6 predicts range 1.689 at t = 0.8 (stated 1.687) and 1.557-1.565 at t = 1.2
  (stated 1.526). The t = 1.2 stated depth is about 3.5 cm (2.3%) "too close", which is label (ToF/click) noise.
- The apparent ball size (18-20 px, with a halo) gives z of 1.4-1.7 m. It is too coarse for speeds (+-10%), but it is consistent with the scale.

## Rows
| qid (o/s/x) | question | current o/s/x | my measurement | verdict |
|---|---|---|---|---|
| 2393/2399/2405 | table width | 59.6 | 59.7 (A, t0.6/0.8 anchor), 58.3 (t1.2 anchor), 60.3 (B) | ok |
| 2394/2400/2406 | table length | 74.5 | 76.4 / 75.9 (A), 74.5 (t1.2 anchor), 76.0 (B) | ok |
| 2389/2395/2401 | v at 0.8 s | 50.9/50.9/52.2 | plane track: 37-42 cm/s (local fit, quad fit, forward difference, all renders); stated-depth avg 0.6-0.8: 38.4 | raw x1.25-1.35, inside the tuned noise correction, not >1.5x: leave |
| 2390/2396/2402 | v at 1.2 s | 57.3/55.0/58.4 | plane track: 39-45; stated-depth avg 0.8-1.2: 46.2 (inflated by the 1.526 depth) | ratio 1.2-1.45, leave |
| 2391/2397/2403 | a at 1.2 s | 30/30/30 | plane track (frames 16-44, quadratic): 3-9 cm/s^2 (25 fps base), 10-11 (24 fps base); stated-depth 3-point route: 26.1 | routes disagree (the label depth noise dominates): no fix |
| 2392/2398/2404 | displacement 0.6-1.6 s | 47/47/47 | plane: 40.2-41.9; start at stated 0.6 point, end on the plane anchored at 1.2: 42.8 | x1.10-1.17, leave |

Velocity profile on the plane (x render, cm per video frame): about 2 at release (frames 12-14), then 1.5-1.6 (frames 16-25),
1.65-1.8 (frames 26-35), and 1.85-1.9 (frames 40-45). The ball rolls at almost constant speed, about 38 -> 45 cm/s.

## Acceleration (not changed)
Physically, the ball barely accelerates (under 10 cm/s^2 over 1.2 s). The current 30 cm/s^2 does, however, match what the three stated label
depths imply (26 cm/s^2 from the average speeds 0.6-0.8 and 0.8-1.2). It is not a wrong object, time or axis.
How the GT acceleration is built from the noisy clicks is unknown. My two routes disagree by about 3x, so rule (a) fails.
Not proposed. If someone later learns that lab acceleration GT behaves like a smooth physical fit, ~8-10 cm/s^2 would be the candidate.

## Fixes
None. The table rows agree with the measurements within 3%. The motion rows sit within the tuned noise-correction band (x1.1-1.45), or,
for acceleration, the evidence does not reach two agreeing routes.
