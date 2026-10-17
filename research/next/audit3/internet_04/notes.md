# Audit internet_04 (internet_0022, internet_0057, internet_0058)

Result: **no fixes proposed.** All 27 scored rows were quick-checked on the frames. No row's quick check differs from the current answer by 15% or more.

## Families / cross-clip consistency
- internet_0022 is a single clip: an overhead office desk (S2, mouse width = 57 mm). The camera is static.
- internet_0057 and internet_0058 are listed as separate families, but they show the same gym, basket and person (cap, beige top, olive cargo pants). Both clips use the gravity prior.
  - Person height: 0057 = 1.77 and 0058 = 1.63, an 8.6% gap for the same person. I measured the person's pixel height in both clips and got about the same value (0057: 328-331 px; 0058: 328-332 px).
    - 0058 is clean. Ball and person share a plane, gravity rms is 0.2-1.3 px, g_px is 2005-2017 (204.5 px/m), and the ball diameter of 50 px gives 0.244 m. 1.60-1.63 m is solid there.
    - 0057's scale is less certain. The ball recedes during the shot and back toward the camera after it. g_px is 1932 / 1763 / 1882 / 1849 on the four segments. The average is about 1850 (188-189 px/m), close to the agent's 1837 (187.4 px/m).
    - The 0057 ball diameter is about 48 px, against 50 px in 0058 at 204.5 px/m. That route gives about 196 px/m.
    - At 196 px/m the 0057 rows would all fall by about 4.5%, and 3162 would become 1.68. This is below the 15% threshold and I can't show which scale the ground truth used, so I leave it as is.
  - Basket to floor: 3.05 (0057) and 3.00 (0058). These are consistent.
- 0022 fps: the file header says 16.67 fps; the dataset says 25 fps. With 25 fps the 0.40-1.00 s window (frames 10-25) holds the hand sweep across the desk. With 16.67 fps it would hold an almost stationary hand. I keep the dataset fps (25), as the agent did.

## Quick checks (my route vs current)
| qid | quantity | current | quick check | route |
|---|---|---|---|---|
| 2107 | tea cup diameter mm | 100.5 | 100.7 | outer rim ~182 px on a 2x crop; mouse = 102-103 px (threshold minAreaRect on frames 0 and 35) -> 0.553 mm/px |
| 2108 | saucer mm | 139.5 | 139.5 (Hough 142.7 incl. shadow) | 252 px |
| 2109 | pencil mm | 176 | 175.6 | tip (794,1166) to end (997,922) = 317 px |
| 2110 | shoulder cm | 47 | 48-49 (pixel scale) | jacket shoulder tips ~870-885 px, frame 35 |
| 2111 | table m | 1.88 | 1.87 | top edge ~3375 px |
| 2112 | monitor cm | 69 | 68.6 | iMac top edge ~1240 px (pixel scale) |
| 2113 | notebook width cm | 13.2 | 12.8-13.0 | quad sides 230-233 px |
| 2114 | notebook length cm | 20.6 | 20.2-20.5 | 365-371 px |
| 2115 | hand avg vel 0.4-1.0 s cm/s | 51 | 51.4 | hand (890,1335) at f10 to (1430,1200) at f25 = 557 px / 0.6 s (25 fps) |
| 3162 | person height m | 1.77 | 1.76 @187.4 / 1.68 @196 | 328-331 px |
| 3163 | basket-floor m | 3.05 | 2.93-3.08 | rim y~305, floor contact y~900 |
| 3164 | v ball 2.00 s m/s | 4.61 | 4.34-4.56 | own colour+motion track; quadratic fit on f54-70; 855 px/s |
| 3165 | v ball 3.00 s m/s | 6.35 | 6.18-6.49 | fit on f79-95; 1217 px/s |
| 3166 | ball-basket 3 s m | 1.79 | 1.72-1.81 | ball (1183,561) vs rim centre (962,305) = 339 px |
| 3167 | person-ball 3 s m | 3.2 | 3.05-3.21 | pelvis (600,707) to ball = 601 px |
| 3168 | ball-floor 4 s m | 1.92 | 1.81-2.02 | ball centre y 520.7 (stabilised); bounce centre 876.5, contact 900 |
| 3169 | walk speed 3.5-5.0 s m/s | 1.39 | 1.30-1.37 | cap x 668 -> 1053 (stabilised) = 385 px / 1.5 s |
| 3170 | ball displacement 2-4 s m | 3.75 | 3.61-3.80 | (741,320) -> (1424,521) = 711 px |
| 3171 | person height m | 1.63 | 1.60-1.62 | cap 572 to sole 900 = 328 px @204.5 |
| 3172 | basket-floor m | 3.0 | 2.91 (planar) / 3.05 (standard) | rim y 303 stab, feet 897 stab |
| 3173 | v 1.00 s m/s | 4.1 | 4.01 | parabola f23-62 |
| 3174 | ball-floor 1.00 s m | 3.37 | 3.34 | 897 - 213 = 684 px |
| 3175 | ball-basket 1.00 s m | 1.07 | 1.07-1.09 | 218-223 px |
| 3176 | v 2.00 s m/s | 5.7 | 5.79 | parabola |
| 3177 | ball-floor 2.00 s m | 2.48 | 2.46 | 897 - 394 = 503 px |
| 3178 | ball-floor 1.40 s m | 4.19 | 4.17 | 897 - 44.5 = 852 px |
| 3179 | avg speed 1.4-2.0 s m/s | 2.88 | 2.86 | path 351 px / 0.6 s |

Camera motion: measured by phase correlation on the scoreboard and the right wall.
- 0057: up to (-15, -17) px, handheld.
- 0058: dy from 0 to -38 px, slow tilt.

Both were removed before fitting. For 0058 the raw and stabilised g fits agree within 0.5%.

## Fixes
None. No row meets the bar: two routes agreeing within 8% and a change of 15% or more.
