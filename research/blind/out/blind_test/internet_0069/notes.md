# internet_0069 (cup pulled by string, static camera, 2D)
Method: background subtraction vs frame 0; per-frame cup body left/right edges (rows 650-1000), frames 54-84.
Quadratic fits of leading edge / centre over 2.0-2.6s: pixel accel ~1530 px/s^2 (range 1520-1640; trailing edge alone 1075, noisy).
Scale 0.32/1530 = 2.09e-4 m/px. Cup height ~550 px (rim top ~505 to base ~1055 at t=2.5s) -> 11.5 cm.
Velocities (fit, px/s): 1830, 1985, 2140, 2290 at 2.0/2.1/2.2/2.3 -> 0.383/0.415/0.447/0.479 m/s.
Displacements: 191 px, 427 px, 490 px -> 4.0, 8.9, 10.2 cm.
Confidence: medium; dominated by accel-scale uncertainty (~10%).
