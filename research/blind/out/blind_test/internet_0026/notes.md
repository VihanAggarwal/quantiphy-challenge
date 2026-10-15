# internet_0026: toy truck pushed toward a sitting baby (29 frames, 24 fps)

Prior: the sofa's total height is 90 cm. Video type 2D, so the main scale is one cm-per-pixel value taken from the sofa.

## Measurements (1920x1080, frame 0)
- **Sofa:** red-colour mask, measured column by column. The backrest top is at y≈152-156 and the floor contact at y≈521 on the left to 539 near the baby. The arm top is at y≈130. Pixel height is 368-415 depending on where it is measured; I used about 395 px, so **0.2278 cm/px**.
- **Baby:** head top y≈377, bottom on the floor y≈664-668, so the sitting height is about 288 px.
- **Truck:** red/blue/yellow HSV mask, with an overlay checked visually. Length (cab front to dumper rear) is about 306-310 px. Height (dumper rim top y≈468 to wheel bottom y≈720) is about 252 px.
- **Man and baby:** bbox centres are about 990 px apart. Measured between floor or body positions, the gap is 1140-1170 px.
- **Camera:** it moves. KLT tracking shows a slow dolly/pan that speeds up over the clip. The floor near the truck shifts about 54 px over the clip; the far background shifts about 60 px and the window sill about 77 px, so there is parallax. Frame timing is uneven: per-frame displacements alternate between large and small.
- **Truck image speed** (front-edge track, polynomial fit): 326 px/s at 0.5 s and 312 px/s on average. With the floor shift removed (camera compensated) it is 365 px/s and 358 px/s.

## Perspective check
Floor-tile vanishing point is at (1572, -237). f is about 2750 px (from the orthogonality of the tile directions), the camera tilts about 16° down and sits about 1.74 m high. The baby is about 16% closer to the camera than the sofa back, and the truck about 22% closer. Physical values from this model:
- baby sitting height 59 cm
- truck length 58 cm, truck height 49 cm
- baby-man floor distance 2.15-2.46 m
- truck speed with camera compensation: 69 cm/s at 0.5 s, 67 cm/s average

## Answers
Mostly the plain 2D pixel ratio, which is the likely annotation method, shaded slightly toward the physical values:

| qid | Question | Plain ratio | Physical | Answer | Confidence |
|---|---|---|---|---|---|
| 2130 | Baby sitting height (cm) | 65.6 | 58.9 | **64** | medium |
| 2131 | Baby-man distance (m) | 2.26-2.65 | 2.15-2.46 | **2.35** | low-medium |
| 2132 | Truck length (cm) | 70.4 | 58.2 | **68** | medium |
| 2133 | Truck height (cm) | 57.4 | 49 | **56** | medium |
| 2134 | Truck speed at 0.5 s (cm/s) | 74.3 | 68.7 | **74** | medium |
| 2135 | Truck average speed (cm/s) | 71.1 | 67.4 | **71** | medium |

For the two speeds, the plain-ratio column uses raw image motion. With the camera motion compensated and the same flat scale, the speeds would be 83 and 82 cm/s. That option was judged less likely.
