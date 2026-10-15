# simulation_0310 - forklift driving away (S3SC, 24 fps, 2560x1440, 72 frames)

## Method
- The camera is static (the background median is stable). The forklift translates in a straight line toward the upper left, forks first.
  It does not rotate, and its wheels do not spin, so all features are rigid. It is at rest at frame 0 and then moves with constant acceleration.
- Calibration (principal point at the image centre):
  - LSD segments on the forklift from 37 frames, fitted with three orthogonal (Manhattan) directions.
  - Result: f = 3598 px (bootstrap sd 10), pitch 22.85 deg, roll ~0, body heading 131.0 deg.
  - Fits that leave out one direction class give f = 3513-3591.
  - Two-vanishing-point checks give f = 3589-3659.
  - The convergence of the LK tracks (motion VP at (-2125,-850)) lies on the fitted horizon.
  - Final f = 3556 px (a 50 mm lens on a 36 mm sensor) is inside that range. f = 3500 and f = 3600 change the answers by about 1-2%.
- Structure from motion for a rigidly translating object, using 174 LK tracks: Schur-complement least squares for the per-frame displacement s(t) and the 3D points.
  The motion direction is constrained to the horizon. Reprojection rms is 1.3 px.
- s(t) has a constant second difference, so the acceleration is constant. A quadratic fit to frames 1-71 is used for the backward differences.
- Keypoints (fork tips, roof strip ends, mast top) were LK-tracked and triangulated over all frames.
  In normalised units: fork tips to rear face 0.4802, roof top to ground (fork top minus 5 cm) 0.2717,
  outer tire faces to the centreline (from the roof strip, mast and rear reflector) 0.0856 half-width.
- Scale (sigma, m per unit), three routes:
  - height prior 2.47 m: 9.09
  - Z-depth to the bbox-centre origin: 9.18 / 9.22
  - Euclidean depth to the bbox-centre origin: 9.10 / 9.22
  - Used: sigma = 9.15.
- Cross-check: rays plus the label depth at t=1 give a 3.11-3.14 m displacement between t=1 and t=2 for a centre origin. This matches 9.15 x 0.3425 = 3.13 m.
- Depth convention: Z-depth is more self-consistent than Euclidean, but the depth difference d2-d1 is too sensitive to discriminate reliably.

## Answers
- v(1.0) = 2.04 m/s (backward difference at frame 24)
- v(2.0) = 4.14 m/s
- a(1.0) = 2.10 m/s^2 (constant)
- length (fork tips to rear) = 4.39 m
- width (outer tire to outer tire) = 1.57 m

## Confidence
- Speeds and acceleration: about +-4%. The main risks are scale (choice of origin, fork thickness) and f.
- Length: about +-3%.
- Width: about +-6%, because of the centreline choice. The fork midpoint would give 1.67 m.
