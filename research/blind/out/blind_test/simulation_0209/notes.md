# simulation_0209: typewriter falls onto a desk (3D Blender, 24 fps, 2124x1080, static camera)

## Camera
- Vanishing points from LSD segments on the desk: the long axis, the short axis and the verticals (pilasters and legs).
  Pairwise f estimates: 2626, 2634 and 2657 px (bootstrap sd about 35 px). Fitting f with a free pixel aspect gives an aspect of 0.993.
  The orthocentre is at (1082, 534), close to the image centre. I used f = 2630 px (hFOV 44 deg), pitch 13.3 deg down and roll 0.
- Table plane: the gun lies at range 4.704 at pixel (1430, 625), which puts its origin 1.228 m below the camera. The table top is
  therefore about 1.231 m below the camera.
- Cross-checks (Euclidean range convention):
  - Fitting the free fall with g = 9.81 gives the base's front-left-bottom corner at range 4.06 at t = 0. The bbox centre is then at 4.27-4.31 (given: 4.32).
  - The typewriter centre at rest on the plane is at range 4.498 (given: 4.501).
  - The fall reaches the plane at frame about 10.4, which matches the visible gap at frame 10 and contact at frame 11.

## Speeds (qids 1588-1590)
- Subpixel tracking of the lowest silhouette point over frames 0-9, fitted with a full perspective free-fall model (rms 0.13 px).
  The fall starts from rest at n0 = -0.11 to -0.135 frames, so the motion is pure translation from about t = 0.
- Backward difference: v_n = (g/24)(n - 0.5 - n0). Results: v(3) = 1.07, v(6) = 2.29, v(8) = 3.10 m/s.
  Bullet damping and substep effects change these by under 1-3%. Confidence: high.

## Table (qids 1584, 1591)
- Top-surface corners: L(472.5, 685.5) and F(1599.2, 525.3) from the silhouette lines; R(1979.8, 640.3) and N(698.9, 877.2) from the front and left edge lines.
  On the plane these form a 2.40 x 1.02 m rectangle with corner angles of 90.4-90.8 deg.
- The molding bead at the corner tips sticks out about 2.1 cm and sits 2.5 cm lower. Including it, the AABB is about 2.44 x 1.06 m.
- Uncertainty: about ±2-3%, mostly from f (±1.5%) and plane height (±1%). Confidence: medium-high.

## Typewriter (qids 1585, 1586, 1592)
- Height: I fitted the paper-rest top edge over frames 3-9 using perspective parallax. h = 0.174-0.182 m; the rest-pose check gives about 0.18. Answer: 0.18.
- Footprint, initial pose (frame 9):
  - Front edge: 0.315 m at yaw -13 deg relative to the table axes (key rows give -14.6 deg).
  - Left side panel: 0.35 m along about +92 deg, so the corner is about 105 deg (the footprint is not a clean rectangle).
  - Rest pose: about 0.32-0.35 x 0.34 m.
- Local dims are about 0.32-0.40 (lateral) x 0.34-0.37 (depth). The AABB on the table axes at t0 is about 0.38-0.45 x 0.42-0.45.
- I answered 0.38 for both length and width as a hedge between the local and world-AABB conventions. Confidence: low-medium.

## Letter (qid 1587)
- Edges fitted on frame 0, with corners L(1315.6, 624.5), N(1363.4, 643.2) and R(about 1409, 635.5); all four are visible apart from the far corner under the gun.
- On the plane: 0.144 m along the table depth and about 0.10 m along the table length, with a 90 deg corner.
- "Length" is taken as the long side, 0.144. I answered 0.14, slightly hedged in case length means the X-dimension (0.10). Confidence: medium.
