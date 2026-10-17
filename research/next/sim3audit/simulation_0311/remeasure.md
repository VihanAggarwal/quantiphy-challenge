# simulation_0311: independent remeasure of qids 1493 and 1494 (car speed at 1.0 s and 2.0 s)

Second measurer. I did not read the other measurer's files in this folder.
My scripts and scratch files are in `remeasure_work/` (about 33 MB; no frame dumps).

## What the clip shows
The scene is a red LaFerrari on a snowy road. The camera is fixed and placed high (pitch about 20.7 deg, roll about 0). The video is 2560x1440, 24 fps, 72 frames. Frame 0 is a held frame (identical to frame 1).

The car moves by pure translation: 392 KLT tracks are straight lines (median perpendicular rms 0.2 px). They meet at the motion vanishing point VP_D = (-1151, -886) +- (12, 9).

### Motion law (exact under projection)
For a point on a translating rigid body, 1/|x - VP_D| is affine in the displacement s.
I fitted s(k) jointly by ALS over 355 tracks (`s3_profile.py`, residual 6e-4 in s units).
- **s(k) is linear.** The per-frame step is 0.0418 at frame 8 and 0.0415 at frame 71, so the speed is constant to better than 1%. The car does not accelerate.
- Independent check: 1/(taillight pixel separation) increases linearly. The increments are 0.026 per frame throughout.
- The same pipeline on sibling **simulation_0300** (`sib0300_*`) gives steps proportional to (2k - 1). That is s ∝ k^2 from rest at index 0, which is the a = 5 m/s^2 law.
- So the 0311 render does **not** show the scripted motion of 0300/0301.

## Route H1: the render's own constant speed V, scaled with the clip's prior H = 1.15 m
Calibration:
- The lateral VP comes from the two round tail-lamp centres tracked over frames 31-71: VP_L = (9726, -871) +- 82 px.
- Orthogonality with VP_D gives f = 4240 px (4207-4272). That is HFOV 33.6 deg, consistent with a 60 mm lens.
- Projected wheel circles in the D-U plane line up with the rim ellipses, which validates D, U and f (`wheelcircles.png`).

Motion stereo (`recon.py`): every point is triangulated in units of V x 1 s.
- Wheelbase (both Ferrari hub badges tracked): 0.4456. This does not depend on f.
- Hub height relative to the tail-lamp midpoint: -0.065 for both axles.
- Tyre radius from radial edge profiles: about 0.060 (rear) and 0.058 (front). So the ground is at -0.124 +- 0.004.
- Roof front-edge contour (epipolar-matched dark-roof/red-hood boundary): up to +0.058 to +0.061. Side-window top edge: +0.05. The roof crest is about +0.060 to +0.066.
- H_u = 0.184-0.190, so **V = 1.15 / H_u = 6.05-6.25 m/s**.
- Cross-check: H/WB = 0.413, which matches a real LaFerrari (1.116 / 2.65 = 0.421). Real proportions scaled to H = 1.15 give WB = 2.73 m and V = 6.13 m/s.
- The tail-lamp separation is then about 1.62 m. The original agent assumed about 1.76-1.85 m per W, which is why its 6.7-6.8 is about 9% high.
- Under H1, the answer is **v(1) = v(2) = 6.15 m/s (+-4%)**.

## Problem: depth_info and the acceleration stated fact do not describe this render
- depth_info (17.8278 m at t = 1, 23.1989 m at t = 2) matches 0300/0301 to 4 decimals.
- In 0311, the tail lamps at frame 24 are 3.45-3.6 V-units from the camera. Their line of motion passes 2.4 V-units from the camera, and the range ratio over 1 s is at most 1.225 (it would need to be 1.301).
- Solving V^2(p^2 + A^2) = 17.83^2 and V^2(2A + 1) = 23.20^2 - 17.83^2 with p = 2.4 has **no real solution**, for any V, any clock offset, and any in-car origin. That holds for both the Euclidean and the Z convention.
- So the depth_info was not computed from this render. It was copied from the 0300 scene (accelerating from rest, a = 5).
- Qid 1497 (acceleration of the car at 1.0 s = 5.0, marked stated fact) also presumes the 0300 motion. The render's acceleration is about 0.
- **1493, 1494 and 1497 must be decided together.** If the annotation record was copied from 0300 (H2), then 1497 = 5 is right and the speeds are the 0300 values. If the labels come from this render (H1), then 1497 is about 0, which is not a usable relative-error label, and the speeds are 6.15.

## H2 values (0300 law s = 2.5 (i/24)^2, confirmed above)
| Clock convention | t = 1 s | t = 2 s |
|---|---|---|
| Backward difference, t = 1 at index 23 (favoured by both 0300 and 0301 agents' depth/origin checks) | 4.6875 | 9.6875 |
| Index 24 | 4.896 | 9.896 |
| Analytic | 5.0 | 10.0 |

## Answer and reasoning
I judge P(H2) at about 0.7-0.8:
- The copied depth_info shows that the annotation record was not computed from this render.
- The question template asks for a nonzero acceleration.
- The task treats 1497 = 5.0 as exact.

The break-even for t = 2 is p = 0.59.

| qid | answer | coverage |
|---|---|---|
| 1493 | **4.9** | Within 5% of 4.69, 4.90 and 5.0. About 20% from H1's 6.15. |
| 1494 | **9.79** | Within 2.2% of every H2 variant. 59% from H1. |

If the orchestrator rejects H2 (that is, it changes 1497 away from 5), use **6.15 / 6.15** instead.
Confidence: medium-low (the choice of hypothesis dominates). Within H1 the measurement is good to +-4%; within H2 it is good to +-2%.
