# simulation_0144 — HIMARS-style truck launching a rocket (S3MC, 24 fps, 35 frames, 1920x1080)

Prior: rocket length 2.9 m. Depth: rocket range 43.064 m at t=0 (inside pod) and 41.127 m at t=0.5 s.
The camera is static. Phase correlation shows less than 0.1 px of drift.

## Rocket track
- I used frame 0 as the background (the rocket is hidden in the top-right tube) and took difference images.
  The trajectory is a straight image line; the residual from the fitted line is under 0.6 px.
- The image has motion blur (shutter about 0.5 frame). I fitted a 1D along-axis profile model per frame for frames 18-30:
  linear nose cone (about 21% of the length), body and sharp tail, convolved with a box blur of 0.5 x image speed.
  This gives tip and tail positions. Tip-to-tail length is 152 px at frame 18 and 197 px at frame 30.
  The length estimate changes less than 1.5% when the blur fraction ranges from 0.4 to 0.6.
- I fitted a 1D projective map u(s) = (p s + q)/(r s + 1) along the line with metric s (tip = s + 1.45, tail = s - 1.45).
  I fitted it jointly with a motion law and with early nose tips (frames 5-17, read from rectified strips).
- Motion: s(t) = s0 + D(3tau^2 - 2tau^3) fits best (Blender Bezier ease-in-out keyframe, starting at t = 0.005 s, T = 3.33 s, D = 52 m).
  A free cubic gives the same result (v0 about 0, a0 = 28.2, jerk -16.9). Constant acceleration fits clearly worse (chi2 164 vs 18).
- Results with the dataset conventions:
  - v(1 s) by backward difference (frame 24) = 19.40 m/s. The instantaneous value is 19.7.
  - a(1 s) by backward second difference = 12.04 m/s^2. The central difference gives 11.70 and the instantaneous value 11.27. I answer 11.9.
  - Average speed is 14.22 m/s as the mean of 34 backward speeds, or 13.81 when spread over 35 frames. I answer 14.05.
- Uncertainty: about 3% from the length definition. There is a faint tail extension of about 5 px, possibly a nozzle or exhaust.

## Camera / scale
- I fitted f jointly with the range constraints at t=0 and t=0.5, assuming the origin is at the rocket centre: f = 2400 px (hFOV 43.6 deg).
  If the origin is at the tail or nose, f is 2333 or 2471. Kinematics are independent of f.
- The rocket direction in camera coordinates is (-0.60, -0.64, -0.48), at 39.6 deg elevation for a level camera.
- I assumed the pod azimuth is aligned with the truck axis and the camera is level. Three checks support this:
  - The image direction of the wheel-centre line matches within 1.5 deg.
  - The front hub ellipse aspect is 0.72 against a predicted 0.71.
  - The reconstructed wheel centres are at equal height (7.43/7.45/7.50 m below the camera).
  - The reconstructed truck also looks right: tandem spacing 1.39 m and wheelbase 4.1 m, which are realistic FMTV numbers.
- Scale anchor: the near wheel plane is placed 0.6 +/- 0.3 m outward of the top-right tube line plane. This gives a camera height of about 8.07 m.

## Sizes
- Tire: the silhouette is 74.5/69.5/70 px tall (front/middle/rear). A cylinder model with 0.3 m tread width corrects for the tread seen from above, giving D = 1.16-1.20.
  Without the correction it is 1.21-1.24. Answer: 1.18 m (confidence medium).
- Vehicle width: the cab front face spans 1002.5 to 1100 px, back-projected onto the front plane, which gives 2.41 m (2.37-2.47 over the f range).
  Answer: 2.41 m (medium-high).
- Road width: I segmented the lavender road band in the Lab b channel (about 30 px tall at x=1460-1910) and projected the edges onto the ground plane (h = 8.07 m).
  The perpendicular separation has a median of 2.62 m (segments range 2.34-2.70). Answer: 2.6 m (medium; assumes flat ground at Z about 50 m).
