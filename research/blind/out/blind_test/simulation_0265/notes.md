# simulation_0265 (A2SS, top-down 2D, spacecraft moving left on uniform grey bg)
- Threshold mask |gray-bg|>25 per frame -> bbox (track.py, track.txt, fit.py).
- Centre x(n) fits quadratic with rms 0.24 px: accel 1.204 px/frame^2 = 693.6 px/s^2, motion starts at t=0 (constant accel).
- Scale = 4 / 693.6 = 0.005767 m/px.
- Length grows linearly with speed (motion blur); extrapolated to v=0 -> ~996 px -> 5.74 m. Width constant 514 px -> 2.96 m.
- Speed (backward diff, constant accel from 0): v = 4*(t - 1/48): 0.5s -> 1.92, 1.0s -> 3.92 m/s.
Confidence: speeds high; length/width medium-high (blur correction, fins included in bbox).
