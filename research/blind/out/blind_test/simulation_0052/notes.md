# simulation_0052 - notes

Scene: static Blender camera (1080x1080, 30 fps) looking roughly perpendicular at a building wall. Far sidewalk carries a hydrant
and two streetlights. Orange Kia-Stinger-like car drives right->left decelerating (stops at ~frame 87). Dark-green classic car
drives right->left fast in the near lane (frames ~29-50).

## Camera
- Vertical vanishing point from building pilaster edges and lamp poles: tan(pitch)/f = 4.45-4.5e-5 -> camera pitched up ~3.85 deg.
- Focal length (the key unknown), several routes:
  1. Orange car: prior a=-2.86 m/s^2 vs the pixel acceleration of the roof shark-fin antenna (centreline): 281 px/s^2 ->
     centreline scale 0.01018 m/px. With range(1)=15.436 m (origin on centreline, pixel ~(630,723)) -> f ~ 1503 px.
     Near-side features (wheel templates) move 1/0.948 faster than the fin -> they sit ~0.8 m nearer than the centreline.
  2. Green car: range pair (10.25 m @1s, 12.768 m @2s) + constant-velocity pixel track (69.5 px/frame) + roof-crest/wheel
     velocity ratio (0.91 -> features ~0.86 m nearer than centre) -> f ~1512-1555 depending on path yaw (~0.8 deg, seen as
     vertical drift + pixel-speed increase); 
  3. Ground plane (lamp bases on sidewalk, curb face, car road contacts) consistent for 1500-1530.
  Chosen f = 1515 px (HFOV ~39 deg). Range-pair check: X(0)^2 - X(1)^2 from prior-based displacement matches the given ranges.
- Camera height above road ~1.50 m (from orange near-side road contact row 803 and from the curb base row 783.5).

## Measurements / answers
- Orange length (1214): front tip crosses image column 540 at frame 21.45, rear tip at frame 54.09; world travel between them
  from the prior (a=2.86, stop at t=2.90 s): 5.10 m (f-independent). Confidence: high.
- Orange height (1215): roof crest row 642.9 at centreline depth (Z=15.39), road at -1.50 m -> 1.50 m. Medium-high.
- Hydrant (1211): rows 662.8-757.0 at range-derived depth Z~17.1 -> 1.04 m. Medium (scales with 1/f).
- Streetlight (1212): rows ~365.5 -> 757 (L 392 px, R 391 px) -> 4.46 / 4.40, mean 4.43 m. Medium.
- Streetlight distance (1219): 3D base origins from ranges + pixel rays -> 7.89 m. Medium.
- Curb (1216): vertical face rows 763.5 -> 783.5 (20 px) at Z_curb=16.22 m -> 0.211 m. Medium (bottom edge could be ~785).
- Green speed at 1.0 s (1213): range-pair-constrained displacement, ~11.9 m/s (11.8-12.0 across f/yaw hypotheses). Medium-high.
- Green height (1217): roof crest row 634.3 (above horizon 642.6) at centre depth ~9.57 m + camera height -> 1.55 m. Medium.
- Green length (1218): blur-corrected silhouette 845 px at frame 38, effective depth calibrated with the orange car -> 4.95 m. Medium.
