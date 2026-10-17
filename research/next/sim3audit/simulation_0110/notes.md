# sim3audit simulation_0110 (family: simulation_0109, simulation_0110; two red blood cells)

Verdict: no fixes. All 5 rows agree with the family and with my own re-measurement.

## Family table (current answers)
| qid | clip | quantity | current | my re-measure |
|---|---|---|---|---|
| 1377 | 0109 | centre-to-centre distance at t=1 | 3.04 | 3.01-3.05 (equal-size / same-velocity for the right-cell depth) |
| 1379 | 0110 | same | 3.06 | 3.03-3.04 (equal-size depth) |
| 1378 | 0109 | diameter | 1.636 | 1.65 (alpha width 112.7 px, Z=22.0155, f=1500) |
| 1381 | 0110 | diameter | 1.66 | 1.652-1.66 (half-level width 245.3 px @f24, 194.3 px @f48, f=2666.7) |
| 1380 | 0110 | thickness | 0.43 | 0.39-0.45 depending on rim profile; torus 0.433 |

The two clips agree within 1.5% on the shared quantities, so neither clip is off by a scale factor.

## Camera
- Both clips use the Blender default camera (50 mm lens, 36 mm sensor): f = 1500 px for 0109 (1080 wide) and
  2666.7 px for 0110 (1920 wide). With these f values, the depth_info (Euclidean range) and the tracked rays reproduce the speed prior:
  4.781 / 4.783 vs 4.7833. The triangle alone gives 1499-1502 for 0109 and 2653-2658 for 0110. In 0110 the motion is almost purely radial,
  so the triangle constrains f only weakly there.
- Scripts: scripts/track.py (luma tracker, track_*.json), scripts/geom.py (f), scripts/sep.py (separation), scripts/axis.py, scripts/profiles.py.

## Thickness (1380): the only row that depends on a model
- Near-rim band (from the occluding crest contour to the bottom silhouette, at the centre column of frame 24) = 66.2 px.
  That matches the agent's 66.1 px. The contour is a sharp luma step (138 -> 117 over 3 px), so it is an occlusion edge, not
  a shading terminator. Using the near-rim depth (~17.3 m), the band is 0.43 m.
- General bound: for any body of revolution, band >= T sin(th). This gives T <= band/sin(th) ~ 0.455-0.46 for th = 68-70 deg.
  So a value near 0.5 is excluded.
- Silhouette h/w = 0.537 and band/w = 0.26 together fit several rim models:
  - torus: th = 67.9 deg, T = 0.433
  - elliptical rim sections with a = 0.15-0.35 R: T = 0.39-0.45
  - The Evans-Fung (smooth dimple) profile does not apply. Its inner flank is too shallow to produce the sharp crest contour seen in the image.
- 0109 shows the cell face-on. Its dimple edge sits at ~0.63 of the radius, which is consistent with the torus and a~0.25 models (T 0.43-0.44).
- Cross-clip check on the view angle: if the 0109 optical axis is exactly the disk axis, then angle(v, n) = 73 deg, which gives th = 70.2 deg in 0110.
  That fits the elliptical rim models with a = 0.15-0.2, which give T = 0.45. This is within 5% of 0.43.
- Conclusion: no independent route gives a value >= 15% away from 0.43. Keep it.
