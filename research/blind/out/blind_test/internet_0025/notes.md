# internet_0025 - canoe (Hallstatt-style wooden boat) crossing a lake, boatman standing at stern

## Measurements
- Video 1920x1080, 473 frames @ 30 fps (15.73 s). Boat moves left->right, side-on; apparent size constant (mask width ~325 px all video) -> motion parallel to image plane.
- Camera pans slightly to follow the boat (pure rotation: SIFT similarity fits on mountains and on shoreline agree, no parallax).
  Background shift at the boat location: -28 px by t=5 s, -42 px at end (max -48.6 near frame 390).
- Boat pixel length (stern end x=700 to bow tip x=1053 at t=0, zoom x8): 353 px.
- Boatman visible extent: hat/head top y~598-600 to bottom of visible legs y~660.7 (feet hidden by hull side) -> ~61 px visible.
  Anthropometry (hat-top-to-shoulder 14 px, hat-top-to-shorts-hem 53.5 px) suggests a full height of ~70-75 px, i.e. feet at the floor
  inside the hull near the waterline (y~672).
- Boat track: template matching of the hull every frame (sub-pixel), mapped to frame-0 coordinates with SIFT background transforms
  (every 10 frames, interpolated). Stabilised y stays at 662+-0.5 px (validates the stabilisation).
  Stabilised speed 27.1-27.6 px/s (path length / time, end-to-end displacement / time, linear fit); raw image speed 24.6 px/s.
  Displacement 0-5 s: 137 px stabilised (110.6 px raw image).

## Scale (main uncertainty)
- Visible boatman 61 px -> 0.0288 m/px (L=10.2 m); physical full height ~70-75 px -> 0.024-0.025 m/px (L=8.2-8.8 m).
- Answers hedged by expected-score optimisation over these hypotheses -> effective ~0.0273 m/px.

## Answers
- 2127 boat length: 353 px * ~0.0275 = 9.7 m (confidence medium; +-12% depending on how boatman height was annotated)
- 2128 average speed: 27.2 px/s * 0.027 = 0.73 m/s (medium; additional ~10% risk if GT ignored camera pan)
- 2129 displacement first 5 s: 137 px * 0.027 = 3.6 m (medium-low; raw image displacement would give ~3.0 m)
