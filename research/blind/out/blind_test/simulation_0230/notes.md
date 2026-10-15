# simulation_0230 (classroom, static camera, 1920x1080, 50 frames @24fps)
Scale: chalkboard outer frame x 320..1692 = 1372 px = 5 m -> 0.003644 m/px at wall plane.
Camera level: ceiling-line vanishing point (958,536) (Hough LSQ). Wall-floor junction y=952, wall-ceiling y~170.
- 724 clock: 113 px (h 114 / v 112) on wall -> 0.412 m (high conf)
- 725 board height: 296..737 = 441 px -> 1.607 (high)
- 726 right chair width: backrest-left (1600, depth .897 of wall) to seat front-right (1792, depth .86) -> ~141 wall-px -> 0.515 (medium)
- 727 teacher table: front top edge 80..772 = 692 px, front at 0.894 of wall depth (floor contact y=1000 vs 952, horizon 536) -> 2.25 (medium)
- 728 ceiling: 952-170 = 782 px -> 2.85 (medium-high)
- 729-732 paper plane: diff-vs-median tracking, bbox centres frames 16-32; speed 69.3 px/f @f24, 61.1 px/f @f30, decel ~1.45 px/f^2 (835 px/s^2).
  Depth unknown (constant apparent size 133 px); hedged scale 0.9*wall = 0.00328 m/px. (low-medium: depth assumption)
- 733-735 cat on table near back (feet y~737, ~0.96 wall depth, scale 0.0035): length 188 px -> 0.66, height 139 px -> 0.49,
  head-front track 350->782 px over 48 frames = 216 px/s -> 0.756 m/s (medium)
