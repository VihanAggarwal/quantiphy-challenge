# simulation_0153 — blue cart moving left->right in a parking garage (S2SC, 24 fps, 42 frames)

## Method
- Static camera. The cart moves laterally at constant depth: the hub y stays constant within 1 px, and template matching needs no scale change.
- Tracking: a template of the sill lights from frame 30 gives sub-pixel x positions for frames 17-41. Hub-ring centres of the
  near-side rear and front wheels were tracked from dark-ring minima.
  The lights x(n) fits a CUBIC exactly (rms 0.04 px). Zero velocity falls at frames 0.05 and 59.0, so this is a Blender
  Bezier ease-in/out between keyframes 59 frames apart. Peak speed is at frame 29.5.
- Relative pixel rates vs lights: rear hub 0.9966, front hub 0.9904, roof-flap tip 0.974. These are depth differences:
  the flap is about 2% deeper than the wheels.
- Tire diameter: the near-face silhouette radius from the hub centre, taken along the hub row with 50% edge crossings over many frames.
  Rear 53.79 px, front 53.57 px, so D ~107.4 px. The tread side that perspective shows on off-centre wheels was excluded.
- Scale: m per lights-px sigma = mean(0.369/107.58*0.9966, 0.369/107.14*0.9904) = 0.0034147.
- Length: front-most point = front tire (front hub + R); rear-most = tip of the rear roof flap ("extending wire").
  World X computed per feature with its own depth ratio (cx = 960). L = 1.913-1.916 m, constant over frames 30-38.
  Plain straddling pixel extent 551 px * 0.369/107.4 gives 1.89 m.
- Motion convention: t = video frame index / 24 (t=1s -> frame 24, t=1.5s -> frame 36).
  v = backward difference; a = backward difference of the backward-difference speed = x''(n-1) for a cubic.

## Results
| qid | quantity | value | confidence |
|---|---|---|---|
| 348 | length incl. flap | 1.914 m | medium-high (scale +-1%, flap-depth correction 1%) |
| 349 | v(1s) | 3.937 m/s | high (v_bd 48.04 px/frame) |
| 350 | a(1s) | 1.478 m/s^2 | medium: other conventions give x''(24)=1.25, x''(23.5)=1.37, Blender-1-index x''(22)=1.71 |
| 351 | v(1.5s) | 3.938 m/s | high |
| 352 | a(1.5s) (decelerating, magnitude) | 1.248 m/s^2 | medium: central x''(36)=1.48, Blender-1-index x''(34)=1.02 |
