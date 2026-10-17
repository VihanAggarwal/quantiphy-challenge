# Lab audit round 2: family 0038 (captured_0038, 0038s, 0038x; one event, shared labels)

Input: `../inputs/0038.json` (21 scored S3 rows = 7 questions x 3 renders). Test inputs only (frames, prior, depth_info);
no labels. Scripts in `scripts/` (frames are read in memory, nothing dumped): `track.py` (ball blob per render ->
`track.json`), `table.py` (table plane, PnP 76.0 x 60.3), `motion.py` (label-style + physical motion), `static.py`,
`noise_sim.py` (context only), `zoom.py`/`zoom_med.py`/`sheet.py`/`median.py` (crops viewed by eye).

Scene: pink bottle, card A-frame tower with one flat card in front, white tumbler, credit card; a ping-pong ball is
pushed by a hand at video f11->12, slides/decelerates to f17, then rolls at constant speed to the right, crossing in
front of the flat white card at f30-35. Stated ranges at t=1.4: ball 0.716, card 0.6867, tower 0.9035, cup 0.874,
bottle 0.9998.

## Capture clock
Double-length steps in all three tracks: f35->36 = 31 px against a steady 16.1-16.3 px (joint straight-line fit of
f17-48: residual sd 0.62 px with a dropped capture frame there, 3.5 px without). f11->12 = 50 px at the push, followed
by 33 px: consistent with the known lab drop after video f11 (a single 50 px interval would need a speed above any
later step). Mapping used: capture c = k (k<=11), k+1 (12..35), k+2 (>=36). t=1.4 s = capture 35 = video 34; the
forward step capture 35->36 = video 34->35 (a normal step). The rolling speed is constant (16.11-16.16 px/capture
frame before the drop, 16.23-16.30 after), so the velocity and displacement results do not depend on the drop
bookkeeping.

## Table plane
Corners BL(448.5,448.3) BR(917.4,466.9) from edge fits, FL(210,538) FR(1138.5,587.5) from zooms (`z_FL`, `z_FR`).
PnP: camera 0.1654 m above the table (0039 round 1: 0.1728 by vanishing points; axes orthogonal, aspect 1.32 vs
1.26, so the plane scale is uncertain by about +-5 %). Ball surface range at capture 35 from the plane: 0.704
(h 0.1654) / 0.746 (h 0.1728) against the stated 0.716, so the stated range sits inside the plane bracket.

## Motion rows
Ball centre: u = middle of the horizontal extent; v = top edge + R_px. The label-style value anchors the clicked
surface range to the stated 0.716 at capture 35 and adds the plane's change in surface range for the other frame. The
smooth value is a straight-line fit of the pixel track against capture time (f17-48 without f30-35, where the ball
overlaps the white card).

| row (qids o/s/x) | current | label-style (noise-free) | physical | verdict |
|---|---|---|---|---|
| v(1.4) (2700/2707/2714) | 60.165 | 39.8 (smooth c35->36, all renders and h); raw blob clicks v34->35: 41.0/43.7/44.9 (f34 blob is pulled left by the white card) | 40.2 (h .1654) - 43.8 (h .1766); 40.9 when rescaled to the stated range | No fix (see below) |
| displacement 0.9->1.4 s (2703/2710/2717) | 20.2 | 20.20-20.30 (capture 22.5->35); 19.4-21.3 if the labeller used capture 23 or 22 | 20.4-22.3; 20.8 rescaled | OK, matches |

v(1.4): the two routes agree (39.8 against 40.2-43.8), and the current answer is about 50 % above them. However, the
current value is not a measurement error. It is the label-noise policy: Claude's 45 (13 % above the physical speed)
times the per-row emulator factor 1.337 (sz2 policy, sigma_z = 2 cm per click, leaderboard contrast p11-p8 = +.015
on S3). With a 2 px click jitter and ToF noise sigma_z per click, `noise_sim.py` gives these MRA scores:

| sigma_z | median label | score of 39.8 | score of 60.165 | best constant answer |
|---|---|---|---|---|
| 1.0 cm | 49 | .727 | .650 | 46.5 |
| 1.5 cm (ladder best fit for small balls) | 55 | .645 | .659 | 49.5 (.704) |
| 2.0 cm | 63 | .575 | .633 | 52.5 |

So the current value is about as good as the noise-free value over the plausible noise range, and it is within 22 %
of the best constant answer, which is under the 25 % bar. No row-specific fact makes the inflation wrong: the
ball is a 4 cm ball at 0.72 m, and the static objects' ToF-to-plane offsets (card +5 %, bottle +1.6 %, cup 0 %) show
cm-level ToF scatter. This is left to the policy level. If the small-ball factor is ever re-tuned (sigma 1.5 cm), this
row would go to about 49-50.

## Static rows (x-render median; route A = stated range at both clicks, route B = table plane h .1654 / .1728)
| row | current o / s / x | route A | route B | verdict |
|---|---|---|---|---|
| poker tower height | 10.42 / 10.38 / 10.43 | 10.25 (front foot) / 9.98 (back foot); apex 417, feet 499.5/495 | 9.64 / 10.07 | OK (2-5 %) |
| cup rim diameter | 8.68 / 8.59 / 8.51 | 8.48 front range, 8.90 axis range (rim 723.5-794.5, row 377) | 8.55-8.97 / 8.93-9.35 | OK |
| ball diameter | 4.0 | rolling blob 47 px wide incl. ~8 px blur at centre range 0.738 -> about 4.05 | ping-pong 4 cm stated in 0021/0036 | OK |
| cup-bottle distance | 17.99 / 17.88 / 17.91 | 17.96 (centre clicks (665,404) at 0.9998, (759,436) at 0.874, the label construction) | axis to axis 15.7-16.6 (physical, not label-style) | OK (label-style matches within 0.5 %) |
| bottle height | 21.05 / 21.05 / 20.94 | 20.61 (top 330.5, bottom-front 478.5) | 20.18 / 21.08 | OK (2 %) |

## Result
No fixes. The static rows agree with route A to within 2-5 %. Displacement 20.2 equals the label-style value. v(1.4)
is 50 % above the noise-free label-style and physical speed (39.8-43.8), but only because of the deliberate
label-noise inflation. It is not a row error, so it is flagged for the policy level only.
