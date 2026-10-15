# internet_0060 - pink box dropped beside a wall (video rotated: gravity points to +x in the image)
- Camera drifts slowly (phase correlation: about -0.33 px/frame in x, up to -11 px in y by the end). Positions are corrected for it.
- Box tracked by background subtraction (background = median of frames 75-100); both edges tracked over frames 53-64.
- A plain quadratic fit gives 11.0 px/frame^2, but the acceleration clearly falls from about 13 to about 9 px/frame^2 and the parabola's vertex does not match the release position.
- A drag model a = g - k v|v| fits better (rms 0.85 px versus 2.2 px). It gives g = 12.97 px/frame^2 and is consistent with release from rest at frame ~50.8 from x = 92.
  Scale: 0.84 mm/px near the start. The box looks ~4% smaller at the floor end (perspective), so about 0.88 mm/px there.
- Box: 97-98 x 102-104 px at the start, 94 x 100 px at rest -> about 8.3 x 8.8 cm (the plain quadratic scale would give about 10 x 10.7 cm).
- Floor contact at x = 1419 (box resting), about 1438 in frame-0 coordinates; box bottom edge at t=0 is x = 140 -> 1298 px -> 1.12 m.
- v(2.00 s): backward difference of the centre = 107 px/frame -> 2.78 m/s (free-fall check: 2.84 m/s).
- Displacement 0-2 s: 545 px -> 0.46 m (free-fall check: 0.46 m).
- Displacement 2.2-3.0 s: box lands at about frame 65 and bounces/slides along the floor, from (1375,645) to (1380,972) -> 332 px after drift correction -> 0.29 m.
- Confidence: medium. The scale choice (drag model vs. plain quadratic) is the main risk, about 15-20%.
