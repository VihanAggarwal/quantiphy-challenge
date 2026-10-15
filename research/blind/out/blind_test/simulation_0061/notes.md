# simulation_0061 - notes

## Camera (fixed, 2160x1080, 24 fps)
- Vanishing points from fitted curb lines: main road VP (1772, 475.5); cross street VP (-5846, 477) (two full-width curb lines each fitted to 0.25 px rms).
  Orthogonal VPs -> f = 2187-2191 px. Horizon row at centre column 475.8 -> pitch 1.66 deg down, roll ~0.
- White van (prior a = 4 m/s^2): template-tracked front wheel, projected on its straight lane line -> quadratic fit gives
  a = 4.06 at f=2200 (4.00 at f~2235) and v(0)=0.02 m/s (van starts from rest). Used f = 2200 px (HFOV ~52.3 deg).
- Camera height from depth_info (range convention verified): bike f14/f38 -> H = 2.814/2.817 m; taxi f14 four-wheel centre gives
  range 40.03 vs given 40.10; pedestrian (off-axis) consistent with range (not optical-axis Z). H = 2.817 m.
- Sidewalks slightly raised: pedestrian anchor/feet rows and curb face suggest ~0.03-0.05 m (used 0.03-0.04 for objects on sidewalks).

## Answers
- 1269 taxi speed at 2.5 s: multi-scale template track of the taxi grille (frames 35-71), rays intersected with grille-height plane
  (grille height from f38 anchor) -> local fits around frame 60 give 4.07-4.12 m/s; column-only VP check 4.09. Answer 4.10. (medium-high)
- 1270 lane width: no lane markings; distance between the two curbs of the main road (ground-plane back-projection) 12.20-12.28 m
  (cross street 12.4-12.9, less precise). Answer 12.25 (interpretation risk: if a "lane" is half the road, ~6.1).
- 1271 white van length: side-on view at f70 (heading 87 deg to LOS) bumper-to-bumper on near-side plane 5.95 m; rounded-box fits at
  f46/f50 5.79-5.91; wheelbase 3.65-3.75. Answer 5.9. (medium-high)
- 1272 taxi length: wheelbase 2.875 m (frame 0 near & far wheels, heading = cross street verified by far/near wheel columns);
  frame-0 rounded-box fits 4.96-5.21, near-side corner analysis ~4.9 + bumper bulge. Answer 5.1. (medium)
- 1273 taxi height (incl. roof sign): f0 1.626, f38 1.596. Answer 1.61. (medium-high)
- 1274 bicycle wheel diameter: white-tyre outer edges, 26 frame measurements 33.1-35.0 px on the bike's lane line -> 0.631 m median. (high)
- 1275 traffic light height: three traffic-light poles (same asset) give 4.99/4.99/5.03 m (sidewalk at road level) or 4.92-4.96 (sidewalk +4 cm). Answer 4.95.
- 1276 streetlight height: four lamps 3.455-3.503 (sidewalk 0) / 3.41-3.45 (+4 cm), lantern tips ~1 cm above finial. Answer 3.44.
- 1277 pedestrian average speed: walks parallel to main road; anchors give 1.213 m/s over 0.58-1.58 s; full-clip column track
  (VP relation calibrated by anchors) 1.199 m/s linear, uniform. Answer 1.21. (high)
- 1278 pedestrian height: head-top to sole, f38/f50/f71 -> 1.815-1.83 (sidewalk 0) / 1.79-1.80 (+4 cm). Answer 1.80. (medium-high)
- 1279 bicycle average speed: rider template track projected on bike lane line: constant velocity 5.258 m/s (rms 5 mm),
  anchor displacement 5.277 m in 1 s. Answer 5.26. (high)
