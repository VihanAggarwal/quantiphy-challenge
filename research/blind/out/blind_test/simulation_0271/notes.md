# simulation_0271 (A2SS, phoenix, top-down view, flying -x)
Method: background-diff mask + template matching of the bird between frames k and k+25/k+50 (the flap cycle repeats every 25 frames, so pose cancels).
Global fit p(f)=A_phase + B f + C f^2: a = 379 px/s^2 (T25-only fit: 380), zero-velocity frame f0 ~0.26 (frames 0 and 1 nearly identical, so it starts from rest). Constant acceleration, residual 3.5 px.
Scale: 2 m/s^2 / 379 px/s^2 = 0.005276 m/px.
- 957 length: beak to tail tip ~705-740 px (faint thin tail tip at low threshold) -> ~730 px -> 3.85 m. Confidence: medium-high.
- 958 wing span: max spread (frames 21/46) 1003-1008 px -> 5.3 m. Folded/raised-wing pose (frame 0) is only ~425 px (2.2 m); if GT uses the frame-1 evaluated bbox, this would be wrong. Confidence: low-medium (ambiguity about pose).
- 959/960 speed: v = a*(t_mid - t0) with backward difference -> 2*(11.5-0.26)/24 = 0.94 m/s, 2*(23.5-0.26)/24 = 1.94 m/s. Independent of pixel scale. Confidence: high.
