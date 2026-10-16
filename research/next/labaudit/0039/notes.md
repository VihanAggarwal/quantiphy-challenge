# Lab audit: family 0039 (captured_0039, 0039s, 0039x). One event, so one label per question

Inputs: `../inputs/0039.json` (21 scored rows: 7 questions x 3 renders). Clip: 24 fps, 49 frames, 1280x720 (SAM2 demo
renders: o = blurred background, s = grey background, x = black background).

Scene: the same lab table and camera set-up as 0037/0038/0040. The table outline matches 0040 to within about 1 px.
On the table are a pink bottle, a white cup, a poker-card tower with a flat card in front of it, and a credit card.
The stated static ranges are identical to those of 0038. A white ball (a ping-pong ball) rests at the back left until
about f19. A hand behind the table pushes it, and it rolls straight toward the camera and slightly to the left at
about 55-60 cm/s. It rolls off the front edge at about f41.

No labels were used. I used test inputs only: frames, `prior` and `depth_info`.

Scripts (all in `scripts/`):
- `median.py`: per-render medians;
- `table.py`: table edges -> vanishing points -> plane, plus a PnP cross-check;
- `static.py`: static sizes by two routes;
- `dist.py`: cup-bottle distance;
- `track.py`, `ballfit.py`: ball blob and extents;
- `motion.py`: displacement and speed.

Zoom crops are `z_*.png`, and contact sheets are `sheet_*.png`.

## Camera and plane (f = 711, pp = (640, 360))
- The table corners are FL(210.8, 535.3), FR(1141.8, 586.8), BR(917.3, 466.5) and BL(448.9, 448.1). The vanishing
  directions are orthogonal to within cos 0.016.
- Camera height above the table: front side 0.1689, side 0.1766, mean **h = 0.1728**. This is the same as 0037
  (0.169 / 0.1765).
- The plane agrees with the stated ToF ranges:
  - bottle base-front range 0.998 vs stated 0.9998;
  - cup base-front 0.885 vs 0.874;
  - ball centre (on the plane 2 cm above the table) 1.027 / 1.013 at f24 (o / s) vs stated 1.014 at t=1.0;
  - ball centre 0.739 / 0.737 at f36 vs stated 0.737 at t=1.5.
- So the time mapping (t=1.0 -> f24, t=1.5 -> f36) and the plane scale are confirmed.

## Static rows
| question (qids o/s/x) | current o / s / x | route A: stated range | route B: table plane, h 0.169-0.1766 | verdict |
|---|---|---|---|---|
| pink bottle height (2726/2733/2740) | 21.05 / 21.04 / 20.94 | 20.57 (top 329.8, bottom-front 477.5 at x=664; 147.7 px) | 19.98 / 20.42 / 20.88 | OK (within 1-5 %) |
| white cup rim diameter (2722/2729/2736) | 8.68 / 8.68 / 8.68 | 8.42 at front range; 8.75-8.84 at axis range (rim edges 724.0-794.5, row 381) | 8.71 / 8.89 / 9.08 at axis depth | OK |
| poker tower height (2720/2727/2734) | 10.42 / 10.42 / 10.43 | 10.11 (apex 416.7, feet 495.5-500.5) | 9.49 / 9.70 / 9.92 | OK (3-9 %; same prop and value as 0037/0038/0040) |
| white ball diameter (2723/2730/2737) | 4.0 | horizontal width 29-30 px at 1.014 m -> 4.1-4.3 (incl. blur); 41-42 px at 0.737 -> 4.25-4.35 (incl. off-axis elongation) | ping-pong ball, stated 4 cm in 0021/0036 | OK |
| cup to bottle distance, centre to centre (2725/2732/2739) | 17.99 / 17.94 / 17.94 | 17.97-18.36 (centre pixels (664, 404) and (759, 436); stated 0.9998 / 0.874) | axis to axis 16.2-17.4 | OK |

In route B, the bottom silhouette at the centre column is the base-front point, because the camera is about 17 cm
above the table. The top silhouette of the bottle is the front rim, because the bottle (about 21 cm) is taller than the
camera height, so the camera looks up at it. The cup rim (about 15 cm) is seen nearly edge-on, less than 1 px open.

## Motion rows (ping-pong ball rolling toward the camera)
Ball centre: the horizontal coordinate is the middle of the white blob. The vertical coordinate is the top plus half the
width, because the lower half of the ball is shaded or in shadow. Centre pixels: f24 (543, 457.5), f36 (497, 501.5).
The o and s renders agree within 1.5 px.

| row | current | route A: stated ranges | route B: rolling on the plane, centre 2 cm up | verdict |
|---|---|---|---|---|
| displacement 1.0-1.5 s (2724/2731/2738) | 27.8 | 28.65 (range change 27.7 plus lateral 6.2) | 27.96-30.43 | OK (3-9 %) |
| v(1.0) (2721/2728/2735) | 52.0 / 52.0 / 53.7 | 57 (range interpolated linearly in time; fwd and central) | o: fwd 55.5-58.1, central 56.5-59.1; s: central 55.5-58.0 | OK (current 5-10 % low; far from the 1.5x bar, so left alone) |

Per-frame steps are noisy at integer-pixel extents (35-100 cm/s per step). The one large step at f35->36 is likely a
frame-timing or blob jitter. The rolling speed is about 55-60 cm/s and roughly constant from f22 to f40.

## Result
No fixes. All 21 rows were checked and each agrees with two independent routes to within about 10 %.
