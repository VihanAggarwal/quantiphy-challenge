# simulation_0066 — method notes

Scene: fixed camera above a 4-way intersection (2160x1080, 24 fps, 72 frames). Objects: white van (accelerating south),
yellow taxi (turns right from southbound into westbound), cyclist (south, constant speed), pedestrian walking west on NW
sidewalk, parked green BMW-like coupe, parked purple W126-like sedan.

## Camera
- Curb lines (RANSAC on colour-segmented road/sidewalk boundaries) + 6 vertical poles -> 3 orthogonal vanishing points.
  Joint fit: f = 854.6 px (HFOV 103.3 deg), pitch 28.4 deg down, roll 0.15 deg, rms 0.14 px. Principal point = centre.
- Scale (camera height h): van side-plane warp track (NCC, 62 frames, rms 3 mm) is a perfect parabola; acceleration in
  h-units 0.5714 * 1.0054 (scale calibrated so triangulated tyre contact lands on Z=0) -> h = 4 / a' = 6.96-7.00.
  Cross-checks: pedestrian range depth 7.05-7.1, van z-depth 7.13, bike z-depth ~6.95, taxi wheelbase = Crown Vic.
  Used h = 7.0.
- Depth convention: bike and van depth pairs fit optical-axis Z with plausible origins (bike: within 0.1 m), pedestrian
  fits Euclidean range. Only used as scale cross-check.

## Answers
- 1330 taxi speed @2.5 s: plane-induced warp of taxi south door panel (plane Y=13.4-13.5) frames 48-71: 4.16-4.23 m/s
  (backward diff at f60 4.19; slight deceleration). Silhouette tangent rates agree (4.05-4.2). -> 4.18. Conf: high.
- 1331 lane width: no lane markings; both roads 11.8-12.0 m curb to curb; cars sit in halves (right-hand traffic,
  taxi turns right into north half) -> half road 5.95. Conf: low (could be full road 12 or ~3 m lanes).
- 1332-1334 van: body width ~2.0 (east roof edge 9.45 vs west side 7.44); east mirror triangulated X=9.77 -> mirror
  span ~2.55; answered 2.45 (hedge toward bbox incl. mirrors). Length: front plate triangulated Y=9.46 (3 frames),
  rear face 15.2-15.35 -> 5.9. Height: q-top parallax (rear-roof tangent) 2.33, roof centre on rear plane 2.31 -> 2.32.
  Wheelbase 3.89, wheel radius 0.38.
- 1335-1337 taxi: motion-parallax triangulation of silhouette tangents during westbound straight phase: front X=-5.90,
  rear X=-0.35 -> L 5.5 (after side-plane correction). Roof sign top Z = 1.635 (two independent parallax fits) -> H 1.64.
  Width: centre line from sign/track ~14.38 vs body side ~13.37 -> ~2.0 body; answered 2.05. WB 2.92.
- 1338 bike wheel: projected 3D circle fit to front tyre at f71: outer white band r=0.347, dark ring r=0.31 -> D 0.68.
- 1339 pedestrian avg speed: head-top track over all frames, X-velocity 1.20-1.23 (constant, straight); range-depth
  pair gives 1.17-1.21 -> 1.22. 1340 height: head top above sidewalk (curb 0.14 m) on walking plane 1.77-1.82 -> 1.80.
- 1341 bike avg speed: rider blue-clothing centroid on Z=1.2 plane, all 72 frames, linear (no accel): 5.615 m/s at h=7;
  z-depth pair gives 5.57 -> 5.6. Conf: high.
- 1342-1344 green car (static): wheelbase 2.70; front face X 16.7, rear-south corner X 21.15 -> corner length 4.5, bbox
  ~4.6; front bumper corner-to-corner 1.65 -> ~1.75; roof tangent tYZ 2.587 with far roof edge ~14.15 -> H ~1.45-1.5.
  Conf: medium-low.
- 1345-1346 purple car (static, partly cut off): WB 3.03 (W126 SEL-like); roof edge tangent 1.846 with centre-line
  geometry -> H 1.40-1.42; front bumper span 1.62-1.67 -> body ~1.8, answered 1.85. Conf: medium.
