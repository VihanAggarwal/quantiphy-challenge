# simulation_0025 — eagle + walking person on a beach (V3MC)

## Setup
- 960x960, 75 frames, 24 fps. The camera is static (phase correlation on the cliffs shows < 0.03 px drift).
- Scripts are in work/: track.py, person*.py, feet.py, planted.py, eagle_seg.py, eagle_fit*.py, final.py.

## Key observations
- Person: mostly frontal view, centroid x 560 -> 522 (-12.5 px/s), feet y 580.5 -> 590.5 (+3.4 px/s), height ~52.6 px.
  Gait stride is 35.5 frames (1.48 s).
- Planted feet: each stance foot stays fixed in x and y for about 12-15 frames. The footprints step down the image
  (582.1 -> 583.6 -> ~585.5 -> 589.3), and the person stays upright (no lean). So the person really walks on a
  horizontal plane toward the camera, heading slightly left, with no sliding.
  => The constant human distance (114.83 m at t=1 and t=2) cannot be the pelvis distance. It behaves like a
  static armature origin, so it is used only as the distance scale (person at about 113 m mid-video).
- Lateral-only motion (f ~ 1150 px, a 5.2 m giant) is ruled out: descending footprints with an upright body
  are impossible for a sideways walk at constant depth.
- Speed prior 1.3 m/s = sqrt(v_r^2 + v_x^2), with v_x = 13.1 px/s * D / f and v_r = 3.4 px/s * D / (y_feet - y_horizon).
  This requires horizon y <= ~286. The sky/cliff-top line (y 250-290) suggests a horizon near y 250-285,
  which gives f in about [2100, 4500]. Measured looming (0.5-1 %/s) is too noisy to narrow this down.
  The step-width alternation of the footprints (3.5 px vs a 9 px mean advance) implies a step width of
  0.12-0.15 m for f 3000-3700, which is consistent.
- Final focal length: f ~ 3435 px (HFOV ~16 deg). It is pinned by a realistic human height (~1.76 m) and is
  consistent with the eagle-size prior and the geometry. Horizon ~y 267, camera ~10 m above the beach.
- Eagle: fit x(t) = (a+bt)/(1+dt) plus wing-beat harmonics (period 25.5 frames). The best-fit d = -0.060/s
  matches the depth info (116.05 -> 108.28 gives -0.063/s), so the eagle moves at constant velocity.

## Answers
- 1109 eagle speed at 1 s: 3D positions from the smoothed image track and the ranges at t=1 and t=2.
  v = (8.5, 0.1, -8.1) m/s, |v| = 11.8 m/s. Sensitivity: f 3000 -> 12.8, f 4000 -> 10.9. Confidence: medium.
- 1111 wingspan: the widest projected span per wing-beat cycle (45-52 px) gives a projected span of
  1.56-1.60 m at f 3435. The view-angle correction is uncertain: 2.2-2.4 m if the eagle faces its velocity,
  1.65 m if it faces the camera. Answer 2.05 m. Confidence: low-medium.
- 1110 length: not separable in the image. Taken as ~0.43 x wingspan (eagle proportions) -> 0.87 m. Confidence: low.
- 1112 person height: 53.5 px standing-equivalent * 113 m / 3435 px = 1.76 m. Confidence: medium
  (it depends on the focal-length choice; the alternative giant-scale reading is ruled out above).
