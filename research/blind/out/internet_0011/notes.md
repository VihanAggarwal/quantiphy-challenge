# internet_0011 — top-down drone view of basketball half court (4K, 107 frames, fps 25 per inputs; container says 20.43 fps)

Scale: prior "court width = 4.88 m" = NBA lane (key) width (16 ft). Key line centres at x~1414-1419 and ~2489-2496 (4K, frame-0 coords)
-> 1077 px = 4.88 m -> 220.7 px/m. Check: baseline->free-throw line 1289 px = 5.84 m (NBA 5.79 m); restricted arc radius ~1.22 m OK.
Camera: drone drifts slightly (ECC homography: ~0.9% zoom, few px shift over clip) -> all frames aligned to frame 0 before measuring.
Tracking: median-background subtraction on aligned frames (1920 scale), per-player centroid / core (opened mask) / bbox centre, plus
manual head/torso clicks on zoomed aligned crops at f0 and f106.

White player: head f0 (1575,605) -> f106 (2100,1965): 6.61 m; centroid 6.57; core 6.61; bbox 6.48; torso 6.49. Path ~ straight.
  -> displacement 6.55 m; average speed = 6.55 m / ~4.26 s (106-107 frames at 25 fps) = 1.53 m/s.
Black player: f0 under the rim (partially occluded by rim/backboard; blob contaminated). head (2006,462)->(2125,1228): 3.51 m;
  torso (2030,440)->(2140,1160): 3.30 m; blob centroid 3.25; bbox 3.19 -> 3.35 m.
Initial distance (f0): heads 2.06 m; torsos/centroids 2.0-2.23 m -> 2.1 m.
Caveat: image-plane scaling with ground-plane key width (annotator-style). Players' torsos/heads are 1.2-1.9 m above ground with drone
~15-25 m up, so true ground displacements may be ~5-12% smaller. If GT used container fps (20.43), speed would be ~1.25 m/s.
Confidence: 2053 medium-high, 2054 medium (fps ambiguity), 2052 medium, 2055 medium (which body point is clicked).
