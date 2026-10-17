# 0010 pendulum: independent re-measurement (second measurer)

qids: 2194 (0010 v@0.6), 2206 (0010X v@0.6), 2196 / 2202 / 2208 (0010 / 0010s / 0010X a@0.6).
All three renders show one event, so they share labels: one velocity value and one acceleration value.
I did not read the other measurer's notes. My scripts are in `remeasure_b/`.

## Data
- Red ball on a string held by a hand. It swings mostly toward and away from the camera, with a period of about 1.21 s.
- Track: I used the HSV red mask on the green-screen render (0010s), which is clean. The original clip's mask picks up
  orange carpet stains, and the X render masks the ball white from frame 12 on. The track gives the centroid u,v and
  an ellipse per frame (`measure.py`, `ballfit.json`).
- Dropped frames: polynomial residual test (`fit residual 0.39 px vs ~1.9`). One drop is clearly between video frames
  35 and 36. The other is between 10/11 and 11/12. So CAP(j) = j + (j>=12) + (j>=36), and capture frames 15, 16, 17
  are video frames 14, 15, 16 under either choice for the first drop.
- Pivot: the top of the string (hand) stays at about (638, 229) px, give or take a few px.

## Models
1. Dynamic spherical pendulum (`dyn.py`, `fitdyn*.py`, `profile_dt.py`): RK4 with g = 9.8, a pivot on the hand ray
   with linear drift, damping, and a pivot-pixel prior. It is fitted to all 49 image centroids, with or without the 6
   ToF anchors. Image rms is 1.07 px.
   - Image-only fit: pivot range 1.49 m, L (pivot to ball centre) 0.339 m. It predicts the 6 anchor ranges within
     3.6 cm rms, with nothing tuned to the anchors.
   - Anchored fits: L = 0.336 m, turning angle about 47 deg, camera tilt about 24 deg.
   - Near turning point: capture frame 18.0, which is 0.722 s on the video-mapped clock.
2. Ray-sphere geometry (`routeB.py`): pivot depth and L come from the anchors (L = 0.35, pivot range 1.51). Depth comes
   from intersecting each ball ray with the sphere. This route is ill-conditioned near frames 12-14 because those rays
   are nearly tangent to the sphere.
3. Sinusoid fitted to the anchors only: range = 1.576 - 0.258 cos(5.197 (t - t0)), T = 1.209 s. t0 is 0.683-0.713
   depending on how the half-frame times are rounded.

## Timing finding (matters for velocity)
The ToF anchors fit best when the depth labelled "t" equals the ball state at model time t + 0.03 to 0.045 s
(profile over offsets: anchor rms 2.8 cm at offset 0, 0.9-1.4 cm at offset 0.03-0.045). At t = 0.6 the residual drops
from +2.3 cm at offset 0 to +0.2 cm at offset 0.04. So the label's depth at "frame 15" looks like the ball one capture
frame later (model 0.64 s). Two explanations fit equally well:
- the label clock is one frame behind my video mapping;
- the depth stream lags the RGB by one frame.

Both give almost the same answer.

## Label-style forward differences (depth at the clicked surface, 25 fps)
| offset type | v(0.6) = abs(P16 - P15) * 25 | a = (v16 - v15) * 25 | vector second difference |
|---|---|---|---|
| none (sync) | 0.70 | -6.7 | 6.8 |
| clock +0.04 | 0.43 | -7.0 | 7.0 |
| depth-only +0.04 | 0.45 | -6.2 | 6.8 |
| clock +0.03 | 0.50 | -7.0 | 7.0 |

Second route (sinusoid range from the anchors, turning time from the video, image lateral steps):
- v = 0.44 at offset +1 frame, 0.70 when synchronous;
- a = 7.5 at offset +1 frame (range part 6.8), 6.6 when synchronous.

Route B (ray-sphere): v 0.67-0.78, a 6.2-8.0 at offset 0. It is sensitive to the pivot position.

Physical values from the anchored dynamic fit:
- at model 0.60 s: speed 0.83 m/s, abs(a) 6.45 (tangential 6.1);
- at model 0.64 s: speed 0.57, abs(a) 6.8.

## Answers
- 2194, 2206 (v at 0.6 s): **0.44 m/s**. The anchor-supported one-frame offset gives 0.43-0.45 (0.50 at a 0.03 s
  offset). With synchronous depth it would be 0.70. Physical speed at 0.6 is 0.83. Confidence: medium.
- 2196, 2202, 2208 (a at 0.6 s): **6.8 m/s^2**, as a magnitude. The ball is decelerating into the near turning point,
  so a scalar speed difference would be negative. Every route and offset gives 6.2-7.5. Physical value is 6.4-6.8,
  and g sin(47 deg) = 7.2 at the turning point. Confidence: low to medium. A one-frame-step second difference of
  hand-clicked ToF points carries noise of several m/s^2, and the sign and smoothing conventions are unknown.
  The noise-free value is robust, though; it does not depend on the timing offset.
