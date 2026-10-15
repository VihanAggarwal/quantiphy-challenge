# internet_0050 - scooter rider on basketball courts (4K, 30 fps, 94 frames)

## Method
- Camera: handheld, slow drift (+13 px x, -8 px y over 3 s) measured by phase correlation on far background; all
  tracking done in frame-0-aligned coordinates.
- Rider: median-background subtraction on aligned band; body-centroid and front-wheel tracks (frames 0-91; 92-93 mask
  picked a wrong blob). Pixel speed 472 (fit) - 476 (displacement/T) px/s -> 474 px/s. Constant speed, wheel contact
  y constant (~1178) => fronto-parallel motion. Scale at rider depth s_r = 474/2.9 = 163.4 px/m.
- Perspective: VP of court depth lines (2051, 933) -> horizon y_h ~ 933 (roll ~0). Camera height hc = (1178.5-933)/163.4
  = 1.50 m. Pole bases y: left 1154.5, right 1165 -> pole scales 147.4 / 154.4 px/m. Board centre vs pole x offsets give
  Z_pole/Z_board = 1.096 (both stands agree) -> board scales 161.6 (L) / 169.2 (R) px/m (~ rider depth).
  Check: rim heights come out 3.09 m (both hoops) vs regulation 3.05 m -> prior is physically consistent.
- Pixel measurements (frame 0): left board 415-670 x 524.5-704 (255 x 179.5 px); right board 3414-3681 x 510-694;
  left pole x 666, right pole x 3408; bird centre ~ (616, 503); rider cap top ~879, soles ~1153 (273.5 px).

## Answers (naive single-scale vs perspective-corrected; chose value covering both)
- 3117 person height: 273.5/163.4 = 1.67-1.68 (same depth as scale) -> 1.68. High confidence.
- 3118 right stand: naive 4.01, physical 4.00 -> 4.0. High.
- 3119 left stand: naive 3.86, physical 4.03 -> 3.94. Medium-high.
- 3120 bird to ground: centre naive 3.99, physical 4.17; feet 3.85/4.03 -> 4.05. Medium.
- 3121 distance between stands: physical 18.2 (poles or boards), naive pole-to-pole 16.8, naive board-to-board 18.4 -> 17.6. Medium.
- 3122 left board width: naive 1.56, physical 1.58 -> 1.57. High (right board gives 1.60).
- 3123 left board height: naive 1.10, physical 1.11 -> 1.10. High.
