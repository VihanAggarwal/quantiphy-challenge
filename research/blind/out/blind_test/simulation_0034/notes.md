# simulation_0034 — notes
Scene: static camera (1080x1080, 24 fps, 72 frames). Person walks left->right on a sand bar; red fishing boat approaches the camera head-on (x≈923 constant, i.e. moves along its own ray); eagle flies away from camera.
Static background verified (median bg diff ~0); water is not animated, so median-background differencing segments the person and eagle cleanly.

## Scale / camera
- Person pixel height (head top to sole, half-max edges + visual zoom): 65–67.5 px, mean ~66; used 66.3 px <-> 1.75 m
  (small allowance for walking pose being lower than the standing height).
- f (optical-axis Z) = 66.3 * 92.19*cos(4.9°) / 1.75 ≈ 3480 px (HFOV ≈ 17.6°). Range-vs-Z only changes results by <0.3% here (all objects within ~6° of the axis).
- Only one route to f (the person); every size answer scales with it. Check: eagle wingspan comes out at ~1.75–1.8 m and boat ~9.4 m tall / ~3–3.4 m wide — all plausible.

## Boat
- ECC affine scale tracking of cabin/hull templates: 1/scale is linear in time (resid 0.0006) => constant velocity.
  Image-scale ratio t1/t2 = 1.045 vs depth ratio 1.0436 => the visible front features sit ~3 m ahead of the origin (consistent with origin at mid-boat).
- Speed = (96.8995-92.8490)/1 s = 4.05 m/s, motion is along the line of sight (x constant; depression ~2°) -> 4.05 m/s.
- Height at t=1 (frame 24): antenna tip y≈200.5 to keel bottom y≈544.5 => 344 px (checked at frames 0/48/71 for consistent scale). With an effective depth of 95.9 m: 9.42 m.
- Width: hull beam 111 px (866.5–977.5) => 3.04 m. Including the crane/davit arm on the port side (left edge at x≈851.5, ~3 m forward): 3.40 m.
  Answer 3.35 is a hedge toward the full-asset bbox, which includes the crane.

## Person
- Centroid x pixel speed 48.2 px/s (linear, steady); y 2.1 px/s. With the ranges at t=1/2, the Z drift is ~0.11 m/s.
  3D speed 1.278 m/s; +~1% for the pelvis gait oscillation in the frame-wise speed average => 1.29 m/s.

## Eagle
- Range 91.69 -> 103.43 m/s => radial speed 11.74 m/s. Wing extent x depth is constant across three flap cycles
  (frames 4, 32, 54: ~6000–6200 px·m), so the range grows linearly (constant speed).
- Transverse motion from the cycle-averaged centroid: ~1.28 m/s lateral, ~0.63 m/s vertical => |v| = 11.83 m/s.
- Wingspan: largest horizontal wing extent (wings near flat) x depth ≈ 6150 px·m => 1.76 m; wings are never perfectly flat in the sampled frames => ~1.78 m.

## Confidence
1139 boat speed: high. 1144 eagle speed: high. 1142 person speed: high (±3%).
1140 boat height: medium (±4%: depends on person px height and the depth offset). 1143 wingspan: medium (±6%).
1141 boat width: medium-low (3.04 hull-only vs 3.40 with the crane).
