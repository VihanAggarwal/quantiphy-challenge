# simulation_0120 — top-down living room, robot cleaner prior 1 m/s

## Camera / scale
- 1080x1080, 24 fps, 49 frames. The camera looks straight down. A least-squares vanishing point of about 140 radial segments (wall slats, TV ends, wall corner, curtain folds) is (539,539), so the nadir is the image centre (540,540).
- Robot track (white-blob centroid, frames 4-32): vx = 8.370 px/frame = 200.87 px/s, residual 0.17 px, no acceleration. That gives 200.87 px/m at the robot-top height (about 0.09 m).
- The perspective is strong: the TV and the walls are visibly foreshortened, and objects at greater height look larger. I estimated the focal length from:
  - the TV, assumed 16:9, on the wall: f ~ 1205 px (1130 if the 4 px top strip is a bezel and not the top face);
  - sofa face ratios (arm vs seat/base) and the console front-face ratio, which give plausible heights at H ~ 6 m;
  - the curtain top (wavy heading visible at the image bottom, ratio 1.60 against the hem): about 2.3 m at H = 6.1, which is plausible.
  Adopted values: f ~ 1207 px, camera height H ~ 6.1 m, floor scale s0 ~ 197.9 px/m. Scale at height h is s(h) = 1207/(6.1-h).

## Measurements
- Robot: diameter from half-max radial profiles is 70.0 px (13 frames x 12 angles, sd 0.3) -> 0.348 m.
- Chessboard (10x10 draughts board): grid fit to 44 black squares gives pitch 8.33 px, so side = 83.3 px; at about 0.42 m height (on the coffee table) -> 0.392 m.
- Tray: edges x 513.1-574.6 (61.5 px) and y 463.5-527.5 (64 px); used 63 px at about 0.45 m -> 0.295 m.
- Sofa: y-outline 206.5 to 832.5. The ends are arm/back tops at about 0.64 m (from the arm side-face ratios 1.09 and 1.06). Offsets from the nadir are 333.5 and 292.5 px at s(0.64) = 221 px/m -> 2.83 m. A planar reading would give 3.12 m.
- TV (wall-mounted on the left wall): the end edges are radial, with L/D_tv = 1.046, where D_tv is the horizontal distance from the nadir to the TV front plane. The wall distance comes from the console:
  - back-top edge r = 321.5, front-top r = 255.5, front-bottom (floor) r = 244.5;
  - so the wall floor projection is at r = 307.7 px, giving D_wall = 1.555 m and D_tv ~ 1.535 m (TV about 2 cm thick);
  - so L = 1.605 m. This is nearly independent of f. Implied TV height is about 0.90 m (16:9), and the console is about 0.26 m high and 0.32 m deep.

## Answers / confidence
- 257 sofa 2.83 m: medium (height assumption, ±3%)
- 258 TV 1.605 m: medium (depends on the console standing on the floor; a floating console would make it about -2%)
- 259 robot 0.348 m: high
- 260 chessboard 0.392 m: high-medium (table height assumed 0.40-0.45 m)
- 261 tray 0.295 m: medium-high
