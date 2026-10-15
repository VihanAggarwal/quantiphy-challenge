# simulation_0223 (S2MC, top-down xiangqi board)
- Scale: piece diameter 85.8 px (half-max/gradient profiles over 7 pieces, 85-86 px) = 0.097 m -> 1.1305 mm/px.
- Board outer rim (orange edge) x 447.5..1489 (top) / 450.5..1485.5 (bottom) -> ~1038 px; y 72.5..1018.5 -> 946 px.
  Length 1.173 m, width 1.069 m. Confidence: good (~3%); slight trapezoid (tilt) and piece-top vs board-plane depth ignored.
- Red general moves straight down column x~960 from frame ~2, leaves board ~frame 41. Tracked by difference vs last frame.
  Video has duplicated frames (9=10, 11=12, 18=19, 20=21, 28=29, 34=35): content belongs to the later index; first copy dropped.
- Track fits constant accel ~1.08 px/frame^2 (cubic rms 0.15 px). Backward-difference speeds: 0.335 / 0.689 / 1.033 m/s at 0.5/1/1.5 s;
  acceleration ~0.70 m/s^2 (cubic gives 0.73/0.70/0.67). Confidence: good.
