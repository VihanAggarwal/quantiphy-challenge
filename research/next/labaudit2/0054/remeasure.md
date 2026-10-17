# 0054 independent re-measure (second measurer): qid 2852

Scope: qid 2852, captured_0054as, "velocity of the white ball at 1.5s in m/s" (current 4.748).
I did not read the other measurer's notes or files in research/next/labaudit*/0054/. I used no labels.
My scripts and frames are in `rm2852/` (scripts/seg.py, orange.py, track_a.py, vp.py, ballfit.py, lm.py, final.py,
boot.py, route2.py, sizes.py, tennis_check.py, orange_size.py). Large arrays went to the session scratchpad, not here.

## Result
| quantity | m/s |
|---|---|
| physical instantaneous speed at t=1.50 s | 4.65 (4.58-4.69) |
| label style, capture 38->39 (= video 36->37; t=1.5 s -> video frame 36 -> capture 38) | 4.97-5.00 |
| label style, capture 37->38 (capture 37 is the dropped frame) | 4.62-4.65 |
| **recommended** | **4.85** (within 5% of both conventions) |

At t=1.5 s the velocity is V = (-0.70, +4.07 down, -2.1 toward the camera) m/s.
Most of the speed is the fall. The ball bounces on the floor at about capture 40 (video 38).

## Clip and renders
- a, as and ax are pixel-aligned: the best shift in the person region is (0, 0) px. Tracking uses the ax
  green-screen masks, which I checked against the original background difference and the as render (f36_detail.png).
- The pale "white" ball (pinkish grey) and the yellow tennis ball are thrown together at about video 22-23.
  They fly toward the camera and to the left, then bounce near the seated person at video 37-38. The a-render
  rows call this pale ball "pink ball".

## Clock
- Orange-ball steps: 15.5, 15.7, **33.1**, 17.8, 18.4 px at video 10->13. Steps for the white and tennis balls are
  normal until video 35->36, which is a double step (vertical 114 px against 43 and 75).
- So capture c = k + (k>=12) + (k>=36). The dropped capture frames are 12 and 37.
- A ballistic fit without the second drop has 5.7 px rms; with it, 0.7 px.
- t=1.0 s is capture 25 (video 24), the anchor frame. t=1.5 s is capture 37.5:
  - capture 38 (video 36) under the treal / rounding convention;
  - capture 37 (dropped from the video) under truncation.

## Geometry
- f = 711 px, principal point at the image centre. The orthogonal wall/baseboard vanishing points give f = 708.
  With f = 770 the fixed-pitch fits get worse (rms 1.3-1.5 px against 0.7).
- Horizon at y about 329, so the camera pitches down about 2.5 deg, with roll about -0.6 deg. The tennis-ball fit
  gives pitch -0.1 deg and roll -1.1 deg. Results barely depend on pitch (see the table below).

## Route 1: 3D ballistic fit anchored by ToF (ballfit.py, final.py)
- Model: P(t) = A + V t + g t^2/2, with |g| = 9.81 and the gravity direction set by camera pitch and roll. I fit the
  pixel centroids of the white ball at capture 24-39 (video 23-37; the bounce is at c40). The centre range at
  capture 25 is anchored to 3.0735 + 0.033 m.
- Residuals are random, all within 1.5 px (rms 0.68 px).
- Over pitch (free / 1 / 2.5 / tennis value) and f (708, 711, 722):
  - c37->38: 4.56-4.65;
  - c38->39: 4.90-5.00;
  - clicked-point version (observed pixels at video 36 and 37, fitted surface ranges): 4.96-4.99.
- Bootstrap (1 px pixel noise, 4 cm anchor noise): c37->38 4.655 +- 0.04, c38->39 5.009 +- 0.04.

## Route 2: gravity-only scale, no ToF input (route2.py)
- The same fit without the anchor puts the range at capture 25 at 3.01-3.24 m. ToF gives 3.107 m for the centre.
- Speeds: c37->38 4.57-4.71, c38->39 4.93-5.05.

## Cross-checks
- The tennis ball's own fit (c24-38, anchor 3.039 + 0.0335) has rms 0.30 px. Without the anchor its range at
  capture 25 is 3.027 m against ToF 3.07 m (1.4%). It gives V(1.5) = (-1.13, 4.30, -1.98), |V| 4.87, so the two
  balls fly alike.
- The fitted white-ball centre at the bounce is 0.81 m below the camera axis at Z 1.86 m, so the floor is about
  0.84 m down. The standing person's feet (y about 535 at Z about 3.5 m) put the floor about 0.86 m down.
- Apparent size from the mask's minor width agrees with the fit for capture 24-36 to about 10%. Later streaks are
  faint and their masks are too narrow, so I did not use size there.
- Orange prior v(0.5) = 2.21: my smooth estimate is about 1.8 m/s, which means about 1 m/s of radial click/ToF
  noise per forward step. Expect the label of this row to be noisy at the 10-20% level whichever convention is used.

## Confidence
Medium. The geometry is solid: two scale routes agree within 2% and the residuals are about 0.7 px. The open
questions are the time convention (c37 or c38, worth 7%) and ToF noise on a small, fast, motion-blurred ball.
