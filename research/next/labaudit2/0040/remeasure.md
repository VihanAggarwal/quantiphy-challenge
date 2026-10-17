# 0040 second measurer: v(white ball, 1.5 s), qids 2742 / 2750 / 2758

I measured these independently. I did not read labaudit/0040 or labaudit2/0040 notes. Scripts and crops are in
`remeasure_b/` (scripts/track.py, table.py, pnp.py, plane.py, arcs.py, freeg.py, size.py, labelstyle.py, optimal.py).
The three renders (a, s, x) are one event and share one label, so all three qids get the same value.

## Clock
- 49 video frames. The ball's x steps over video 33-40 are 30.1, 33.3, **61.3**, 34.2, 36.0, 32.1, 33.3 px.
  So capture frame c37 was dropped between video 35 and 36, and c = k + (k>=12) + (k>=36). Video 36 is c38.
- Check with a 3D gravity arc over video 34-40 (f=711): drop after v35 gives 1.19 px rms. No second drop gives
  4.7 px, a drop after v34 gives 9.3 px, and a drop after v36 gives 7.0 px.
- t=1.5 s is c37.5. **A** = c38->c39 (video 36->37). **B** = c37->c38 (c37 is not in the video, so its click
  comes from the fitted arc).

## What happens
- The ball is thrown from the left and bounces on the table in front of the tape and card tower at about c34
  (video 33).
- It rises past the card tower and over the cup's top. The apex is at about c38.3 at camera height, and the ball
  passes in front of the cup: at video 38 it occludes the cup's right edge.
- It lands near the table's right edge at about c42.8, bounces up to the right, and is off the table by c50.
- At c38 the motion is almost all lateral: about 33 px/frame to the right, nearly level, drifting slightly toward
  the camera.

## Geometry
- Table PnP on the x render, using four corners from fitted edges:
  - The front edge is 76.0 cm and the depth is 60.3 cm. The swapped assignment fails, with 50-80 px reprojection
    error.
  - The camera is about 16.3 cm above the top (f 711).
- Credit card on that plane: the long edge is 8.28 cm at f 711 against 8.56 true. So the plane scale is about 3%
  short.
- ToF / plane range at f 711 for static objects: card 1.066, tower 1.066, tape 1.058, cup 0.995.

## Route 1: 3D gravity arc (arcs.py)
- Model: a ballistic fit to the pixel centroids of video 34-40, with gravity of 981 cm/s^2 along the table normal.
  Rms is 1.2 px.
- The arc's height above the table at c34 comes out as 2.0 cm, which equals the ball radius at the visible bounce.
  So gravity and the table plane agree.
- Centre range at c38 is 71.0 (a), 72.8 (s) and 72.9 (x) at f 711, and 73.8-75.7 at f 740. The stated surface
  range is 70.45 (centre about 72.45), which is consistent.
- Physical speed does not depend on f:
  - |v(c38)| = 81-83 cm/s;
  - chord c38->c39 (A) = 80-82;
  - chord c37->c38 (B) = 87-89;
  - |v(c37)| = 96-98.
- The range rate at c38 is only -0.4 to -0.5 cm/frame.
- A free gravity direction (joint arcs) moves the ranges by about 4% but leaves speeds at 78-80.

## Route 2: ToF-anchored label emulation (labelstyle.py)
- Method: P = 70.45 m-range times the unit ray at f 711 for the first click, and (70.45 + dr) times the unit ray for
  the next click.
- Click pixels are the smoothed arc positions: c37 (722.3, 368.8), c38 (754.6, 356.2), c39 (787.3, 359.1). The
  raw tracks agree within 1-3 px.
- Lateral part:
  - A: 32.8 px gives 3.17 cm/frame, or 79 cm/s;
  - B: 34.9 px gives 3.37 cm/frame, or 84 cm/s.
  - With f 740 these are 4% lower.
- With the model dr and no ToF noise: A = 78.5 and B = 82.5.
- ToF noise adds in quadrature and only increases the value. With an independent sigma on dr:
  - sigma 1 cm: A median 82, B median 86;
  - sigma 2 cm: A median 88 (mean 92), B median 91 (mean 95);
  - sigma 3 cm: A median 95 (mean 104), B median 99 (mean 108).
- Calibrating dr against the static objects (ToF = 1.06 x plane) would give dr of about +2.3 cm and A of about
  98. However, the ball's own ToF readings fall below that calibration: c38 by 3-5 cm and c50 by 10-12 cm. The
  c50 reading (62.7) conflicts with the arc-3 gravity fit (centre 72.7) and with the ball's apparent size, so I
  treat it as a ToF outlier.

## Score-optimal value (optimal.py)
- Mixture: 60% A / 40% B; f 711 (75%) / 740 (25%); a dr offset of 0 (60%) or +2.3±1.5 (40%); a ToF sigma of
  1, 2 or 3 cm; and 2.5 px click jitter.
- Label distribution: median 92.6, mean 101, p10-p90 76-138.
- Expected MRA item score: 0.803 at x = 89-90, 0.798 at 85, 0.792 at 95, 0.769 at 100, and 0.733 at the current
  106.08.

## Verdict
- **Best value: 90 cm/s** for 2742, 2750 and 2758 (same label). Confidence is medium-low, because the label
  depends on one unknown ToF reading.
- Physical speed: 81-83 cm/s at c38, 87-89 cm/s for the c37->c38 chord.
- The current 106.08 sits above every noise-free route: physical 80-89, label-style 78-84. Only the heavy-noise
  mean reaches it.
