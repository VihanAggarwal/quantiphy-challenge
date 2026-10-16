# Lab audit: family 0016 (captured_0016 / 0016s / 0016x), one event, shared labels

The clip has 49 frames at 24 fps, 1280x720. The camera is high and pitched steeply down (about 45-55 deg, from the far person's
body axis and the vanishing point of the wall seams). The near person (grey shirt, left edge) holds the Franklin "=100=" soccer ball
at the hip until about frame 27 and throws it between frames 28 and 31. The ball is in flight over frames 32-41 and the far person
(right) catches it at frames 41-43.
- t=1.5 s is frame 36. The ball is in flight at about (812, 77) px, with stated range 1.402 m.
- t=1.0 s is frame 24. The ball is still held at the near person's hip, at about (285, 595) px (circle fit).

Constants used: f=711 px, principal point (640, 360).
Scripts: `track.py` (matte components), `ballsize.py`, `circfit.py`, `people.py`, `physfit.py` / `physfit2.py` (3D ballistic fit,
numpy LM in `lm.py`). Images: `montage_x.png`, `ballcrops_o.png`, `heldcrops.png`, `held_24_grid.png`, `ov24.png`, `catch_grid.png`.

## Rows

| qid | render | question | current | my estimate | verdict |
|---|---|---|---|---|---|
| 2281/2285/2289 | o/s/x | distance between two people (cm) | 225.2 / 224.3 / 224.5 | 222-226 (range over plausible clicks 206-233) | keep |
| 2282/2286/2290 | o/s/x | soccer ball diameter (cm) | 18.36 / 19.0 / 18.45 | 15.4-16.4 here; 17.8 by prop transfer from 0034 (tennis 6.7 cm) | keep (gap <15%, no concrete error) |
| 2283/2287/2291 | o/s/x | ball velocity at 1.5 s (m/s) | 2.27 / 2.48 / 2.44 | 1.5-3.1 depending on timing model; plausible-gravity fit 2.6-2.7 | keep (motion row, not >1.5x off) |
| 2284/2288/2292 | o/s/x | ball displacement 1.0-1.5 s (cm) | 134.7 / 139.7 / 134.0 | 132 (robust range 120-144) | keep |

### People distance
I back-projected near-person clicks at range 0.843 m and far-person clicks at range 2.372 m. I tried 8 near-person click positions
(head, shoulder, torso, hip) against 6 far-person positions (head to legs). Every combination gives 206-233 cm, and torso to torso
gives 222-226 cm. Because the two ranges differ by 1.53 m, the result is insensitive to where the clicks were made. The current
answer of about 225 cm is right.

### Soccer ball diameter
**Route 1 (this clip, frame 36, stated range).** The ball is motion-blurred, so I measured its extent perpendicular to the motion
direction on the x-render matte: 89-95 px. Correcting for the off-axis ellipse gives a tangential size of about 86 px. The surface
depth is z = 1.402 / 1.103 = 1.271 m.
- Using the surface depth, D = 86 x 1.271 / 711 = 15.4 cm.
- Using the ball-centre depth (range plus R), D is about 16.4 cm.
- The 3D ballistic fit with a size term gives D = 16.3-16.9 cm. This is the same measurement, not an independent route.

**Route 2 (prop transfer).** captured_0034 shows the same Franklin "=100=" ball (same patch and text layout) next to a stated
6.7 cm tennis ball. The earlier labsize audit got 17.75-17.78 there, and 17.78 from the stated basketball in 0035.

The two routes agree within about 8% (16.4 against 17.8). The current 18.4 is 3-12% above them, which is below the 15%
threshold, and I have no concrete reason to call it wrong. The GT for the size of a blurred, moving ball, taken from edge clicks
plus ToF, is itself uncertain. Keep. (The 0016s value of 19.0 is a round direct answer, 3.5% off its twins. That is not worth a change.)

### Velocity at 1.5 s
Matte centroids of the ball, frames 32-40: (587,256) (641,199) (689,156) (735,121) **(812,77)** (845,70) (872,70) (894,77)
(913,91).
- The 35->36 step (89 px) is about 1.7-2x its neighbours (58 and 33 px).
- The near person's arm and torso component shows the same anomaly: bbox width step 48 against 30/30, and area step 7.0k
  against 4.5k/2.3k.
- So there is probably a timing irregularity, a dropped capture frame between 35 and 36.

Ballistic fits with g = 9.8 m/s^2 and the depth anchor 1.402 m at frame 36:
- Uniform timing, gravity free: RMS 7.3 px, |v| = 2.7 m/s.
- Gravity fixed to the scene estimate (pitch 40-55 deg, roll 0), free gap fitted at 1.7-1.8 frames: RMS 1.4-4.0 px,
  |v(1.5 s)| = 2.56-2.72 m/s, forward difference 36->37 = 2.6-2.7 m/s.
- Gravity free plus gap: RMS 1.1 px but an implausible gravity direction (pitch -10 deg), with |v| = 1.6 m/s.

A plain image-step forward difference 36->37 with no depth change gives 1.4 m/s. A backward step gives about 3.8 m/s. The current
2.27-2.48 sits inside the plausible 1.5-3.1 band and is nowhere near the 1.5x error threshold. Keep, per the instruction not to
touch tuned motion rows.

### Displacement 1.0 s to 1.5 s
At frame 24 the ball is held and sharp. A circle fit gives centre (285, 595) and an 89-96 px extent. Corrected for the off-axis
ellipse, its tangential size (about 82-90 px) is close to the 86 px at frame 36, so z24 is about z36, about 1.27 m. That puts the
ball at roughly 1.48 m range: it sits below and in front of the near person, whose clicked 0.843 m point must be the head or
shoulder, since the camera looks down past them.

Displacement = |P36 - P24| = 132 cm. Sweeping z24 from 1.0 to 1.45 m gives 119-144 cm. The current 134-140 cm is right.

## Result
No fixes for family 0016. 12 rows checked, all kept.
