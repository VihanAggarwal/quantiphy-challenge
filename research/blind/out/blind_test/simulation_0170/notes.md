# simulation_0170 — astronaut drifting toward the camera (S3SS, 24 fps, 80 frames, 1920x1080)

## What the scene shows
- The camera does not move. The moon limb on the left stays put. There are symmetric black letterbox bars at rows 0-85 and 994-1079,
  so the principal point is taken as (960,540). The astronaut's head is clipped by the top bar from frame 74 on.
- The astronaut starts at about (1652,785) and ends at about (980,290). Its image size grows about 2.19x. It also turns slightly:
  the in-plane tilt goes from -18 deg to -31 deg.

## Method
1. Mask: threshold on a blurred greyscale image (20/40/80), a morphological close, then the largest component (overlays checked).
   For each frame I took the bbox height H, the PCA body length L, sqrt(area), and centroids. I also tracked a point with SIFT similarity
   transforms, both chained frame to frame and directly against reference frames, to get a scale and a fixed body point.
2. Motion model: a straight 3D line with Blender Bezier easing, P(n) = P0 + s(n/79)*D, where s = smoothstep (3x^2-2x^3).
   - Depth progress 1/size matches smoothstep over frames 0..79. A fitted Bezier handle fraction h of 0.32-0.35 rules out 0.39.
   - Local fits at the start (scale and displacement against frame 0) give motion starting at frame 0 (a ~ 0..-0.25). Local fits at the
     end give motion stopping at frame 79.
   - Depth ratio rho' = Dz/Z0 = -0.5425 +- 0.007. Independent routes agree: chained SIFT scale -0.543, L -0.539, image-track
     perspective fit -0.540..-0.545, start-local scale -0.5425, end-local scale -0.535.
3. Scale: Z(n) = Z24*q(n). Lateral X = (u-cx)Z/f with f = H24*Z24/2.2, where H24 ~ 260 px (vertical extent at 1 s, height prior 2.2 m).
   The depth anchor 23.137 m is used as the Euclidean range (as documented), which gives Z24 = 22.49 m and f ~ 2657 px
   (HFOV ~39.7 deg). That f is close to the Blender default 50 mm/36 mm (2667 px), which supports the range convention.
   The Z convention would give f = 2734 and make every answer +2.2%.
4. Result: D = (-6.53, -3.53, -13.86) m, |D| = 15.72 m over 79 frames. Speed = backward difference |P(n)-P(n-1)|*24 at n = 24t.
   Acceleration = (v(n)-v(n-1))*24, reported as a magnitude.

## Answers (range convention; Z convention in brackets)
| qid | quantity | value | [Z conv] |
|---|---|---|---|
| 1399 | v(0.5 s) | 3.56 m/s | 3.64 |
| 1400 | a(0.5 s) | 6.28 m/s^2 | 6.42 |
| 1401 | v(1 s) | 5.99 m/s | 6.12 |
| 1402 | a(1 s) | 3.64 m/s^2 | 3.72 |
| 1403 | v(2 s) | 6.87 m/s | 7.02 |
| 1404 | a(2 s) | 1.65 m/s^2 | 1.69 (sensitive to the difference convention: a central difference gives ~1.76) |
| 1405 | v(3 s) | 2.46 m/s | 2.52 |
| 1406 | a(3 s) | 6.94 m/s^2 | 7.10 |

A model-free check (per-frame 3D from scale and track, local cubic fits) gave v = 3.9/6.1/6.8/2.4 and a = 6-6.6/3.1-3.4/1.5-2.3/6.9-7.7,
which agrees within its noise.

## Confidence
- Speeds at 1 s and 2 s: high (+-3%).
- Speeds at 0.5 s and 3 s: medium-high. They depend on the frame-index convention: if t maps to video frame 24t-1, they would be about 10% lower.
- Accelerations at 0.5 s, 1 s and 3 s: medium-high.
- Acceleration at 2 s: medium. It is close to the zero crossing, so it is sensitive to the difference convention.
