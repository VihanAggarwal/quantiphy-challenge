# simulation_0067 — measurement notes

Video: 2160x1080, 72 frames @ 24 fps, static camera. Video frames 0 and 1 are identical (duplicated first frame).
Objects: white van ("white car", accelerating up-left along road A, heading 127.5 deg), yellow taxi (turns right
into the cross street), cyclist, pedestrian on right sidewalk, static purple Mercedes-W123-like sedan, static green car.

## Camera
- Vanishing points from sub-pixel refined curb/road edges (w/vpref.py, vpref2.py): road-A VP (119,-45), cross-street
  VP (2711,-46) -> horizon y=-45.3, roll ~0; f = 1106 px from orthogonal VPs (principal point = image centre),
  HFOV ~89 deg, tilt ~28 deg.
- Scale (camera height H): van rear hub tracked by template matching (hub_RL.json, 72 frames); ground-plane track
  is a perfect parabola (rms 1.2 mm normalized; cubic term ~0), so a = 4 m/s^2 gives H - z_hub = 6.747 -> H = 7.11 m.
  Sensitivity: horizon +/-2 px -> H +/-0.05.
- Cross-checks: (a) pedestrian depth (range to pelvis) gives H 7.05-7.18 depending on foot/pelvis convention and
  sidewalk height; foot-under-pelvis consistency favours sidewalk ~flush and H~7.1. (b) range convention (Euclidean)
  is required: optical-axis Z would need H ~8.8 for the pedestrian, inconsistent. (c) van depth_info fits an origin at
  ground-level box centre (between axles, centred laterally) with a 2-frame offset. (d) the static purple car comes
  out at real W123 size (wheelbase 2.78 vs 2.795).

## Answers
| qid | quantity | answer | method / confidence |
|---|---|---|---|
| 1347 | taxi speed @2.5 s | 4.1 m/s | Both visible taxi tyres tracked (frames 30-71). Speed at the car centre (0.95 m to the left of the tracked right tyres) ~4.09-4.15 for frames 56-66. Medium-high. |
| 1348 | lane width | 12.2 m | No lane markings. The road is 12.0-12.4 m curb to curb (both streets agree, from projected curb lines). The van drives on the road centreline, so "lane" is read as the road strip. LOW: if it means one traffic lane, the value is ~3-4 m. |
| 1349 | van width | 2.1 m | Brake-light centreline l=0.99 (triangulated over 41 frames). The left side is at -0.03 and the right edge ~2.0 (rear views), so the body is ~2.04 m; the small mirrors were added. Medium. |
| 1350 | van length | 5.7 m | Rear about -1.1 m and front bumper about +4.57 m from the rear hub (box fit + bumper ray/plane). Medium. |
| 1351 | van height | 2.2 m | Third brake light triangulated at z=2.21 m. Side-silhouette roof edge is 2.1-2.13 m. Box hull fit gives 2.04 m, which underestimates. Medium. |
| 1352 | taxi length | 4.8 m | Two-tier car-model fit, frames 50-62: body 4.68 m. Frame-0 left-side corner-to-corner is 4.72 m, plus the bumpers. Medium-low. |
| 1353 | taxi height | 1.65 m | Roof sign triangulated over frames 40-66: text top about 1.24 m above the tyre hubs (hub ~0.37 m), plus about 0.05 m to the housing top. Medium. |
| 1354 | taxi width | 1.85 m | Plate and sign centreline is 0.94-0.98 m inboard of the right tyre faces. The model fit gives 1.63 m at the beltline, and tumblehome was added. Medium-low. |
| 1355 | bicycle wheel diameter | 0.66 m | Projected-circle overlays on the front wheel (frames 8 and 16): the outer tyre edge matches r=0.33 m. Medium-high. |
| 1356 | pedestrian average speed | 1.23 m/s | Head track gives 1.217 and feet track 1.237 (1-2 s window averages), heading 37.6 deg. Medium-high. |
| 1357 | pedestrian height | 1.82 m | Head top on the vertical through the depth-anchored pelvis gives 1.85-1.87 m. Head lean was corrected; the foot-based estimate is about 1.81 m. Medium. |
| 1358 | bicycle average speed | 5.4 m/s | Rider-head track at z=1.61 m gives 5.43, constant speed. Front-hub positions give 5.35. Medium-high. |
| 1359 | purple car width | 1.72 m | Two-tier fit gives 1.40-1.43 m at the beltline (the far side is hidden), plus tumblehome. Consistent with a W123 (1.79 m). Medium-low. |
| 1360 | purple car height | 1.45 m | Two-tier model fit gives a roof of 1.42-1.46 m. Medium-high. |
| 1361 | purple car length | 4.6 m | Model fit gives 4.43 m, plus the front chrome bumper overhang. Medium. |

Scripts are in w/ (cam2.py camera model, track.py tracker, vanbox/vanfit*, car2/car3 two-tier fitter, tri3.py
brake-light triangulation, taxitri.py, ped2.py/pedzc.py, wheelfit.py, bike.py).
