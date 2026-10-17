# Audit simulation_0307 family (plane: clips 0303 V3SX / 0305 V3SS / 0307 V3SC)

## Family structure
- All three clips are the same render. The plane is in the same pixel position in every frame index, with the same pose and the same camera.
  Only the background changes: 0303 is sky, 0305 is a grey studio floor with the plane's shadow, 0307 is forest terrain.
  The plane bbox per frame matches across the clips to within a few px (cmp.py).
- The prior (22.16 m/s) and depth_info (102.6664 / 121.8263 m) are identical in all three. The plane must have one length and one width.

| qid | clip | quantity | current | provenance |
|---|---|---|---|---|
| 1471 | 0303 | length | 14.4 | agent (3D KLT cloud, f=3470, fps 25) |
| 1476 | 0305 | length | 14.2 | agent (triangulation + shadow planform, fps 24) |
| **1481** | **0307** | **length** | **10.0** | **agent: OUTLIER** |
| 1472 / 1477 / 1482 | 0303/0305/0307 | width | 18.4 / 19.0 / 17.8 | consistent (within about 6%) |
| 1473 / 1478 / 1483 | all | displacement 0.5-1.0 s | 11.08 | constant velocity verified, so 22.16 x 0.5 |

## Why 1481 = 10.0 is wrong
The 0307 agent took the left wing boom (about 9.6-9.85 m) as "the longest fore-aft element". It states that the
"nozzles/ventral fins end around -4.2 to -4.8". That is false. The plane has a centre-line tail cone with a ventral fin that
extends about 3.5-4 m behind the nacelle nozzles. In frame 1 its tip is at px (1898, 933), the pointed end at the right of the
silhouette. The 0307 agent read this element as part of a boom/nacelle pair.

## Re-measurement (my own, scripts track*.py, recon2.py, pool*.py)
- Method: KLT tracks with a forward-backward check, then a pure-translation model. All tracks share one FOE: (-750.7, -477.1) from
  0307 alone and (-748, -475) pooled, with median track rms 0.66 px.
- Per-track frames-to-contact n_j comes from 1/rho being linear in the frame index. That gives Z_j = (22.16*cos(phi)/fps)*(n_j + i).
- Body axes: fore = V, and roll 0 (the horizon passes through the FOE), so lateral = V x up.
- Top view (frames/topview_pool.png):
  - left boom: fore +5.6 to -3;
  - nacelle nozzles: about -4;
  - centre-line tail cone tip: about -8.1 to -8.5, seen in 0303, 0305 and 0307 tracks alike (0307 tracks rms 0.45 px);
  - wingtips: lateral +/-9.
- 0307's own tracks only (tracks3_0307): fore extent 13.4 m (fps 24) or 12.9 m (fps 25), from the tail tip to the canopy-side probe.
  The f dependence is under 0.5% for f 3470-3590. This is a lower bound, because the boom nose is not tracked on the dark background.
- Pooled tracks (adding the 0305/0303 boom-nose and wingtip corners):
  - f=3480: length 14.33 / width 18.64 at fps 24, and 13.76 / 17.89 at fps 25.
  - Length/width ratio is 0.77 regardless of scale.
- fps check (fpscheck.py), origin at the 3D bbox centre, frames 25/50:
  - With fps 25 the depth labels are reproduced: d1 102.5-103.0 and d2 121.6-122.2, origin shift 0.2-0.4 m.
  - With fps 24 the origin would have to sit about 4.7 m aft of the centre, and d2 is still off by 0.3 m.
  - So the scene is probably 25 fps, as in 0303's metadata, which makes the length about 13.8. Either way it is 13.8-14.3.

## Decision
- Route A (re-measured on frames, scale from the speed prior): 13.8-14.3 m.
- Route B (family siblings, other methods): 14.4 (0303) and 14.2 (0305).
- The routes agree within about 4%. The current 10.0 is 28-30% below every route.
- Fix: **1481: 10.0 -> 14.2**, consistent with the family.
- Widths (17.8-19.0) and displacements (11.08) are left unchanged. My span of 17.9-18.6 sits inside the family spread.
