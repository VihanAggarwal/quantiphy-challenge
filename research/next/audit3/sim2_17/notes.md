# Audit sim2_17 (robots 0218/0218_seg/0219, xiangqi 0224/0224_seg, soccer 0251/0251_seg/0252)

All 41 rows are scored. I checked all of them. **No fixes are proposed.** No row meets all three conditions: two independent routes agreeing within 8%, a gap of at least 15% from the current answer, and a concrete error.
One row pair (689/1943, chess-board length) is a near miss and is described below. One family inconsistency (soccer 0251 vs 0252) is flagged.

Scripts are in this folder: grab.py (crops), track_ball*.py / ball_center.py (ball tracks), rect.py (rotates the board-slope frame).
The key crops I looked at are in img/.

## Family tables (current answers)

| family | quantity | clip A | clip B | clip C | consistent? |
|---|---|---|---|---|---|
| robots | big-robot length | 0218: 3.00 | 0218_seg: 3.00 | 0219: 2.94 | yes |
| robots | big-robot height | 3.05 | 3.05 | 3.07 | yes |
| robots | parking long side | 5.84 | 5.77 | 5.82 | yes |
| robots | tyre (road-wheel) diameter | 0.34 | 0.34 | 0.338 | yes |
| chess | board length | 0224: 1.32 | 0224_seg: 1.32 | - | yes, but both rest on the same method (see below) |
| chess | v at 0.5 / 1 / 1.5 s | 0.35 / 0.72 / 1.086 | 0.345 / 0.700 / 1.048 | - | 2-4% apart (the seg answers are slightly low) |
| chess | a at 0.5 / 1 / 1.5 s | 0.74 x3 | 0.719 / 0.704 / 0.688 | - | about 5% apart |
| soccer | v at 0.5 / 1 / 1.5 / 2 s | 0251 (= seg): 5.44 / 5.10 / 4.78 / 4.44 | 0252: 6.62 / 6.06 / 5.50 / 4.94 | - | NO: 0252 is 11-22% higher (see the flag) |

0218 and 0219 share the camera and the big-robot motion: frame 24 is identical apart from the small robot.
0218_seg is the same footage as 0218.

## Quick checks (my own route, on the frames)

| qid | clip | quantity | current | quick check | diff | method |
|---|---|---|---|---|---|---|
| 637 | 0218 | big robot length | 3.00 | 3.01 | 0% | 0218_seg silhouette bbox at frames 16/20/24 (x 793-1443 at f24). Each edge is scaled at its own depth using its own px speed: drill 54.1 px/f -> 4.563e-3 m/px; rear 51.0 px/f -> 4.840e-3 m/px. X=(x-960)*s gives 3.01 at all three frames. |
| 638 | 0218 | big robot height | 3.05 | 3.03-3.07 | <1% | silhouette y 271-894. Bottom uses the track scale (template-matched track speed 50.78 px/f -> 4.859e-3); top uses the handle-plane scale 4.88-5.01e-3; cy=540. |
| 639 | 0218 | parking long side | 5.84 | 5.78 (centre-centre) | 1% | separator runs at 6 rows (y 850-900). X = h*(x-960)/(y-540) is constant along each line, so the horizon is at 540. Left X=-1.93, right X=+3.85, with h = 354 px * 4.859e-3 = 1.72 m. Inner edges 5.42, outer edges 6.11. The depth side is about 2.7-3.3 m for f 2667-3200, so the side along the wall is the long one. |
| 640 | 0218 | tyre diameter | 0.34 | 0.335 | 1.5% | road wheel 69 px at the track plane |
| 641 | 0219 | big robot length | 2.94 | 3.01 | 2.3% | same footage and motion as 0218 |
| 642 | 0219 | big robot height | 3.07 | 3.05 | <1% | same as 638 |
| 643 | 0219 | parking long side | 5.82 | 5.78 | <1% | same as 639 |
| 644 | 0219 | tyre diameter | 0.338 | 0.335 | 1% | same as 640 |
| 645 | 0219 | small robot v at 1 s | 0.82 | 0.81-0.82 (local 0.79-0.85) | <2% | small robot isolated as the 0219-minus-0218 difference. Centroid moves 8.44 px/f over the whole clip (8.2-8.7 locally around f24). Ground-contact scale h/(y_c-540) = 1.72/423-428 = 4.02-4.07e-3. |
| 646 | 0219 | small robot height | 1.22 | 1.21-1.25 | <2% | difference mask, full-body frames: 300-307 px at the same scale |
| 689 | 0224 | board length | 1.32 | 1.35 using the agent's method; 1.10-1.21 corrected for perspective | 9-20% | **near miss**, see below |
| 690 | 0224 | v 0.5 s | 0.35 | 0.37 | 5.7% | track of the piece along the slope in the rectified frame, re-indexed for dup/skip frames (dups 1,6,13,25,28,35,38,41; skips 5,10,23,27,34,37,40; this pattern is confirmed by the step sizes). Quadratic fit, rms 0.4-0.5 px, a = 1.02 px/f^2. Scale 0.097/76.5 px. |
| 691 | 0224 | a 0.5 s | 0.74 | 0.745-0.756 | 1-2% | same fit |
| 692 | 0224 | v 1 s | 0.72 | 0.745-0.752 | 3.5-4.4% | same fit |
| 693 | 0224 | a 1 s | 0.74 | 0.75 | 1% | same fit |
| 694 | 0224 | v 1.5 s | 1.086 | 1.12-1.13 | 3-4% | same fit |
| 695 | 0224 | a 1.5 s | 0.74 | 0.75 | 1% | same fit |
| 847 | 0251 | v 0.5 s | 5.44 | 5.45-5.48 | <1% | ball centre and edges from rows that have no shadow, against a median background. Quadratic fit, rms 0.6-0.9 px. Ball 48-50 px on 4x crops -> 7.17e-3 m/px. |
| 849 | 0251 | v 1 s | 5.10 | 5.16 | 1% | same |
| 850 | 0251 | v 1.5 s | 4.78 | 4.84-4.86 | 1.5% | same |
| 848 | 0251 | v 2 s | 4.44 | 4.53-4.57 | 2-3% | same |
| 851 | 0252 | v 0.5 s | 6.62 | 6.51-6.55 | 1-1.7% | top-down camera. Ball 70 px (70-71 on 4x crops) -> 4.914e-3. |
| 852 | 0252 | v 1 s | 6.06 | 5.94-5.96 | 2% | same |
| 853 | 0252 | v 1.5 s | 5.50 | 5.36-5.37 | 2.5% | same |
| 854 | 0252 | v 2 s | 4.94 | 4.77-4.80 | 3% | t=2 s is past the clip end (41 frames), so this is a constant-deceleration extrapolation |
| 1939 | 0218_seg | big robot length | 3.00 | 3.01 | 0% | as 637 |
| 1940 | 0218_seg | big robot height | 3.05 | 3.05 | 0% | as 638 |
| 1941 | 0218_seg | box long side | 5.77 | 5.78 | 0% | as 639 |
| 1942 | 0218_seg | tyre diameter | 0.34 | 0.335 | 1.5% | as 640 |
| 1943 | 0224_seg | board length | 1.32 | 1.10-1.21 | 9-20% | near miss, as 689 |
| 1944 | 0224_seg | v 0.5 s | 0.3451 | 0.37 | 7% | twin of 690 |
| 1945 | 0224_seg | a 0.5 s | 0.719 | 0.75 | 4% | twin of 691 |
| 1946 | 0224_seg | v 1 s | 0.7002 | 0.745 | 6% | twin of 692 |
| 1947 | 0224_seg | a 1 s | 0.7035 | 0.75 | 6.6% | twin of 693 |
| 1948 | 0224_seg | v 1.5 s | 1.048 | 1.12 | 6.9% | twin of 694 |
| 1949 | 0224_seg | a 1.5 s | 0.688 | 0.75 | 9% | twin of 695 |
| 1996-1999 | 0251_seg | v 0.5 / 2 / 1 / 1.5 s | same as 0251 | same as 0251 | <3% | twin |

No quick check differs by 15% or more except the board length (689/1943).

## Near miss: chess-board length (689, 1943), current 1.32. No fix.

What the agent did: it took the along-slope length of the board's top frame at the NEAR outer edge (1057 px; I get 1060.7 px between the near corners (425,945) and (1381,486)) and multiplied by the piece scale, giving 1.354. It also took the horizontal extent (about 1003 px -> 1.285) and answered 1.32, between the two.

Why this is biased high: the camera is level and looks straight along the board's depth axis. The left and right end edges, the box edge and the grid file lines all converge exactly on (960,540). So the board extends far in depth: the far top edge is 1.39-1.45x farther than the near top edge (from the ratios of the end-edge u and d coordinates). The piece slides well behind the near edge, so its scale does not apply to the near edge.

Rotate the image by -25.64 deg about the vanishing point. Then u is along the slope and d is perpendicular to it; d = f*D/Z, where D is the plane's offset from the optical axis.
- Piece: diameter 75-78 px along u (76.5 used). Its bottom near rim is at d = 121.5, which gives D_surface = 121.5 * s_p * (1 - r/Zp) = 0.1527 m. This does not depend on f.
- Near outer top edge: d = 133.7. Length = 7.93 * D_rail. The far edge gives 8.06 * D_rail, which is consistent.
- The far rail's inner wall spans about 6 px of d (range 4-9). That makes the rail top about 0.9 cm above the playing surface, so D_rail is about 0.1436 and **L_along-slope is about 1.14-1.15** (range 1.10-1.16).
- Occlusion at frame 39: the piece covers the left rail's outer edge at image points where the rail depth is 1.22-1.32 Zn, so Zp/Zn < about 1.22. If the piece slid on a convex hull at rail-top height, the lowest possible ratio is 1.12. Together: **L between 1.10 and 1.20.**
- The departure timing at the left end (the piece is off the board and has dropped by video frame 40) suggests an even larger Zp/Zn (L about 1.0). That conflicts with the occlusion bound, so I set it aside.
- What "length" means is also uncertain. Along-slope local length: about 1.15. World-AABB horizontal extent: about 1.05-1.1. Board depth W = 4.3e-4 * f, which is about 1.16 with the default 50 mm camera (f = 2667) but is not pinned down.

Result: the plausible labels are about 1.05-1.21, all below 1.32 by 9-25%. The best single value is about 1.15 (14-15% below the current answer).
This fails the strict criteria: the corrected value is under 15% from the current answer, and the second route is only a bound. So no fix is proposed. If the orchestrator accepts a soft fix, set 689 and 1943 to about 1.15; that value is within about 6% of every interpretation above.

## Flag: soccer 0251 (+ seg) vs 0252, a family inconsistency left unchanged

Both clips measure correctly in their own frame time base (my fits agree with the agents' within 3%). But in ball-diameter units, 0252's velocity law matches 0251 sampled 1.25x more densely:
- At frame 0, v252 = 0.862 diameters per frame, against 1.25 * v251 = 0.875.
- The deceleration ratio is about 1.6-1.9, against the 1.56 expected for a pure time rescale.
- The frame counts are 51 vs 41, a ratio of 1.244.

So this is probably the same simulated roll rendered at two frame rates (for example 0251 at 30 fps, or 0252 at about 19.2 fps), with both encoded at 24 fps. The questions at t=2 s exist for both clips; that fits a clip length of 2.08 s for both, which would mean 0252 is the odd one.
However, the dataset fps column says 24 for both, so the labels may well be per-frame displacement * 24 (the current answers). I cannot say which clip, if either, is wrong:
- If 0252 is really about 19.2 fps, its labels would be about 5.4 / 5.1 / 4.75 / 4.4.
- If 0251 is really 30 fps, the labels for 0251 and its seg twin would be about 6.7 / 6.2 / 5.65 / 5.1.

No change is proposed.

## Other notes
- The 0224_seg answers are 2-7% below its twin 0224 and 4-9% below my fit. They could be made equal to 0224's values, but that is under the threshold.
- 645: the agent wrote 0.845 and the current answer is 0.82. My whole-clip mean speed gives 0.81-0.82, so 0.82 is fine.
- 639/643/1941 (parking long side) depend on which line edges count: centre-to-centre is 5.78, inner 5.42, outer 6.11. The current answers sit at centre-to-centre.
