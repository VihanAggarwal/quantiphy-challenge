# simulation_0126 — air-hockey table, top-down (S2MS), 1080x1790, 24 fps, 72 frames

## Scene
Fixed camera looking straight down at an air-hockey table (principal point ~ image centre; scale uniform along the
puck path: puck width constant 65.3 px from y=720 to 1690 px, so the table plane is parallel to the image plane).
Orange puck moves straight down along x=537.9 px at constant speed (frames 2-40), bounces off the bottom wall
(~frame 40/41), returns upward at constant lower speed. Two red handles (mallets): "top" handle (x=531.6) slides
down from y=535 to y=754 during frames 1-6 then stays; "right/bottom" handle (x=712.7, y=1432) is static.

## Scale
Puck diameter 0.074 m. Sub-pixel luma half-level edges over many rows/frames: horizontal width 65.3 px
(chroma-half-max gives 64.2, outer extent ~66). Small perspective (camera height H) seen as silhouette elongation
along the radial direction: handles k~0.0045 (rim height/H), puck ~0.0013 (thickness/H); corrected to the table plane:
puck 65.22 px -> 1.1346 mm/px (table plane), 1.1339 mm/px at puck-origin height.

## Measurements
- Top handle width 115.2 px (max chord) -> 0.130 m; right/bottom handle width 106.8 px, minus perspective
  elongation (~0.8 px, off-axis by 174 px) -> 105.8 px -> 0.120 m. The two handles are genuinely different sizes
  (same shadow offsets => both rest on the table; not a depth effect). Answer = mean 0.125 m (within ~4% of either).
- Puck speed: linear fit y(t) frames 2-40: 24.413 px/frame; frames 41-71: 9.344 px/frame (constant both sides).
  v(0.5 s)=24.413*24*1.1339e-3 = 0.664 m/s; v(2.0 s)=9.344*24*1.1339e-3 = 0.254 m/s.
- Horizontal (image-x) distance between handle axes: 712.74 - 531.63 = 181.1 px -> 0.2055 m.
  (Alternative full planar distance would be ~0.80 m; not used.)
- Shortest distance puck <-> right handle: interpreted as minimum centre-to-centre distance over the video
  (puck passes the handle's y at frames ~30 and ~66): dx = 712.74 - 537.88 = 174.9 px -> 0.198 m.
  (Edge-to-edge gap alternative would be ~0.101 m; not used.)

## Answers / confidence
- 282 handle diameter: 0.125 m — medium (handles differ: 0.130 vs 0.120; hedged mean).
- 283 v(0.5 s): 0.664 m/s — high.
- 284 v(2.0 s): 0.254 m/s — high.
- 285 horizontal distance between handles: 0.2055 m — medium-high (interpretation = image-horizontal).
- 286 shortest puck-right handle distance: 0.198 m — medium (centre-to-centre vs edge gap ambiguity).
