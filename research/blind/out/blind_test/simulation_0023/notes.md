# simulation_0023 — boat + eagle (V3MC), 960x960, 75 frames @ 24 fps, static camera

## Camera / scale
- Range convention (Euclidean distance to origin) used; principal point (480,480).
- Focal length from the eagle speed prior: eagle centroids (same wing phase, flap period = 24 frames)
  at t=1 (471.1,372.9) and t=2 (741.9,369.5) with ranges 116.05 / 108.28 m; |p2-p1| = 11.84 m
  gives f = 3390 px (head-spot feature: 3414 px). HFOV ~16.1 deg. Straight-line model predicts the
  frame-0 eagle x within 2 px (constant-velocity check).
- Cross-checks: under the range convention the boat displacement (t=1->2) is antiparallel to the eagle's
  (179.6 deg) at this f -> both move along one world axis at ~43 deg from the image plane; z-convention
  fails this (~3 deg off). Horizon at y~454 from boat (cabin template y vs depth) and eagle level flight.

## Boat speed (1101)
- Multi-scale template tracking of cabin (75 frames, NCC 0.8-1.0). Position along the 3D motion line
  solved per frame; linear fit residual 6 mm -> constant speed 4.04 m/s (f=3390; 4.10 at f=3290,
  3.98 at f=3500). Backward-difference/local fit at t=1: 4.05. Answer 4.04 m/s. Confidence high.

## Boat height (1102)
- Mast top y=305.5 (frame 24, bg-diff), hull/rudder bottom ~625 (hull fully above water: rudder visible).
  319.5 px * Z(~103.4)/f = 9.72-9.78 m across frames 24/36/48. Answer 9.75 m. Confidence medium-high
  (unknown submerged part, if any).

## Boat length (1103)
- Heading from motion: 42.7 deg from image plane (bow left/away). Bow tip (stem top) x=195 @f24, stern
  rightmost 443, start of stern curvature 392 (shading). Projected onto the centreline plane:
  rounded-stern model 10.4-10.5 m, transom model ~10.0 m, bow-to-rudder 9.9 m. Answer 10.3 m.
  Confidence medium.

## Eagle wingspan (1105)
- Wing-horizontal frames (4-7, 32-34, 42-43): image extent 45-52 px; with the wing axis perpendicular to
  the flight direction (projection factor 0.683) and perspective modelled: W = 2.29-2.61 m. Answer 2.5 m.
  Confidence medium.

## Eagle length (1104)
- Body (white head to dark tail end) in V-phase frames spans 15-19 px horizontally; body axis projection
  factor 0.73 -> 0.7-0.88 m; top of the wing-down arc gives ~0.8 m. Answer 0.85 m (slight hedge
  toward typical eagle proportions). Confidence low-medium.
