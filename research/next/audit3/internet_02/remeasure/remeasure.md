# internet_02 independent remeasure (qids 3259, 3083)

Inputs read: the input json, agent notes for internet_0070 and internet_0044 only. I did not read the other measurer's notes.md or scripts.
Scripts are in scripts/. Small text tracks are kept, and every PNG crop has been deleted. The folder is under 0.1 MB.

## 3083: internet_0044, velocity of the white ball at 2.50 s (prior g = 9.8 m/s^2)
- The PTS check shows a constant 30 fps, and frame 75 is at exactly 2.500 s.
- Tracking: median-background subtraction plus a white mask at full resolution, with a centroid for each frame (ball_track_full.txt).
  Camera drift (phase correlation on the wall/lamp area) is about 0.1-0.2 px/frame. It is subtracted before fitting.
- Pixel g from free parabola fits on the clean arcs (A 50-59: 19.73, B: 18.2 (one clipped frame), C 72-80: 19.44, D 82-89: 19.64,
  E 92-99: 19.48) gives g_px = 19.5 px/frame^2, so s_g = 9.8/900/19.5 = 5.584e-4 m/px.
- Second scale route: the vertical FWHM diameter of the ball at apex frames (f76, f86, f95) is 72-73 px. A standard 40 mm ping-pong ball then gives
  s_ball = 5.56e-4 m/px, which agrees with s_g to 0.4%. Both scales are taken at the ball's own depth.
- f75 lies in the middle of arc C (bounces at about f71 and f81; apex at f76.2). Velocity at f75 from the arc-C parabola fit:
  vx = -14.5, vy = -22.6 px/frame, |v| = 26.9 px/frame, which is 0.450 m/s. Fixing g at 19.5 gives the same value. Central differences give 0.446 for ±2 frames and 0.456 for ±3 frames.
- The value is sensitive to the convention because the ball is near its apex. A backward difference (74->75) gives 0.563 and a forward difference (75->76) gives 0.316.
  The previous value of 0.611 probably comes from a one-sided backward difference. The instantaneous speed at t = 2.50 s is 0.45.
- **Best: 0.45 m/s** (speed magnitude). Confidence is medium: the measurement is solid to about 3%, and the risk lies in how the ground truth defines velocity.

## 3259: internet_0070, length of the speedboat (prior v(1.00 s) = 11 m/s, fps 29.97)
- Camera: a slow pan right. The tree band (phase correlation) shifts -0.41 px/frame at f30, and the cumulative shift is -54 px by f120.
- Boat px speed at f30 (t = 1.00 s), from template tracking (4 templates and ±4 to ±10 frame quadratic fits, all consistent):
  raw 15.52 px/frame, camera-corrected 15.93 px/frame (the image velocity is nearly horizontal, vy = -0.3).
  Scale = 11/(15.93*29.97) = 0.02304 m/px. Without the pan correction it would be 0.02365.
- Apparent length at f30 (zoomed crops with a pixel ruler): the bow tip is at x = 398.8. The transom/hull start, right next to the stern flag, is at 198-200,
  which gives a hull of 200 px. Hull readings at f26, f30, f34 and f44 are 203, 200, 196 and 193, shrinking slowly as the boat recedes. The far edge of the flag is at about 180, which gives 219 px including the flag.
- Route 1 (ratio at the same frame, where foreshortening cancels): hull 200 px * 0.02304 = 4.61 m. Including the flag, 219 px gives 5.05 m.
- Route 2 (passing time, in camera-stabilised coordinates): the stern reaches the bow's f30 position about 12.5 frames later, which is 0.417 s, and 0.417 s * 11 m/s = 4.59 m.
- Plausibility: the bimini is 69 px, which is 1.6 m. That fits a 5-6 m bowrider.
- **Best: 4.8 m.** This sits between hull-only (4.6) and flag-inclusive (5.05), and it is within 5% of both conventions.
  Confidence is medium for the clip's own prior.
- **Family conflict:** internet_0030 is exactly frames 44-85 of internet_0070 (frame MAD match 1.1, against 3.6 for the next best). Its stated prior is
  length = 3.2 m. With the same pixels, 3.2 m implies 7.0-7.7 m/s at 1 s rather than 11 m/s. The two stated priors are therefore physically
  inconsistent, by a factor of 1.43-1.57. Anchored to 0070's own prior, the length is 4.6-5.05 m. If the dataset reused the 0030 size, the ground truth would be 3.2 m.
  I kept the own-prior value. 3.2 m is also implausible for a bowrider with a bimini that is planing with heavy spray.
