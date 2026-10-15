# simulation_0088 (V2MX, 2D sim, 24 fps, 30 frames, 1920x1080)
Scene: static camera looking up at sky; eagle ("big bird") and crow/raven ("small bird") fly leftward horizontally
at same image row (body line y~553). Video frames 0 and 1 are identical (duplicate first frame).
Camera static: phase correlation of high-passed sky texture gives ~0 shift.

Method: per-frame mask = colour distance from median sky colour; connected components per bird; subpixel extents of
max-darkness profiles (thr 30/60). Eagle length constant 137-138.7 px across x=69..1504 -> no perspective, planar scale valid.
- Big bird: beak/tail edges linear, 119.55/119.71 px/frame -> 2871 px/s. Scale s = 17.98/2871 = 0.006262 m/px.
- Small bird: 73.22/73.25 px/frame (frames 2-24) -> 11.01 m/s (constant).
- Distance @0.3s (frame 7, t*fps=7.2): bbox centres 975.5 vs 1343.65 (dy~2 px) -> 368 px; wing-root centres give ~373 px;
  relative speed 46.4 px/frame, so frame 7.1 hedge -> ~372 px -> 2.33 m. (Frame-alignment risk: if GT is at video frame 8, 2.60.)
- Big bird length 137.5-138.7 px -> 0.863 m. Wingspan: flaps, projected span 175-324.5 px (period ~12.6 frames);
  used max (flat wings) ~325 px -> 2.035 m (realistic eagle). If GT were at start pose (183.6 px) it would be 1.15 m.
- Small bird length 85.5-86.3 px -> 0.539 m; span 107-163 px (period 9), max ~162.6 -> 1.018 m.

Confidence: 130 high; 132, 134 high; 131 medium (origin + frame alignment); 133 medium (pose choice); 135 medium-high.
