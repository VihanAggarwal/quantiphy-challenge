# Audit sim2_15 (families 0165/0166/0167 bike+van, 0181/0183/0185 boxes on ramp, 0234/0235 basketball)

Result: 45 rows checked, all scored. **No fixes proposed.** Every quick check falls within about 10% of the current
answer. The two road-width rows that sit lowest (Q395 and Q400) are definition-limited and below the 15% fix threshold (details below).

## Family consistency (step 1)
- Bike/van (prior: bike 5.52 m/s in all 3 clips). Bike wheel 0.726/0.726, bike length 1.766/1.77/1.80, van length 4.59/4.60,
  van speed 6.88/6.90. The van/bike pixel-speed ratio is 1.2465 in the top-down view (0167) and 1.2457 in the side view (0166, after the depth correction), so the
  clips are consistent.
  - The main road the bike crosses has answers 8.94 (Q387) and 8.96 (Q390), both curb-to-curb, but **8.15 (Q395)**, which is between the paint lines in the top-down view. The 9% gap comes from
    two sources: (a) road definition (curb vs paint), and (b) the top-down scale. The top-down scale comes from the bike's tracked features, which sit above the ground, so
    ground distances come out about 4-5% short. Two checks give this: the bike takes 37.9 frames to cross the outer paint lines in the side view and 36.1 frames in the top-down view
    (ratio 1.05), and the side-view outer paint width of 8.71 m maps to 525 px top-down, so the ground scale is 0.01659 m/px against the bike-derived 0.01597.
  - The 0166 notes mention a cross street of about 9.1 m. That figure assumed the focal length (f≈3750) and is not used in any answer. The top-down
    ratio method below gives 6.4-6.9 m.
- Boxes (3 different objects, priors 2.338/1.58/3.18 m/s^2). The camera and scene are the same, and in every clip the free-fall pixel acceleration / g
  matches the prior-based scale within 1% (I re-measured 261 px/m for 0181, and 233-235 px/m for 0185). The 0-0.3 s free-fall acceleration should be identical in all three:
  answers are 9.4/9.0/9.4, all within 6% of both 8.86 (backward-difference v(f7)/0.3) and 9.81. Harmless.
- Basketball (prior: ball 0.282 m in both clips). Green band 1.29 vs 1.277, which agree after each clip's own depth correction (1.136 vs 1.038).
  Motion: v(0.5 s) 0.985/1.007, a 2.03/1.99, v(1.5 s) 1.07/1.08, a 1.92/1.87. Consistent.

## Notes skimmed (step 2)
The low or medium confidence flags are all definition hedges: 0181 height (flap), 0181 v(1.5 s) (box reaches the end of the ramp and tips), 0185 size
(rotated cube, world AABB vs local axes, with or without the bow), 0235 panes (opening vs period) and trophy (with pedestal), and road widths. No wrong methods found.

## Quick check of every row (step 3)
| qid | clip | quantity | current | quick-check route / value | verdict |
|---|---|---|---|---|---|
| 386 | 0165 | bike wheel diam | 0.726 | crop: 65-66 px x 0.010952 m/px (bike 21.0 px/f from bg-mask bbox) = 0.71-0.72 | ok |
| 387 | 0165 | main road width | 8.94 | own row profiles: X/H outer paint -1.523..+2.460, H = 2.186 m -> 8.71 (curb about 8.94) | ok (definition) |
| 388 | 0165 | bike length | 1.766 | bg-mask bbox 161-162 px -> 1.76-1.77 | ok |
| 389 | 0166 | bike wheel diam | 0.726 | same object as 386 | ok |
| 390 | 0166 | main road width | 8.96 | same road as 387 | ok |
| 391 | 0166 | bike length | 1.77 | same as 388 | ok |
| 392 | 0166 | van length | 4.59 | blob 431-436 px x s_van 0.010602 = 4.57-4.62; top-down 285-289 px x 0.01597 = 4.55-4.62 | ok |
| 393 | 0166 | van tyre diam | 0.785 | crop 71-72 px x 0.010602 = 0.75-0.76 (-3 to -4%) | ok |
| 394 | 0166 | van speed 1 s | 6.88 | blob edge 27.0 px/f -> 6.87; top-down ratio 18.0/14.42 x 5.52 = 6.89 | ok |
| 395 | 0167 | crossing (main) road width | 8.15 | top-down outer paint 514-525 px x 0.01597 = 8.2-8.4; curb 549 px = 8.77; ground-corrected x1.04 = 8.7-9.1; side view 8.71-8.94 | 5-10% low vs siblings, below threshold |
| 396 | 0167 | bike length | 1.80 | side-view 1.77 | ok |
| 397 | 0167 | car length | 4.60 | crop 282-289 px -> 4.5-4.6 | ok |
| 398 | 0167 | car width | 1.87 | crop 114-117 px -> 1.82-1.87 | ok |
| 399 | 0167 | car speed 1 s | 6.90 | blob tracks: bike 14.42 px/f, car 17.8-18.2 px/f -> 6.8-6.97 | ok |
| 400 | 0167 | cross street width (bike+car) | 6.15 | top-down outer edge lines 384 px x 0.01597 = 6.13; ground-corrected 6.37; curb-to-curb 410-416 px = 6.55-6.9 (x1.04 = 6.8-7.2); scale-free ratio to the side-view main road gives 6.37 (paint) / 6.73 (curb) | 4-12% low depending on definition, below threshold |
| 436 | 0181 | a 0-0.3 s | 9.4 | template 2nd diff 4.45 px/f^2 = 2563 px/s^2 -> 261 px/m (= prior scale 263); v(f7)/0.3 = 8.9; true g 9.81 | ok (hedge) |
| 437 | 0181 | v 1 s | 2.90 | own template track 31.84 px/f -> 2.92 | ok |
| 438 | 0181 | v 1.5 s | 3.9 | template 42.0 px/f (35->36) = 3.85; rear-corner x-min track about 3.3; constant-a extrapolation 4.07 | ok (range 3.3-4.1) |
| 439 | 0181 | width | 1.07 | edges 377/379 -> 655/661 = 278-282 px / 261 = 1.07 | ok |
| 440 | 0181 | height | 0.775 | front face 228-420 = 192 px = 0.735; with flap 0.82 | ok (hedge) |
| 441 | 0183 | a 0-0.3 s | 9.0 | centroid v(f7)/0.3 = 8.9 | ok |
| 442 | 0183 | v 1 s | 2.01 | centroid quadratic fit 2.06 (prior scale) / 1.98 (g scale) | ok |
| 443 | 0183 | v 1.5 s | 2.82 | 2.85 / 2.74 | ok |
| 444 | 0183 | length | 1.25 | front face 405->701 = 296 px / 241-243 = 1.22-1.23 | ok |
| 445 | 0183 | height | 0.75 | 236 -> 416-425 = 180-189 px = 0.74-0.78 | ok |
| 446 | 0185 | a 0-0.3 s | 9.4 | centroid v(f7)/0.3 = 9.07 | ok |
| 447 | 0185 | v 1 s | 3.17 | 3.17 (prior scale) / 3.21 (g scale) | ok |
| 448 | 0185 | v 1.5 s | 4.73 | 4.76 / 4.82 | ok |
| 449 | 0185 | length | 0.50 | silhouette 136 px includes side face; front-face world-X about 120-126 px -> 0.51-0.54 | ok (local-axis alternative 0.39) |
| 450 | 0185 | height | 0.585 | silhouette 145 px including bow and perspective -> at most 0.62; body 0.515 | ok (hedge) |
| 761 | 0234 | backboard length | 1.50 | 794->1152 = 358 px x 0.00378 x 1.108 = 1.50 (1.35 without depth correction) | ok |
| 762 | 0234 | backboard height | 0.875 | 71->280 = 209 px -> 0.875 | ok |
| 763 | 0234 | green band | 1.29 | 680->980.5 = 301 px x 0.00378 x 1.136 = 1.29; sibling 0235 gives 1.277 | ok |
| 764 | 0234 | v 0.5 s | 0.985 | hue-mask track, local quadratic: 0.971-0.983 | ok |
| 765 | 0234 | a 0.5 s | 2.03 | 2.01-2.03 | ok |
| 766 | 0234 | v 1.5 s | 1.07 | 1.05-1.06 | ok |
| 767 | 0234 | a 1.5 s | 1.92 | 1.87-1.89 | ok |
| 768 | 0235 | trophy height (with column) | 1.10 | 505 -> 928-937 = 423-432 px x 0.00259 = 1.10-1.12 | ok (definition) |
| 769 | 0235 | pane length | 0.542 | dark openings 196-205 px x 0.002763 = 0.54-0.57 | ok |
| 770 | 0235 | pane height | 0.409 | 147-150 px -> 0.406-0.414 | ok |
| 771 | 0235 | green band | 1.277 | 441->904 = 462 px x 0.002763 = 1.277; sibling 1.29 | ok |
| 772 | 0235 | v 0.5 s | 1.007 | 0.976-0.987 | ok |
| 773 | 0235 | a 0.5 s | 1.99 | 2.04-2.06 | ok |
| 774 | 0235 | v 1.5 s | 1.08 | 1.056-1.067 | ok |
| 775 | 0235 | a 1.5 s | 1.87 | 1.87-1.89 | ok |

No quick check differs from its row by 15% or more, so no in-depth re-measurement was needed under the protocol. The road widths got extra work anyway (above).

## Fixes
None.

Optional consistency note (not a fix; below the 15% rule): Q395 (8.15) and Q387/Q390 (8.94/8.96) are the same road. If someone harmonises them, about 8.9
(curb-to-curb, ground-corrected) is supported by both views. Q400 (6.15) would correspondingly be about 6.4-6.7.
