# Audit internet_07 (clips internet_0064, internet_0068, internet_0069)

Each clip is its own family, so there are no twins to compare against. The three agent notes were read.
- 0068 (acorn) and 0069 (cup) were filmed against the same wall and baseboard on the same table, but with different camera placements (the baseboard brackets are 1310 px apart in 0068 and 1185 px apart in 0069). Both priors are accelerations.
- 0064 (basketball and person) has the prior g = 9.8 m/s^2.

Only measurements on the frames were used. Scripts are in `scr/`; the small track files are `*.txt`.

## Camera motion
- **0064:** a slow, nearly linear pan of about -0.27 px/frame in x (tx goes from +7 at f60 to -17 at f156) with a small tilt. This does not change g. It biases the person's walking speed by about +2.5%, and that bias is included in the quick check.
- **0068:** a few px of drift and a noisy zoom term (k = 0 to 0.005). After compensation the acorn's acceleration changes by only -1% to +5%.
- **0069:** a real zoom pulse, probably focus breathing as the cup enters the frame. The table-patch similarity fit (`cam69t.txt`) and the two baseboard brackets agree: k rises from about 0.001 (f55) to about 0.010 (f75) and returns to 0 by about f87. Opposite x-shifts of the left and right brackets confirm it (at f72: -1.2 px and +9.9 px). Compensating for it lowers the cup's pixel acceleration by about 3-5%.

## Quick checks (every scored row)

| qid | clip | quantity | current | quick check (route) | diff | verdict |
|---|---|---|---|---|---|---|
| 3213 | 0064 | person height m | 1.74 | 611-638 px x 2.76e-3 = 1.69-1.77 (bg-diff extent, cap to back/front shoe) | <3% | keep |
| 3214 | 0064 | ball v @3.0 s | 2.8 | 2.70 (central diff vx 887, vy -407 px/s; g_px 3506/3565 on the two arcs) | 3.6% | keep |
| 3215 | 0064 | ball v @3.6 s | 5.1 | 5.15 raw / 5.20 fit | 1-2% | keep |
| 3216 | 0064 | person v @4.4 s | 0.93 | torso-band centroid 10.8 px/f + pan 0.27 -> 0.92 | 1% | keep |
| 3217 | 0064 | ball bottom to floor @3.5 s | 1.57 | 1.58 (bounce at f114.1 from the arc intersection, floor y 1059) | <1% | keep |
| 3218 | 0064 | ball disp 3.5-3.7 s | 1.07 | 374 px -> 1.04 | 3% | keep |
| 3219 | 0064 | person disp 4-5 s | 0.82 | torso 275.5 px + pan 8 -> 0.78 | 5% | keep |
| 3220 | 0064 | ball diameter cm | 24.4 | d_eq 84-90 px (87) -> 24.0 | 2% | keep |
| 3243 | 0068 | acorn height cm | 8.0 | about 433 px (stem top ~537 to body bottom ~970) x 1.734e-4 = 7.5 | 6% | keep (the agent notes said 7.46; the source of 8.0 is unknown, but the gap is under 15%) |
| 3244 | 0068 | v @2.0 | 0.445 | cap dark-centroid track, quadratic 59-72: a = 4400 (comp 4390-4530) px/s^2, v = 2561 px/s -> 0.444 | <1% | keep |
| 3245 | 0068 | v @2.1 | 0.521 | 3001 px/s -> 0.520 | <1% | keep |
| 3246 | 0068 | v @2.3 | 0.675 | 3881 px/s -> 0.673 | <1% | keep |
| 3247 | 0068 | disp 2.0-2.1 cm | 4.82 | 279.3 px -> 4.84 | <1% | keep |
| 3248 | 0068 | disp 2.1-2.2 cm | 5.65 | 319.9 px -> 5.55 | 2% | keep |
| 3249 | 0068 | disp 2.2-2.3 cm | 6.44 | 368.4 px -> 6.39 | 1% | keep |
| 3250 | 0068 | disp 2.3-2.4 cm | 7.12 | 411.2 px -> 7.13 | <1% | keep |
| 3251 | 0069 | cup height cm | 10.5 | 545 px (530-561) x 0.32/1430 = 12.2 (full extent); about 11.0 if the cylinder's depth is taken into account (see below) | 5-16% | keep (the two routes disagree) |
| 3252 | 0069 | v @2.0 | 0.3497 | 0.430 | +23% | **FIX** |
| 3253 | 0069 | v @2.1 | 0.3789 | 0.462 | +22% | **FIX** |
| 3254 | 0069 | v @2.2 | 0.4081 | 0.494 | +21% | **FIX** |
| 3255 | 0069 | v @2.3 | 0.4373 | 0.526 | +20% | **FIX** |
| 3256 | 0069 | disp 2.0-2.1 cm | 3.652 | 4.46 | +22% | **FIX** |
| 3257 | 0069 | disp 2.1-2.3 cm | 8.126 | 9.88 | +22% | **FIX** |
| 3258 | 0069 | disp 2.3-2.5 cm | 9.313 | 11.16 | +20% | **FIX** |

## internet_0069 in depth (cup pulled by string)

### What is wrong with the current answers
1. **They break the stated prior.** The current answers equal the agent's own numbers (0.383, 0.415, 0.447, 0.479, 4.0, 8.9, 10.2) multiplied by 0.913. The agent notes do not explain this factor. As a result the current velocities imply (0.4373 - 0.3497) / 0.3 = **0.292 m/s^2**, not the stated 0.32.
2. **The agent's pixel acceleration comes from the leading edge.** The agent got 1530 px/s^2, with velocities of 1830 px/s at 2.0 s, from the leading edge plus a diff-mask "centre". The mask includes the cup's cast shadow on its trailing side. The leading edge of a cylinder seen off-axis does not move like the cup itself:
   - The silhouette width is 452 px at f62 (left of frame), 416 px at f70 (centre) and 450 px at f78 (right of frame). That is the sec(theta) widening of a cylinder away from the image centre, which gives f of about 1550 px.
   - The widening adds about +500 px/s^2 to the leading edge and about -500 px/s^2 to the trailing edge. I measured R-edge 1600-2000 and L-edge 900-1100, against about 1450 for the centre. The agent saw the same split ("trailing 1075").
   - The current answers' implied 1676 px/s^2 sits near the biased leading-edge value.
3. **The camera zoom pulse was not removed.** It adds about 3-5% to the raw pixel acceleration.

### Two independent rigid-body routes
- **Route A:** the midpoint of the body silhouette edges (gradient edges; left edge from rows 560-840, right edge inside the handle hole from rows 640-760). Frame 61 is dropped because the left edge sits at the frame border. Track rms is 0.3-0.7 px.
- **Route B:** template matching of the handle only, without the knot or string, using templates from f64 and f69. f57-60 are excluded because the left baseboard bracket passes behind the handle there.

Route A runs about 1.7 px/frame faster than route B throughout (a 2% silhouette-perspective term). Both routes give the same acceleration on the same window.

| route | window (frames) | a_px raw | a_px compensated | v(2.0) m/s raw / comp |
|---|---|---|---|---|
| A mid | 62-72 / 62-73 / 63-73 / 62-75 | 1483 / 1470 / 1449 / 1455 | 1452 / 1422 / 1403 / 1398 | 0.417-0.428 / 0.425-0.444 |
| B handle | 62-72 / 62-73 / 63-73 / 62-75 | 1425 / 1435 / 1450 / 1455 | 1375 / 1359 / 1369 / 1379 | 0.416-0.426 / 0.439-0.447 |

- Routes A and B agree within 3% on every row.
- The other trackers support the same answer. The knot template gives 1420-1540. The handle-plus-knot template on window 62-75 gives 1485 raw / 1382 comp.
- Two variants were rejected:
  - Intensity-moment centroids failed because auto-exposure and lighting change the background.
  - A small lower-handle template was ambiguous.

### Fix values
I used the constant-acceleration model with a = 0.32 m/s^2 and v(2.0) = 0.430 m/s. This is the midpoint of raw and compensated, A and B (spread +-2.5%).
- Velocities: v(2.1) = 0.462, v(2.2) = 0.494, v(2.3) = 0.526.
- Displacements: 2.0-2.1 = 4.46 cm, 2.1-2.3 = 9.88 cm, 2.3-2.5 = 11.16 cm.
- These match the measured position differences at scale 0.32/1430 = 2.238e-4 m/px. For example, 69->75 gives 11.10 (B) and 11.27 (A); 63->69 gives 9.73 (B) and 9.95 (A).

Other conventions give even larger values. With forward differences, or with the local velocity profile (which is flat over f61-64), the acceleration over [2.0, 2.3] comes out at about 1100-1360 px/s^2. So the proposed values are the conservative (smallest) correction.

### Height (3251) is not changed
- With the full visible extent of 545 px (back rim edge at about 502 to front base edge at about 1061), the height is 12.2 cm.
- The base ellipse (minor semi-axis about 60 px) shows the camera is at about rim height and looks down at the base. The axis length (base-ellipse centre about 998 to rim about 507, 491 px) gives about 11.0 cm, and the front generator corrected for its depth gives a similar value.
- These two routes do not agree within 8%, and 11.0 is within 5% of the current 10.5. So the height is left as it is.

## 0068 / 0064
- **0068:** all rows were confirmed by an independent cap-centroid track: acceleration 4400-4480 raw, 4390-4650 compensated, against the agent's 4440.
- **0064:** g_px is 3506-3600 on both arcs, against the agent's 3531. The ball diameter of 87 px gives 24.0 cm, which is consistent with the ball-plane scale. Every row is within 5%.

No fixes are proposed for 0064 or 0068.
