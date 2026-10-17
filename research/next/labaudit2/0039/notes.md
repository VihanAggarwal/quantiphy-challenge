# Lab audit round 2: family 0039 (captured_0039 / 0039s / 0039x; one event, labels shared)

Input: `../inputs/0039.json`. It has 21 scored S3 rows: 7 questions x 3 renders. None carries a round-1 fix (round 1
found no fixes; see `../../labaudit/0039/notes.md`).

I used test inputs only: frames, `prior` and `depth_info`. I used no labels.

Scripts are in `scripts/`. The camera model is f = 711 px with the principal point at (640, 360). Every frame is held in
memory, and only a few PNG crops are written to `png/`.

**Result: no fixes.** Every row agrees with two independent routes to within 12%: within about 6% for the static rows
and the displacement, and 6-21% for v(1.0). No row comes near the round-2 bars (25% for motion, 12% for static).

## Geometry
- **Table plane** (`plane.py`, x-render median of frames 0-9):
  - Corners: FL (210.5, 535.3), FR (1141.8, 586.8), BR (917.1, 466.3), BL (449.2, 448.0).
  - Vanishing-point route: camera height h = 0.1687 from the front and back edges and 0.1760 from the sides; mean
    0.1724 (the same as round 1).
  - PnP route: h = 0.163, with 3-5 px reprojection error.
  - I use h = 0.1724 +- 2%.
- **Scale checks:**
  - Credit card on the plane (`card3.py`, corners read from intensity profiles): 8.75-8.86 x 5.44-5.77 cm at h, and
    8.57-8.68 x 5.33-5.65 at 0.98h. The ID-1 size is 8.56 x 5.40. So the plane scale is within about 2-3%, and some
    of that is edge blur.
  - Base-front ranges on the plane: bottle 0.997 (stated 0.9998), cup 0.887 (stated 0.874).
- **Dropped frames:** the ball track has one double-length step, at video 35->36: du/dv = -8.3/+8.5 px against about
  -4/+4 px for neighbouring steps, in both o and s. So source frame 37 is missing.
  - The earlier drop (video 11->12) falls while the ball is at rest. Motion energy under the table rises slightly at
    11->12, which is weak evidence.
  - I take the regular 25->24 pattern: capture index = video (k <= 11), video+1 (12..35), video+2 (k >= 36).
- **Time anchors** (plane route; ball centre 2 cm above the table; ToF reads the ball's front surface = centre range
  - 2 cm):
  - Surface range at video 24 (capture 25): 1.015 (o) / 0.999 (s), stated 1.014 at t = 1.0.
  - Surface range at capture 37 (interpolated between video 35 and 36): 0.737 / 0.734, stated 0.737 at t = 1.5.
  - If the stated value is the centre range instead, capture 38 (video 36) fits as well. That is within the 2% plane
    scale.
  - So t = 1.0 is capture 25 (video 24), and t = 1.5 is capture 37 or 38.

## Motion rows

**Ball track** (`track2.py`): a whiteness mask (V > 165, S < 60), with a circle fitted to the upper 75% of the
contour. The pixel residual about a quadratic fit is 0.5 px. The o and s renders agree to within 1-2 px. The x render
is grey-tinted and is not tracked; it shares the label.

### v(1.0) (qids 2721 / 2728 / 2735; current 52.0 / 52.0 / 53.7 cm/s)
The label-style value is |P(cap 26) - P(cap 25)| x 25, with P(cap 25) = 1.014 x ray(click at video 24).

| route | o | s |
|---|---|---|
| A: plane, 3D quadratic fit, forward difference 25->26 (windows video 21-40 ... 23-33) | 59.4-65.6 | 58.8-64.5 |
| A: plane, linear fit (mean speed over the window) | 57.5-62.6 | 55.0-61.8 |
| A: plane, raw per-step 24->25 | 69.9 | 58.1 |
| B: stated anchors (range linear in capture time, 1.014 -> 0.737), raw or smoothed clicks, t1.5 = cap 37 | 59.6 | 59.1 |
| B: same, t1.5 = cap 38 | 55.3 | 54.8 |
| C: apparent size (blur offset fitted to the anchors) | 85-94 | 85-94 |

Route C is rejected. The mask width is an integer number of pixels, and the motion-blur and off-axis widening grow as
the ball nears, so the range rate is inflated. At the anchors it agrees by construction only.

The ball decelerates after the push. Plane-route window speeds (cm/s):

| capture frames | o | s |
|---|---|---|
| 21-25 | 71 | 81 |
| 25-31 | 59 | 57 |
| 31-38 | 60 | 56 |
| 35-42 | 52 | 52 |

The physical speed at t = 1.0 is about 60 +- 4 cm/s. The current 52.0 / 53.7 is 6-21% below the routes, so it is
**not a fix** (the bar is 25%). A value of about 59 would sit nearer the centre of the routes, but the evidence does
not meet the bar.

### Displacement 1.0 -> 1.5 s (qids 2724 / 2731 / 2738; current 27.8 cm)
- Label-style (stated ranges at both ends, clicked centres): 28.50 (cap 37) / 28.66 (cap 38). The o and s renders
  agree to within 0.1, and raw and smoothed clicks agree to within 0.05.
- Plane route: 28.8 / 31.0 (o) and 27.6 / 29.7 (s), for cap 37 / cap 38.
- The current value is 3% below the label-style value. **OK.**

## Static rows (`static.py`, `ballsize.py`; x-render median, intensity-profile edges)

| question (qids o/s/x) | current | A: stated range (label-style clicks) | B: table plane, h +- 2% | verdict |
|---|---|---|---|---|
| pink bottle height (2726/2733/2740) | 21.05 / 21.04 / 20.94 | 20.54 (top 329.5, base-front 477.0) | 20.03 / 20.44 / 20.85 | OK (0-5%) |
| cup rim diameter (2722/2729/2736) | 8.68 / 8.68 / 8.68 | 8.42 at 0.874; 8.96 at the axis range (rim 724.0-794.5, row 381) | 8.55-8.91 (rim in the vertical axis plane) | OK |
| poker tower height (2720/2727/2734) | 10.42 / 10.42 / 10.43 | 10.51 (front-card foot), 10.12 (left foot), 10.03 (mid) | 9.32-9.95 | OK (A within 4%, B 5-10% lower) |
| white ball diameter (2723/2730/2737) | 4.0 | half-max width: 4.19 / 4.29 at rest (plane range 1.27-1.29); 4.22-4.28 at t = 1.0; 4.5 at t = 1.5 (motion blur) | ping-pong ball, stated 40 mm in 0021/0022/0028/0033 | OK (blur adds 1-2 px) |
| cup-bottle distance (2725/2732/2739) | 17.99 / 17.94 / 17.94 | 18.06 (centre clicks (664.5, 403.5) and (759.5, 436); +-15 px vertically: 18.04-18.08) | 17.87-18.61 (axis to axis, or front mid-height points) | OK |

Notes on the static rows:
- **Poker tower.** The flat card in front of the tower measures about 10 x 5 cm on the plane (rough corners), so the
  cards are not standard 8.9 cm poker cards and a tent height above 9 cm is possible. The stated range 0.9035 is 2.5-5
  cm farther than the feet's plane range (0.853-0.880). That fits a click higher up the tent.
- **Cup rim.** The camera is only about 2.5 cm above the rim plane, so intersecting the rim plane is ill-conditioned.
  Route B therefore puts the rim extremes in the vertical plane through the cup axis.
