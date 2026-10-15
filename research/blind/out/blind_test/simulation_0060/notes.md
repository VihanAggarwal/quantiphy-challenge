# simulation_0060 - notes

## Camera model (pinhole, principal point at image centre 1080,540, zero roll)
- Road-edge vanishing point (far road curbs, fitted lines): (1208, -42.7) -> horizon y=-42.7; road yaw +3.2 deg.
- Focal length: vertical-pole VP (y~8600) -> f~2170; cross-road curb slope + orthogonality -> f~2280-2320;
  van depth at t=0.58 vs t=1.58 (range convention, origin at wheelbase midpoint, ~0.95 m inboard) -> f~2200-2250.
  Range (Euclidean) convention fits; optical-axis Z convention does not (predicts 21.29 vs 22.73).
  Adopted f=2200 (HFOV ~52 deg), pitch 14.8 deg down.
- Camera height from the prior: van front-hub track (template matching, 70 frames) projected on plane z=0.385;
  quadratic fit of path length gives a=4.01 m/s^2 at H=5.214 -> H=5.20 m (nearly independent of f).
  Van ranges then fit with origin at body centre. Lamp-post heights (3.33-3.40 m at 35-50 m) consistent -> flat ground, horizon OK.
- Depth cross-checks: bike (origin ~hub height) within 1-2%; pedestrian pelvis consistent with sidewalk ~0.1 m;
  taxi ranges are ~3-4% shorter than model with centre origin (unexplained; maybe origin offset).

## Answers
- 1258 taxi speed @2.5s: tire-bottom ground track f56-71 -> 3.99-4.08; roof-sign-top track (z=1.59) -> 4.10-4.29;
  rear-track pixel separation confirms ground-model depth rate. ECC scale was biased (side panel). -> 4.15 m/s (med conf).
- 1259 lane width: far road gray surface between curb bottoms = 11.6 m (to sidewalk top edges 12.1-12.5). No lane markings,
  interpreted "lane" as the road strip -> 11.7 (low conf; half-road would be ~5.8).
- 1260 white van length: silhouette extremes intersected with near-side plane, frames 48-58 -> 5.87 (+bumper rounding) -> 5.9 (med-high).
  Van wheelbase 3.75 m.
- 1261 taxi length: wheelbase measured 2.87-2.93 (broadside f14) / 2.95-3.07 (rear view) ~= real Crown Victoria 2.91;
  rear end always occluded; length from Crown Vic proportions (L/wb=1.85) and partial overhang measurements -> 5.45 (med).
- 1262 taxi height incl. roof sign: f14 broadside 1.57-1.59, f60 rear view 1.56-1.67 -> 1.59 (med).
- 1263 bike wheel diameter: wheel outer width 58-61 px at Z~23.3-23.6 -> 0.62-0.65 -> 0.64 (med-high).
- 1264 pedestrian speed: depth-derived pelvis displacement f14->f38 = 1.195 m in 1 s; head-top ground track 1.21-1.25;
  feet f0->f71 1.11-1.16 -> 1.22 (med).
- 1265 pedestrian height: head top / feet rows at f0,f50,f60,f71 with ground model (sidewalk 0.1-0.15) -> 1.76-1.79 -> 1.77 (med-high).
- 1266 bike average speed: wheel template track f1-56, constant velocity: ground model 5.35, depth chord f14->f38 5.27 -> 5.3 (high).
- 1267 green car width: mirror span 378 px (mirror height ~1 m -> Z~11.6) -> ~2.0 m; rear body 412 px -> ~1.70 m.
  AABB assumed to include mirrors, slightly hedged -> 1.92 (low-med; body-only would be 1.70).
- 1268 purple car width: mirror span 122.5 px at Z~33.5 -> 1.86; front bumper 116.75 px at Z~31.6 -> 1.68.
  Hedged toward mirrors -> 1.82 (low-med).
