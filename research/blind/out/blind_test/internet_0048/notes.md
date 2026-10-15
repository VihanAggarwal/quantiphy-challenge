# internet_0048 notes
- Camera drifts slowly (phase-corr on wall strip): ~-0.21 px/frame x, -0.39 px/frame y; compensated.
- Ball (colour track frames 34-60) projectile: vertical a = 3708 px/s^2 -> 2.643 mm/px at ball depth (g=9.8). Fit rms 1.8 px.
- Ball diameter ~90 px -> 23.8 cm (basketball, consistent). Answer 24 (high conf).
- Horizontal vx 1950 px/s -> v(1.5s, apex) = 5.16 m/s; disp 1.2-1.8 s = 3.10 m (high conf).
- Ball bottom at apex row 351 (f45), floor contact row ~870 at bounce (f61, +5.8 px drift) -> 1.39 m gap (med; center height would be ~1.51).
- Floor-seam vanishing point (Hough+RANSAC) row ~608 at f0 -> horizon. Ball contact is 33 px below wall base -> wall ~1.12x farther than ball -> wall scale ~2.96 mm/px.
  Pads: 8 pads over 1721 px -> 215 px wide, 629.5 px tall -> 63.7 x 186 cm; standard 2'x6' (61x183). Answer 62 / 184 (med).
- Person: feet ~877 row, horizon-based depth ratio -> 0.93x ball depth -> 2.446 mm/px. Mid-stance height ~715 px incl cap -> 1.75; answer 1.72 (med-low).
- Person speed: torso/head x moves ~555 px between f75 and f105 (drift-compensated) -> 1.36 m/s (med).
