# Audit sim2_13: families simulation_0087 (0085/0086/0087, car + bike) and simulation_0159 (0154-0158, shark + turtle)

Result: **no fixes proposed.** All 41 rows were tabulated. The 38 scored rows that are not stated facts were each quick-checked on the frames with one independent route. No quick check differs from the current answer by 15% or more, so no row needed the in-depth second route.

## 1. Family consistency

### Car + bike (0085, 0086, 0087): one scripted motion seen by three cameras at different distances
| clip | car a_px (px/f^2, early) | bike v_px (px/f) | bike/car ratio | m/px (car prior) | m/px (bike 5.07 stated fact) |
|---|---|---|---|---|---|
| 0085 | 0.8895 (agent; my coarse edge fit 0.85-0.89) | 26.665 | 29.98 | 0.007866 | 0.007922 |
| 0086 | 0.526-0.531 | 16.006 | 30.2 | 0.01318-0.01329 | 0.01320 |
| 0087 | 0.701-0.706 | 21.105 | 30.1 | 0.00985-0.0099 | 0.01001 |

The expected ratio is (5.07/24)/(4.03/576) = 30.19. The car prior (4.03 m/s^2, the early constant-acceleration regime, which matches the stated fact "car acceleration at 1.0 s = 4.03" in 0087) and the stated bike speed of 5.07 give the same scale within 1% in every clip. So all three clips are scaled correctly.

Sizes agree across the family:
- car length: 5.69 / 5.70 / 5.66
- car width (mirror-inclusive bounding box): 2.42 / 2.40 / 2.46
- bike length: 1.71 / 1.69 / 1.70

The motion directions differ between clips (in 0085 both objects move left; in 0086 and 0087 they move in opposite directions), and the starting offsets differ. Distances therefore cannot be shared across clips and were checked per clip.

### Shark + turtle (0154-0158): same camera; every clip has the same pixel scale
- The shark appears at about 905-925 px long in every clip.
- From the shark-speed prior (7 m/s, mid-clip ~58-59 px/f): 0.00494-0.00502 m/px.
- From the turtle-acceleration prior (2.639 m/s^2):
  - 0158 agent: 532 px/s^2.
  - My rest-constrained rear-edge fit on 0157: 529-543 px/s^2, long baseline 533. This gives 0.00495 m/px.
  - The 0157 agent used 544.7, giving 0.004845 (2% low; harmless).
- 0154 and 0155 are near-identical takes. The shark starts slower there (~42 px/f over frames 0-2) and runs at ~59 px/f mid-clip. In 0156 it moves at a constant ~58 px/f.
- 0158 is the "accelerating" take: the shark accelerates from rest at about 7.0 m/s^2, and the turtle at 2.639 m/s^2. The turtle tracks in 0157 and 0158 are identical frame by frame.
- 0156 has the turtle at constant speed (~21.8 px/f, i.e. 2.59-2.61 m/s).

Sizes across the family:
- shark length: 4.6 / 4.6 / 4.57 / 4.524. Consistent.
- turtle length: 1.60 (0156) / 1.52 (0157) / 1.677 (0158). The spread is about 10%.
  - The 0157 agent's 315 px extent excludes the faint head patch. In 0157 frame 24 the head is too faint to segment; in 0158 frame 24 the head reaches x≈1509. With the head, the extent is 320-350 px depending on the flipper pose (0156 median ~331 px; 0157 frames 32-40 329-337 px; 0158 frame 24 ~349 px). That is 1.6-1.73 m at 0.00495 m/px.
  - So 0157's 1.52 is probably about 8-12% low. This is below the 15% threshold, so it is not proposed as a fix. Harmonising the three turtle-length rows to about 1.65-1.68 would be a reasonable optional tidy-up.

## 2. Agent notes
I read all eight clips' notes.
- None mark an answer as low confidence. Distances, car width (mirror ambiguity) and turtle length (pose) are marked medium.
- The methods are sound: scale from the prior with perspective-aware tweaks, and backward-difference speeds `a*(n-0.5)/24`.
- No unit slips, wrong-object priors or camera-motion issues were found (all cameras are static).

## 3. Quick checks on every scored row
Method:
- Silhouettes come from a clean composite or median background (`car_track.py`, `sea_track.py`, `turtle_ext.py`), with bounding-box extents and centres per frame.
- Each clip uses its own scale. The car clips also use the scale from the stated 5.07 m/s bike speed.

| qid | clip | quantity | current | quick check | diff | fix? |
|---|---|---|---|---|---|---|
| 109 | 0085 | bike speed 1.0s | 5.07 | stated fact | - | locked |
| 110 | 0085 | bike length | 1.71 | 214 px x 0.00792 = 1.70 | 1% | no |
| 111 | 0085 | car length | 5.69 | 726-740 px (motion-blurred) x 0.00787 = 5.71-5.82 | 1-2% | no |
| 112 | 0085 | car width | 2.42 | 316 px (incl. shadow fringe) x 0.00787 = 2.49 | 3% | no |
| 113 | 0085 | dist 1.0s | 6.06 | dx 659 px, dy 338 px -> 741 px x 0.00787 = 5.83 | 4% | no |
| 114 | 0085 | dist 2.0s | 5.23 | dx 556 px, dy 338 px -> 651 px -> 5.13 | 2% | no |
| 115 | 0085 | car speed 1.5s | 5.97 | 4.03 x 35.5/24 = 5.96 | 0% | no |
| 116 | 0086 | bike speed 1.0s | 5.07 | stated fact | - | locked |
| 117 | 0086 | bike length | 1.69 | 129 px x 0.0132-0.0133 = 1.70-1.72 | 1-2% | no |
| 118 | 0086 | car length | 5.70 | 439 px at rest (incl. fringe) x 0.01318 = 5.79 | 2% | no |
| 119 | 0086 | car width | 2.40 | 190 px x 0.01318 = 2.50 | 4% | no |
| 120 | 0086 | dist 1.0s | 5.45 | dx 376.5 px, dy 171 px -> 413.5 px -> 5.45 | 0% | no |
| 121 | 0086 | dist 2.0s | 16.3 | dx 1216.5 px, dy 171 px -> 1228.5 px -> 16.19 | 1% | no |
| 122 | 0086 | car speed 1.5s | 5.99 | 5.96 | 0.5% | no |
| 123 | 0087 | car acceleration 1.0s | 4.03 | stated fact | - | locked |
| 124 | 0087 | bike length | 1.70 | 171 px x 0.01001 = 1.71 | 1% | no |
| 125 | 0087 | car length | 5.66 | 581-601 px (blurred) x 0.00985 = 5.72-5.9 | 1-4% | no |
| 126 | 0087 | car width | 2.46 | 251 px x 0.00985 = 2.47 | 0% | no |
| 127 | 0087 | dist 0.5s | 18.5 | dx 1820 px, dy 254 px -> 1838 px x 0.00985-0.0100 = 18.1-18.4 | 1-2% | no |
| 128 | 0087 | dist 1.0s | 14.5 | dx 1411 px, dy 254 px -> 1434 px -> 14.1-14.35 | 1-3% | no |
| 129 | 0087 | car speed 1.0s | 3.96 | 4.03 x 23.5/24 = 3.95 | 0% | no |
| 353 | 0154 | shark length | 4.6 | ~905-917 px x 0.00495-0.00497 = 4.49-4.56 | 1-2% | no |
| 354 | 0154 | shark displacement | 13.7 | 7 x 47/24 = 13.71; pixel path ~2700-2730 px x 0.00495 = 13.4-13.5 | 0-2% | no |
| 355 | 0155 | shark length | 4.6 | as 353 (same take) | 1-2% | no |
| 356 | 0155 | shark displacement | 13.6 | as 354 | 1% | no |
| 357 | 0156 | shark length | 4.57 | 917 px (snout x≈388 to tail x≈1305 at frame 24) x 0.00497 = 4.56 | 0% | no |
| 358 | 0156 | shark displacement | 13.71 | 58.06 px/f x 47 = 2729 px x 0.00495-0.00502 = 13.5-13.7 | 0-1% | no |
| 359 | 0156 | turtle speed 1s | 2.61 | rear edge, frames 14-46: 21.8 px/f x 24 x 0.00495 = 2.59 | 1% | no |
| 360 | 0156 | turtle length | 1.60 | 320-350 px x 0.00495 = 1.58-1.73 (median ~331 px -> 1.64) | 2-3% | no |
| 361 | 0157 | turtle length | 1.52 | with head 329-349 px x 0.00495 = 1.63-1.73 | ~8-12% | no (<15%) |
| 362 | 0157 | turtle speed 1s | 2.51 | 2.639 x 23.5/24 = 2.58; rear edge frames 22-26 22.5 px/f -> 2.67 | 3% | no |
| 363 | 0157 | turtle speed 1.5s | 3.83 | 3.90; rear edge frames 34-38 33 px/f -> 3.92 | 2% | no |
| 364 | 0158 | turtle length | 1.677 | 1.63-1.73 | ~0-3% | no |
| 365 | 0158 | turtle speed 1s | 2.584 | 2.58 | 0% | no |
| 366 | 0158 | turtle speed 1.5s | 3.904 | 3.90-3.92 | 0% | no |
| 367 | 0158 | shark length | 4.524 | 885-917 px x 0.00495 = 4.38-4.54 (family 4.57-4.6) | 1% | no |
| 368 | 0158 | shark length | 4.524 | same | 1% | no |
| 369 | 0158 | shark acceleration 1s | 7.009 | nose rest-model 1684 px over 37 frames -> 2.46 px/f^2 = 1417 px/s^2 x 0.00495 = 7.02 | 0% | no |
| 370 | 0158 | shark speed 1s | 6.863 | 7.02 x 23.5/24 = 6.87; nose frames 23-24 58 px/f -> 6.89 | 0% | no |
| 371 | 0158 | shark speed 1.5s | 10.368 | 10.38; tail frames 34-38 87-88 px/f -> 10.3-10.4 | 0% | no |

## Fixes
None. Every quick check is within 15% of the current answer; most are within 4%. The largest gap is qid 361, the 0157 turtle length: 1.52 against a family-consistent 1.65-1.70 (~10%). That is below the fix threshold and is noted here only as an optional harmonisation.

Scratch: small JSON tracks and PNG crops only; the folder is about 5 MB.
