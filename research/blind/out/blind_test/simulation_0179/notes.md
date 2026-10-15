# simulation_0179 (A2MC, trolley accelerating rightward, static camera, 24 fps, 60 frames)
- Tracking: median background + diff mask; bbox y constant (636-883) => trolley moves parallel to image x at fixed depth.
- Quadratic fit of x(t): accel 290 (left edge) / 302 (right edge) / 296 px/s^2 (mask mean). Starts ~at rest at t=0.
- Camera from floor tiles: orange tile pitch linear in y (horizon y~213); fit of tile rows + pitch => f~2670 px (HFOV~40 deg), pitch ~7 deg,
  cam height 3.31 m assuming 0.5 m tiles. Check: trolley accel at its ground depth (y~870) = 1.502 m/s^2 vs prior 1.507 -> tiles = 0.50 m (independent confirmation).
- Scale at trolley: 1.507/296 = 0.00509 m/px.
- 430 length: x-extent 222 px (frame 0), small perspective correction -> ~220 px -> 1.12 m (medium confidence).
- 431 height: top 636 px vs ground at depth y870 via camera model -> 1.20 m (x1.003) -> 1.21 (medium).
- 432 gate: near wooden post base y~955, frame top y~52 -> 4.0 m via pitched camera model (medium).
- 433 orange tile: 0.50 m (high).
- 434/435: backward diff from fit: 295/591 px/s -> 1.50 / 3.01 m/s (high).
