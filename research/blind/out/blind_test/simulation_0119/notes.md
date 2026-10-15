# simulation_0119 (V2MC, top-down Blender scene, 1080x1080, 48 frames @24 fps)

Scene: camera looks straight down at a square coffee table (rounded corners) on a shag rug; 10x10 checker board
on the table, glass chess pieces, dark grey tray with book/sculpture. One glass piece (rook-like, at x=533) slides
straight down the image from y=520.5 to y=572 (frames 0..36), then stays still.

## Tracking (track4.py)
Background composite (frame 47 above y=546, frame 0 below) -> |diff| mask -> largest blob per frame.
Centre y linear in frame: slope 1.4216 px/frame (resid std 0.25 px), top edge slope 1.4237. Motion frames 0->36
(36 frames = 1.5 s), total 51.2-51.5 px. Constant speed (linear keyframes).
Pixel speed 34.12 px/s -> 0.04 m/s => 1.1724 mm/px at the piece-origin plane.

## Perspective
Camera looks straight down (board 336x337 px, table 665.5x665 px project square). Standing pieces off-centre
show top displaced radially (pawn: 10 px at r=198 px; tall piece: 29 px at r=293) => camera ~900 px-equivalents
(~1.05 m) above table, f ~ 850-950 px. Piece origin base vs centre changes board scale by <=2.9%; used
compromise factor 1.01 -> board-plane scale 1.184 mm/px. Table top assumed ~1 cm below board top (+1%), tray rim
~2 cm above board (-1.5%).

## Measurements (edge profiles, prof.py / prof2.py)
- Moving piece silhouette diameter: ~34.4 px (Hough r=17.2; mask bbox 35; edge profiles 34-35).
- Board: x 247.5-583.3, y 504.3-841.5 -> 336.5 px (10 squares of 33.65 px).
- Tray outer rim: x 433.5-681 (247.5 px), y 233.5-491.5 (258 px) -> not exactly square; used ~254 px.
- Table: x 111.7-777.2, y 211.6-876.5 -> 665.2 px.

## Answers
- 252 piece diameter: 34.4 px * 1.184 mm = 0.0407 m (confidence medium-high)
- 253 board side: 336.5 * 1.184 = 0.398 m (high)
- 254 tray length: 254 * 1.184 * 0.985 = 0.297 m (medium; x/y extents differ by 4%)
- 255 table side: 665.2 * 1.184 * 1.01 = 0.795 m (high)
- 256 distance moved: 0.04 m/s * 1.5 s = 0.060 m (= 51.3 px * 1.172 mm) (high)
