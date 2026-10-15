# simulation_0063 - notes

## Camera model (fixed camera, level, roll 0)
- Horizon v=527 from regression of 5 identical streetlights (v_base = v_hor + k*(v_base-v_top), resid <1 px; k=0.6262).
- Vanishing points (curb lines, constrained to horizon 527): VP1 x~-114 (road D1), VP2 x~5030 (cross road D2).
  Perpendicular roads -> f = 2172 px (HFOV ~53 deg). Range of VP-based f 2153-2213.
- depth_info verified as Euclidean RANGE (bike/van displacement directions only parallel to road with range convention; optical-Z gives 10-20 deg errors).
- Camera height above road h=2.182 m from the PRIOR (white van a=4 m/s^2): van side windows tracked (subpixel, 4 edges,
  rms 9 mm), mapped onto van side plane (offset from wheel-ground contacts), quadratic fit a=4 -> plane offset 28.25 m -> h.
- Cross-checks at f=2172: bike (depth pair + wheel contacts) h=2.173; pedestrian (pelvis range + feet) h_sidewalk=2.168;
  van depth pair -> half-width 0.94 m (plausible); taxi centre range frame 38 = 22.87 vs 22.95 given. All consistent within ~1%.
  (An earlier VP2 estimate 4875 led to an inconsistent f~2240 solution; the refined VP2 resolved it.)

## Answers
- 1293 taxi speed @2.5 s: wheel-contact template tracks (multi-scale, fixed template) -> ground plane -> car centre;
  quadratic fits + backward difference at frame 60: 4.05-4.08 m/s. Answer 4.07. Confidence medium-high.
- 1294 lane width: no lane markings; road D1 width 11.77 m, cross road 10.9-11.15 m. Answer 11.4 (assumes "lane" = road strip).
  Confidence LOW (could be half-road ~5.7).
- 1295 van height: roof silhouette at v=529-530 (just below horizon) -> 2.14-2.15 m. Confidence medium-high.
- 1296 van length: near-side body corners 5.40 m (frames 66,71), wheelbase 3.70; + bumper rounding/protrusion -> 5.6. Medium.
- 1297 taxi length: side view frames 14-20 (perpendicular view) 5.29 (near plane) / 5.51 (centre plane); depth-anchored 5.42. Answer 5.42. Medium.
- 1298 taxi height: roof-sign top 1.62 m (frames 60, 71); roof 1.47 (=Crown Vic). Medium-high.
- 1299 taxi width: tire contacts FL outer / FR inner -> outer-outer ~1.96 +body -> 1.98. Medium.
- 1300 bike wheel diameter: vertical tire extent 43-45 px on bike plane -> 0.63-0.64 m. Medium.
- 1301 traffic light height: 4 instances, ratio dv/(v_base-527)=2.31-2.36 x h_sidewalk 2.168 -> 5.05 m. Medium.
- 1302 streetlight height: h_sidewalk/k = 2.168/0.6262 = 3.46 m. Medium-high.
- 1303 pedestrian avg speed: ground displacement frame0->71 3.63 m / 2.96 s = 1.226 m/s; depth-based 0.58-1.58 s: 1.21 m/s. Answer 1.23. Medium-high.
- 1304 pedestrian height: standing at frame 0, 242.5 px -> 1.85 m (walking frames ~1.80). Answer 1.84. Medium.
- 1305 bike avg speed: head template track (constant speed, accel ~0) on bike plane 26.97 m -> 5.33 m/s. Medium-high.
