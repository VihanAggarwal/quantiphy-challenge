# simulation_0191 (2D, 120 fps, box free-falls onto catering truck roof)
- Tracked box bottom edge (HSV brown mask, cols 560-800) frames 0-58; quadratic fit -> a = 1737-1784 px/s^2 (~1760), release at t~0 from rest, lands ~frame 61.
- Scale: 1760 px/s^2 / 9.8 = 179.6 px/m.
- Box: 408 px wide (x 530-938), ~196 px tall (front face 212-408) -> 2.27 m, 1.09 m. (medium)
- Truck: x 122 (rear lamp bracket) to 1840 (mirror) = 1718 px -> 9.57 m; top of roof rails y~348 to ground 1062 = 714 px -> 3.98 m. (medium)
- Tire: ~165 px -> 0.92 m. (medium)
- Speeds: free fall from rest at t=0, backward difference v = g*(t - 1/240): 1.92, 3.88 m/s. (high)
