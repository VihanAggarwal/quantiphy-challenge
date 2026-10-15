# simulation_0026 (S3MC: boat + walking person, beach scene, 960x960, 75 frames @24 fps)

## Camera / scale
- Static camera. Person height prior 1.75 m; person pixel height (half-max of head-top / feet-bottom edges, bg-subtracted,
  frames 14-74) = 53.3-54.1 px, use 53.8 px -> at range 114.83 m: f = 53.8*114.83/1.75 ~= 3530 px (HFOV ~15.5 deg).
  Cross-checks (weak, plausibility): wheelhouse door ~1.84 m, railing ~0.8 m at the boat's depth with this f.
- Range vs Z convention irrelevant here (all objects within ~7 deg of the optical axis, cos > 0.99).
- Horizon is NOT well constrained (boat FOE gives y~455, beach/shoreline consistency suggests y<=395 => boat bobs);
  shown that L and H change < 0.3% for horizon 241..455.

## Boat (3D reconstruction)
- Boat moves left & away: range 103.157 -> 106.091 m (t=1->2), image track -91.8 px/s; 3D heading ~45 deg from image
  plane (FOE x ~ -2980 px). Wheelhouse side/aft faces both visible -> bow points left-away, stern (transom) faces camera-right.
- Origin assumed at hull mid-length on centerline; centerline vertical plane through origin along heading; image points
  (bow tip, transom centre, mast top, keel bottom) intersected with that plane at t=1 and t=2 (independent, agree to 0.15%).
- Length (bow tip to transom centre) L = 10.31 m (f 3480..3580 -> 10.39..10.24). Transom-centre location +-0.3 m.
- Height (mast top incl. small tip to lowest keel point; hull appears to sit on the water surface, keel visible) H = 9.43 m
  (f range -> 9.57..9.30).
- AABB caveat: if the dataset uses world AABB and the boat is diagonal (45 deg) in world, horizontal AABB dims ~7.7 m.
  Answer for length hedged toward that: 10.0 m (L=10.3 most likely). Height unaffected by yaw; assumes mast included.

## Person speed at 1.0 s
- Range constant (114.8319 vs 114.8356) -> motion perpendicular to line of sight; speed = pixel speed * 1.75/53.8 m/px.
- Torso template tracking: horizontal 12.6-13.0 px/s; vertical descent (terrain slope, stepwise with gait) 3.3 px/s mean,
  5-8 px/s locally around frame 24. |v| = 0.425 (smoothed) .. 0.47-0.49 (local, frame 22-26). Answer 0.45 m/s.

## Confidence
- 1113 height 9.4 m: medium (mast inclusion assumed; f +-2%).
- 1114 length 10.0 m: medium-low (L=10.3 local length; world-AABB-orientation ambiguity could give ~7.7).
- 1115 speed 0.45 m/s: medium (gait bobbing / smoothing ambiguity +-8%).
