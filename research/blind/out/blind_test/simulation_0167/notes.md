# simulation_0167 (top-down 2D, 1920x1080, 24 fps, 80 frames)
Scale: bike tracked by template matching (frames 5-59) = 14.44 px/frame -> 346.6 px/s; prior 5.52 m/s -> 0.01597 m/px (full res).
- 399 car speed @1s: template match on car, constant 18.0 px/frame (frames 14-35) -> 6.90 m/s. Confidence high.
- 397/398 car: bright-mask bbox 287-289 x 114-116 px; +mirrors ~118 -> 4.60 m x 1.87 m. Medium-high.
- 396 bike: rear wheel to front ~113 px (frame 60 zoom) -> 1.80 m. Medium.
- 400 main road (bike+car on): edge lines at y~354-363 and ~735-743 -> ~385 px -> 6.15 m. Medium (definition of road extent).
- 395 crossing road: edge lines x~1199-1211 and ~1700-1713 (sidewalk at 1730) -> ~510 px -> 8.15 m. Medium.
