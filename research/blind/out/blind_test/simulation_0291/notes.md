# simulation_0291 (V2SC, 2D side view, fish swimming left, 2560x1440, 24 fps, 72 frames)
Method: median-background subtraction at full res (max-channel diff > 8, open/close), fish mask verified by contour overlay (frame 36).
- Pixel speed: linear fit of centroid / left / right edges over frames 8-70: 531-534 px/s (constant, no vertical motion).
- Scale: 0.67 m/s / 532 px/s = 1.259e-3 m/px.
- Length: bbox width median 606 px (590-615 across fin animation), manual frame 36 nose 1245 -> tail tip 1848 = 603 px -> 0.76 m. Confidence medium-high.
- Height: bbox height 294 px (dorsal fin top to lower tail lobe) -> 0.37 m. Confidence medium (fin pose / AABB convention).
- Displacement 0.5-1.0 s: constant speed -> 0.67*0.5 = 0.335 m (measured centroid 267 px -> 0.337 m). Confidence high.
