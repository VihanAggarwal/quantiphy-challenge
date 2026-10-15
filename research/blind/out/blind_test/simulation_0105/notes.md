# simulation_0105 — ice cube falling toward a teacup on a saucer (2D, 1080x1080, 24 fps, 47 frames)

## Method
- Static camera; background = median of frames 5-20 (cup static, cube absent). Cube appears at frame 21 at the top,
  falls straight down (x = 539.4 px constant) and disappears behind the cup front wall at frame 46 (falls into the cup -> same depth as cup).
- Projection: cube shows no top/bottom face at y=24 px or y=945 px, its apparent height is constant (26.5 px) everywhere,
  cup rim and saucer rim are perfectly straight horizontal lines, saucer seen as a side-on trapezoid -> orthographic (or extremely
  long focal) horizontal view, so a single metres-per-pixel scale is valid.
- Track: sub-pixel half-max top/bottom edges of the cube per frame (frames 22-45). Pure quadratic fit: a = 681.4 +- 0.3 px/s^2,
  rms residual 0.05 px. Damping model test: k=0 preferred strongly (k=0.04 Blender default rejected). Vertex (rest) at frame -0.35.
- Scale: 9.8 / 681.4 = 0.014382 m/px.

## Measurements
- Cube height: 26.47 px (mean sub-pixel half-max height over 24 frames, width 26.07 px) -> 0.381 m.
- Cup+saucer: rim top edge y=974.0, saucer foot bottom y=1073.54 -> 99.5-100 px tall -> 1.434 m.
  Saucer is widest part: x 450.95 .. 637.0 -> 186.0 px -> 2.675 m (handle at x~468 is inside saucer extent).
- Velocity at 1.0 s (frame 24): backward difference of fitted track (p24-p23)*24 = 28.2 px/frame -> 9.74 m/s
  (raw edge-midpoint diff 9.72; equals g*(23.5+0.35)/24, i.e. nearly scale-independent).

## Answers / confidence
- 211 cube height 0.381 m — high (scale +-0.1%, extent +-1%).
- 212 cup+plate height 1.434 m — medium-high (possible rim outline row ambiguity +-1%; assumes orthographic view).
- 213 cup+plate width 2.675 m — high.
- 214 cube velocity at 1.0 s 9.74 m/s — high (depends only on frame convention; 1-based would give ~9.33).
