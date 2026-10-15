# simulation_0111 — boat under a bridge, nadir (top-down) Blender camera

Video 1174x2048 (1152-px content + 11-px black side padding), 24 fps, 211 frames (frame 0 black).
Camera is static and looks straight down: water-plane scale is the same at the top and bottom of
the frame (boat width 84-85 px everywhere, constant pixel speed). The boat moves straight down
image-y (x drift 0.0001 px/px).

## Scale from the prior (boat speed = 2 m/s)
- Boat tracked by background subtraction, template matching and per-feature fits (frames 3-75 and 202-210).
  Different features move at slightly different pixel speeds because they sit at different heights:
  interior/template 5.45, centroid 5.47, hull tips (rim) 5.49-5.50, bow post tip 5.53 px/frame.
- Rim-level scale = 2 / (5.495*24) = 0.01517 m/px. This is the depth at which the hull outline is measured.

## Boat (qid 224 length, 225 width)
- Axis-aligned bbox: 236 px long (bottom-of-frame position, where the bow-post parallax adds nothing;
  238-239 px at the top), 84.5-85 px wide. Boat axis is about 3.6 deg off image-y, which changes these by under 0.5%.
- L = 236*0.01517 = 3.58 m; W = 84.7*0.01517 = 1.29 m. Confidence: high (about ±3%).

## Bridge (qid 226 width)
- Outer handrail-to-handrail extent in the flat mid-span: 456.5 px vertically. The bridge is rotated
  5.5 deg in plan, so the perpendicular extent is 454.4 px. The ends slope down like steps or ramps:
  the top and bottom railings bend toward each other at both ends.
- Perspective: the deck sits above the water. Railing parallax gives h_rail/Z_deck = 0.06, and the
  mid-span lamp posts give about 0.23 Z_deck. The deck height above the water is not directly observable;
  I assumed about 2-4 m, giving a scale factor (Z-h_top)/(Z-z_rim) of about 0.84 ± 0.04.
  This gives a true perpendicular width of about 5.8 m (range 5.4-6.2). Same-plane estimate: 6.9 m.
- If the ground truth is the WORLD axis-aligned bbox with world = image axes (which the exact
  image-y boat motion suggests), the rotated bridge's along-canal AABB = W cos5.5 + L sin5.5 is about 7.3-8.1 m
  (L = 16-24 m, much of it outside the frame).
- Answer 6.6 m is a hedge between about 5.8 (local dims) and about 7.7 (world AABB). Confidence: low-medium.
