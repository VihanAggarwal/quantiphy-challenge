# internet_0068 - acorn pulled by string (2D, static camera)
Method: background = frame 96 (empty scene). Diff mask (>40, opened 15x15) gives acorn extents; acorn crosses frames 53-74.
Position = midpoint of trailing/leading edges (cancels motion-blur bias; L-only gives a=3690, R-only 5155 px/s^2).
Quadratic fit frames 59-72 of midpoint: a = 4421 px/s^2 (row-averaged midpoint variant: 4474); residual ~1.5 px. Used 4440.
Scale = 0.77 / 4440 = 1.734e-4 m/px (frame width ~33 cm).
Height: stem top y~536 to body bottom y~966 at frame 60 -> 430 px -> 7.46 cm.
Velocities = instantaneous from fit (central): 2565, 3007, 3892 px/s -> 0.445, 0.521, 0.675 m/s.
(forward 0.1s differences would give ~0.48/0.56/0.71; backward ~0.40/0.48/0.64.)
Displacements (frames 60->63->66->69->72), avg of two midpoint tracks: 277.9, 326, 371.5, 410.7 px -> 4.82, 5.65, 6.44, 7.12 cm.
Confidence: displacements/height medium (scale hinges on noisy accel prior); velocities medium-low (convention).
