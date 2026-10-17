# internet_0069 independent remeasure (qids 3252-3258)

Prior: the cup's acceleration from 2.00 s to 2.30 s is 0.32 m/s^2, so v(2.3) - v(2.0) = 0.096 m/s.
Every answer is 0.096 m/s times a pixel ratio, so only pixel kinematics matter:
R(t) = v_px(t) / [v_px(2.3) - v_px(2.0)].

## Scene and camera
- Static tripod shot: wall, baseboard and wood floor. A cup is pulled left to right by a string tied to the top of its handle.
- The cup is in view from frame ~55 to ~84. The left edge enters the frame at frame 61. t = frame/30.
- Camera: no pan, but there is a slow focus-breathing zoom. The baseboard markers at x=410 and x=1580 spread apart by ~12 px
  (+1%) between frames 57 and 75 and then relax again. The vertical baseboard-to-floor spacing confirms this.
  Cup height is ~567-573 px and constant to within the zoom, so the cup stays at one depth.
- Main pitfall: off-axis widening of the cup silhouette. Body width at row 800 is 453 px at x~230, 413 px at the image
  centre and 451 px at x~1670 (it follows the cylinder 1/cos(theta) law, f~1570 px). So a single edge is not linear
  in world X.
  - Leading edge alone gives R(2.0)=4.0 (a_px 1535). This explains the original notes' 1530 px/s^2 and v=0.383.
  - Trailing edge alone gives R=5.5.
  - The silhouette midpoint at a fixed row is exactly linear in X under a pinhole camera.

## Route 1 (primary): silhouette-midpoint track
- Per-row gradient peaks (3-channel |d/dx|, ramp centre, so motion blur does not bias them).
- Robust straight-line fits:
  - left edge over rows 650-900;
  - right edge over rows 650-785 (handle gap) and 885-950 (below the handle);
  - both evaluated at row 800.
- Frames 59-60 (left edge off-screen) use the right edge minus a half-width taken from a linear width trend.
- Centre track c(t) for frames 61-79 fits a quadratic with rms 0.3 px. The acceleration is constant: a_px = 1413-1446 px/s^2 across windows 59-72, 60-70 and 59-79, deg 2/3.
- v_px(2.0) ~ 1922-1926 px/s, giving R(2.0) = 4.43-4.55. Adopted R(2.0) = 4.50.
- Scale = 0.32/1430 = 2.24e-4 m/px (axis plane). Cup size check: about 9.2 cm diameter x 11.5 cm tall, which is a plausible mug.

## Route 2 (check): string-knot track
- Template match of the R-B "string" map around the knot at the top of the handle (a rigid 3D point, so linear in X).
- Frame-to-frame displacements 65 -> 91 px/frame. A linear velocity fit gives R(2.0) = 3.9-4.9 (noisy, mean ~4.3).
- This agrees with Route 1 within its noise.

## Sensitivity (not applied)
- Zoom-corrected centre track (marker-interpolated similarity): a_px ~1320-1375 and R(2.0) ~4.7-5.0, so velocities are ~+7%.
- Not applied: the GT prior and answers are almost certainly derived from raw-frame annotation, and the raw track
  is also the smoother of the two (rms 0.3 vs 0.35-0.75 px).
- Velocity convention: instantaneous (central). A forward 0.1 s difference would add +0.016 m/s.

## Answers (raw centre, R(2.0)=4.50, constant a = 0.32 m/s^2)
| qid | quantity | value |
|---|---|---|
| 3252 | v(2.0) | 0.432 m/s |
| 3253 | v(2.1) | 0.464 m/s |
| 3254 | v(2.2) | 0.496 m/s |
| 3255 | v(2.3) | 0.528 m/s |
| 3256 | disp 2.0-2.1 | 4.49 cm (fit ratio 0.4675 s x 0.096) |
| 3257 | disp 2.1-2.3 | 9.93 cm (1.035 s) |
| 3258 | disp 2.3-2.5 | 11.2 cm (1.168 s; cubic fits give 11.05-11.1) |

Confidence: medium. The ratio is solid to ~3% for a linear tracker. The residual risk is which point the GT
annotation tracked (a leading-edge or bbox-with-handle track would move the answers by -11% / +15%) and the zoom (+7%).

Scripts are in scripts/ (edges3.py, linefit.py, zoomcorr.py, knot.py, markers.py). The final tracks are in tracks_final.json.
