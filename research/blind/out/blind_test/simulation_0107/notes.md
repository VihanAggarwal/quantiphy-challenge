# simulation_0107 - two viruses moving apart (2D, V2MX), 24 fps, 72 frames 1920x1080

## Observations
- Static camera, uniform grey background (206). Two spiky virus meshes; frames 0 and 1 identical, then constant-velocity
  motion: left virus moves left, right virus moves right (slightly up). Both leave the frame by ~f69.
- Depth constant for both (whole-object vertical extents constant: L 511 px, R 577 px over ~45 frames).
- Right virus image is 1.126x larger than left (core radius 138.75 vs 123.27 px at f1).

## Measurements (px/frame)
- Frame-to-frame template matching (frames 2-38): L (-14.20, +0.07), R (+13.78, -0.685).
- Robust ray-cast circle fit on the spherical core (origin proxy), frames 1-22: L (-14.21, +0.04), R (+13.7745, -0.680).
  |vL| = 14.205, |vR| = 13.794 -> ratio 1.0298.
- Core centres (linear fit): f24 L (367.1, 582.7), R (1624.0, 599.5) -> sep 1257.0 px;
  f48 (extrapolated, partly out of frame) L (26.0, 583.6), R (1954.6, 583.2) -> sep 1928.5 px.
- Focal length rough estimate from off-axis core stretching ~2300-2600 px (parallax of front spike tips gave 2900-3300).

## Scale (single plane, from prior)
- s = 1.7393 / (24 * 13.794) = 0.0052538 m/px.
- Same-depth hypothesis: vL = 1.791 m/s; d(1.0s) = 6.604 m; d(2.0s) = 10.132 m.
- Alternative (same physical size, right virus closer by 1.1256): vL = 2.016; d1 ~ 7.18; d2 ~ 10.87 (includes depth gap ~1.6 m).
- Frame-index ambiguity (first frame duplicated): if t=1.0s maps to video frame 23, d1 = 6.457, d2 = 9.985 (same depth).

## Answers (lightly hedged toward the alternative; still within ~3% of the same-depth values)
- 218 left virus speed: 1.84 m/s (same-depth 1.791). Confidence: medium-high.
- 219 distance at 1.0 s: 6.72 m (same-depth 6.604). Confidence: medium.
- 220 distance at 2.0 s: 10.35 m (same-depth 10.132). Confidence: medium.
