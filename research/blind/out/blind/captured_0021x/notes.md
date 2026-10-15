# captured_0021x — ping pong ball rolling toward camera on a small table (lab, segmented, 1280x720, 24 fps)

## Observations
- Ball sits still at the back edge of the table (u,v ~ 723,416, width ~17.6-18 px) until t~0.96 s, then is flicked
  toward the camera, rolls down the table and drops off the front edge at t~1.6 s.
- The video is a 25 fps capture resampled to 24 fps: one dropped frame between here-frames 35 and 36 (v jump 7.8 px vs ~3.2 px).
  Mapping used: here-frame i shows orig frame round(i*25/24) -> t = that/25. So t=1.0 -> frame 24, 1.2 -> 29, 1.24 -> 30,
  1.4 -> 34, 1.44 -> 35 (the dataset's 25 fps forward difference pairs).
- Ball centre: HSV mask (S<60, V>185) centroid (+0.9 px v bias measured against circle fits), horizontal width from row profiles.

## Geometry
- f = 711 px, principal point (640,360). Table top corners from sub-pixel edge-line fits on frames 43-48:
  FL (463.1,482.7) FR (962.8,494.9) BR (848.7,427.3) BL (574.5,423.8).
- Rectangle fit (4 corners, f=711; residual 0.25 px): camera pitch 0.92 deg down (horizon v~349), roll -0.2 deg, table yaw 6 deg,
  W/H = 3.555, L/H = 4.204 (H = camera height above table top).
- Ball-centre plane height h_ball from GT depths (t=1.0 1.511 m, t=1.4 1.03 m) = 0.1483 m at BOTH points (consistent);
  from ball widths (f=711) 0.144-0.149. H = h_ball + 0.02 = 0.165-0.169.

## Answers
- 2520 speed at 1.2 s: 3D ball track = ray / plane intersection calibrated to GT depths. Z per 0.04 s decelerates
  (sliding phase): 1.85,1.41,1.63,1.30,1.16,1.12,1.00,0.91,0.83 m/s; raw fwd diff 1.20->1.24 = 1.117 m/s, linear fit at
  1.22 = 1.13 m/s (incl. small x component). Width-based depth gives ~1.0-1.4 (noisy). Answer 113 cm/s. Confidence medium.
- 2521 speed at 1.4 s: ball has reached ~constant rolling speed; raw fwd diff 1.40->1.44 = 0.71, average over 1.36-1.56 = 0.77
  (plane) / 0.86 (width), plus ~0.08 lateral. Answer 79 cm/s. Confidence medium-low (GT uses noisy ToF diffs).
- 2522 displacement 1.0->1.4: (u,v,depth) pinhole with given depths: 48.2 cm (depth as Z) / 48.6 (as range). Answer 48.3. High.
- 2523 table width (left-right, shorter side): 3.555*H = 58.6-60.1 cm across calibrations. Answer 59.5. Medium-high.
- 2524 table length (front-back, longer side): 4.204*H = 69.1-71.1 cm. Answer 70.3. Medium (assumes width=shorter side).
