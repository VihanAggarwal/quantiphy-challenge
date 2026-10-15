# simulation_0151 - notes

Scene: underground garage, fixed camera looking straight down the corridor (corridor vanishing point ~(957,536), close to the image centre, so there is no pitch or yaw).
The yellow sports car (near) and the blue cart (farther back) pull out of the right-hand bays and drive to the left, parallel to the image plane.
Both stay at a constant depth: tyre pixel size and hub row stay constant.

## Scale
- Yellow tyre outer diameter is about 184-186 px (radial edge analysis on hub-aligned averaged frames; the top is in the fender's shadow). Used 185.5 px, which gives 4.119 mm/px at the tyre plane.
- Blue tyre outer diameter is about 73.1 px (left/right/bottom edges, frames 36-41), which gives 5.048 mm/px.
- The floor-contact rows (884.4 vs 818.7, horizon ~536) give a depth ratio within about 1% of the tyre-size ratio.
- f: depth_info is treated as Euclidean range to the tyre origin (hub at mid-plane, +0.13 m behind the outer face). The front hub at t=0.5 s is at (1651.5, 791.8), which gives f ~ 2630 px (HFOV ~40 deg).
  - Using optical-axis Z instead would raise f, and so the cart depth and lateral width, by about 4%.
- Blue cart near-tyre depth is about 13.27 m.

## Motion
- Tracking: rim ellipse fits (yellow) plus NCC patch templates (body and roof features) with sub-pixel peaks.
- Both cars follow Blender's default Bezier ease, a smoothstep from frame 0 to 59 (keyframes 1 to 60).
  - Yellow fit: rms 0.27 px. Free fit: t0=0.12, T=58.7.
  - Blue fit: roof lights rms 0.05 px over frames 11-41.
  - The two cars share the same a/v ratio, as expected for a shared timing.
- Yellow, front-rim plane: D = 4034 px. Backward speed at frame 24 is 98.30 px/frame. Backward-backward acceleration (centred at 23.0) is 1.532 px/f^2, and 1.414 px/f^2 if centred at 23.5.
- Blue, tyre plane: D = 1333 px. v24 = 32.49 px/f, a = 0.506 px/f^2 (0.467 if centred at 23.5).
- Answers: speed is v_px*24*scale. Acceleration is about 0.98*a_back*576*scale, a slight hedge between the backward and central conventions.
  - Yellow: 9.71 m/s and 3.56 m/s^2.
  - Blue: 3.93 m/s and 1.44 m/s^2.

## Blue car width
- Read as the lateral (side-to-side) AABB extent.
- Frame-0 oblique view, near and far front tyres:
  - Far-tyre outer silhouette at 1595 vs near outer face at 1636 (hub 1672.45 - R 36.5) gives Zfo/Zno ~1.064.
  - The floor contact of the far tyre's inner face gives 1.053 plus the tread width, which is consistent.
  - Track outer-to-outer is about 0.064*13.27, about 0.85 m.
- The roof edge (far silhouette in frame 0 and near silhouette in frame 41, linked by the measured 1034.7 px displacement) is as wide as the track, 0.83 +/- 0.08 m.
- Lateral width is about 0.85 m; answered 0.87.
- Alternative reading, "width" = horizontal on-screen extent (cart length, front tyre to visor tip): about 1.90 m. Not used.

## Confidence
- Yellow speed: high (+/-3%).
- Blue speed: high (+/-3%).
- Accelerations: medium. The convention (backward vs central, frame offset) spreads them by about +/-8%.
- Width: low-medium. The main risk is the definition (lateral 0.85 vs length 1.9).
