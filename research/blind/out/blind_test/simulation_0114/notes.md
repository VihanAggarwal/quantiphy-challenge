# simulation_0114 — plane, 2D top-down view, acceleration prior 18 m/s^2

Video: 1080x1920, 80 frames, 24 fps, static camera. Yellow light aircraft seen from above, nose pointing down,
accelerating from rest straight down the frame (x stays ~670 px). It leaves the frame after frame 76; frame 79 is a clean background.

Method
- Tracking: background subtraction against frame 79 using a yellowness channel ((R+G)/2-B), then the weighted
  centroid per frame (work/track2.py). Bounding-box track by HSV threshold as a cross-check (work/track.py).
- Quadratic fit y(t): a = 344.0 px/s^2 over the full track (other windows and the bbox-edge track give 337-347), v0 ~ 0,
  vertex at t = 0.004 s, so it starts from rest at frame 0. Residual rms 0.77 px. Wingspan stays constant (within ~1%, blur)
  along the track, so there is no perspective change and a single scale applies.
- Scale: 18 / 344.0 = 0.05233 m/px.
- Sizes from static, unblurred frames 0-4, subpixel half-max silhouette extremes (work/extent3.py):
  wingspan 166.0 px (30% threshold 167.9), nose-to-tail 104.4 px (30% threshold 106.4; a faint propeller line at the nose).
  Used 166.5 px and 105 px.
- Speed at 1.5 s: backward difference of the fitted track at frame 36 = v0 + a(1.5 - 1/48) = 507.6 px/s -> 26.56 m/s
  (equivalently 18 m/s^2 * ~1.476 s from rest).

Answers
- 233 width (wingspan, horizontal in the image): 8.71 m. Medium confidence: risk that "width" means the other AABB axis.
- 234 length (nose to tail): 5.49 m. Medium confidence: same axis ambiguity.
- 235 speed at 1.5 s: 26.56 m/s. High confidence: mostly independent of the pixel scale.
