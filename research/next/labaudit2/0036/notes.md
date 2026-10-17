# Lab audit round 2: family 0036 (captured_0036, 0036s, 0036x), one event, 15 scored rows

I used test inputs only (frames, `prior` = ping-pong ball 4 cm, `depth_info` = 1.010 m at 0.9 s and 0.716 m at 1.4 s) and no labels.
Scripts are in `scripts/`, crops and overlays in `img/`. Frames were extracted to the session scratchpad, not to this folder.

## Setup (re-measured independently of round 1)
- **Scene.** A ping-pong ball rests at the back-left of the lab table (video 0-11). A hand pushes it at about video 12-13 (it slides fast at first, then settles into a roll from about video 17). It rolls diagonally toward the camera and to the right, reaches the right side edge at video 35 and falls off (36-39). The camera sits about 18 cm above the table top with almost zero pitch.
- **Dropped frames.** The x step goes 28.5, 29.8, 32.0, then **70.7** (video 35->36), then 38.9. That double step means a capture frame is missing between video 35 and 36. This matches ffmpeg 25->24 rounding (capture = round(k*25/24)): capture 12 and 37 are dropped, so video k<=11 -> k, 12..35 -> k+1, >=36 -> k+2.
  - The earlier drop (11->12) can't be seen because the ball is still at rest, and the hand is too blurred to track (`img/push.png`).
  - With this mapping, 0.9 s = capture 22.5, between video 21 and 22, and 1.4 s = capture 35 = video 34. The label's forward differences are capture 22->23 or 23->24 (video 21->22 or 22->23) and 35->36 (video 34->35). Every frame involved exists.
- **Track** (`track.py`): background difference (median of video 41-48) AND a white mask, in all three renders. The renders agree within about 1 px. Clicks are taken as the render-averaged centroid, raw or locally smoothed.
- **Size** (`size2.py`, `img/size_marks.png`): the vertical diameter, from the steepest top-edge rise to the darkest contact-shadow row. This measure does not depend on motion blur.
  - Values: 21.1 px at rest, 29.9 at 0.9 s, 41.5 at video 34. Video 35 is 43.0, from the s render; the original render's bottom edge latches onto the table edge there.
  - **The two stated depths need the same scale.** K = (stated surface range + R) x d = 30.8 at 0.9 s and 30.6 at 1.4 s. So the size route and the stated depths are consistent within 1%. (K/D = 766 px; f = 711 needs a 4.3 cm ball. I give every result for both f = 711 and f = 766.)
- **Table plane** (`plane.py`): lines fitted to the x-render table mask (side edges and back edge, rms 0.2-0.4 px) and to the original's top/front-face boundary (rms 0.75 px).
  - Normal (-0.031, 0.999, 0.03). The corner angle is 88.6 deg at f 711 and 89.3 deg at f 766.
  - The ball-centre plane height from the stated points is 0.166 / 0.159 (f 711) or 0.154 / 0.149 (f 766).

## Label-style emulation (`labelstyle.py`, `variants.py`)
The method: P = surface range x ray(click), then the forward difference over one capture frame (0.04 s). The range comes from one of three routes, each scaled to the stated depths: an anchor at 0.9 s, at 1.4 s, or time-interpolated between them.
- **S (size):** a linear or quadratic fit of 1/d against capture time.
- **P (plane):** the table normal, with the height taken from the stated points.
- **L (line):** a straight 3D path through the two stated ball centres. Each frame's click ray is intersected with that path.

In the table, "phys" is the smooth centre velocity (quadratic fit, central difference).

| qids (o/s/x) | question | current | S (f711 / f766) | P (f711 / f766) | L (f711 / f766) | phys | verdict |
|---|---|---|---|---|---|---|---|
| 2666/2671/2676 | v at 0.9 s (cm/s) | 76.7 / 77.5 / 77.5 | 80-89 / 78-86 | 78-86 / 75-82 | 91 / 87 | 79-92 | 1-16% low: keep |
| 2667/2672/2677 | v at 1.4 s (cm/s) | 95.0 | 86-98 / 83-95 | 82-86 / 80-83 | 82 / 79 | 82-90 | 0-20% high: keep |
| 2668/2673/2678 | displacement 0.9-1.4 s (cm) | 43.5 | 43.3-43.7 / 41.7-42.2 | 40.6-43.7 / 39.4-42.1 | 43.8 / 42.2 | | OK |
| 2669/2674/2679 | table width (m) | 0.596 | front (across) edge 0.575-0.598 at the stated-point camera height (f711) | lab table 60.3 cm (short side) | | | OK |
| 2670/2675/2680 | table length (m) | 0.745 | receding side 0.70-0.73 (plane) | lab table 76.0 cm | | | OK |

Notes:
- **Radial component.** At 0.9 s every route gives about -58 to -71 cm/s. At 1.4 s the routes spread from -40 (L) to -59 (S, linear fit). The lateral component is well fixed by the pixels: about 55-59 cm/s at 0.9 s and 71-75 cm/s at 1.4 s.
  - Even the largest radial estimate keeps v(1.4) at or below 98, and the smallest keeps it at or above 79. So 95 cannot be 25% off.
  - Likewise, no route puts v(0.9) above 92 or below 75.
- **Constant roll.** The physical roll is close to constant at 85-90 cm/s from about 0.7 s to 1.44 s. The average over the stated interval, 43.5 cm / 0.5 s = 87 cm/s, agrees with that.
- **Where the size route runs high.** It gives a slightly higher v(1.4) than L/P (up to 98 with a linear 1/d fit). The path bows by 1-2 cm in range in the middle frames. That could be real, or it could be a sub-pixel bias in the shadow row; either way it is within noise.
- **Width vs length.** The edge geometry gives side/front = 1.21 (f 711) or 1.31 (f 766), against 1.26 for 76.0/60.3. So the across edge is the short side.
  - "Width = across / length = receding" and "width = short / length = long" give the same answer, so the two cannot be swapped.
  - The current 0.596 / 0.745 is within 1-2% of the lab table prior.
- **Render difference.** The o and s/x renders differ by 1% on v(0.9) (76.72 vs 77.52) although they share one label. That gap is harmless and I did not change it.

## Result
**No fixes.** I checked all 15 rows. Every motion row is within 25% of every route at both focal lengths: the largest deviations are -16% for v(0.9) against L, and +16-20% for v(1.4) against L/P. The static rows are within 2% of the lab-table prior and agree with the plane geometry.
