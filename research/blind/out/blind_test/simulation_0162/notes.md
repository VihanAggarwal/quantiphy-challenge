# simulation_0162 — blue ball rolling left->right along a lane (2D side view, static camera)

## Method
- Static camera (frame 0 = empty background). Ball tracked by background difference; sub-pixel silhouette edges
  (gradient peaks of |frame-bg|) on side rows + top edge, robust circle fit per frame (scripts/vert.py -> circ3.txt).
  Partial-entry frames 9-19 tracked via right edge minus half-width (scripts/edges3.py).
- Ball diameter in px near image centre (no off-axis elongation): 78.3-78.8 px (circle fits, chord widths, visual zoom).
  Used D = 78.5 px -> 0.21/78.5 = 0.002675 m/px. Ball depth constant (size symmetric left/right; off-axis
  elongation symmetric about x=960 -> f ~ 2000 px, hFOV ~ 50 deg). Motion parallel to image plane -> linear px->m.
- Silhouette centre shows a once-per-revolution circular wobble (x and y in quadrature, amplitude ~1.17 px):
  mesh centre offset from the rotation centre (origin). Origin = rotation centre moves smoothly, so fit
  x(t) = smooth(t) + A cos(phi) + B sin(phi), phi = x_smooth/rho (best rho ~ 39.9 px, rolling). Residual rms 0.15 px.
- Smooth model: exponential approach to terminal speed (tau ~ 31 frames, v_inf ~ 30.4 px/frame); poly4/5/6 agree.
- Speed = backward difference x(k)-x(k-1); acceleration = backward second difference, k = t*24.

## Results (px/frame -> SI with 24 fps, 0.002675 m/px)
| qid | quantity | px | answer |
|---|---|---|---|
| 377 | v(1s)  | 16.21 px/f   | 1.041 m/s |
| 378 | a(1s)  | 0.453-0.468 px/f^2 | 0.716 m/s^2 |
| 379 | v(2s)  | 23.91 px/f   | 1.535 m/s |
| 380 | a(2s)  | 0.209-0.216 px/f^2 | 0.330 m/s^2 |

## Confidence
- Speeds: high (model spread <1%, scale ~1%). Rolling-radius cross-check suggests scale could be ~1.8% lower.
- Accelerations: medium (model spread ~3-5%, frame-convention ~3%). If GT origin wobbled (not expected), accel would differ a lot.
