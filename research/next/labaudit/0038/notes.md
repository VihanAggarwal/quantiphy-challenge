# Lab audit: family 0038 (captured_0038, 0038s, 0038x)

The three renders come from the same footage (SAM2 demo outputs: o = blurred background, s = green, x = black). Each is 49 frames at 24 fps, 1280x720, and they share one set of labels.
The static scene is the same as in captured_0039, with identical stated depths, and the same props as in 0040:
- a pink bottle
- a poker-card A-frame tower with one card lying flat in front of it
- a white tumbler cup
- a dark-blue credit card near the front edge of the table

A white ball (a ping-pong ball) is held at the left table edge until f11. A hand pushes it at f11->12. From about f17 it rolls at constant speed to the right across the table, passing in front of the flat card at f30-35 (t=1.25-1.46 s).

Stated values: credit card 85.6 mm. Ranges at t=1.4: ball 0.716, card 0.6867, poker tower 0.9035, cup 0.874, bottle 0.9998.

## Geometry (scripts/table.py, static.py)
- Table top (x-render median): back corners come from fitted edges, BL (448.5,448.3) and BR (917.5,466.9); front corners FL (210,538) and FR (1138,588) are read from zooms.
  The corners are orthogonal at f=711 (cos -0.003). The plane from IPPE PnP with 76.0 x 60.3 gives a camera height above the table of 16.6 cm.
- Credit card on the plane: long edges 8.53 and 8.58 cm (true 8.56), short edges 5.49 and 5.80 (true 5.40), so the plane scale is about 1.00.
  - Card-centre plane range is 0.652 against a stated 0.687, a ratio of 1.053. ToF reads about 5 % longer here, as in 0040.
  - Cup front-base plane range is 0.876 (stated 0.874).
  - Bottle front-base plane range is 0.984 (stated 0.9998).
- Ball centre plane range at 1.4 s is 0.723, so the front surface is at 0.703, against a stated 0.716 (2 % apart). The plane and the stated depth agree.

## Static rows
Pixel reads from the x-render median (zooms z_objs, z_poker, z_card):
- Bottle: top 330, front-bottom 478.5, sides 642 and 689.5.
- Cup: rim top 375, rim width 723.5 to 794.5 (71 px), front bottom 498.5.
- Poker tower: apex 416.5, front-card foot 500, back-card foot 495.

The camera is 16.6 cm above the table, below the bottle top. Both the bottle's top and bottom silhouettes are therefore front-surface points, so route A at the stated range is consistent.

| row | current (o / s / x) | route A: stated range | route B: plane s=1 / s=1.053 | verdict |
|---|---|---|---|---|
| poker tower height | 10.42 / 10.38 / 10.43 | 9.90-10.39 (back foot to front foot) | 9.49-9.71 / 9.99-10.22 | ok (within 3-7 %) |
| cup rim diameter | 8.68 / 8.59 / 8.51 | 8.48 (8.90 at axis depth) | 8.47-8.89 / 8.92-9.34 | ok |
| white ball diameter | 4.0 | vertical extent f40: about 39.5-41.5 px at plane range 0.72, giving 3.9-4.2 cm | ping-pong 4 cm is stated in 0021 and 0036; 0040 measured 3.88-3.94 | ok |
| cup-bottle distance | 17.99 / 17.88 / 17.91 | 17.93 (centre clicks at stated ranges; 17.77 axis to axis) | 16.26-16.52 / 17.12-17.39 | ok |
| bottle height | 21.05 / 21.05 / 20.94 | 20.68 | 20.26 / 21.32 | ok |

## Motion rows (scripts/track.py, motion.py)
I tracked the ball by difference from the per-pixel median in the x and s renders. The two tracks agree within 1 px.
- The centre x is the mid point of the blob's horizontal extent. The centre y is the top edge plus the radius, because the bottom blends into the table.
- From f17 the ball rolls at a constant 16.2-16.4 px/frame.
- **Dropped frame.** The single step f35->36 is 30.4 px, twice the normal step. I confirmed it visually in crop_pass_o.png. This points to a dropped frame, consistent with a 25->24 fps resample.

Depth models:
- M1: constant range 0.736 (stated 0.716 plus the ball radius).
- M2: table plane at s=1.
- M3: plane rescaled so that range(1.4 s) = 0.716.
- M4: plane at s=1.053.

| row | current | my estimate | verdict |
|---|---|---|---|
| v(1.4) | 60.165 (all renders). Raw physical 45 times the leaderboard-tuned label-noise model (history: 44.4 or 45 raw, then 56.25, then 60.16) | 39.1-41.5 cm/s (fit f24-33 at 24 fps), 40.6-43.2 on a 25 fps time base, 42-45.5 by forward difference f33->34 | Left as is. The raw 45 is within about 10 % of my physical speed; the excess comes from the intentional noise correction. Not a wrong object, time or segment. |
| displacement 0.9->1.4 s | 17.3 (dmed: median of direct answers) | 19.7-21.0 (24 fps time; M1/M2/M3/M4 = 19.8/19.8/20.2/21.0), 20.6-21.9 with the 25 fps mapping. Cross-check: the constant 40 cm/s times 0.5 s is 20 cm | Soft. The current value is about 13-21 % low, but not >1.5x, so it is not changed under the motion-row rule. If motion rows are ever revisited, about 20.2 cm is the measured value. |

Side note: if the labeller took the forward difference at video frame 35->36 (t=1.4 at 25 fps), the label would include the dropped-frame double step, about 77 cm/s. This cannot be verified, and it is another reason to leave v(1.4) alone.

## Result
No fixes. Every static row agrees with both routes within about 7 %. The motion rows are not grossly wrong. The displacement row is noted as soft (about 15 % low) but is left unchanged by rule.
