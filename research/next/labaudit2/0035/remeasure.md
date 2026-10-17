# 0035 independent re-measure (second measurer) — qids 2619, 2628, 2637

All three rows ask the same question: "velocity of the soccer ball at 1.6 s, in cm/s", on renders a, as and ax of one event, so they share one label.
I did not read notes.md, tr_*.json, xmask_*.json or scripts/ in this folder. All my work is in `rm2/`: the scripts are in `rm2/scripts/`, the tracks are `rm2/track_ax.json` and `rm2/radius_ax.json`, and the PNG/JPG checks are in `rm2/frames/`.

## Timing
- Each video has 49 frames at 24 fps. The step lengths show two dropped capture frames. Soccer-ball step from video frame 11 to 12 is (+32,+20) px, about twice the (+16,+10) px steps around it. Basketball step from video frame 35 to 36 is -9.5 px, about twice the -5 px steps around it.
- The drops fit the mapping capture j = floor(i*25/24 + 0.5) exactly, with capture frames 12 and 37 dropped.
- So t = 1.6 s is capture 40 = video frame 38, and the forward step goes to capture 41 = video frame 39. This holds whether the label used the 24 fps or the 25 fps index.

## Pixel track
- Source: render ax (green screen). Soft-alpha centroid, plus a subpixel circle fit to the alpha = 0.5 edge.
- Second tracker on render a (grey background, bright/dark threshold): agrees to within about 0.5 px per frame.
- Near capture 40 the ball moves in a nearly uniform roll after the collision (capture 31 to 49). The step is (-3.0, -3.1) px per capture frame. At video 38 the ball centre is at (499.0, 351.1) and its diameter is about 44.6 px.

## Depth and geometry
- In depth_info, the second "t=1.6s soccer 2.412 m" entry is actually the basketball. It matches the basketball's range on the floor plane, 2.521 - 0.116 = 2.405.
- Soccer-ball surface range at 1.6 s is 3.052 m, so the centre range is about 3.147 m (radius about 9.5 cm).
- Camera model: f = 711, principal point (640, 360).
- Floor plane fitted from:
  - the 4 ToF points, with the ball centres at heights R_s and R_b above the floor, and
  - size-based trajectories of both balls (range proportional to 1/diameter, anchored at the 1.6 s ToF value).
- Result: camera pitch about 35.75 deg, camera height about 1.9 m.
- Cross-check of the plane: the vertical vanishing point from the locker seams gives pitch 31.5 deg, which is within 5 deg of the plane fit.

## Route 1: ray-plane intersection of the pixel track (main)
- Linear fit over capture 31 to 49, evaluated as the capture 40 to 41 step.
- Ball centre speed: 67.4 cm/s (lateral 46.0, range rate 49.2).
- Label-style speed (the visible surface point at range 3.052 m): **66.4 cm/s**.
- Variants:

  | Variant | Speed (cm/s) |
  |---|---|
  | Plane from ToF points only | 68.0 |
  | Plane from trajectories only | 64.6 |
  | f = 680 | 68.4 |
  | f = 750 | 64.3 |
  | f = 800 | 62.1 |
  | R_s from 8.5 to 10.5 cm | 65.2 to 68.2 |
  | Principal point moved by 20 px | 66 to 67 |

- Raw single-step difference from capture 40 to 41 with my own centres: 70.9 cm/s.

## Route 2: apparent size gives the range rate
- Lateral speed of the surface point: 44.6 cm/s.
- Range rate from the slope of log(diameter):
  - capture 31 to 49: 37 cm/s, which gives a total of **58 cm/s**.
  - shorter windows: 19 to 25 cm/s, which gives a total of 49 to 55 cm/s.
- I trust the short windows less. The diameter residuals swing by about ±1 px over roughly 25 frames, which looks like the rolling ball's shape varying with rotation and biases short-window slopes.
- Over the whole track (capture 22 to 49), the size data follows the plane prediction (log-log slope -0.93).

## Route 3: ToF anchors
- From capture 15 (0.6 s) to capture 40 (1.6 s), the ToF centre range grows by 0.294 m. The plane predicts 0.323 m.
- Scaling route 1's range rate by that ratio gives a range rate of about 45 and a speed of about **63 cm/s**.

## Answer
- Label style, noise-free forward difference: **about 65 cm/s** (range 58 to 68).
- Physical ball-centre speed: about 64 to 67 cm/s.
- The current answer of 44 cm/s matches the lateral (image-plane) part alone, about 44.6 cm/s. It leaves out the range increase of about 1.5 to 2 cm per frame, which ToF depth would record.
- Label noise: click jitter and ToF noise in a single-step forward difference push the magnitude up. My Monte Carlo puts the best answer between 66 and 73 under moderate noise. So I would not go below about 63.
- Recommended value for 2619, 2628 and 2637: **65 cm/s**. Confidence: medium.
