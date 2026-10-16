# Lab audit: family 0032 (captured_0032, 0032s, 0032x)

All three renders come from one event, so they share one set of labels. Each is 49 frames at 24 fps, 1280x720.
Render o is the real background, s is blue-white and x is black. In x the table and balls are cleanly isolated.

The released 24 fps clips come from 25 fps capture. A frame is dropped after video frames 11 and 35 (qp labnoise `treal`).
I confirmed the drop after frame 35: between video frames 35 and 36 both balls jump about twice their usual step (tennis 31 px against 15-17 px).
All speeds below are on the 25 fps capture clock.

## Scene
- The tennis ball (stated 6.7 cm) sits at the back-right edge of the table. From video frame 21 it rolls left.
- Around frames 29-31 it hits the white ball (ping-pong ball, 4.0 cm; the depth_info names it ping_pong_ball).
  - The tennis ball carries on to the front-left and falls off the left side at frames 42-45.
  - The white ball rolls toward the camera and slightly right. It is still on the table at frame 48.
- Stated ranges at t=1.5 s (video frame 36): tennis ball 1.183 m, ping-pong ball 1.353 m.

## Geometry (scripts/median.py, table.py, geo.py, scale.py, sens.py)
- I took the table-top corners from the median of the x render: BL(574.4,424.7), BR(851.2,428.7), FL(463.3,482.6), FR(963.4,495.2).
  The front edge is the boundary between the top and the front face, found from the gradient.
- At f=711 the two vanishing directions are orthogonal (cos -0.011). The view is grazing: the horizon is at y≈350.
- Camera height above the top, solved from each stated range at f36:
  - tennis ball: 0.1734 m;
  - ping-pong ball: 0.1728 m.

  The two agree, which independently checks the plane. Using h from the tennis ball, the plane predicts a ping-pong range of
  1.350-1.362 m (stated 1.353) over f=690-730, cy=350-370 and ±1.5 px corner shifts.
- Table rectified with h=0.173: 61.6-63.7 cm across the image and 70.4-73.1 cm in depth. The known table is 60.3 x 76.0.

## Tracks (scripts/track.py, size.py, route_a.py, capclock.py)
- I tracked the yellow and white balls by HSV threshold in x and o. The two tracks agree within about 1 px.
- After the collision the white ball's horizontal width grows from 22 px to 29 px between f36 and f48, in both renders.
  Its centre also moves down 23 px. Both mean it is moving mainly toward the camera.
- Route B (table plane): intersect the ray with the plane of the ball centre, h minus the radius.
- Route A (size): range = stated range at f36 × width(f36)/width(t), and the centre is back-projected along that range.

## Rows
| qid(s) | question | current | route A | route B | verdict |
|---|---|---|---|---|---|
| 2538/2544/2550 | table width | 59.6 | known table 60.3 | 61.6-63.7 (across image) | ok |
| 2539/2545/2551 | table length | 74.5 | known table 76.0 | 70.4-73.1 (depth) | ok |
| 2542/2548/2554 | distance between balls at 1.5 s | 29.5-29.7 | 29.5 (stated ranges), 29.7-29.8 (size) | 29.9-30.0 | ok |
| 2543/2549 | white-ball diameter | 4.0 | ping-pong ball 4.0 cm stated in other clips; 22.3 px wide (with blur) at 1.353 m = 4.2 cm | | ok |
| 2540/2546/2552 | tennis ball v at 1.5 s | 88.1 / 83.0 / 88.1 | 90-95 (±0.12 s fits) | 80-88 (fits), 88-90 (forward at f36) | ok |
| 2541/2547/2553 | white ball v at 1.5 s | 49.6 | 75-84 (fits starting at f36) | 76-95 (local fits around 1.5-1.52 s) | probably low by 1.3-1.6x, not changed (see below) |
| **2537** | white ball v at 1.6 s | **40.0** | 60-73, median about 66 | 62-65 | **fix to 64** |

### White ball at 1.6 s (qid 2537): the current value is wrong
- The current value is p8 = 25 cm/s × 1.6 (label-noise cap).
- The stored base track (research/labnoise/out/tracks_test.pkl, qid 2537) puts the white ball at a constant range of 1.183 m.
  That is the tennis ball's range. The track has no depth motion, so it reads about 22-24 cm/s of purely lateral and vertical image motion (sin psi = 1.0).
- In reality the ball rolls almost straight at the camera:
  - Route B: range 1.355 m at f36 and about 1.06 m at f48, which is 0.48 s on the capture clock.
  - Route A gives the same: 1.353 m to 1.04-1.06 m.
- Per frame the motion is 2.4-2.6 cm radial and only 0.65 cm lateral, so sin psi is about 0.39. This is a wrong-axis error.
- Speed at 1.6 s (capture frame 40, which is video frame 38):
  - Route B: 61.4-64.3 from ±0.08-0.12 s linear fits. Sensitivity to f, cy and the corners is 62.3-65.0.
  - Route A: 60-73 from smoothed windows, median about 66.
  - The mean over f36-f48 is about 64 from both routes. The ball rolls at a nearly constant speed after the slide-to-roll transition.
- The ratio to the current value is 1.53-1.65 before any label-noise inflation.
- Running the label emulator on the route B track, read-only (scripts/emu_factor.py), gives:
  - mean label / true = 1.32;
  - median label / true = 1.16;
  - MRA-optimal factor about 0.9.

  Proposed value: 64, the physical speed with no factor.

### White ball at 1.5 s (2541/2547/2553): left at 49.6
- This is the same root cause (base 31 × 1.6).
- Right after the collision the ball slides at about 100-120 cm/s (frames 33-35). It drops to rolling speed, about 63 (3/5 of v0 for a thin shell), by frame 37.
- The asked time falls on the dropped capture frame 37, inside that transition.
- Route B fits give 76-95 and the forward step at f36 gives 37 (x) and 76 (o).
- Route A is unreliable before f36, because the tennis ball overlaps the white ball at f32-33 and blurs it.
- So the two routes do not pin one number within 8%. The ratio 1.2-1.9 does not clearly pass the >1.5x gate for motion rows, so I left these rows unchanged.
  A value of about 70 would probably score better, but the evidence is below the bar.

## Result
One fix: qid 2537 (captured_0032, white ball v at 1.6 s), 40.0 → 64.
That question exists only in the o render. Every other row is consistent with the measurements.

The frames were deleted to save disk space (the disk is about 99% full). Re-create them with `scripts/extract.py`.
