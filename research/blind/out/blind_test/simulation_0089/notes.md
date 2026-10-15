# simulation_0089 (S2MX, 2D planar, 24 fps, 1920x1080, 30 frames)
Scene: bottom view of two birds against sky. Big bird (bald-eagle model) flies LEFT, small bird (crow/raven model) flies RIGHT,
both on image row y~555. Frames 0 and 1 identical (animation keyed from frame 1). Big bird exits left at frame 6; small bird exits right at frame 9.
Method: median background (frames 10-29, empty sky), |diff|>40 mask, connected components -> per-frame bbox/edges.
Scale: small-bird length 108-110 px (mean 109.3) = 0.94 m -> s = 0.00860 m/px (single planar scale; no perspective cues,
both birds keep constant pixel length while crossing the frame).
- Big bird length: 174.8 px -> 1.503 m (high confidence).
- Wingspans: y-extent varies with flapping (small 135-205 px, big 230->384 px over frames 0-5). Assumed GT AABB taken at the
  first-frame pose (frame 0 = frame 1): small 169 px, big 230 px; +3% hedge toward larger (max/rest pose) values.
  Big 2.04 m, small 1.50 m (low-medium confidence; if GT uses max/rest pose they would be ~3.3 m and ~1.8 m).
- Speeds (constant): small 91.9 px/frame (beak and tail edges) -> 18.97 m/s; big 150.3 px/frame -> 31.0 m/s
  (big bird off-screen at 0.3 s; constant-velocity extrapolation, track perfectly linear frames 1-6). High confidence.
- Distance at 0.3 s (frame 7): small centre x=1730.5, big centre extrapolated x=-201.8 -> 1932 px -> 16.62 m (medium-high;
  ~+2.5% if t=7.2 frames used).
