# simulation_0257 (A2MC, 2D, 40 frames @30fps)
Plant (pot succulent) released from rest at ~frame 0 near top of frame, free-falls onto table (~frame 15).
- Template matching (frame-10 template) on frames 0-14; quadratic fit frames 4-14: a = 6.90 px/frame^2 (resid <0.5 px), release n0 = -0.06 frame.
- Scale: 9.8 / (6.90*900) = 1.578e-3 m/px (at plant depth).
- Speeds (backward diff, constant g): v(n) = 9.8*(n - n0 - 0.5)/30 -> f6: 1.817, f12: 3.776 m/s (scale-free; raw diffs 38/80 px agree). High confidence.
- Plant: height ~64 px (65 at frame 10, 69 at frame 0 seen from below), width ~48 px -> 0.101 m, 0.0757 m. Medium.
- Table: front edge 518..1538 (1020 px), back corner 1523; plant lands near back -> ~1000 px at plant depth -> 1.578 m. Telephoto view, perspective ~3%. Medium-high.
- AC (LG unit): 132..637 = 505 px -> 0.797 m (depth assumed ~ plant depth). Medium.
- Phone right of plant: 1142..1192 = 50 px -> 0.079 m (x-extent). Medium.
