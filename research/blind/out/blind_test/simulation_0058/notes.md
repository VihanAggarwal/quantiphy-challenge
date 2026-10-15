# simulation_0058 - method notes

Scene: static Blender camera at a 4-way intersection (2160x1080, 24 fps, 72 frames; frame 0 duplicates frame 1).
Objects: yellow taxi turning from the left cross road toward the camera; white van (prior a = 4 m/s^2) crossing L->R;
cyclist crossing L->R; pedestrian walking toward the camera on the left sidewalk; static green BMW (front view) and purple Mercedes (rear view).

## Camera calibration
- Main-road vanishing point from curb lines: VP1 = (1261.3, 428.3); principal point assumed at the image centre.
- Focal length from three routes: (a) vertical-pole lean (vertical VP) 2165 +/- 40; (b) convergence of the near and far cross-road curbs (VP2) ~2130;
  (c) the van's measured acceleration equals the exact prior of 4.0 at f ~ 2130-2135 (with the camera height taken from the bike depth). Used f = 2135, roll ~ 0.
- Camera height H = 2.815 m from the bike range (27.1221 m at t = 1.58 s, ground contact under the wheels).
- Checks: van-origin range 30.9-31.07 vs 31.07 given (and 29.78-29.88 vs 29.92); taxi-centre range 25.5-25.6 vs 25.70; bike at frame 14 27.85 vs 27.81;
  near and far lamp posts both 3.43 m tall; taxi wheelbase 2.92 m (Crown Vic 2.91 m); green BMW body width 1.71 m (E24 1.725 m).
- Anomaly: the pedestrian's given ranges are ~4% longer than the foot-based ground-plane geometry gives (pelvis origin offset or scaling?). The pedestrian answers are hedged between the two.
- Sidewalk curb height ~0.06 m, measured from the curb face.

## Measurements
- 1233 taxi speed at 2.5 s: template track of the front fascia (frames 44-71) intersected with its height plane gives a near-constant 4.05-4.13 m/s (the scale route agrees). Answer 4.1. Confidence: high.
- 1234 lane width: no lane markings. Main road curb-to-curb is 11.83 m (cross road 11.85 m). Answered with the full road width. Confidence: low, because the definition is ambiguous.
- 1235 van length: front bumper (frame 50) and rear bumper (frame 62) located on the near-side plane and tied together by the rigid template track. 5.94 m. Confidence: medium-high.
- 1236 taxi length: side views at frames 2 and 9 with a box model (rear end to the far-front corner): 5.06-5.11. Answer 5.15 to allow for corner rounding. Confidence: medium.
- 1237 taxi height: top of the roof sign is 1.68 m (frames 60 and 71 agree); roof without the sign is ~1.47. Answer 1.63 (hedged). Confidence: medium.
- 1238 bike wheel diameter: vertical tire extent of ~51 px on the bike plane (Y = 26.97 m) gives 0.645 m. Confidence: high.
- 1239 streetlight height: near-left lamp 3.425 m and a far lamp 3.437 m. Answer 3.43. Confidence: high.
- 1240 pedestrian speed 0-1 s: the bearing-based track on the walking line X = -8.85 gives 1.11-1.12 m/s; the given depths imply ~1.19. Answer 1.15. Confidence: medium.
- 1241 pedestrian height: head top over the ground point gives 1.79-1.83 (mean 1.81); the depth-scaled value is ~1.88. Answer 1.84. Confidence: medium.
- 1242 bike speed: constant 5.35-5.37 m/s over frames 13-71 (the bike is occluded earlier); slightly reduced for the duplicated first frame. Answer 5.34. Confidence: high.
- 1243 green car width: body at the front corners is 1.71 m and mirror-to-mirror is ~2.05 m. Answer 1.96 (leaning to the mirror-inclusive bounding box). Confidence: medium.
- 1244 purple car width: rear corners 1.70, bumper 1.74, mirrors ~1.79. Answer 1.78. Confidence: medium-high.

Scripts are in w/ (C.py = camera model; van2.py, bike3d.py, taxispeed.py, vanlen.py, taxilen.py, ped*.py).
