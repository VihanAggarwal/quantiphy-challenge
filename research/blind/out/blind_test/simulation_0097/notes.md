# simulation_0097 (A2MX, 2D, 24 fps, 41 frames, 1920x1080)
Scene: side view on uniform grey background; Cybertruck-like car accelerating leftwards from rest (frames 0-2 static),
Air China A320-like plane flying rightwards at constant speed (enters at frame 3, fully visible 18-38).

Method: background colour (135,125,132) difference masks; per-frame subpixel edge/centroid tracks (scripts/car.py, car2.py, extent.py, prof*.py).
- Car pixel acceleration: quadratic fits on centroid / left edge / right edge / midpoint over frames 2-40 and sub-ranges:
  212.5-213.7 px/s^2, adopted 213.4 px/s^2 (fit rms <0.15 px, acceleration constant). Scale = 10/213.4 = 0.04686 m/px.
- Plane: constant velocity 53.395 px/frame (right edge frames 3-38, centroid 18-38) = 1281.5 px/s -> 60.05 m/s.
- Car extents (frame 0, static, coverage-corrected): length 120.5 px, height 39.5 px.
- Plane extents (frames 18-38, incl. faint APU tail cone): length ~802 px, height (fin top to nacelle bottom) 237.5 px.
Sanity: plane length 37.58 m = real A320 (37.57 m); car 5.65 x 1.85 m ~ Cybertruck -> single planar scale confirmed.

Answers: 174 plane speed 60.05 m/s (high confidence); 175 car length 5.65 m (high); 176 car height 1.85 m (med-high);
177 plane length 37.6 m (high); 178 plane height 11.13 m (medium-high; depends on whether AABB includes hidden gear etc.).
