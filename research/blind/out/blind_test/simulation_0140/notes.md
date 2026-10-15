# simulation_0140 - bird flying across a courtyard; facade with "BE DIFFERENT" sign

## Scene
- Static camera, 1920x1080, 24 fps, 100 frames. The front facade is frontal: window rows stay level to within 1 px across the image,
  and the left-wall window edges give a consistent vanishing geometry with cx ~ 960.
- The bird (a duck) comes out of a lit window on the LEFT wall. In frames 0-5 it is clipped at the window's left edge (x ~ 192),
  which shows the wall is real 3D geometry. It then flies an arc to the right.

## Bird track
- Background = per-pixel median of all frames. Bird mask = |frame - bg| > 18, keep the largest blob; centroid per frame. Overlays checked.
- The track fits a circle traversed at constant angular speed (rms 4 px): R = 1094 px, 21.1 deg/s, pixel speed ~402 px/s.
  Speed shows no trend along the path (< 0.4 %/s), which points to constant depth Z.
- Positions: t=0 is (209, 871). The bird is still behind the wall here, so this is extrapolated; it matches the visible beak tip to within 2 px.
  t=0.5 is (334, 715).

## Focal length
- Bird route: Euclidean depths 25.328 and 24.899 m with constant Z. Solving f^2 = (r0^2 - rho*r1^2)/(rho-1) with rho = (25.328/24.899)^2
  gives f = 2610-2660 px (several fits, robust to a +-1 frame time offset). Z_bird = 24.18 m.
- Window route: front-window opening ~120.5 x 164.5 px. If the opening were exactly 1.48 m wide at Z = 34.37, f would be 2790.
  The frame is recessed (~0.7 m from parallax) and probably narrower than the opening, so 2790 is an upper bound.
- Blender default 50 mm lens gives 2667. Also, a path radius of exactly 10 m would need f = 2647.
- Adopted f = 2640 px (HFOV ~40 deg).

## Answers
- 1502 window height: opening ratio 164.5/120.5 x 1.48 = 2.02. Frame height through f: 2.05-2.14. Answer 2.05 m (medium).
- 1503/1504 sign: letter extents 695 x 81 px (640.6-1335.6, 270.5-352). Plane Z ~ 34.3 m (34.5 Euclidean, near the axis).
  Width = 695 x 34.3 / 2640 = 9.03 m; height = 81 x 34.3 / 2640 = 1.05 m (medium; scales with 1/f).
- 1505 distance from the path plane to the wall: 34.37 - 24.18 = 10.2 m (medium-high).
- 1506 path length: 402.5 px/s x 99/24 s x (24.18/2640) = 15.2 m (medium; scales with 1/f).
- 1507 speed at 1.0 s: ~404 px/s x 0.009159 = 3.70 m/s (medium).
