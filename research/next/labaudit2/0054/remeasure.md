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

---

# Independent second measurer (m2_indep): qids 2863, 2840, 2862, 2847

I wrote this section without reading any other 0054 notes. My scripts and outputs are in `research/next/labaudit2/0054/m2_indep/`.

## Scene and timing
- "Pink ball" and "white ball" are the same object: a pale pink/white ball about the size of a tennis ball. Only two small balls appear (it and the yellow-green tennis ball), and the question templates use both names (2842 vs 2854).
  - Renders a/as/ax share labels, so 2840 and 2863 should equal the as-row label for the white ball at 1.5 s.
- The juggler tosses both balls toward camera a. They fall down-left and bounce on the carpet, then rise toward the seated person.
- Dropped capture frames are c12 and c37:
  - The basketball steps 31 px between video 11 and 12, against 17 px for its other steps.
  - Both small balls take about twice their usual step between video 35 and 36.
  - Mapping: capture c = floor(i*25/24 + 0.5), so video 36 = c38, video 37 = c39, video 38 = c40.
  - Check: a ballistic fit on video 23..35 predicts the video-36 position, taken as c38, to within 2-3 px.
- t = 1.5 s is c37.5:
  - **A** = c38->c39 (video 36->37). This is what rounding half-up, banker's rounding and labnoise `treal` all give.
  - **B** = c37->c38 (floor rounding). c37 is not in the video.

## Method
- Tracks came from two routes that agree to 2-3 px: SAM mask centroids in ax (alpha-weighted), and background-difference centroids in a.
- 3D: a ballistic fit with g = 9.8 on the capture clock, using f = 711, the principal point at the image centre, and the gravity direction from the vertical vanishing point (camera pitch 0.9 deg, roll 0.7 deg).
  - The fit is anchored to the depth_info ranges at c25 (white 3.0735, green 3.039), with the ball radius added to get the centre.
  - Fit residuals are 0.8 px rms.
- Cross-checks:
  - A gravity-only fit with no ToF anchor gives a white c25 range of 3.09, against 3.11 from the anchor. This supports f = 711 and the 25 fps clock.
  - The bounce frames match: white bounces at c39.8, observed in video 38; green at c38.8, observed in video 37.
  - Camera height from the bounces is 0.915-0.935 m. The basketball gives 0.92-0.94 m.
  - Varying f from 700 to 722, freeing the gravity direction (2.7 deg change), or dropping the hand-held points changes the speeds by 1-2%.

## Results
| qid | quantity | label-style A (c38->c39) | label-style B (c37->c38) | physical at t=1.5 s (c37.5) | camera-b cross-check | **best** |
|---|---|---|---|---|---|---|
| 2840 (a), 2863 (ax) | pink (= white) ball v at 1.5 s | 4.94 (fit chord); 4.97 from clicks (0.85-1.0 px fit residuals); 5.0-5.3 if the click is at the streak-extent midpoint | 4.45-4.6 | 4.58 (4.77 at c38) | 4.24 phys / 4.60 chord A | **4.85 m/s** |
| 2862 (ax) | green ball v at 1.5 s | **3.0-3.5, central 3.3**: the ball bounces at c38.8, inside the c38->c39 step, so the c39 click (340, 657) sits near the floor. Up to about 4.0 if ToF reads the floor just behind the ball. The ballistic chord without the bounce would be 5.2. | 4.7-4.9 | 4.85 (4.71 gravity-only) | 4.54 phys | **3.5 m/s** (choice depends on the convention; 4.8 under B) |
| 2847 (as) | white ball diameter | - | - | blurred-disk model fit on the real a render at apex frames v26-29: 16.8-17.2 px at Z = 2.91-2.66 m, giving 6.85, 6.72, 6.58, 6.44 (mean 6.65 cm) | the green tennis ball in the same frames and method gives 6.50 (the stated tennis ball is 6.7); the white/green pixel-size ratio is 0.95-1.0 at equal depth | **6.7 cm** |

## Notes
- Answers of 5.9-6.7 m/s for pink are not supported by the physics. At impact the vertical speed is about 4.9 m/s and the horizontal speed about 2.1 m/s, while the ball is still above the floor. Labels that large would need a ToF miss, such as background depth read at a blurred click.
- Expected credit over the A/B convention, with p(A) = 0.65:
  - white: 4.8-4.85 is best, scoring about 0.97 whichever convention holds;
  - green: 3.5 is best (about 0.87); 4.0 scores about 0.81 and 4.8 about 0.73.
- The t=0.5 basketball range (2.3557) is inconclusive about the convention. A floor-plane prediction gives c12 +12 cm, c13 +6 cm and c14 -1 cm, and it is sensitive to pitch and principal point at the ±4 cm level.
- Camera b (bx tracks, free gravity direction, b anchors 1.235 and 1.331) gives speeds about 7% lower. It is less reliable: the balls overlap and are blurred in the masks, and the gravity-only fit puts it 12% off its own anchors.
