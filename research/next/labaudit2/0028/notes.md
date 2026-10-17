# Lab audit round 2: family 0028 (captured_0028, 0028s, 0028x). One event, one label set.

This round re-checks the motion and S3 rows on top of round 1 (research/next/labaudit/0028/notes.md).
Scripts are in scripts/ and image crops in img/. Frames are read straight from the mp4s and not dumped.

## Clock and event timeline
Scripts: track.py, arcs.py.
- The ball was tracked on the x render (black background) and on the o render. The two centroid tracks agree to within 1 px.
- **Dropped frame between video 35 and 36 (confirmed).** The step dy is 73.5 px against 22 px for the previous step and 30 px expected. It is a double capture step.
  The drop between 11 and 12 can only be seen weakly, because the ball is held and moves slowly (2.4 px against 0.6 and 1.5 px for the neighbouring steps).
  It matches the usual pattern of drops after video frames 11 and 35, so capture n = k + (k>=12) + (k>=36).
- Parabola fits of the image y on the 25 fps capture clock (x render; the o render is the same within 0.1 frame):

| phase | capture frames | result |
|---|---|---|
| release / fall vertex | n = 21.7 | |
| fall | n 22-26 | 8.4 px/fr^2. g at Z~1.6 is 6.9 px/fr^2; the approach term 2 f Ydot Zdot / Z^2 adds part of the difference. |
| **bounce 1** | **n = 27.26 (t = 1.09)** | fall/arc-1 intersection |
| arc 1 | | 7.65 px/fr^2, which gives Z_eff = 1.46 m on the 25 fps clock. This is consistent with the ranges. |
| **apex 1** | **n = 32.88 (t = 1.315)** | |
| bounce 2 | n = 38.66 | |
| apex 2 | n = 43.63 | |

- So the stated times are "t=1.1 = bounce 1" and "t=1.3 = max height".
  The labeller's frames are most likely n=27 (video 26, the lowest frame, t=1.08) and n=33 (video 32, the highest frame, t=1.32).
  t=1.0 is n=25, which is video frame 24.

## Ranges (surface range, the same quantity as the ToF)
Scripts: width.py, model3d.py, route3.py.
- The size scale comes from the half-max width in sharp frames only. Blurred frames are unusable: the exposure is about one full frame, so the streak length roughly equals the step.
  - With k = 30.6 px*m (the ping-pong ball in 0032), apex 1 (video 31-33, w 21.5-21.9) gives a centre range of 1.41. That is consistent with the stated 1.4115 at the surface.
  - Apex 2 (video 41-42, w 24.7-25.6) gives 1.21-1.23.
  - The held ball (w 18.4, partly hidden by fingers) is at <= 1.66-1.69.
- **Approach speed in arc 1 (Zdot)**, by route:

| route | Zdot (m/s) |
|---|---|
| ToF anchors: (1.557 - 1.4115) over bounce to apex (0.225-0.24 s) | 0.61-0.65 |
| ToF at the bounce plus size at the apex | 0.71 |
| Size trend inside arc 1 | ~0.35-0.6 (noisy) |
| Apex-to-apex range budget (0.19-0.20 m in 0.43 s, with v2 <= v1) | 0.45-0.84 |
| Table plane at bounce 1 | too sensitive: 1 px is ~2 cm, and h/vh/contact row give 0-1.2 |
| Image x-drift with zero lateral velocity | 0.63 (fragile) |

  - The apex-to-apex budget means Zdot ~ 0.9 is ruled out.
  - Conclusion: Zdot = 0.45-0.75, central ~0.6.
- **The ToF at t=1.0 looks wrong.** The stated 1.805 is ~15-20 cm farther than the physical range (~1.60-1.66: the held ball is at <= 1.69 and the bounce at ~1.56-1.58).
  At that frame the blurred ball is in front of the person's hand and arm, so the ToF pixel probably mixes in the background.

## Rows (one label for all three renders)
Here "label-style" means clicks back-projected with the stated depths, plus the next-frame ToF, taken as a forward difference on the 25 fps clock.
The MC column uses a click sigma of 2 px and a ToF sigma of 2 cm (the labnoise fit). Scripts: emulate.py, emulate2.py.

| qids | question | current | label-style | physical | verdict |
|---|---|---|---|---|---|
| 2474/2480/2486 | v at 1.0 s | 385 / 397 / 385 | The next-frame ToF is unknown, so the label spans 207-548 for ToF(n26) = 1.805 down to 1.60. Interpolating the stated anchors gives 331 if the t=1.1 anchor is at n27.5 and ~380 if it is at n27. | 165-190 (central difference); 190-215 forward | Leave: consistent with the interpolation route, and no two routes pin a value. |
| **2475/2481** | **v at 1.3 s** | **93.375** | Deterministic 49-78 for Zdot 0.45-0.75 (central ~66); ToF-anchor route 64-68. MC median 65-83; MRA-best 51-69. | 55-66 (horizontal approach ~0.6 m/s; vertical ~0 at the apex; forward-difference vertical 0.2 m/s) | **Fix to 71.925** (see below) |
| 2487 | v at 1.3 s (x) | 71.925 | same as above | same as above | OK, keep |
| 2476/2482/2488 | a at 1.0 s | 980 | Smooth emulation with the interpolated depths gives ~900-1000 (pixel second difference 6 px at 1.7 m, radial second difference ~0). With a 2 cm ToF noise the second difference has sigma ~30 m/s^2, so this cannot be determined. | ~g, or 1.1-1.2 g if the ball was pushed down | Leave |
| 2477/2483/2489 | a at 1.3 s | 980 | Smooth emulation gives ~950-980 (7.7 px/fr^2 at 1.41 m) | g | Leave |
| 2478/2484/2490 | distance 1.1 to 1.3 s | 29.1 / 29.3 / 27.3 | For (n27, n33): straight 26.6, smooth path 27.9, MC path median 30.6. Other frame choices give 23-30. | Bounce-to-apex arc ~28-30 | Leave |
| 2479/2485/2491 | max height | 25.0 | Camera-vertical difference of the clicks: 21.9. 3D distance: 26.6. | Bottom rise 24.8-25.2 (fall time and pixels); centre above the table ~27 | Leave (the definition is ambiguous; 25 sits in the middle) |

## The fix: qid 2475 and 2481 (v at 1.3 s, o and s renders), 93.375 -> 71.925
- **Where 93.375 came from:** Claude's base value 75 times the labnoise factor 1.245.
  - That factor came from stored o and s tracks with sin_psi ~1.0, that is, ball motion perpendicular to the line of sight with no depth motion.
  - The x track of the same event had sin_psi = 0.09, giving a factor of 0.959 and the value 71.925.
  - Both renders share one label, so the 1.245 rests on a wrong-axis track (the same failure as 0032's qid 2537).
- **Measured geometry at the apex:** the ball moves mainly toward the camera at ~0.6 m/s, plus the forward-difference vertical 0.2 m/s, so sin_psi ~0.3.
- **Two routes:**
  - Route 1, the ToF anchors, gives 64-68.
  - Route 2, the ToF-free size, plane and drift routes, gives Zdot 0.45-0.71, so a label of 50-73 with central ~62.
  - The routes agree within ~6% on ~62-68. A ~70 value is also what the MC label distribution supports.
- **Why 93.4 is out:** it needs Zdot ~ 0.9 m/s (deterministic) or a ToF sigma >= 4 cm. The apex-to-apex size budget excludes Zdot >= 0.84.
- **Expected score:**
  - With ToF sigma 1-3 cm and Zdot 0.45-0.75, 71.9 beats 93.4 by 0.01 to 0.15 per row.
  - It ties at Zdot 0.9.
  - It loses at most 0.013 only if the ToF sigma is 4 cm.
- The new value equals the x render's 71.925, so all three renders of the event carry the same answer. It is ~30% below the current 93.375.

## Result
There is one fix, applied to the two renders that disagreed: 2475 and 2481, 93.375 -> 71.925. qid 2487 already has 71.925.
All other rows were left unchanged.
