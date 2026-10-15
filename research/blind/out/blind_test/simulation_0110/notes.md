# simulation_0110 - two red blood cells receding from a fixed camera (3D sim, 1920x1080, 24 fps, 72 frames)

## Tracking
- Luma (Y) segmentation (bg Y=206, cell rim ~140, threshold 173), subpixel per-row/column crossings -> extents;
  alpha-weighted centroids. (Chroma is 4:2:0 subsampled, so r-g masks have 2-px steps; luma is full resolution.)
- Script: s2/track3.py -> s2/track3.json. Both cells move in straight lines at constant velocity:
  1/width is linear in frame (rel. rms 0.1%), projective-linear u,v fit rms 0.6 / 0.3 px. No visible rotation (s2/cmp.py).

## Focal length / depth convention
- Triangle: |P(2s)-P(1s)| = 4.7833 m, ranges 17.9557 / 22.715 m, rays from smoothed left-cell centroid at frames 24/48.
  Range (Euclidean) convention -> f = 2644 px (hfov 39.9 deg); Z convention would give f = 5245 px.
- Check by perspective: log(h/w) of both cells vs view-elevation change. Slope S = 1.30 (L) / 1.26 (R) at f=2644, but
  2.66 / 2.47 at f=5245. A rigid disk with aspect 0.537 cannot exceed about 1/aspect = 1.87, and torus or EF RBC models give 1.23-1.34.
  So the range convention with f ~ 2640 holds (it is also the documented convention).
- Time convention: t = frame/24 (frame 24 = 1 s). A shift of one frame changes f by about 2%.

## Answers
- Separation at t=1 (frame 24): left-cell position from range + ray; right-cell depth from equal-size width ratio
  (0.3% further away). The difference is (3.054, 0.049, 0.052) m, so |d| = 3.06 m.
- Diameter: horizontal extent 246.8 px at Z=17.88 m, with the off-axis disk-width factor 1.0045 -> 1.661 m; frame 48 gives 1.659 m. -> 1.66 m
- Thickness: the band from the near-rim crest contour to the bottom silhouette at the near column is 90.3 / 66.1 / 51.8 px
  at frames 0/24/48. It gives T = 0.431 m after near-rim depth correction (circular rim tube). That model with T/D=0.26 and e=22 deg also
  reproduces h/w=0.537 and the measured slope S=1.28, so the picture is self-consistent. Alternative profiles give 0.40-0.44, and an earlier rim+crest 3D
  fit gave 0.428. -> 0.43 m

## Confidence
- 1381 diameter: medium-high (f from triangle; error about 3%).
- 1379 separation: medium-high (same f dependence, plus timing).
- 1380 thickness: medium (profile-model dependent, about 7%; assumes thickness = the cell's own z-dimension).
