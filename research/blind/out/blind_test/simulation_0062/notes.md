# simulation_0062 - notes

Scene: static camera, level, looking straight down a main road (vanishing point = image centre (1081,539.4); principal point (1079.5,539.5)).
Cross street perpendicular to the view. White van (the "white car") and bicycle cross left->right at constant depth;
yellow taxi turns right from the cross street toward the camera; pedestrian walks toward camera on left sidewalk.
Video 2160x1080, 72 frames @24 fps; frames 0 and 1 are identical (static first frame).

## Calibration
- Van rear template track (frames 19-71, NCC): pure lateral motion, x(i) quadratic, acc = 0.5331 px/frame^2 (rms 0.28 px)
  -> 307.1 px/s^2; prior 4 m/s^2 -> k = f/Z_nearside = 76.77 px/m.
- Van depth info (Euclidean range convention verified: no vertical/scale drift -> constant Z, d14^2-d38^2 fits lateral motion):
  origin X offset solved from d14^2-d38^2 = 45.0 -> X38 = -2.73 m, Z_c = 29.18 m.
- f = k * (Z_c - 0.96) = 2166 px (hFOV ~53 deg; ~36 mm on 36 mm sensor).
- Van tire bottom v=617.6 -> camera height H = 1.0175 m; fH = 2204.
- Curb ~0.04 m (curb-face band), sidewalk top = 0.04 m.
- Cross-checks: taxi depth at f14 reproduced within 0.7%; bike tire contact depth within 0.5% of depth-info.

## Answers
- 1280 taxi speed @2.5 s: front-tire contact depth Z=fH/(v-cy) frames 50-71, linear (rms 0.016 m) -> 4.06 m/s; lateral ~0.15 m/s. -> 4.05 (high conf).
- 1281 lane width: no markings. Main road curb-to-curb 11.77 m (curb base lines slopes -0.256/+0.131), cross street 12.03 m.
  Taxi drives exactly at the centre of the right half on both roads (half-width ~5.9-6.0 m). Ambiguous: full road ~11.9 vs one lane ~6.0.
  Hedged answer 7.0 (low conf).
- 1282 van height: roof silhouette 453 px, tire 617.6 -> 2.14-2.18 -> 2.16 (med-high).
- 1283 van length: frame 71 extents 1578 (far-rear corner) to 2058 (near-front corner) with depths Z_c+-0.98 -> 5.80-5.85 -> 5.83 (med-high).
- 1284 taxi length: 3D footprint fits at frames 0/7/14 (rear bumper corner, grille centre, far-front corner, rear-wheel contact),
  estimates 4.86-5.28, median ~5.08 (low-med).
- 1285 taxi height incl. roof sign: sign top half-max at frames 7,14,60,71 -> 1.61-1.63 -> 1.62 (roof alone ~1.41) (med).
- 1286 taxi width: frontal view f71: body 1.83-1.91 m, mirrors ~2.02 m -> 1.95 (med).
- 1287 bike wheel: circle fits to white tire ring, outer half-max radius ~26.0 px at Z=26.94 -> 0.65 m (med-high).
- 1288 traffic light: two instances, base on sidewalk + sign apex -> 5.00 / 4.99 m -> 5.0 (high).
- 1289 streetlight: near post, plinth base v=685.5, top 182.3 -> 3.40 m (far instance 3.29, less precise) (med).
- 1290 pedestrian avg speed: hair-top / hair-centre tracks + depth info -> Z slope 1.22-1.25 m/s, X const -6.05 m -> 1.24 (med-high).
- 1291 pedestrian height: K=(cy-v_top)*Z=1811 -> head top 1.854 m above road minus 0.04 sidewalk -> 1.81 (med-high).
- 1292 bike avg speed: rider template 17.81 px/frame constant, Z=26.94 -> 5.32 m/s (5.24 if static first frame counted) -> 5.3 (high).
