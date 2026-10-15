# simulation_0141 - man walking away down an arched corridor (static camera, 1920x1080, 24 fps, 60 frames)

## Geometry (all from code on the median/max background and per-frame masks)
- 4 longitudinal floor-grout lines fitted (rms < 0.4 px). Vanishing point (959.1, 540.4), which is essentially the image centre,
  so the camera is level and looks straight down the corridor. Horizon y_h = 540.4.
- Floor model: Z = K / (y - y_h), with K = f*Hc. Lateral position u = X/Hc = (x - 959.1)/(y - 540.4). Neither depends on f.
- Tile grid: longitudinal lines at u = -0.809, -0.099, 0.606, 1.318, so the lateral pitch is 0.709 Hc.
  Transverse lines at y = 1064.0, 1003.0, 955.0, 915.9: uniform 1/(y - y_h) spacing of 2.511e-4, so the pitch along Z is 2.511e-4 K.
- Foot plants (dark shoe pixels V<30, reflections excluded): R 1051.5, L 971.6, R 912.6, L 867.7, R 832.7.
  The step in 1/(y - y_h) is a uniform 3.661e-4, so step = 3.661e-4 K. The feet do not slide.
  Heel-offs at frames 4.7, 16.8, 29.5, 42.0 and 54.8 give a step period of 12.53 frames (0.522 s).
  Lateral position: right foot u = -0.548, left foot u = -0.659, so the path is straight and parallel to the corridor.
- K (scale): the prior speed taken as the average speed gives K = 2413. The depth difference (5.03 - 4.15 over 0.5 s, about 0.878 m in Z,
  i.e. 1.757 m/s) gives K = 2504. Used K ~ 2460 (+/- 2%).
  NOTE: the absolute depths (4.15 / 5.03) do not match the image. They would put the pelvis about 0.7 m behind the rear stance foot.
  They fit the image if they are shifted by about -10 to -12 frames in time, so only their difference is used.
- Walls: the left wall/floor edge is a radial line at u = -3.595 (detected over x = 0..500). The right boundary is the colonnade,
  whose inner column faces are at u = 2.42-2.48 (2.45 used). The man walks along the corridor centre line (-0.575).
- Man height ratio: head top / floor at the head's Z gives Hm/Hc = 1.404 at the top of the bob (mid-stance) and 1.352 at the bottom.
  The head bob is 0.048 Hc.

## Focal length / camera height (the main uncertainty)
f is not fixed by depth or speed, because everything they measure lies along Z. Two hypotheses were considered:
- Square tiles: f = 2824, Hc = 0.87 m, man 1.22 m. Rejected: the step/height ratio would be 0.74, which is impossible for a natural
  walk with planted feet. The bob/step ratio also fits normal-human gait better with larger Hc.
- Normal adult gait: step 0.88-0.92 m, so the man is about 1.8-1.87 m and f is about 1870-1950 (about a 35 mm lens, HFOV about 53 deg).
  Tiles then come out at about 0.62 x 0.92 m (3:2).
- Chosen: H = 1.82 m, so Hc = 1.296 m and f is about 1900.

## Answers
- 1508 height: 1.404 * Hc, about 1.82 m. Confidence medium-low (rests on a human-size/gait prior, about +/-7%).
- 1509 total distance: v_avg * duration. Candidates are 4.16 / 4.23 (1.693 m/s x 2.458 or 2.5 s) and 4.32 / 4.39 (1.757 m/s).
  Answered 4.26. Confidence high (within 5% of all candidates).
- 1510 tile side: along-corridor pitch 2.511e-4 * K = 0.62 m (f-free). The lateral pitch would be about 0.92 m if the "side" meant that.
  Confidence medium.
- 1511 left wall: (u_foot - (-3.595)) is 2.94-2.99 Hc, about 3.84 m. Confidence medium-low (scales with Hc).
- 1512 right wall (colonnade): (2.45 - u_foot) is 3.00-3.05 Hc, about 3.92 m. Confidence medium-low (scales with Hc, and the wall is assumed to be the colonnade).
