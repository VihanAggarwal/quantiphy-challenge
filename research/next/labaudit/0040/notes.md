# Lab audit: family 0040 (captured_0040, 0040s, 0040x)

All three renders come from the same footage (SAM2 demo outputs: o = blurred background, s = green, x = black), 49 frames at 24 fps, 1280x720.
They share one set of labels. The scene has a glass jar, a tape roll, a poker-card tower with one card lying flat in front of it,
a white tumbler cup and a credit card on the lab table. A white ball (a ping-pong ball, 4 cm) is thrown from the left. It bounces on the table
in front of the tape at about f33 (t=1.375), passes over the poker tower, crosses just above the cup rim at f36-37 (t=1.50-1.54),
bounces on the table again near the right edge at about f41 (t=1.71), then flies right and off the table toward the camera.

Stated depths: ball 0.7045 m at t=1.5 and 0.627 m at t=2.0; card 0.69, poker tower 0.91, tape 0.973, cup "8420m". The cup value is a typo for 0.842 m.
None of the current answers uses the typo value.

## Geometry checks
- Table top (x-render median mask, fitted edges). The corners FL(210,538), FR(1138,587), BR(917.8,467.1) and BL(448.5,448.8) are orthogonal at f=711 (cos -0.0004).
  Camera height above the table is 16.4 cm.
- Credit card on the rectified plane: long edges 8.73 and 8.49 cm, against 8.56 cm true, so the plane scale is about 1.0. The card-centre range on the plane is 0.654 m,
  but the stated range is 0.69. Stated (ToF) ranges are about 5 % larger than the geometric ones (poker-tower base: 0.853 vs 0.91). Labels are built
  from ToF depths, so route A below, which uses the stated ranges, is the label-consistent one.
- Ball size: the minor axis of the motion-blurred blob is the tangential diameter, f*D/(d*cos th).
  - t=1.5: minor 39.7 px at 0.7045 m gives D = 3.88 cm.
  - t=2.0: minor 56.6 px at 0.627 m, off-axis cos 0.789, gives D = 3.94 cm.
  - With D=4 cm, the size-based ranges reproduce the two stated anchors within +3 % and +1 %.

## Static rows (scripts/static.py)
| row | current (o / s / x) | route A: stated range | route B: table plane s=1.0 / 1.05 | verdict |
|---|---|---|---|---|
| poker tower height | 10.42 / 10.34 / 10.25 | 10.43 | 9.71 / 10.20 | ok |
| cup rim diameter | 9.00 / 8.48 / 8.48 | 8.33 (8.68 at silhouette depth) | 8.79 / 9.21 | ok (render spread 6 %, my values bracket both) |
| white ball diameter | 4.0 | 3.88 (t=1.5), 3.94 (t=2.0) | 0037 states the ping-pong ball as 4 cm | ok |
| tape diameter | 10.47 / 10.46 / 10.47 | 10.57 (11.06 at silhouette depth) | 10.64 / 11.15 | ok (within 6 %) |
| cup height | 14.82 / 14.73 / 14.73 | 14.65 | 14.68 / 15.41 | ok |

Side note: the poker cards measure about 10.5 cm long in the image at the stated range, which is larger than a standard 8.9 cm card.
Both the label route and route B agree on about 10.2-10.4 cm, so the current value is label-consistent.

## Motion rows (scripts/track2.py, speeds.py, ballistic*.py)
I tracked the ball by difference from the per-pixel median in the x and s renders. The two tracks agree within 1 px.
In the o render the arm dominates the difference before f36.

| row | current | my estimate | verdict |
|---|---|---|---|
| v(1.5) | 106.08 (all) | forward diff f36->37: 71-76 cm/s; central f35->37: 114-122; ballistic fits: 81-127 | ok (inside the bracket, not >1.5x) |
| v(1.4) | 106.08 (all) | f33->34 / f34->35 / f33->35: 126-135 cm/s for every depth model | lowish (~1.25x) but not >1.5x, so left as is |
| path 1.5-1.9 s | 39.81 / 39.81 / 39.48 | per-frame sum f36->f45.6: 36.5-38.6 cm (4 depth models x 2 renders) | ok |

Depth models used:
- linear between the stated anchors;
- linear fit of the size ranges;
- that fit rescaled to the anchors;
- constant 0.7045 m.

All give the same speeds within 5 %.

Ballistic fits with g = 9.8 m/s^2 along the table normal do not reproduce the stated ranges (0.56-0.65 at 1.5, 0.80-0.84 at 2.0).
With depth pinned by size or the anchors, the implied g is 7.4-8.1 m/s^2. Likely causes are ping-pong drag and spin, or timing.
I did not use these fits for decisions.

The f35->36 step (61 px) is about twice the neighbouring steps (31-36 px). This is likely blob bias from semi-transparent motion-blur edges over the white card and cup.
SAM2 compositing makes the card and cup rim look in front of the ball, but the stated ball range of 0.70 m and the ball size put the ball 10-20 cm in front of them.
This is why v(1.5) is uncertain between about 75 and 120 cm/s.

## Result
No fixes. Every static row agrees with two routes within about 6 %. The motion rows are within the noise bracket and none is >1.5x off.
