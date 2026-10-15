# simulation_0288 (V2SS, top-down koi, 2560x1440, 24 fps, 72 frames)
Method: full-res median background; mask = |frame-bg|>9 excluding neutral dark shadow (V<140,S<35), close+fill. Overlays verified (frames 36, 69).
- Fish swims right->left at constant speed; frames 0=1 and 70=71 duplicated. Nose (mask xmin) moves 23.2 px/frame steadily (2012->434 over frames 2..70); slight curved path (y wiggle ~55 px) -> path speed ~23.25 px/frame = 558 px/s.
- Scale: 0.67 m/s / 558 px/s = 0.001201 m/px.
- Length: frame 69 (fish straight, horizontal) x-extent 658 px -> 0.790 m (conf. medium-high).
- Width: frame 69 y-extent incl. pectoral fins 241 px -> 0.289 m (medium; body-only would be ~0.15 m).
- Displacement 0.5->1.0 s (frames 12->24): nose moved (276, 18) px -> 0.332 m; constant-speed chord 0.335 m -> 0.334 m (high).
