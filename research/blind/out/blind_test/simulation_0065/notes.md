# simulation_0065 — notes

Scene: static Blender camera over a 4-way intersection (2160x1080, 24 fps, 72 frames). White van (Chevy-Express-like) drives straight
away up the main street with constant acceleration from rest; cyclist goes straight up the street at constant speed; yellow taxi
(Crown-Vic-like, roof sign) turns right into the cross street at ~constant speed; pedestrian walks right on the near-right sidewalk.

## Camera
- Main-street vanishing point (4 curb lines, consistent to ~3 px): (807, -196) -> horizon y=-196, zero roll.
- Vertical VP from 6 poles: (1078, ~6857) -> f = sqrt(736*6317) = 2156 px (HFOV 53 deg); cross-street VP predicted 20095 vs measured 20205 (check OK).
  Taxi wheelbase identical at headings 31 deg and 6 deg only for f~2156 (second check).
- Camera height above road H: conflicting routes
  * van prior a=4 m/s^2 + rear-face VP-scaling track (a/Z0=0.2198 /s^2, constant over clip) + ground shadow contour moving with van: H = 8.11-8.15
  * van prior + rear-tyre contact: ~8.1-8.2; pedestrian pelvis depth: 8.13 (+curb)
  * bike depth difference + wheel-contact track: 7.96 (rim bias -> ~8.03); taxi absolute depth with centre origin: 7.99-8.05
  * van depth difference is inconsistent with the prior (implies a=3.64), treated as unreliable.
  Adopted H = 8.10 m (all answers scale ~linearly; +/-1.5% band). Depth convention: Euclidean range fits better than Z-depth.
- Curb ~0.08 m (far-curb face strip), sidewalk plane at 8.02 m below camera.

## Measurements (H=8.10)
- 1318 taxi avg speed: per-frame 3-part silhouette model fit (profiled body + cabin + sign, chamfered corners; dims fitted jointly
  on 11 frames, poses per frame), centre track smoothed (poly deg 4-8) -> path 11.9 m over 71/24 s -> 4.02 m/s (speed ~constant 4.0;
  manual wheel-contact centres frames 38-71 give 3.9-4.2). Confidence: high.
- 1319 lane width: no lane markings. Curb-to-curb main street width 11.63 m (cross street 11.5). Lane = half road (2-lane) -> 5.8.
  Alternatives 11.6 (whole road) or 2.9 (4 lanes). Confidence: low (interpretation).
- 1320 van height: rear-face plane from prior/shadow-consistent depth Z0=18.17 m at t=0.58; roof-rear edge (above 3rd brake light) 2.27 m;
  triangulated roof-front silhouette 2.15 (lower bound). Answer 2.26. Confidence: medium.
- 1321 van width: rear body 1.97 m; mirror tips triangulated over frames 14->40: span 2.48 m. Bbox likely includes mirrors -> 2.38 (hedged). Confidence: medium-low.
- 1322 taxi length: profiled model fit 5.14 m (box-corner extremes 4.95-5.03 before rounding correction). Confidence: medium.
- 1323 taxi height: roof 1.45 m, roof sign top 1.605 m -> 1.60 (sign included). Confidence: medium.
- 1324 taxi width: body 1.89, mirror-to-mirror 2.03 -> 1.97. Confidence: medium.
- 1325 bike wheel diameter: wheel hidden behind rider (seen from behind); typical asset value 0.68. Confidence: low.
- 1326 traffic light height: base-to-sign-apex, two identical lights: 4.98 and 4.96 -> 4.97. Confidence: medium-high.
- 1327 pedestrian speed 1-2 s: torso centroid on plane z=1.3 -> 1.17; feet 1.16; head 1.10 -> 1.16. Confidence: medium.
- 1328 pedestrian height: head-top ray vs vertical over feet midpoint, per frame median 1.81 (range 1.75-1.86). Confidence: medium.
- 1329 bike avg speed: rear-wheel contact track (ridge detector), linear fit 0.667 H/s -> 5.40; depth-based displacement 5.31 -> 5.37. Confidence: high.
