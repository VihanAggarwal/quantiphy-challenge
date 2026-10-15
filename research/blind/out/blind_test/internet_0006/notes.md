# internet_0006 - nadir drone view of a 2-lane rural road (1080x1920, 172 frames, fps 30)

Camera: static (phase correlation drift < 3 px over the clip, ~0.5% scale drift at the very end) -> no motion compensation needed.
Prior: lane width = 3.66 m. Road: asphalt ~73-77 px wide (half-max edges), dark verge/edge bands to ~85 px.
Lane width = 37-38 px (asphalt edge to centre line) or ~42 px (dark edge band to centre line).
Used compromise lane = 39 px -> 0.0938 m/px (hedge: ~5-7% either way). Slight perspective: road ~4% wider at top than bottom.

Vehicle pixel lengths (zoomed gridded crops + diff-mask/profile extents over many frames):
- white car 75 px (mask 75-76, profile 73-77); width ~28 px
- black car 63 px (visual 63 on 2 frames; profile 62; mask 68 includes blur/shadow)
- motorcycle 31 px (visual 30-32 on 3 frames)

Speeds (template-matching track, sub-pixel, linear over visible span):
- motorcycle 9.385 px/frame (moving down, frames 0-119), very constant
- white car 8.725 px/frame (moving up, frames 0-154); 8.63 low in frame -> 8.85 top (partly perspective)
- black car 8.43-8.48 px/frame average (accelerates 7.9 -> 8.9 px/frame)

Answers (m, m/s): moto len 2.91, moto speed 26.4, white len 7.04, white speed 24.6, black len 5.91, black speed 23.8.
Note: real-world these are large (true lane is probably ~2.5 m: car width 28 px ~1.85 m) but the prior defines the scale.
Confidence: medium; dominant uncertainty is how the annotator measured lane width (37.5 vs 42 px, +-6%).
