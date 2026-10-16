# Lab audit, family 0014 (captured_0014 / 0014s / 0014x): one event, one label set

Inputs: `../inputs/0014.json` (33 scored rows = 11 questions x 3 renders). Test inputs only; no labels used.
Video: 1280x720, 24 fps, 49 frames. Scene: lab table (76.0 x 60.3), white board leaning as the slope, beige ball
held at the board top by a hand until ~f9-f10 (0.38-0.42 s), rolls down f12-f18, leaves the board ~f18-f19.
Camera f = 711 px, pp (640, 360), depth = range at the clicked point.

Scripts (all in this folder): `extract.py` (frames), `crop.py`/`sheet.py` (zoom crops), `edges.py` + `plane.py` +
`tplane.py` (table edges, vanishing line -> table normal N = (0.026, 0.879, 0.476), plane offset c),
`homog.py` (table homography with 60.3 x 76 sides), `book.py`, `cookie.py`, `board.py`, `ballsize*.py`,
`track.py`/`vel.py`/`vel2.py`/`edges_ball.py` (ball track and 3D speeds).

## Table plane
Corners (s render f40, line fits, residual < 0.4 px): FL (424.2,501.3) FR (729.8,454.4) BR (658.3,308.1) BL (448,332.1).
The front edge is the 60.3 side (PnP with f 711: reprojection 1.1 px vs 13.8 px the other way round).
Plane offset c (n.X = c): table dims give c 0.86-0.89 (62.4 x 76.6 at c 0.89); stated depths of pen / book / slope_near
give c 0.89-0.92. Every plane-based number below is given over c 0.873-0.918.

## Row verdicts (current answer -> my measurement)
| question | current (o / s / x) | measured (routes) | verdict |
|---|---|---|---|
| cookie diameter | 8.37 / 8.53 / 8.61 | 33-34 px x 1.7355/711 = 8.0-8.3 (round in image, faces camera) | ok |
| ball diameter | 6.50 / 6.59 / 6.29 | half-max width 26.5-27.4 px on the board f12-f16 at range 1.73-1.76 = 6.5-6.7 (f8-9 widths 28-30 include the fingers) | ok |
| cup height | 14.11 x3 | vertical-axis fit on the table plane (rim centre y 344.5, base y 397-402): 14.1-16.0; ratio route (rim 37 px, minor 16-17 px -> view angle 62-64 deg) 14.0-14.3 | ok |
| pen length | 14.94 x3 | plane 14.3-15.0, stated-depth route 14.86, table homography 14.2 | ok |
| book length | 17.26 x3 | plane 18.3-19.7, homography 18.0-19.3 (same prop in 0023: fronto-parallel 19.6-21.2) | ok (+5..12%, below threshold) |
| book width | 10.31 / 10.93 / 11.05 | plane 9.2-9.7, homography 9.0-9.5, board-bottom ruler (24 cm) 10.1; prop answer in 0023/0024 11.28 | ok-ish, routes disagree with each other more than with the answer: no fix |
| book height | 1.46 x3 | page block 4-5 px here (~1.1-1.35), 0023 rest view ~1.6 | ok |
| slope length | 30.80 x3 | stated depths at top/bottom-mid 30.87; bottom edge on the plane + top at 1.854: 31.5-34.7 | ok |
| slope width | 24.09 / 24.0 / 25.34 | stated depths 24.2-24.4; bottom edge on plane 23.3-24.1; homography 22.5; same board in 0023 24.3 | ok |
| displacement 0-0.6 s | 16.21 / 16.60 / 16.22 | stated depths 1.818 / 1.7288 at f0 and f14-f14.4: 16.7-18.0; plane 15.2-16.2 | ok |
| velocity at 0.6 s | **83.77** / 125.60 / 125.14 | see below: physical 106-121 forward, 105-114 centred | **o row wrong** |

## Velocity at 0.6 s (the only fix)
Ball centroid track (background-difference, s and x renders agree to <0.5 px; top-edge track gives the same
increments): y = 329.6, 340.9, 354.4, 370.4, 389.4 at f12..f16 (x 546-550).
- Route 1 (board plane: bottom edge on the table plane, top-mid at stated 1.854): forward speeds f13->14, f14->15,
  f15->16 = 100 / 115 / 133 cm/s at c 0.89 (95 / 110 / 128 at c 0.905; 106 / 121 / 139 at c 0.873).
  Ranges on that plane at f14/f15 = 1.76/1.73, matching the stated t=0.6 ball depth 1.7288 (time base consistent).
- Route 2 (stated depths only: ball at range 1.7288 at the f14.4 pixel, moving parallel to the stated slope
  top->bottom line): 92 / 106 / 124 cm/s.
- Route 3 (kinematic bound): between f10 (ball still at the board top) and 0.6 s the ball covers 17.8-20.0 cm, i.e.
  97-109 cm/s on average while accelerating, so v(0.6) > ~100 cm/s.
Physical v(0.6): forward f14->f15 106-115 (routes 1 at c 0.905/0.89 and 2 agree within 4-8%), centred 105-114.
With the usual small-ball label-noise inflation (x1.1-1.3) the label is expected near 120-145.
The two sibling renders (same label) answer 125.6 / 125.1. The o row's 83.77 traces to
`research/gates/out/base.csv`: geometry 89.3 with flags `geo:default_focal; geo:prior_motion_below_noise`
(the s/x rows used the camera focal, 98.3 / 99.4), then x0.94 instead of the x1.1-1.26 the siblings got.
It sits below the kinematic lower bound and is 1.27-1.45x below the physical speed (1.49x below the sibling answer).
Proposal: 2240 -> 125.14 (= captured_0014x answer; also the labmot render-pool value). s/x rows unchanged.
Caveat: against the 1.5x motion guard this is borderline (1.49x vs the sibling consensus); the evidence that it is
the o value, not the s/x values, that is off is the physical measurement above.

## Not changed but worth knowing
- Book: the light-blue notebook is the same prop as 0023/0024 (current 20.5 x 11.28 x 1.46 there). Here the long
  side recedes; my plane/homography routes give 18-19.7 (current 17.26, -5..-12%), width 9.0-10.1 (current
  10.3-11.05). Neither meets the 15% threshold with two agreeing routes.
- Video timing: f11 -> f12 jumps ~20 px while f12->f13 is 11 px (hand push or a dropped frame at release); it does
  not affect the f13-f16 speeds used above.
