# simulation_0175 — airplane over rock island (V2MC, 1920x1080, 40 frames @ 24 fps)

## Scale (from prior: plane speed 153.582 m/s)
- The camera is static. The plane flies left and stays horizontal (y is constant), at constant image size.
- Pixel speed is 61.33 px/frame. Sources: centroid fit 61.24, nose-edge fit 61.31, row-band cross-correlation 61.4.
  This gives 1471.8 px/s, so the scale is **0.10435 m/px** at the plane's depth.

## Plane length (qid 420)
- Measured nose tip (faint glass outline) to horizontal-stabiliser tip. The length changes with x in a V shape
  (476 down to 458 and back up to 468 px). This is parallax between the near and far stabiliser tips. The minimum,
  when the tail sits at the principal point, gives the centreline length: ~459 px (456–462 depending on threshold).
- 459 px x 0.10435 = **47.9 m** (ratio is consistent with a scaled CRJ-type jet). Confidence: high (~3%).

## Rear (main-gear) wheel diameter (qid 422)
- There are two dark wheel blobs: the near and far main gear. Their offset grows linearly with x, pointing to a
  vanishing point at about (1004, 588), which is the true horizon.
- Sub-pixel half-max widths, taken perpendicular to the parallax direction over frames 9–32: median ~11.5 px
  (range 10.3–12.6).
- 11.5 px x 0.10435 = **1.20 m**. Confidence: medium (pixel quantisation, ~±8%).

## Stone cliff height (qid 421)
- Depth check: the ocean edge at y=893 is not the true horizon. Wave texture is barely compressed there, and the
  wheel-parallax vanishing point puts the horizon at about y=588.
- The plane's shadow on the water (y≈974) moves at 55.5–56.5 px/frame against 61.3 for the plane, so the shadow
  depth is 1.095 x the plane depth. For ground points, depth ∝ 1/(y−588). This puts the cliff base (y≈1003–1023)
  at 0.97–1.03 x the plane depth, so the single 2D scale applies.
- Rock only: base about y=1023, rock summit about y=628, giving 395 px = 41.2 m (40.3 m with perspective).
  Including the trees on top (tips at y≈522): 501 px = 52.3 m.
- Answer **43.0 m**: a hedge toward rock-only, since the question says "stone cliff" and the rock base may be
  sunk into the sand. Confidence: low–medium; the main risk is whether the bounding box includes the trees (~52 m).
