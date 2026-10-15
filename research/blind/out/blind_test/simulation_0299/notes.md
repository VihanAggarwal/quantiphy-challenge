# simulation_0299 — forklift driving away (3D sim, static camera, 2560x1440, 24 fps, 72 frames)

## Method
- Clean background = frame 0 with the forklift region replaced by frame 71; mask by abs-diff > 30.
- KLT tracked 227 features over all 72 frames. All tracks are straight lines (median max deviation 0.5 px) and meet in one
  forward vanishing point (-1135, -479), so the forklift moves in a straight line without turning.
- Lateral VP from the two red reflectors on the overhead-guard rear crossbar (a symmetric pair), over 72 frames: (7082, -490).
  The horizon through both VPs has slope -0.0014, so roll is about 0. Orthogonality gives f = 3527-3545 px (bootstrap 3526-3561),
  i.e. HFOV ~40 deg and camera pitch ~18.8 deg down.
- 3D displacement profile s(t) from the projective geometry (ray angles + motion direction): a quadratic fits with rms 0.3 mm,
  v0 ~ 0 and t0 = 0.001 s. So the forklift starts from rest at t=0 with constant acceleration. With a = 2 (prior): s = t^2.
- Check against depth_info: r2^2 - r1^2 = 6F + 9 gives the origin's coordinate along the motion axis F = 12.275 m, at
  11.46 m perpendicular distance from the camera. In the reconstructed body (f=3530) this puts the origin on the lateral
  centre line, ~7 cm above the ground and between the axles. That is a plausible rig root, so f and the kinematics agree.
- Sizes: motion stereo (known translation s(t)*D in metres) triangulates every tracked feature / silhouette extreme in a body frame
  (forward D, lateral, up). The length does not depend on f (4.238 for f = 3400-3700); width and height change ~0.5%/1% of f.

## Answers
- 1448 speed @1.0 s: backward diff 24*(1-(23/24)^2) = 1.958 m/s (instantaneous 2.0). Confidence high.
- 1449 speed @2.0 s: 24*(4-(47/24)^2) = 3.958 m/s (instantaneous 4.0). Confidence high.
- 1450 length: fork tip (fwd 15.23) to counterweight rear face (fwd 10.99) = 4.24 m. Confidence medium-high.
- 1451 width: near-side wheel outer faces at lat 7.81-7.83, symmetry plane (reflector midpoint) at 8.549, so 2*0.73 = 1.46 m.
  The far-side contour gives 1.41 (a lower bound). Range 1.42-1.48 for f = 3450-3600. Confidence medium.
- 1452 height: overhead-guard top (-5.25) to ground (-7.70, wheel bottom + 3 cm tangent correction) = 2.45 m (2.40-2.47). Confidence medium.
