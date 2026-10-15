# simulation_0025 — notes

Video: 960x960, 75 frames, 24 fps, static camera. Beach scene: person walking right->left near the shoreline
(x 560->522 px, feet y 580->591), eagle flying left->right across the frame (x 234->954, y ~370-395), exits at frame 66.

## Measurements (code: work/*.py)
- Background = per-pixel median of all frames (clean). Masks by |frame - median|.
- Person: torso centroid, shirt top, feet bottom tracked every frame. Image velocity (linear fit, 75 frames):
  (-12.65, +3.30) px/s, |v| = 13.08 px/s, residual 0.4 px. Feet are planted (stance foot stays within 0.4 px for
  ~12 frames; stride 19 px per 35-frame gait cycle = body displacement) -> natural gait, uniform translation.
  Apparent size constant (height change -0.3+-0.3 px/s) -> motion perpendicular to the line of sight,
  consistent with depth_info (114.8319 -> 114.8356 m).
- Person bbox height (head top to feet) 53.5 +- 1 px.
- Eagle: dark-pixel mask; flap period ~25.2 frames (1.05 s). De-flapped track fitted with a perspective
  (Mobius) + Fourier model. Max tip-to-tip horizontal extent 50-53 px (frames 34, 42, 60, 61).

## Scale (hypothesis A, used for answers.json): prior is exact
- 1.3 m/s = |3D displacement| per s of the person (back-projected at R=114.83 m) -> f = 1150.7 px (HFOV 45.3 deg).
- Person height = 53.5 px * Z(114.4 m)/f = 5.32 m (54 px -> 5.37).
- Eagle: 3D positions from image rays + ranges at t=1,2 s; speed profile from track: 29.6 (t=0) 28.7 27.8 (t=1) 27.0 26.1 (t=2) m/s;
  backward difference at t=1 s = 27.8 m/s (uniform chord t=1..2 would be 27.0).
- Wingspan: max tip-to-tip extent * Z/f = 4.6-4.9 m -> 4.8 m. Length not visible (eagle seen front-on) -> 0.43 x span = 2.05 m.

## WARNING — strong inconsistency found (hypothesis B)
- The eagle's image track has a perspective curvature c = -0.058..-0.064 /s (many subsets, model-free
  same-phase triplets give median -0.060). With the given eagle ranges, a uniformly moving eagle requires
  f >= ~2500 px (c = -0.0627 at f=inf, -0.065 at f=3450). f = 1150 needs c = -0.083 (rms 4.4 px vs 1.8 px),
  i.e. A is only possible if the eagle decelerates ~5%/s (1.7 m/s^2).
- Under A everything is ~2.9x real size (5.3 m person, 4.8 m eagle) and the person's gait (stride 0.36 h, 1.46 s cycle)
  is a slow stroll, which for a normal 1.8 m human is 0.44 m/s, not 1.3.
- Hypothesis B (prior 1.3 m/s is a nominal/wrong value, eagle uniform, f from a 1.78 m human, f ~3440 px):
  eagle speed 11.8 m/s, length ~0.72 m, wingspan ~1.65 m, person height ~1.79 m.
  (f=3000: 12.9 m/s, 0.8 m, 1.85 m, 2.05 m.)
- Chose A because the task facts state priors are exact and scenes may be arbitrarily scaled; B values are 0.34x of A.

## Confidence
- If A holds: height 5.35 (+-4%), eagle speed 27.8 (+-5%), wingspan 4.8 (+-8%), length 2.05 (+-20%, proportion-based).
- Overall low-moderate: the A/B ambiguity (factor ~3) dominates.
