# simulation_0264 (A2SS, 2560x1440, 24 fps, 72 frames)
Spacecraft flies right->left at constant height/depth (bbox height constant 311 px), accelerating from rest; leaves frame ~f67.
Method: background = last frame (empty); |diff|>25 mask, y<1060 to exclude floor shadow; per-frame bbox.
- Nose (left edge) track f2-f52: quadratic fit residual 0.41 px; a = 655.9 px/s^2 (cubic gives ~652-655, i.e. constant accel). v=0 at t~0.007 s.
- Scale: 4 m/s^2 / 655.9 px/s^2 = 0.006098 m/px (nose tip ~ on centreline, so ~origin depth).
- Length: bbox width min ~980 px (f45-49, tail near image centre; off-centre frames inflated up to 1024 px by perspective of depth extent) -> 5.98 m.
- Height: 311 px raw; ~10 px of near-side bottom perspective inflation -> ~305 px -> 1.86 m.
- Speeds (backward difference, constant a): v(t)=a*(t-1/48-0.007): 0.5 s -> 1.89-1.92 -> 1.90; 1.0 s -> 3.89-3.92 -> 3.90.
Confidence: speeds high; length medium-high (+-3%); height medium (+-5%).
