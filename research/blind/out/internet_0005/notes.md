# internet_0005 (Solna Centrum metro platform, woman in yellow walking left->right)

## Method
- Camera static (phase correlation drift < 1 px over 178 frames).
- Median background; woman tracked by background difference (+ yellow-jacket colour mask).
  Linear fit of x-centre over t = 0..5.8 s: 54.73 px/s (two independent trackers agree: 54.72 / 54.73; rms 0.8 px).
  She walks parallel to the image plane (constant y, constant apparent height).
- Scale at her depth: 1.25 / 54.73 = 0.02284 m/px.
- Floor tile lines (perpendicular to the platform edge) fitted per row; vanishing point (421, 301) -> horizon y = 301,
  which coincides with the woman's head top (~300) -> camera height ~ woman's height (~1.7 m), consistent.

## Measurements
- Woman: head top y ~300-301, shoe bottom y ~374.5-375 -> 74-75 px -> 1.70 m.
- Signs: board/post centres x = 328.0 and 538.7 -> 210.7 px -> 4.81 m with single 2D scale.
  Post bottoms at y ~362 (above the platform-edge strip) => signs lie farther than the woman
  (ground-plane ratio 73.5/61 ~ 1.2 -> up to ~5.8 m in 3D). Answer hedged toward 2D: 4.95 m.
- Light right above her head = lowest (farthest) row of canopy lights (y ~250): visible tube ~48-50 px
  (half-max 45.5 px) -> 1.10-1.14 m; 3D estimate ~1.1-1.25 m. Answer 1.13 m.
- Floor tiles: line spacing along the platform at the woman's foot line (y=374.5) = 52.7 px -> 1.204 m;
  spacing at y=370 is 49.5 px and the ratio 1.065 matches the horizon-based depth ratio exactly.
  Answer 1.18 m (between 2D-naive 1.13-1.20 and 3D 1.20).

## Confidence
- 2031 height: high. 2033 tiles: medium-high. 2032 light: medium (which light is ambiguous).
- 2030 signs: medium (depth of signs vs woman uncertain; 2D vs 3D convention).
