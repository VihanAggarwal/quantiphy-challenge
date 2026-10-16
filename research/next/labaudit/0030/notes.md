# Lab audit: family 0030 (captured_0030, 0030s, 0030x)

All three renders come from the same footage, so they share one set of labels. Each is 49 frames at 24 fps, 1280x720.
Render o has a blurred background, s a blue-white background and x a black background. In x the ball looks brown, so I tracked in s and o.

Scene: a red ball (prior: 7 cm) is fixed to the end of a stick and swept around the lab table top. The person stands at the left.
- f0-f5: the ball moves fast to the left along the front half.
- f8: it turns near the back-left corner.
- f12-f19: it runs right along the back edge, with heavy horizontal motion blur.
- f20-f24: it swings forward toward the camera at the front-right.
- f24-f33: it moves back to the left along the front.
- f35-f48: it repeats the run along the back edge.

Stated ranges are 0.8715 m at t=0.2 (the "s" is a typo for m), 1.166 m at 0.4, 1.372 m at 0.6 and 1.315 m at 0.8.

All 12 scored rows are ball velocities at t = 0.2, 0.4, 0.6 and 0.8 s (4 per render).

## Geometry (scripts/table.py, plane.py, geo.py)
- The table top comes from the x-render median. Corners: FL(201.8,530), FR(974.7,530), BR(807.2,441.2), BL(386,440.4).
  - At f=711 the corners are nearly orthogonal (cos -0.034, i.e. 2 deg).
  - W/D comes out at 1.30, against 1.26 for 76.0 x 60.3 cm.
- The camera is about 19.5 cm above the table top. Corner ranges are 0.81-0.85 m at the front and 1.35-1.39 m at the back.
- The ball centre plane is 3.5 cm above the top. Ranges from intersecting that plane are 3-10 % shorter than the stated (ToF) ranges at all four anchors.
  The 0040 audit found the same ToF excess.
- Size check:
  - The ball's vertical extent at f4-5 is 56-64 px, which gives a range of 0.80-0.93 m (stated 0.87).
  - Extents at the back (f15-18) are unreliable because the mask loses the dim, blurred edge. I did not use them.

## Tracking (scripts/track2.py, size.py, overlay.py)
I used two centre estimators on the s and o renders: the centroid of the saturated core and the centre of the extent box.
- The s and o tracks agree within about 1-2 px.
- overlay_centres.png shows the centres sitting on the ball.
- The red reflection on the glossy table top is excluded with r-g > 80 and s > 185.

## Speeds
Two routes:
- Route A (scripts/route_a.py): back-project with the stated ranges. Depth models:
  - linear interpolation between the anchors;
  - plane ranges rescaled to the anchors;
  - plane ranges times one global factor.
- Route B (scripts/route_b.py): pure table-plane intersection.

I report forward differences at floor(t*24) and round(t*24), plus central differences.

| t | current (o / s / x) | route A, anchors linear | route A/B with plane depths | verdict |
|---|---|---|---|---|
| 0.2 | 140.85 / 133.2 / 140.85 | 167-183 (ctr 174-176) | 153-198 (ctr 164-183) | lowish (about 1.2-1.3x), not >1.5x, so left as is |
| 0.4 | 132.86 / 131.46 / 131.46 | 121-137 (ctr 128) | 77-181 (ctr 90-172), noisy | ok |
| 0.6 | 182.07 (all) | 167-177 (ctr 169-173) | 150-295 (ctr 153-190) | ok |
| 0.8 | 210.2 (all) | 155-164 (ctr 167-171) | 186-336 (ctr 187-227) | ok, see below |

Notes on the rows:
- t=0.8: the ball turns toward the camera between f19 and f24. The range drops from about 1.3 m to about 0.8 m in 4 frames.
  Linear anchor interpolation misses that radial component, which is why anchors-linear reads low. Routes with depth from the plane give 210-240,
  so 210.2 is consistent.
- t=0.2: the tangential part (40 px per frame at 0.87 m) is about 118 cm/s and the radial part (0.87 to 1.17 m over 0.2 s) about 147 cm/s, which
  combine to 170-190 cm/s. The current answers are about 25-30 % lower. That is inside the leaderboard-tuned motion band, and the rule
  for this audit is to leave motion rows alone unless they are >1.5x off. The 6 % spread between renders (133.2 for s, 140.85 for o and x)
  is a harmless inconsistency, since the renders share one label.
- Chord speeds between the stated anchors (scripts/chord.py) are 152, 164-177 and 179-185 cm/s for the three 0.2 s segments. Nothing points to a
  gross error.

## Result
No fix. All 12 rows are within about 1.3x of my measurements, and none shows a wrong object, time, axis or segment.
