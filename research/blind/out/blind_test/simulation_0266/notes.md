# simulation_0266 (2D top-down, spacecraft moving left, 24 fps, 2560x1440)
Method: template matching (ship body template from frame 50, TM_CCOEFF_NORMED, sub-pixel parabola) gives nose-direction x per frame.
Quadratic fit frames 1-60: x = 1630.2 - 0.4435 n^2 (rms 0.5 px), vertex (v=0) at n~0 -> constant accel 0.887 px/frame^2 from rest at t=0.
Scale: prior a=4 m/s^2 -> 0.887*24^2 = 510.9 px/s^2 -> 0.007829 m/px. Ship apparent size constant (no depth change).
Sizes (bg-subtraction mask + zoomed crop, frames 44-50 on clean snow): length ~754 px (nose to rear fins) -> 5.90 m; width ~364 px (outer flaps) -> 2.85 m.
Speeds (backward diff, constant accel from rest): v(0.5s)=4*11.5/24=1.92 m/s (measured diff 10.2 px/f -> 1.92); v(1.0s)=4*23.5/24=3.92 (measured 20.95 px/f -> 3.94).
Confidence: speeds high; sizes medium (bbox includes fins/flaps; perspective of 3D extent minor).
