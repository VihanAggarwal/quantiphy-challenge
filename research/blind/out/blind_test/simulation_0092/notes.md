# simulation_0092 (S2MX, 1920x1080, 24 fps, 73 frames)
Scene: Cybertruck (bottom, y~631-674) and Air China airliner (y~299-554) both moving left at constant
pixel speed on a uniform grey background; static camera. Frames 0 and 1 are duplicates.

Method: background = median of last 3 (empty) frames; per-frame |diff| profiles; subpixel half-max edges.
- Car length at image centre (straddling principal point, frames 34-43): 127.3 px (126.9-127.7).
  Off-centre widths grow to ~135 px (end faces visible -> perspective cue, W/Z ~0.0096).
  Scale = 127.3/5.67 = 22.45 px/m.
- Cross-check: plane fuselage depth 93 px -> 4.14 m (= A320 fuselage height) -> same scale; plane length
  6.73x car (real A320/C919 ratio 6.6-6.85) -> both objects at the same depth plane.
- Car height 42.26 px -> 1.88 m raw; perspective (seeing near wheel bottom / far roof edge) ~1 px -> ~1.83.  Answer 1.85.
- Plane length 856.6 px (nose and tail-cone edges, frames 20-30, constant) -> 38.2 m.
- Plane height 254.3 px (fin tip 299.5 to near-nacelle bottom 553.9) -> 11.33 m -> 11.3.
- Speeds: constant. Car 28.50 px/frame (edges in centre region; template 28.62 on near side face) -> 30.5 m/s.
  Plane nose/tail edges 57.02 px/frame (template on fuselage side 57.72 = nearer surface) -> 61.0 m/s.
Confidence: car speed/plane length/plane speed high (~2%); plane height medium-high; car height medium (perspective/tilt +-3%).
