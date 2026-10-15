# simulation_0100 (S2MS, 24 fps, 1920x1080, 58 frames; frames 0 and 1 identical)

Scene: static camera, side view. Red fishing boat moving right on the surface; shark swimming left in the
cut-away underwater region. Both move purely horizontally (constant image row, constant pixel size).
Prior: boat length = 10 m.

## Method
- Background = frame 0 / frame 57 composite (each object absent on one side); per-frame |diff| masks.
- Boat length: subpixel half-level edge crossings of the column-max diff profile, frames 22-56:
  860-862 px (thr dependent), slight perspective trend; adopted 860.5 px -> scale 0.011621 m/px.
  Extremes: stern hull (row ~526) and bow tip (row ~367), both on the centreline.
- Boat motion: subpixel bow edge on 5 rows, linear fit frames 1-57: 17.872 px/frame (rms resid 0.1 px,
  no acceleration, no vertical motion) = 428.9 px/s.
- Shark motion: template matching, 10.828 px/frame constant = 259.9 px/s.
- Shark extents: snout is rendered as a faint light-blue patch with a bright rim (included);
  width 278.6 px (std 0.6 over 45 frames), height 104.4 px (dorsal fin tip to pectoral fin tip).
- Single planar scale (2D video). Supporting evidence: boat speed 4.985 and shark speed 3.02 m/s are
  both near round numbers -> shark lies in the boat's plane, no refraction magnification.

## Answers
- 187 boat speed @1.0 s: 428.9*0.011621 = 4.98-5.00 -> 4.99 m/s (high confidence)
- 188 shark speed @1.0 s: 259.9*0.011621 = 3.02 m/s (high-medium; assumes same depth plane)
- 189 shark length: 278.6 px -> 3.24 m (medium-high)
- 190 shark height: 104.4 px -> 1.213 m; camera looks slightly down (~5 deg) so near pectoral fin tip
  is projected a bit low; small correction -> 1.19 m (medium)
