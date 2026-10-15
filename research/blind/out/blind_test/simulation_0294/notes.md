# simulation_0294 (2D sim, butterfly flying right->left, side view)
- Blue HSV mask bbox per frame (track.py, track.txt). Linear fit of bbox centre x over frames 0-63: -31.3 px/frame = 751 px/s.
- Scale from prior 0.32 m/s -> 4.26e-4 m/px. Depth roughly constant (shadow y constant, size ~constant).
- 1026 wing length: horizontal (front-back) wing extent: flat wings 420-513 px, raised wings ~400-410 px; used ~470 px -> 0.20 m. Low confidence (ambiguous which dimension; span is along line of sight and unmeasurable; span estimate ~0.24 m).
- 1027 displacement 0.5-1.0 s (frames 12->24): bbox centre moved 363.5 px -> 0.155 m; constant-speed 0.16 m. Answer 0.157. Medium-high confidence.
