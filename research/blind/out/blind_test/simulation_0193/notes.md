# simulation_0193 (Jupiter + Galilean moon models, top-down view)
- Camera looks straight down on orbital plane: the four red orbit rings and moon tracks are circles (common centre 958.1,542.5).
- Tracked moons by median-background differencing (100 frames). Common-centre circle fit radii (px): Io 159.66, Europa 205.04, Ganymede 267.30, Callisto 414.72. Uniform angular speed (periods 5.34/10.66/21.39/42.68 s).
- Pixel speeds (omega*R*fps): Io 187.9, Europa 120.8, Ganymede 78.5-79, Callisto 61.05 px/s.
- Scale from prior: 0.627 / 61.05 = 0.010270 m/px (all objects in same plane; perspective on Jupiter's silhouette negligible).
- Moon diameters from edge half-max profiles + thresholded equivalent diameter (green channel, 4x upsample): ~11.7-12.4 px (blur/shading -> +-1 px, ~8% uncertainty). Jupiter silhouette ~170 px (168-171).
- Confidence: speeds & orbital diameters high; Jupiter diameter good; moon diameters medium.
