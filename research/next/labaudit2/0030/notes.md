# Lab audit round 2: family 0030 (captured_0030, 0030s, 0030x; one event, labels shared)

Input: `../inputs/0030.json`. It has 12 scored rows, all S3: the red ball's velocity at t = 0.2, 0.4, 0.6 and 0.8 s, for
3 renders each. There are no static rows, and no row carries a round-1 fix (round 1 found none; see `../../labaudit/0030/notes.md`).
I used test inputs only: frames, `prior` (7 cm ball) and `depth_info`. I used no labels.

**Result: no fix.** There is one near-miss, v(0.2), described below. All other rows sit inside the spread of the label-style routes.

Scripts are in `scripts/` and image crops in `img/`. Frames are read straight from the mp4s, and no frame dumps are written.

## Clock (scripts/track.py, track_mask.py)
- **Ball silhouette from the x render.** In x, the ball's SAM mask is drawn as a dull brown fill, while the table is
  pixel-identical to the s render and the background is black. So mask = |s - x| > 60 and x not black.
  - This gives the full ball outline, with the highlights and the blurred rim, and without the red reflection on the
    glossy table (`img/mask_s.png`).
  - The s and o strict-mask centroids agree with it to within 1-3 px.
  - Round 1's strict mask dropped the highlight band at the top of the ball, so its centres sit 3-9 px low.
  - The x render has no fill in video frames 0-4 (very fast frames).
- **Dropped capture frames.** These show as double-length steps of the silhouette centroid:
  - video 11->12: 50.4 px, against 17.1 before and 33.0 after;
  - video 35->36: 44.1 px, against 15.2 before and 29.5 after.
  - So capture n = k + (k>=12) + (k>=36), the usual pattern.
- **Asked times on the capture clock:**

  | t | capture n | video frame | forward difference |
  |---|---|---|---|
  | 0.2 | 5 | 5 | n5->6 = video 5->6 |
  | 0.4 | 10 | 10 | n10->11 = video 10->11 |
  | 0.6 | 15 | 14 | n15->16 = video 14->15 |
  | 0.8 | 20 | 19 | n20->21 = video 19->20 |

## Ranges (scripts/depths.py)
Three routes give the range per frame:

| route | how |
|---|---|
| Plane | Ball centre on the plane 3.5 cm above the table top, using round 1's corner plane (camera 19.6 cm above the top). I re-checked the corners on the s median (`img/corners.png`). The vanishing-point horizon is y = 334, which gives h = 0.193 from both the front and the back edge widths. |
| Size | f x 7 cm / the minor axis of an ellipse fitted to the silhouette. The minor axis is the blur-free direction. |
| Stated | Surface ranges 0.8715 / 1.166 / 1.372 / 1.315 at n5 / 10 / 15 / 20. |

Cross-checks:
- **Size and plane agree** to 0.992 +- 0.024 on n31-50 (no anchors there) and 1.023 +- 0.010 on n5-11. That validates f = 711, h = 0.193 and the 7 cm ball together.
- **Stated minus route surface range** at the 4 anchors: plane +4.6 / +4.4 / +10.6 / -2.5 cm; size +1.9 / +0.2 / +9.0 / +5.3 cm.
  - The ToF reads about 3 cm long on average.
  - The n15 anchor (small, blurred ball at the back edge) reads about 10 cm long.
- **Change in range between anchors** (stated / plane / size, in cm):

  | anchors | stated | plane | size |
  |---|---|---|---|
  | n5->10 | 29.4 | 29.8 | 29.4 |
  | n10->15 | 20.6 | 12.4 | 22.1 |
  | n15->20 | -5.7 | +6.1 | -9.5 |

  - The front half is tightly pinned: the ToF offset at n5 and n10 is the same.
  - At the back the plane is ill-conditioned (1.5 cm/px), and the frame-to-frame radial rate there is not pinned by any route.

## Rows (scripts/label_style.py, mc_score.py)
The label-style value is 25 x |d(n+1) u(click n+1) - d_stated(n) u(click n)|. d(n+1) is modelled in two ways:
- **persist:** d_stated(n) plus the route's smoothed change in range;
- **meanbias:** the route's range at n+1 plus the mean ToF bias of the four anchors.

The anchor-linear model is also included. The MC adds 2 px click jitter and ToF sigma_z = 1-3 cm.
"Physical" is the speed from the plane-route 3D fit, as a forward difference (FD) and as an instantaneous value.

| qids (o/s/x) | t | current o / s / x | label-style routes (cm/s) | physical | verdict |
|---|---|---|---|---|---|
| 2508 / 2512 / 2516 | 0.2 | 140.85 / 133.2 / 140.85 | plane 177 (persist), 198 (meanbias); size 162-174 (persist), 167 (meanbias); anchor-linear 166; strict-centroid clicks + plane 196 | FD 177, instantaneous 185 | **near-miss, no fix** |
| 2509 / 2513 / 2517 | 0.4 | 132.86 / 131.46 / 131.46 | 122-150 (plane persist 134, size 129-134, anchor-linear 122; plane meanbias 163) | 133-135 | ok |
| 2510 / 2514 / 2518 | 0.6 | 182.07 (all) | 175-204 with a persistent n15 offset (plane 181-183, anchor-linear 177-185, size 195-204); 222-256 if the +10 cm n15 ToF excess does not persist | 157-163 at plane ranges (170-177 at the stated scale) | ok (low end; the routes disagree) |
| 2511 / 2515 / 2519 | 0.8 | 210.2 (all) | plane persist 221, size persist 248; anchor-linear / plane meanbias 168; size meanbias 290 | FD 204, instantaneous 172 | ok (current sits mid-spread) |

### Near-miss: v(0.2) (qids 2508, 2512, 2516)
**Geometry at n5:** the ball is coming round the front-left towards the back-left corner. Most of its motion is
radial: about 6.3 cm/frame (~158 cm/s), with only about 75 cm/s tangential.

**The radial rate is well determined:**
- plane +6.36 cm/frame;
- size +5.7 (smoothed) / +6.2 (raw);
- anchor-linear +5.9;
- stated, plane and size all agree on the n5->10 change.

**Label-style central value:** about 172-177 cm/s.

| criterion | met? |
|---|---|
| (a) two routes agree within 12% (plane 177 against size 162-174) | yes |
| (b) current off by at least 25% | no: 140.85 is 18-20% low and 133.2 is 23-25% low |

Expected item score (MC, mean over the depth models):

| answer | sigma_z = 1 cm | sigma_z = 2 cm | sigma_z = 3 cm |
|---|---|---|---|
| 140.85 | ~.77 | ~.71 | ~.65 |
| 165 | ~.85 | ~.74 | ~.64 |

So the gain is about +0.02-0.08 per row, and nothing at sigma_z = 3 cm. If the bar is relaxed, 165 for all three renders is the
robust choice. The s render's 133.2 is the most off and also disagrees with the o and x renders, which share its label.

### Why v(0.6) and v(0.8) are left
- At the back the next-frame ToF is unpinned.
  - The n15 anchor carries about +10 cm of ToF excess, and whether that persists into n16 changes the label from about 185 to about 250.
  - At n20->21 the ball turns towards the camera. The plane and size routes give 2-10 cm/frame raw radial change, and 6-8 cm/frame smoothed.
- Both current values (182.07 and 210.2) sit inside the plausible label spread. No two routes pin a different value.

## Result
No fix. All 12 rows are left unchanged.
