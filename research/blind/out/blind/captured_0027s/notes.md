# captured_0027s (lab, segmented, red-ball pendulum swinging toward/away from camera)

## Measurements
- Ball mask by HSV red threshold every frame (49 frames, 24 fps file). Centroid (u,v) and equivalent diameter d (40-70 px).
- The 24 fps file is a 25 fps original with frames dropped: fitting with true time t_n = round(n*25/24)/25 cuts the
  pendulum-fit cost from 473 to 157 (drops at n=12 and n=36; a visible 28 px jump at frame 35->36). Dataset t=0.2 -> frame 5,
  t=0.24 -> 6, t=0.6 -> 14, t=0.64 -> 15.
- 3D from size: Z = f*0.07/d, f = 711 (lab FOV). A damped nonlinear pendulum fit (g = 9.8, pivot with linear drift, camera tilt, small
  perpendicular swing) gives rms residual ~1 px, L = 0.337 m, and with f left free f = 708 px. So gravity independently confirms the scale (f 711).
- Model kinematics (true motion): fwd-diff (25 fps) speed v(0.2) = 1.367 m/s, v(0.6) = 0.976 m/s; d|v|/dt(0.2) = -2.6 m/s^2,
  vector 2nd difference 5.8 m/s^2.
- Given "book" depths (1.0995 at 0.2, 1.151 at 0.6) do not match the ball's size depth at the same instant (1.020, 1.177).
  They match it exactly if the depth stream leads RGB by ~48 ms with scale 1.013 (ToF/RGB unsynced). Under that labelling:
  v(0.2) = 1.19 m/s, v(0.6) = 1.25 m/s, d|v|/dt = -3.6 m/s^2.
- Answers lean toward the depth-lag hypothesis (more likely, ~0.65) and are pulled a little toward the no-lag values.
- Shoulder breadth: the person is fully removed by segmentation, so nothing can be measured. Prior guess 40 cm (depths of the two shoulders differ by 4.5 cm, a negligible effect).

## Answers / confidence
- 2604 v(0.2) = 124 cm/s (range 119-137), medium
- 2605 v(0.6) = 118 cm/s (range 98-125), medium-low
- 2606 a(0.2) = 400 cm/s^2 (|d speed/dt| 260-360; vector 580-710; label noise large), low
- 2607 shoulder breadth = 40 cm (prior only), low
