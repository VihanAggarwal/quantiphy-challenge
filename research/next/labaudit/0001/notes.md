# Lab audit, family 0001 (captured_0001; one render, 49 frames, 24 fps, 1280x720)

Scene: a tennis ball sits on the top edge of a white board inclined toward the camera. The board sits on the lab table.
The ball stays still until frame ~28 (1.17 s), rolls down from about frame 29, reaches the bottom edge at frame ~38 (1.58 s),
rolls on the table toward the camera, then leaves the table front edge at frames 43-45.
Camera model used: f=711 px, cx=640, cy=360. Depths treated as range along the click ray.

Scripts: scripts/track.py (2D yellow-mask track), scripts/board.py (board mask edges), scripts/slope.py (slope length routes),
scripts/track3d.py (3D track: ray intersected with the slope plane offset by r=3.35 cm), scripts/ballsize.py (circle fit).
Frames: frames/fNN.png; montage.png, montage2.png, zoom33_40a/b.png, board48.png.

## Geometry checks
- Board edges (frame 48 mask): top y=353.5, bottom y=493; left edge x 570->539, right x 721->735.
- Board width from the stated end depths: 23.99 cm at the top and 23.94 cm at the bottom. The two agree, so the stated depths match the board ends and f.
- The vanishing point of the side edges is (674,-97). Up-slope direction (0.040,-0.540,0.840), about 32.7 deg incline relative to the camera horizontal.
  The depth-only route gives the same incline (32.5 deg).

## Rows
| qid | question | current | my routes | verdict |
|---|---|---|---|---|
| 2141 | ball size | 6.7 | circle fit R=22.0-22.1 px at frame 0. Label depth taken as centre: 6.86 cm; label depth as front surface (+r): 7.07 cm. Frame 38 (sharp) with plane-route range 0.861: 6.90 cm. Stated tennis ball prior elsewhere: 6.7 | OK (within 2-5%) |
| 2142 | slope length | 30.80 | (1) back-project far/near end mids with 1.136/0.884: 31.8 cm; (2) near end plus vanishing-point direction meeting the top-edge ray: 32.0 cm (implies a far range of 1.138, matching 1.136); f=700/720 gives 32.0/31.7 | OK (3-4% off; clicks are likely a little inside the edges) |
| 2143 | displacement 0-1.5 s | 23.20 | (1) label depths at frame-0/frame-36 click pixels: 23.4 cm; (2) slope-plane route, centre to centre at frame 36: 25.2 cm; the slope-plane position at range 0.912 (between frames 35 and 36): about 23 cm | OK |
| 2144 | v at 1.5 s | 116.6 | 3D plane track: forward difference 36->37 at 24 fps gives 126 cm/s; a=3-4.3 m/s^2 from a start at about 1.21 s gives 90-130 cm/s | OK, not grossly off (left alone per rules) |
| 2145 | v at end of slope | 142.17 | sqrt(2 a L), with a 3.0-4.3 and travel 0.315 m: 137-165 cm/s; table-phase size-range track for frames 38-43 at 24 fps: about 119 cm/s; plane forward differences near the bottom are noisy (76-126) | OK, not grossly off (left alone per rules) |

Caveat on motion: the frame-to-frame image steps are uneven (35->36 jumps 40 px after a 17 px step, and there are ghost/blend
trails in frames 36-37). This looks like frame-rate conversion (dropped or blended frames), so per-frame speeds are unreliable.
None of this gives evidence that either speed row is more than 1.5x off.

Result: no fixes for family 0001.
