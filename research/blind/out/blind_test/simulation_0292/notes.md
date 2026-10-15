# simulation_0292 (V2SS, 2560x1440, 24 fps, 72 frames)
Scene: drone lifts a black cylindrical column vertically out of a delivery robot; static camera.
Scale: tracked drone plate top (dark threshold, x 1290-1370) per frame; motion starts at frame 2, then constant
-7.137 px/frame (linear fit residual 0.39 px) = 171.3 px/s. Prior 0.96 m/s -> 0.005605 m/px.
- 1020 length (diameter): column silhouette width 88 px (x 1289-1377, rows 511-655 at frame 70) -> 0.49 m. Confidence high.
- 1021 height: column from cap edge under drone hub (y~485) to bottom (y~661) at frame 70 = ~176 px -> 0.99 m.
  Ambiguity: if the hub (y 474-484) belongs to the column it would be ~1.05 m. Confidence medium.
- 1022 displacement 0.5-1.0 s: constant speed, 12 frames * 0.04 m = 0.48 m (measured 85 px = 0.476 m). Confidence high.
