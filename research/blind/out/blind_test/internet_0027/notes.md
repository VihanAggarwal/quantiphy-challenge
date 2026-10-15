# internet_0027 - billiard break, top-down 4K view (3840x2160, 78 frames, dataset fps 25; container says 22.3 fps)

## Method
- Balls are tracked by an edge-based RANSAC circle fit (Lab colour distance from the local felt, radial gradient, mostly using the
  lit upper arc): edgefit.py / edgeseries.py -> edgeseries.json. Colour-mask tracks (track.py) used to seed the trackers.
- Camera: slight handheld drift (~ +12,-26 px over the clip). Corrected with purple (static all clip) + black (static from ~f20).
- Frame timing: the per-frame steps of every moving ball alternate 2:1 (into odd frames = 2 units, into even = 1 unit), i.e. the
  frames are not evenly spaced. I used t_n = n/25 + (n odd)/75 (so the mean rate is still 25 fps). With this timing the quadratic fits leave
  0.5 px rms (nominal timing leaves 4.3 px rms).
- Scale: the apparent ball diameter changes across the image (226 px at the top, 246 px at the bottom), so the camera is tilted.
  Fitted d(u,v) = 220.43 + 0.00117u + 0.01126v (yellow + purple + black, rms 0.47 px); purple is 232 px, black 239.5 px.
  Physical back-projection: P = (57.2/d)(u-cx, v-cy, f), with f between 2500 and 6000 px. I also computed the naive single-scale values
  (57.2 mm / local d).

## Answers
- 2136 initial purple-black centre distance (f0): 597.0 px -> 14.50 cm (naive) / 14.6-14.8 (perspective). Answer 14.6. Confidence high.
- 2139 final purple-black (f77): 727.2 px -> 17.66 (naive) / 17.7-17.95. Answer 17.7. Confidence high.
- 2137 white average velocity 1-2 s: drift-corrected displacement f25->f50 is 1082.7 px, on a straight path -> 25.7-26.3 cm/s
  across the scale choices (26.15 if f25's real time offset is used). Answer 26.0. Confidence high.
- 2138 orange (solid 5) at 1.00 s: smooth fit gives 1003 px/s -> 24.4-25.0 cm/s. Answer 24.8. RISK: a plain backward difference
  f24->f25 hits a long (2-unit) step and would give ~32.7 cm/s; a forward difference would give ~17. Confidence medium.
- 2140 yellow (solid 1, left) at 2.00 s: speed 15.9 cm/s, tangential deceleration 199 px/s^2. With a naive constant scale that is
  4.9 cm/s^2; with the full perspective model it is 4.05 cm/s^2 (the ball rolls away from the camera). Answer 4.5 (a hedge between them).
  Confidence low-medium: the label may be noisy.
- Distances are taken centre to centre. If the 22.3 fps container rate were the true time base, every speed would be x0.89 and the acceleration x0.80.
