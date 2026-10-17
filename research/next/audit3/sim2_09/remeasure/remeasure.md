# sim2_09 independent remeasure: qids 662, 664 (simulation_0221, vacuum acceleration at 1 s and 2 s)

I measured these from scratch and did not read ../notes.md or any other file in ../.
Prior: vacuum diameter = 0.438 m. 24 fps, 80 frames, 1920x1080, fixed near-nadir camera.
Sibling simulation_0222 shows the same scene and camera with diffuse lighting (no sun or shadow band) and the same scripted motion. The two tracks agree to within 0.3 px on every frame.

## Scale
- Edge-based circle and ellipse fit of the vacuum outline. A radial gradient picks the edge on 720 rays; the fit is then refined robustly.
- Off-centre positions look elongated along the radius because the side wall is visible in perspective (h/H ~ 0.008). The tangential (minor) axis is the true top-disc diameter.
- Minor axis in 0222 at frames 0, 12, 24, 36, 48, 60 and 79: 120.12, 120.13, 119.82, 119.88, 120.00, 119.97, 120.04. In 0221: 120.4, 119.9, 119.5.
- D = 120.0 px, so s = 0.438/120.0 = 3.650 mm/px. The height and perspective corrections cancel to below 0.5%.

## Tracks
- Route 1: gradient-edge circle fit at every frame, in both clips (track_*_edge.csv).
- Route 2: background-median difference with a whiteness mask, then a mask circle fit or centroid (track_*_v1.csv; for 0222 split into maskfit and maskcen).
- The vacuum moves from frame 1 to frame 69 and is at rest from frame 69 on.

## Motion model (strong evidence)
The track is a Blender Bezier F-curve with keys at video frames 0, 39 and 69 (Blender frames 1, 40, 70):
- Image x uses Blender auto handles: time-handle fraction 1/2.5614 = 0.3904, flat ends, and an interior slope equal to the mean of the two chord slopes. The rms residual is 0.11 px (0222) and 0.17 px (0221) with only 3 free values. Scanning the handle fraction gives a sharp minimum at 0.39; with 1/3 the rms is 5 px.
- Image y uses flat handles at all 3 keys (the key at frame 39 is the y minimum) with time-handle fraction 1/3. The rms residual is 0.05 px.
- I cannot explain why the handle fractions differ between x and y, but both fits sit at the noise floor.

Speed series from the model (m/s, backward differences):
- Frames 21 to 26: 1.698, 1.732, 1.758, 1.775, 1.785, 1.786.
- Frames 45 to 50: 1.763, 1.832, 1.893, 1.943, 1.981, 2.006.

The model reproduces the speed rows: v(0.5 s) = 1.075, v(1 s) = 1.775, v(2 s) = 1.943.

## Accelerations (t = 1 s is video frame 24; t = 2 s is frame 48)

| definition | qid 662 (1 s) | qid 664 (2 s) |
|---|---|---|
| backward: (v_n - v_{n-1})*fps, v = backward-difference speed | **0.42** | **1.21** |
| instantaneous d\|v\|/dt at t (equals backward at frame n+1) | 0.22 | 0.91 |
| central (v_{n+1} - v_{n-1})/2*fps | 0.32 | 1.06 |
| backward difference at frame n-1 / n+1 | 0.62 / 0.22 | 1.46 / 0.91 |

- The model gives identical numbers on 0221 and 0222, from both the edge track and the mask track (to 0.01).
- Model-free check: local cubic and quartic fits of position over +-5 to 8 frames give 0.40-0.47 (backward) and 0.19-0.27 (instantaneous) at frame 24. At frame 48 they give 1.12-1.25 (backward) and 0.81-0.95 (instantaneous); the local cubics slightly over-smooth the jerk there.

## Answers
- **662: 0.42 m/s^2.** Low confidence. The value is measured precisely, but the speed is near its peak (frame 25.5), so it depends strongly on the definition and on frame alignment. The instantaneous derivative would give 0.22.
- **664: 1.21 m/s^2.** Medium confidence. The instantaneous d|v|/dt would give 0.91; a central difference would give 1.06.

I chose the backward definition to match the stated speed convention, applying the same backward difference to speed.
