# Audit sim2_26: notes

Families: all 8 families in this item contain a single clip (0088, 0117, 0119, 0126, 0148, 0160, 0187, 0115_segmented).
So there are no sibling clips to cross-check against, and step (1) reduces to checking consistency inside each clip
(same scale used for every row, and an object's sizes consistent with its own speeds and sizes).
All 41 rows are scored. None of them has 'stated fact' or 'earlier audit fix' provenance.
The agent notes for simulation_0115_segmented do not exist (the path in the input is missing), so that clip was checked from scratch.

Scripts are in scripts/. Frames were read with OpenCV inside the scripts. The only files saved are a few small PNG crops.

## Quick-check table (my route vs current)

| qid | clip | quantity | current | quick check (my route) | diff | verdict |
|---|---|---|---|---|---|---|
| 130 | 0088 | small bird v(0.3 s) | 11.00 | crow 73.2 px/f; eagle 119.7 px/f => 0.006260 m/px => 11.00 | 0% | ok |
| 131 | 0088 | bird distance at 0.3 s | 2.33 | frame 7: bbox centres 976 vs 1344 = 368 px => 2.30 (frame 8 would give 2.60) | 1% | ok (frame-convention risk, 12%) |
| 132 | 0088 | eagle body length | 0.863 | bbox 137-138 px => 0.86 | 0% | ok |
| 133 | 0088 | eagle wingspan | 2.035 | flapping, y extent 176-324 px; max => 2.03 | 0% (pose choice) | ok, pose ambiguity not resolvable |
| **134** | 0088 | **small bird body length** | **0.94** | **84.1-86 px => 0.527-0.539** | **+75%** | **FIX => 0.535** |
| 135 | 0088 | small bird wingspan | 1.018 | max y extent 161-164 px => 1.01-1.03 | 0% | ok |
| 241 | 0117 | ball diameter | 0.0675 | own gravity fit 6289 px/s^2 => 1.558e-3 m/px; ball ~44.6 px => 0.0695 | 3% | ok |
| 242 | 0117 | door height | 2.60 | 1476-1482 px at ball scale => 2.30 (coplanar); the agent's depth factor 1/0.88 => 2.61 | 13% if coplanar | ok (depth hedge, below 15%) |
| 243 | 0117 | door width | 1.27 | 708-733 px => 1.10-1.14 coplanar, 1.25-1.30 with the depth factor | <=13% | ok |
| 244 | 0117 | lock length | 0.334 | 188-189 px => 0.294 coplanar / 0.334 | 13% | ok |
| 245 | 0117 | lock width | 0.072 | ~41 px => 0.064 / 0.072 | 12% | ok |
| 252 | 0119 | piece diameter | 0.0407 | diff-bbox width 34 px; speed 1.43 px/f => 1.17 mm/px => 0.040 | 2% | ok |
| 253 | 0119 | board side | 0.398 | 336-337 px => 0.394 (0.398 with the agent's +1% plane factor) | 1% | ok |
| 254 | 0119 | tray length | 0.297 | 247-258 px (agent); not re-profiled, consistent with montage | - | ok |
| 255 | 0119 | table side | 0.795 | 665 px both axes => 0.779-0.795 | 2% | ok |
| 256 | 0119 | distance moved | 0.060 | motion stops at frame ~35-36; 0.04 m/s x 1.5 s; 51 px => 0.060 | 0% | ok |
| 282 | 0126 | handle diameter | 0.125 | red-mask 111 / 100.5 px vs puck 64 px (same mask) => 0.128 / 0.116 | 2% | ok (two handles differ) |
| 283 | 0126 | puck v(0.5 s) | 0.664 | 24.41 px/f, puck 64.5 px => 0.672 | 1% | ok |
| 284 | 0126 | puck v(2.0 s) | 0.254 | 9.345 px/f => 0.257 | 1% | ok |
| 285 | 0126 | horizontal handle distance | 0.2055 | 712.2 - 532.2 = 180 px => 0.207 | 1% | ok |
| 286 | 0126 | shortest puck-right handle distance | 0.198 | centre dx 174.4 px => 0.200 (edge gap would be 0.10) | 1% | ok (interpretation) |
| 343 | 0148 | train v(1 s) | 49.16 | own gradient correlation gives the same shifts 355.8...391.0 px/f, frames 7-18; extrapolation as in the notes | 0-1% | ok |
| 344 | 0148 | train v(0.5 s) | 44.55 | 371.5 px/f x 24 x 0.004986 => 44.45; window ~356 px (agent 361) | 0-1.5% | ok |
| 345 | 0148 | train acceleration | 9.28 | ~3.2 px/f^2 x 576 x 0.004986 => 9.2 | 1% | ok |
| 346 | 0148 | door length | 2.3 | width 342 px => 1.71; visible height >= 421 px => >= 2.10 (bottom hidden) | - | ok (interpretation hedge, not measurable) |
| 347 | 0148 | pillar height | 3.1 | 665 px visible => 3.32 at train scale, ~3.0 at wall depth | - | ok |
| 372 | 0160 | table length | 2.51 | outer ~1673 px => 2.62; cloth ~1530 px => 2.40 (ball 48-49 px) | 4% | ok (hedge) |
| 373 | 0160 | table width | 1.374 | outer ~918 px => 1.44; cloth ~788 px => 1.24 | 4-10% | ok (hedge) |
| 374 | 0160 | pocket diameter | 0.118 | ~75-76 px => 0.118 | 0% | ok |
| 375 | 0160 | ball v(0.5 s) | 1.349 | raw steps around frame 15: 27.9-29.3 px/f => 1.31-1.38 | <2% | ok |
| 376 | 0160 | ball v(1 s) | 1.561 | 33.1-33.4 px/f => 1.556-1.570 | 0.5% | ok |
| 451 | 0187 | truck length | 8.78 | own shift track (2.07-2.09 px/f^2) plus front at f38 = 1380 and rear from f40/f44/f46 => 1476-1515 px => 8.5-8.7 | 1-3% | ok |
| 452 | 0187 | truck height | 3.36 | rail top ~352 to tire bottom ~928 => 576 px => 3.32 | 1% | ok |
| 453 | 0187 | tire diameter | 0.773 | crop 132-135 px => 0.76-0.78 | 1% | ok |
| 454 | 0187 | v(1 s) | 10.29 | shift(30) = 59.7-61.6 px/f => 10.3-10.66 | 0-3.5% | ok |
| 455 | 0187 | v(1.5 s) | 15.67 | shift(45) = 91 px/f => 15.74 | 0.5% | ok |
| 1819 | 0115s | boat length | 4.63 | own quadratic fit: a = 0.2407 px/f^2 => 0.02164 m/px; length 217-227 px => 4.70-4.91 | 2-6% | ok |
| 1820 | 0115s | boat width | 1.91 | 87-88 px => 1.88-1.90 | 1% | ok |
| 1821 | 0115s | boat v(1 s) | 5.06 | backward diff from the fit at frame 24: 9.75 px/f => 5.06 | 0% | ok |
| 1822 | 0115s | dock length | 12.28 | minAreaRect 573 px => 12.40 | 1% | ok |
| 1823 | 0115s | dock width | 2.12 | minAreaRect 97.7 px => 2.11 | 0.5% | ok |

No quick check other than 134 differs from the current answer by 15% or more.

## Fix: qid 134 (simulation_0088, body length of the small bird) 0.94 -> 0.535

- The crow flies straight left along a horizontal line (body row y ~ 552) and is seen from below, so its beak-to-tail axis lies along image x and is fully visible in every frame 2-24.
- Route A uses the colour-distance mask (|frame - median sky| > 60), connected-component bbox width: 85-87 px in all frames.
  Scale is 0.006262 m/px (eagle bbox edges move 119.6 px/f, 17.98 m/s prior), so the length is 0.539 m. This is also what the
  measuring agent itself wrote in its answers.json (134: 0.539).
- Route B uses the subpixel half-max of the max-over-rows darkness profile (rows 540-566). That gives 83.3-84.9 px, median 84.3 px, frames 2-24.
  Scale from the eagle centroid speed, 119.68 px/f, is 0.0062595 m/px, so the length is 0.528 m. A third variant (luma darkness, half-max of the global column profile, frames 16-24, crow alone) gives 84.1 px, or 0.527 m.
- Routes A and B agree within 2%. The current 0.94 m is 75% above them.
- Why the current value is wrong: 0.94 m would need a 150 px body, which matches no body extent in the clip. It is close to the crow's mid-flap span
  extent, which varies 105-164 px. The value is also not the measuring agent's answer (0.539), so it was overwritten downstream. It is inconsistent with the
  same clip's other answers, which use the same 2D scale: the speed 11.0 m/s (130) and the span 1.018 m (135). The pixel length/span ratio of the crow is 0.52.
  With the current answers the ratio is 0.92, which is anatomically implausible for a crow or raven. In a 2D (planar) D2 scene, a depth explanation would also have to rescale 130 and 135, and it does not.
- Proposed value: 0.535 m (between routes A and B).

## Rows with interpretation risk (not changed; no measurement can settle them)
- 131: the frame index for t = 0.3 s. Video frames 0 and 1 are identical. The frame-8 reading would be 2.60 (+12%).
- 133: the wingspan of a flapping eagle (max 2.03 vs the start pose 1.15).
- 242-245: the depth of the ball in front of the door (the agent's rho = 0.88 hedge; coplanar values are 12-14% lower).
- 346: door "length" (height >= 2.1 m vs width 1.71 m).
- 372/373: outer box vs cloth.
- 286: centre-to-centre vs edge gap.
