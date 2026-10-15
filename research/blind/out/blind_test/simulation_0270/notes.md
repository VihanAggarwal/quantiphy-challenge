# simulation_0270 (A2SS phoenix, 2D)
- Mask: HSV saturation>60 on grey studio bg; per-frame bbox/centroid (track.py -> track.txt).
- Wing-flap period 25 frames; fit x(t)=quadratic + 3 harmonics (fit.py). cx, xmin, xmax all give a=282 px/s^2, v(0)~0 (starts from rest, constant accel). y ~ constant.
- Scale: 2 m/s^2 / 282 px/s^2 = 0.00709 m/px.
- Length: median horizontal extent 590 px (frame0 565) -> 4.1 m (med conf; 3D pose/wings).
- Height: median vertical extent 408 px (frame0 403; range 320-453 with flap) -> 2.9 m (med-low conf).
- Speeds: v=a*(t-1/48) backward diff -> 0.97 @0.5s, 1.97 @1.0s (high conf).
