# simulation_0234 (S2MC, basketball bouncing in front of gym wall)
- Ball: colour-threshold track (track.py). Pure vertical motion at constant image size; diameter 74.6 px (subpixel diff edges, bbox 74-75).
  Scale in ball plane s = 0.282/74.6 = 0.003780 m/px.
- Camera level (backboard edges vertical, baseline horizontal). Horizon ~514-540 (lane-line VP symmetry gives 514; centre 540).
- Ball is in front of wall: floor contact y~1042 vs wall base y=980.5 -> Z_wall/Z_ball = 1.132-1.140 (use 1.136).
- Backboard 358 x 209 px; under-board bracket narrows 328->320 px toward wall -> board ~2.5% closer than wall: Z_bb/Z_ball ~1.108.
  761 length = 358*s*1.108 = 1.50 m; 762 height = 209*s*1.108 = 0.875 m (aspect 1.71, standard). Confidence medium (depth ratio).
- 763 green band (wall) 680->980.5 = 301 px * s * 1.136 = 1.29 m. Confidence medium.
- Motion: bounce at frame 24; fall accel 0.93 px/f^2, rise 0.88 px/f^2 (local quadratic fits, local.py).
  764 v(0.5s, frame 12 backward diff) = 10.86 px/f -> 0.985 m/s; 765 a = 0.93*576*s = 2.03 m/s^2.
  766 v(1.5s, frame 36) = 11.78 px/f -> 1.07 m/s; 767 |a| = 0.88*576*s = 1.92 m/s^2. Confidence high.
