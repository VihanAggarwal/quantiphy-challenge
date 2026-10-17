# Lab audit round 2: family 0034 (captured_0034b/bs/bx), 21 scored rows (7 questions x 3 renders)

**Result: no fix.** Every current answer is inside the band my two routes allow. I used test inputs only (frames, `prior`, `depth_info`) and no labels.
- Scripts are in `scripts/`. Tracks are in `track_*.json` and `vsize_ax.json`. Crops are in `img/`.
- The 0034a/as/ax rows of the test split are not in this family's scored list. I used camera a's frames as inputs because its depths are the stated ones.

## Setup

**Two cameras, and b is a different take.**
- Camera a is a side view at table height. It is the ToF camera: the stated ranges fit it. The tennis balls appear 73 px (left) and 65 px (right) tall at 1.2 s, against a prediction of 71.6 / 62.7 for 0.706 / 0.776 m surface range at f 711.
- Camera b is a high oblique view from the opposite side of the table, so b-left is a's right ball.
- The motions do not match, so b is a **different take**:
  - In a, the right ball starts rolling at video frame 21-22 and the left ball at 26, after a 1 cm hand pull-back.
  - In b, both balls start at video frame 24-25.
  - No constant time offset reconciles the two balls.
  - The props also sit in different places. Soccer-ball-to-bag spacing is 19 cm in b and 28 cm in a.
- b nevertheless carries a's exact `depth_info`, so its labels are presumably a's annotation (copied). I computed label-style values from camera a and used camera b only for physical sizes, which are the same props.
- The earlier pooling of the a and b direct answers (build_labmot, "one event") therefore pooled two takes. It also probably mixed the left and right balls: a's direct L/R = 63/56, b's = 56/65. The pooled values stay inside the no-fix band below.

**Time base.**
- Both balls show a double pixel step at video 35->36 in a (684->639 px). b-right shows the same jump (697->677).
- So capture 37 is dropped (and capture 12, which cannot be checked because the balls are static then). The mapping is: video k<=11 -> capture k; 12..35 -> k+1; >=36 -> k+2.
- t = 1.2 s is capture 30 = video 29. The forward difference is video 29->30.

**Focal length.**
- Camera b, calibrated from the 4 table-top corners (76.0 x 60.3 cm), gives f = 692-705 px (rms 0.4 px). Its scale is confirmed by the tennis ball: predicted 31.0 px, measured 31 px.
- In camera a, the ball sizes at the stated surface ranges fit f of about 711-730.
- The numbers below use f 711, with f 745 as the alternative.

**Range along the track.**
- The table plane is useless in a: the camera sits about 6 cm above the ball-centre plane, a grazing view. Its plane-route speeds swing from 58 to 76 depending on the click row.
- So the range comes from the ball's vertical image extent (`vsize.py`: top edge, plus the dark SAM outline at the bottom). It is smoothed and scaled to the stated range at video 29 (route **S**).
- Route **C** keeps the stated range constant, i.e. the lateral component only.
- The left ball recedes about 0.6-0.9 cm per frame after 1.2 s: its height goes from 73.5 px to 67 px by video 35, and from 68 to 62 px during the rebound. The right ball approaches slightly (63 to 66 px).

## Label-style values (surface point = stated range along the click ray, forward difference on the 25 fps capture clock)

Sources: `labelstyle.py` and `cross_render.py`. Clicks are hue centroids in the ax, a and as renders, plus template matching on a.

| qids (b/bs/bx) | question | current | label-style f711 (S / C; renders) | f745 (S / C) | physical (centre, f711) | verdict |
|---|---|---|---|---|---|---|
| 2591/2598/2605 | left ball v at 1.2 s | 74.84 | 70.2 / 68.2 (ax), 68.7 / 66.6 (a), 63.8 / 61.6 (as) | 68.0 / 65.9 | 69 | current is 7-17% high: keep |
| 2592/2599/2606 | right ball v at 1.2 s | 74.78 | 64.1 / 63.3 (ax), 65.4 / 64.6 (a), 62.6 / 61.7 (as) | 61.6 / 60.8 | 66 | current is 14-23% high, below 25%: keep |
| 2596/2603/2610 | left ball total distance | 54.38 | 39.7 / 32.6 (all renders within 0.2) | 38.6 / 31.4 | 41.2 / 34.2 | see below: keep |
| 2597/2604/2611 | right ball total distance | 65.03 | 46.5 / 43.9 (all renders within 0.4) | about 45 / 42 | 48.3 / 45.8 | see below: keep |

**Pixel steps at 1.2 s (video 29->30).**
- Left ball: 31.9 px (ax centroid), 31.2 (a centroid), 32 (template, score 0.99), 28.9 (as).
- Right ball: 25.0 / 25.5 / 24 / 24.4 px.
- The left ball is decelerating at this moment. Template steps are 38, 32, 26 and 25 px over video 28->32.

**Total distance.**
- Left ball = forward roll to the collision at video 37 (27.5 lateral, 30.1 with recession) + rebound (5.2 lateral, 9.6 with recession). The rebound runs back-left and away from camera a: the image climbs from y 476 to 470 and the ball shrinks 9%. The 1 cm pull-back is included.
- Right ball = 39.6-40.6 forward + 4.2-6.0 rebound.

**Why the totals are kept although they are about 36-40% above the deterministic value.**
- The current answer = pooled direct answer x the labnoise click/ToF noise factor (1.58 / 1.60). That factor is a deliberate model of how per-frame ToF noise inflates summed path labels.
- With my own camera-a track, the pipeline's emulator (`noise_check.py`, sigma_px 2, moving frames) gives the expected path label below.

  | ToF noise sigma_z | left ball | right ball |
  |---|---|---|
  | 0.5 cm | 42 | about 50 |
  | 1 cm | 50 | about 65 |
  | 2 cm (the fitted value) | 70 | about 100 |

- The current 54 / 65 lies between the noise-free and noisy expectations, matching a ToF noise of about 1 cm. I cannot show it is wrong without labels.
- By the same model, the speeds would be expected at 75-85 (sigma_z 1-2 cm, median). That brackets the current 74.8 from above, while the noise-free values bracket it from below.

## Static rows

| qids | question | current | route 1 | route 2 | verdict |
|---|---|---|---|---|---|
| 2595/2602/2609 | soccer ball diameter | 17.76 | a: silhouette 144 x 142 px at a stated 0.894 m surface range. Physical 19.0 (f 711) / 18.1 (f 745). A label chord with both edge clicks at 0.894 m gives 17.2 / 16.5 | b: table calibration (no stated depth), silhouette 95 x 97 px -> **18.2-18.6** | within 2.5-4.5% of b and inside a's band: keep (agrees with the 17.8 prop transfer to 0016/0035) |
| 2594/2601/2608 | pencil bag length | 19.48 | a: lateral extent 131 px at about 1.05 m -> 19.3. The bag lies a little diagonal: the left end face is visible and the near end is taller, 47 vs 43 px. Per-end ToF depths would give about 20-21 | b: the bag is a triangular-prism pouch with flat ends. Base edge on the table: **19.9**; zipper ridge at h 5.5-7.2 cm: **19.2-19.6** | keep (the raw silhouette PCA of 23.7 includes the end faces; a capsule model, 22.6, is the wrong shape) |
| 2593/2600/2607 | pencil bag height | 7.22 | a: 46-47 px mid-bag at 1.05 -> 6.8-7.0 (6.6 at the near end) | a, per-click depths: ridge about 4 cm behind the front-bottom edge -> up to about 7.9 | within 3-10%: keep |

## Files
- `scripts/track_a.py`: hue track of both balls.
- `scripts/vsize.py`: vertical size per frame.
- `scripts/labelstyle.py`: S/C/P routes.
- `scripts/cross_render.py`: a/as/ax renders and template matching.
- `scripts/noise_check.py`: labnoise emulator applied to my track.
- `scripts/calib_b.py`: camera b from the table corners.
- `scripts/soccer_a.py`, `scripts/soccer_b.py`: soccer ball diameter in each camera.
- `scripts/bag_a.py`, `scripts/bag_b.py`: pencil bag measurements.
