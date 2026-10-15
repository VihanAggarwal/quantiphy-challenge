# simulation_0152 - notes

Scene: static camera in a parking garage (1920x1080, 24 fps, 42 frames). A blue cart (near) and a yellow sports car (farther behind it)
both drive left->right parallel to the image plane (wheel-centre y and size constant over time -> no depth motion).

## Camera
- Ceiling light strips converge at VP = (959.4, 539.2) = image centre -> level camera, optical axis along the corridor.
- Blue tire near-face diameter D_b = 107.7 px (chords at frames 30-39, near the VP column, where both side edges are near-face silhouettes).
- depth_info 9.312 m (Euclidean, tire origin) -> Z_centre = 9.16 m -> f = Z_nearface*D_b/0.369 ~ 2655-2667 px = Blender default 50 mm/36 mm
  (2666.7 px). The "right front tire" therefore behaves as the visible near tire; the far-tire reading would give a non-standard f ~2470.
- Camera height from blue contact ~1.40 m.

## Scales (m/px at each car's near face)
- Blue: 0.369/107.7 = 0.003426.
- Yellow: tire near-face diameter ~187-188 px (left/right edges at frame 21, lower-arc chords) -> 0.00407 m/px.
  The shared-floor cross-check gives 0.00397 (about 2.7% lower; the cars seem to sit slightly differently on the floor), so I weighted the direct value.

## Tracks
- Yellow: circle fit of the white rim per frame, frames 10-30 (cubic fit, rms 0.02 px). At frame 24: backward v = 101.10 px/frame;
  2nd backward diff = 1.576, central = 1.333, gradient = 1.455 px/frame^2.
- Blue: ECC sub-pixel tracking of rigid near-side features (side lights) and the hub. v24 = 48.04 px/frame (hub 48.05);
  2nd backward = 0.751, central = 0.634, gradient = 0.692 px/frame^2.

## Answers
- 1542 yellow speed = 101.10*24*0.00407 = 9.87 m/s (+-2%).
- 1544 blue speed = 48.04*24*0.003426 = 3.95 m/s (+-1%).
- 1543 yellow accel: backward-diff convention 3.69, central 3.12. Answer 3.62, weighted toward the backward convention (medium confidence).
- 1545 blue accel: backward 1.48, central 1.25. Answer 1.45 (medium confidence).
- 1541 blue car width, taken as the lateral (depth-direction) extent: the far front tire's outer face peeks out right of the near tire.
  Near/far depth ratio rho = 0.918 (frames 20-23); the roof front corners give 0.913-0.919.
  W = Z_near*(1/rho - 1) = 9.12*0.089 ~ 0.81-0.84 m -> 0.82 m. Medium-low confidence: if "width" meant the extent along the motion
  (the car's length), the answer would be ~1.9-2.0 m.
