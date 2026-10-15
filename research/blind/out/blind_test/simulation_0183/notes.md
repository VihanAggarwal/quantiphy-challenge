# simulation_0183 notes
Scene: fixed camera, tool box free-falls (frames 0-8) onto a blue ramp, then slides down it with constant acceleration (frames ~14-44).
Tracking: background = frame 0 with box region patched from frame 44; abs-diff mask + minAreaRect centre (track2.py, track.txt). Masks verified with overlays.
Scale: slide pixel acceleration ~380 px/s^2 (quadratic fit of arc length, frames 14-44) -> prior 1.58 m/s^2 -> 0.00416 m/px.
Cross-check: free fall pixel accel ~2370 px/s^2 -> g/2370 = 0.00414 m/px. Excellent agreement; using 0.00415 m/px.
441: free fall, v(0)=0, backward-diff v at 0.3 s ~2.66-2.74 m/s -> ~9.0 m/s^2 (8.9-9.8 depending on convention). conf high.
442: v(1s)=fit 384.6 px/s (backward-diff shifted) *0.00415 = 2.01 m/s. conf med-high.
443: v(1.5s)=678 px/s -> 2.82 m/s. conf med-high.
444: box front face ~301-335 px wide (side face perspective ambiguity) -> 1.25 m. conf medium.
445: box height ~185-190 px -> 0.75 m (0.70-0.78). conf medium.
