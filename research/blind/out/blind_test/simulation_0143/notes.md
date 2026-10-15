# simulation_0143 — notes

Static camera (background composite from frames 0 and 99 subtracts cleanly). 1920x1080, 24 fps, 100 frames.

## Camera geometry
- 5 longitudinal floor joints fitted to sub-pixel accuracy (rms 0.4-0.7 px). They meet at VP (959.6, 539.4), which is the image centre.
  Transverse joints are exactly horizontal. So pitch, roll and yaw are all 0 relative to the floor grid.
- Longitudinal joint spacing: d(dx/dy) = 0.7068, so s_across = 0.7068*H.
- Transverse joint rows: 1064.1, 1003.1, 955.0, 915.9, 883.4, 856.5. Spacing in 1/(y-vy) is 2.497e-4, so s_along = 2.497e-4*f*H.
- Man silhouette: head top sub-pixel track, foot-contact plateaus (stance foot dark with reflection directly below).
  At mid-stance (head peaks), (y_contact-vy)/(vy-y_top) = 2.504 +/- 0.013 (7 steps). With the man at 1.8 m
  (head-top peak about 1.79), the camera height is H = 1.278 m. This does not depend on f.

## Inconsistency found
- With depth_info, K = Z*(vy - y_top) is 883.7 at t=0 and 886.1 at t=0.5. This is self-consistent and best matches
  optical-axis Z. It implies f ~ 1724 px.
- But with f = 1724, consecutive planted footprints are 1.1-1.6 m apart (1.5 m at a double-support frame) for a man whose
  hip is 0.88 m high and who bobs only 5 cm. Legs of about 1.15 m would be needed, which is anatomically impossible.
  The stance feet are planted (contact rows stable to +/-1 px for 12 frames), so the feet are not sliding.
- Anatomy (step about 0.85 m, natural 1.4-1.6 m/s at a cadence of 1.94 steps/s) gives f ~ 900-1000.
  A 3:1 tile gives f = 943, and an 18 mm lens gives 960. Used f = 955 (HFOV ~ 90 deg).
- With that f, the depth_info is about 1.83x the image-consistent depth (Z0 ~ 3.96 m against the given 7.21 m).
  Following "the prior is exactly true", answers are in prior-consistent world units.
  Under a depth-units hypothesis, the speeds would be about 1.8x larger (~2.5 / 2.8 m/s).

## Answers
- 1382 tile: across 0.903 m (bold joints), along 0.305 m (faint joints). The tile is a 3:1 rectangle, probably 0.9 x 0.3.
  Answered 0.9 (the prominent side). Confidence low: the GT could be the short side 0.3, or 0.55 in depth units.
- 1383 v(1s): mid-stance pelvis positions (head-peak depth plus footprint average), 2-step mean speed 1.42 m/s.
  Mid-stance speed dip corrected by about -0.07, giving 1.35 m/s. Confidence medium (world-vs-depth unit ambiguity).
- 1384 v(2s): 2-step mean 1.56 m/s, mid-stance dip gives 1.52 m/s. Confidence medium.
- 1385 a(2.5s): the trend acceleration is only ~0.02 m/s^2. Frame 59-60 falls in the early-stance deceleration phase
  (heel strike at frame 56, mid-stance at 61.9). Instantaneous |d|v|/dt| with a +/-0.10 m/s gait speed oscillation
  is about 1.2 m/s^2. Answered 1.2. Confidence low.

Scripts: work/*.py (floor.py, vp.py, trans.py, man.py, track.py, contact.py, traj.py, world.py, final.py).
