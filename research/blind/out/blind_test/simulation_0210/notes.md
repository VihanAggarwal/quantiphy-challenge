# simulation_0210 notes
- 1920x1080, 50 frames @24fps, static camera facing wall squarely. Cat walks left->right in front of furniture group (bench+lamp+vase, mirror leaning on wall).
- Cat track (dark-threshold centroid and bg-subtraction bbox edges): 17.8 px/frame = 427 px/s -> 0.0022 m/px at cat depth.
- Perspective: assumed level camera (horizon y=540; wall-floor line horizontal, no visible tilt). Floor contact rows: cat 1031, bench feet 1001/975 (centre 988), mirror base 978, wall base 950.
  Camera height H=(1031-540)*0.0022=1.08 m; scale at floor row y = H/(y-540). Bench/lamp/vase scale 0.00241 m/px (x1.096 vs cat).
- Pixel extents: cat length 306 (avg bbox), height 222 (tail top to paws); bench 1456..~1934 (right end at frame edge, centred via legs/shelf) = 478, height front 201 / rear 184;
  shade 105 h x 216 w; lamp 512..800 = 288; vase 586..799 = 213; mirror top 399, x 1631..1874 (top) / 1652..1902 (bottom).
- Mirror height = H + 141 px * scale near wall.
- Confidence: cat dims high; bench/lamp/vase medium (depth ratio depends on horizon assumption, +-5%); bench length medium (right end cut by frame); mirror medium.
