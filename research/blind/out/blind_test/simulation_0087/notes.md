# simulation_0087 — top-down view, bike (constant speed, moving right) + Cybertruck-like car (accelerating, moving left)

Video 1920x1080, 24 fps, 54 frames. Frames 0 and 1 identical (motion starts at ~frame 0/1). Static camera (bike pixel speed constant 21.15 px/f in both halves).

## Tracking (scripts: edges2.py, car_edges.py, mirror.py, tm.py, feat.py, an4.py, final.py)
- Clean background composited from frames 0/53; subpixel silhouette edges (th 30/60 on |I-bg|).
- Bike: rear edge 21.148 px/f, front-wheel edge 21.044 px/f (rms 0.15 px); length ~169.6 px near image centre (th30 170.0 / th60 168.7); wheel axis row 430.3.
- Car: front-edge (dark face) track frames 2-49, mirror centroids frames 17-53, template track frames 2-50, rear edge frames 37-53.
  All rigid features give constant velocity ratios (perspective): front edge = mirror/1.0208, template = mirror/1.010, rear = mirror, roof-rear edge = mirror*1.0097
  -> camera height ~35-45 m, f ~3900 px (FOV ~27 deg).
- Car pixel acceleration (mirror units) NOT constant: ~0.70-0.71 px/f^2 for frames 4-26, rising to ~0.83 by frame 50. a(23-24)=0.701, v(23->24)=16.70 px/f.
- Car silhouette length 574.9 px (frame 53, front at top edge), mirror-to-mirror width 249.6 px (rows 563.5-813.1), body w/o mirrors ~213 px.

## Scale
- Bike prior 5.07 m/s -> 0.01004 m/px at wheel axle height; perspective (car mirrors ~1.1 m) -> car mirror-height scale ~0.00983.
- Car prior 4.03 m/s^2: if taken at 1.0 s -> 0.00998 m/px; if taken where a_px~0.71 (early frames) -> 0.00985. Used s_car = 0.00985 m/px (compromise; spread ~1.5%).

## Answers
- 123 car accel @1.0s: 0.701*576*s = 3.97-4.03 -> 4.0 (high confidence)
- 124 bike length: 169.6 px with bike-edge scales -> 1.70 m (high)
- 125 car length: 574.9 px * 0.00985 -> 5.66 m (high; 5.61-5.72)
- 126 car width (AABB incl. side mirrors): 249.6 px -> 2.46 m (medium: body-only would be ~2.10 m)
- 127 distance @0.5s: dx 18.33, dy 2.56 (origins = silhouette centres, dz~0.45 assumed) -> 18.5 m (medium-high)
- 128 distance @1.0s: dx 14.29, dy 2.56 -> 14.5 m (medium-high)
- 129 car speed @1.0s: 16.70 px/f *24*s -> 3.96 m/s (high)
