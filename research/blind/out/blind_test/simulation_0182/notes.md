# simulation_0182 — box falls onto a roller ramp and slides down it (24 fps, 40 frames, 1920x1080)

## Camera (fixed, pitch 0, roll 0)
- The main-wall mortar lines (71 LSD segments) meet at VP_L = (-5122, 540). That puts the horizon at y = 540, and the vertical lines are vertical.
- The side-wall strip at x<131 (5 mortar lines) meets at VP_R = (1700, 540). If the two walls are perpendicular, f = sqrt(740*6082) = 2121 px.
- Orthogonality of the box's own faces (edge heights at the 3 visible vertical edges): f = 2124.
- Free fall with g = 9.81 and the frame-0 depth: f ~ 2130-2145 (g_ff = 9.84 at f=2125; damping makes it slightly less than 9.81).
- The prior gives a(slide) = 2.338. The fit gives 2.366 at f=2125, which implies f ~ 2150.
- Chosen f = 2135 px (~40 mm lens on a 36 mm sensor).

## Box geometry (frame 0, the box is aligned with the walls)
- Cuboid from edges plus the VPs, with the range to the centre = 9.522 m.
  - H (body) = 0.750 m.
  - Side parallel to the wall / ramp = 1.06-1.07 m.
  - Side perpendicular to the wall = 1.595 m. An IoU scan over 5 frames allows 1.50-1.60, so I take ~1.57.
- The silhouette fit (IoU 0.97) confirms the dimensions. H and L are tightly constrained; W is only weakly constrained.
- The centre projects to (588, 352). At t=0.5 the in-plane model gives a range of 9.391 m against the given 9.384 m, so it checks out.
- The near long top flap is raised ~9 deg. Its free edge rises ~0.084 m above the body top, so the AABB height including flaps is ~0.83 m.

## Motion
- Frames 0-7 are free fall from rest. The pixel acceleration matches g, and Q1 (t=0.2 s, frame 4.8) falls in this phase. Answer 9.78: damping would give ~9.73, no damping 9.81.
- The box lands at about frame 8 and rotates onto the 28.6 deg ramp, which is parallel to the wall. It then slides with no yaw.
- I fitted a 3D cuboid to each frame's silhouette, with the centre held in the vertical plane through P0 parallel to the wall. Residuals of the trajectory are 1 mm rms.
- A quadratic fit over frames 14-37 gives a = 2.36-2.38 m/s^2, consistent with the prior of 2.338.
- The backward-difference speed at frame 24 is v(0.979 s) = 2.946 m/s at f=2125, which is 2.93 at f=2135.
- At frame 36 it is v(1.479 s) = 4.13 m/s at f=2125, which is 4.11 at f=2135.

## Answers / confidence
- 1424 accel at 0.2 s: 9.78 m/s^2. High confidence: free fall.
- 1425 speed at 1.0 s: 2.93 m/s. High: about ±3%, driven by f.
- 1426 speed at 1.5 s: 4.11 m/s. High: about ±3%.
- 1427 length: 1.55 m. Medium. This is the long side (perpendicular to the wall, 1.57-1.6). If "length" means the side along the ramp, the answer would be 1.06.
- 1428 height: 0.80 m. Medium. The body is 0.75 and the AABB with the raised flap is 0.83, so 0.80 sits between them.
