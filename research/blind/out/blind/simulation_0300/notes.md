# simulation_0300 - red LaFerrari-type car driving away from a fixed camera (2560x1440, 24 fps, 72 frames)

## Geometry / calibration
- Background median + frame differencing gives the car mask. KLT tracks (about 150-1000 features) plus tracked taillight centres and yellow hub caps all move along straight image lines that meet at the motion vanishing point VP_u ~ (-1080..-1110, -447..-462). Pure translation, no yaw.
- The taillight pair is a lateral (car-axis) direction. Its lines over frames 21-71 meet at the lateral VP (~7000, -420). The camera roll measures 0.24 deg, so the camera has no roll. Orthogonality VP_u . VP_l = -f^2 gives f = 3470-3545 px (zero-roll, horizon-constrained 3508-3545). The Blender default of 50 mm/36 mm would give 3556. Used f = 3545 (HFOV ~40 deg). Pitch is ~18.5 deg down.
- Kinematics: the image scale about VP_u (R_ref/R(t) = Z(t)/Z_ref) is quadratic in t, with the car starting from rest at t0 ~ 0.00-0.01 s. Frames 0 and 1 are identical, and the early displacements go as n^2. With a = 5 m/s^2, s(t) = 2.5 (t - t0)^2, so the displacement from t=1 to t=2 is 7.45-7.5 m.
- Metric 3D reconstruction: each tracked point's depth is Z1 = u_z*Ds/q. The given ranges were checked against an origin near the bbox centre: |O(1)| and |O(2)| match 17.83 and 23.20 within 0.3-1.4% (scale factor k ~ 1.006). Two independent scales (the kinematic one and depth_info) therefore agree.

## Answers
- Speeds (backward difference, a = 5 from rest at t0 ~ 0): v(1) = 2.5*24*(1 - (23/24)^2) = 4.90, and v(2) = 9.90 m/s. The instantaneous values 5 and 10 are within 2%. Confidence: high.
- Size, in car axes relative to the taillight midpoint at t=1. Extremes come from (a) 3D tracked features and (b) radial silhouette extremes about VP_u with kinematic depth:
  - rear -0.23 m (centre-bottom diffuser)
  - nose +4.05..4.07 m (from early frames; the late frames see only the hood)
  - So L = 4.30 * 1.006 = 4.33 m. A scaled real LaFerrari (4.70 * 0.925) gives 4.35. Confidence: medium-high.
  - Width: the body is about +-0.92 m (1.84), the mirrors +-0.95 m (1.91). The grey slab parts behind the rear wheels (part of the model, moving with the car) reach +-1.08..1.11 m, so the full AABB is ~2.21. Answered 2.17, hedged slightly toward the without-slabs case. Confidence: medium, because it depends on whether the slabs are in the GT bbox.
  - Height: roof top ~ +0.43. Ground = front hub (-0.338) minus tire radius 0.28-0.30, i.e. -0.62..-0.64. That gives H ~ 1.05-1.07. A scaled real LaFerrari gives 1.03. Answered 1.05. Confidence: medium-high.
- Wheelbase 2.43 m and taillight spacing 1.43 m are consistent with a model at ~0.92-0.93 scale of a real LaFerrari.
