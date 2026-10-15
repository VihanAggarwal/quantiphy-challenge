# simulation_0258 (A2MC, 2D planar view, fixed camera)
Scale: pen falls (released ~t=0, horizontal, 65 px long), tracked by differencing vs frame 0 over frames 4-15.
Quadratic fit: a = 6154 px/s^2 -> 1.593e-3 m/px (prior g=9.8).
Speeds (backward diff of fit, 30 fps): f6 -> 1.85 m/s, f12 -> 3.81 m/s (high confidence).
Sizes (pixel extents x scale): plant ~61 px tall (leaf top 808 to pot base 869) -> 0.097; plant ~47 px wide -> 0.075;
table top 518-1539 = 1020 px -> 1.62; AC 132-636 = 504 px -> 0.80, bumped to 0.82 since AC sits behind table (further depth);
phone horizontal extent ~50 px -> 0.081 (assumes long side along depth). Medium confidence for sizes.
