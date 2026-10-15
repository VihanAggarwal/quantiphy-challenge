# simulation_0031 - boat / person / eagle on a beach (960x960, 75 frames, 24 fps)

## Camera model (the main finding)
- Vertical lines are exactly parallel in the image: cliff basalt columns (best shear 0.000), mast (-0.004),
  davit pole (0.000), wheelhouse edges (0.000). That means a camera with **zero pitch and zero roll**.
- The boat stays level on the water. Its waterline and the underwater parts do not move relative to the
  hull in frames 0-60. Its image scale change (1.000 -> 0.975) matches the depth ratio 130.35/133.74.
  For a level path with a horizontal camera, the principal point has to be about 790 px **above** the
  image top: a large vertical lens shift (horizon at y ~ -790).
- Focal length from the boat's own horizontal geometry, fitted jointly with its heading. Lengthwise
  lines are the deck rails (slope 0.355) and the roof port edge (0.32-0.34). Crosswise lines are the mast
  yards (-0.137) and the door top (-0.127). Best fit f ~ 6750 px (Monte Carlo 5-95%: 6250-7500); boat
  heading ~31.5 deg from the optical axis, which matches the motion heading of ~29 deg.
  f = 3200 has an rms misfit of 10 deg.
- Independent checks of a shallow ~12 deg view: (a) the spread eagle wings are almost horizontal in the
  image (measured slope -0.05; f=6600 predicts -0.09, f=3200 predicts -0.40); (b) the person's shadow
  is thin (~3 px); (c) the wheelhouse roof's visible area.
- The FOV range 8-103 deg caps f at 6864. Chosen f = 6600 px (FOV 8.3 deg), cx' = 480, cy' ~ -789.

## Person prior vs depth info
- The person's ground contact (the shadow line at the feet) moves down 41 px in 3 s. The shadow is
  horizontal, and by t=3 it covers the ground where the feet stood at t=0. So the person **walks toward
  the camera** (Z falls ~2.8% over 3 s). The per-cycle image displacement also grows ~0.85%/s.
- So the human depth_info (139.95 -> 139.98, constant) does not match the video at t=2. The naive
  constant-depth calibration (f~3200, 3.07 m tall person) is physically inconsistent: it needs a ~25 deg
  downhill path, and it conflicts with the boat, eagle and shadow geometry.
- With f=6600, D_person~140 m at t=1 (supported by terrain: the person is ~0.7 m above the water level
  taken from the boat's waterline) and a gentle ~2 deg beach slope, the person's speed is ~1.3 m/s, which
  matches the prior. Gait: cycle 35.5 frames, so the feet are planted with no sliding.

## Answers (f = 6600 px)
- 1123 human height: image height 76 px (mid-stance), f/Z = 48.7 px/m at D=139.95 -> **1.58 m**
  (f range 6250-6864 gives 1.51-1.66). Confidence medium.
- 1127 boat speed: cabin template track plus depth at t=1 and t=2. V = (-1.87, 0, +3.39) m/s,
  |V| = **3.87 m/s**. Constant velocity is consistent with the track. Confidence medium-high.
- 1125 boat length: stem at u~98; transom corners at u~303 (port) and u~357 (starboard); local
  Jacobian 51 px/m, heading 31.5 deg -> **9.2 m** (plus or minus 7% from heading). Confidence medium-low.
- 1126 boat width: hull beam ~2.0-2.2 m (cabin is 1.32 m wide, far bulwark offset). The davit arm
  reaches ~0.8 m outboard to starboard. Hedged **2.4 m**. Confidence low.
- 1124 boat height: mast top (v=433) to the lowest visible underwater appendage at the stern (v~918):
  8.3 m. Above the waterline it is 7.7 m. **8.3 m**. Confidence medium-low.
- 1129 eagle speed: centroid at frames 24 and 48 (same wing-beat phase) plus depth. V = (5.4, 0.1, -9.9),
  **11.3 m/s**. The flight is level, which supports the model. Confidence medium.
- 1130 eagle wingspan: fully spread frames 5-6 and 31-33 show 72-75 px (low threshold). The wing axis
  is foreshortened about 0.89 (heading ~29 deg) -> **1.76 m**. Confidence medium-low.
- 1128 eagle length: the body is not resolvable (~10-15 px, heavily foreshortened). Taken as
  ~0.41 x span -> **0.72 m**. Confidence low.

## Main risk
If the ground truth used a world where the person moves at constant depth (f~3200), all sizes would be
~2.1x larger, with boat speed ~4.9 and eagle speed ~15.2. The geometric evidence strongly rejects that
world.
