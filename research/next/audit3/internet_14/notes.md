# Audit internet_14 (10 single-clip families, 30 scored rows)

Every family here has one clip, so step (1) became a consistency check across the rows of each clip
(same scale, same fps convention, same camera compensation). Each clip's time stamps match the dataset fps
(for example 0.52 s = 13/25 and 1.72 s = 43/25), so the dataset fps is used throughout, not the container fps.
Quick-check scripts are in `scripts/` (OpenCV on the frames; no frame dumps kept).

## Quick checks (one independent route per row)

| qid | clip | quantity | current | quick check (route) | verdict |
|---|---|---|---|---|---|
| 2044 | 0008 | sailboat speed | 4.1 | Dark-hull centre 290 to 853 px over 17.5 s gives 32.2 px/s. Hull 94-100 px = 12 m. Result 3.9-4.1 | ok |
| 2045 | 0008 | speedboat speed | 30.0 | Leading edge f260 to f320: 232 px/s × 0.127 = 29.5 (single scale). Depth-aware ×0.78 gives ~24 | ok (convention) |
| 2046 | 0008 | speedboat length | 5.21 | Dark extent 37-41 px gives 4.8-5.2 | ok |
| 2104 | 0021 | plane speed | 65 | Centre ~1000 px camera-compensated in 2 s. Scale 40 m / 293-360 px gives 56-68 | ok |
| 2105 | 0021 | plane to roof at 0 s | 72 | 534-545 px vertical to the dark roof below gives 65-74 | ok |
| 2106 | 0021 | displacement 0-2 s | 128 | 1000 px × 0.111-0.137 gives 111-137 | ok |
| 2127 | 0025 | canoe length | 9.7 | Boat 352 px. Boatman visible 60 px gives 10.3; full body 70-75 px gives 8.2-8.8 | ok |
| 2128 | 0025 | canoe speed | 0.73 | Template track: 396 px raw + 51 px pan over 15.73 s gives 28.4 px/s, so 0.72-0.82 | ok |
| 2129 | 0025 | displacement 0-5 s | 3.6 | 110 px raw + 31 px pan gives 3.2 (raw) to 4.0 | ok |
| 2995 | 0028 | blue bag length | 0.76 | Logo patch 70 px/frame (template), bag 2584 px, 36.9 frames: 0.77 at 24 fps | ok |
| 2996 | 0028 | orange suitcase length | 0.70 | 2240 px at 74 px/frame: 0.63 (24 fps) to 0.74 (20.5 fps) | ok |
| 3022 | 0033 | plate speed 0-0.52 s | 0.73 | Red blob f0 to f13 is 279 px raw, 274 px after drift, 527-537 px/s. Fork 144-150 px gives 0.71-0.75 | ok |
| 3023 | 0033 | plate speed 1-1.6 s | 0.26 | f25 to f40 is 128 px raw, 114 px after drift: 0.26-0.29 | ok |
| 3024 | 0033 | avocado size | 13.8 | Six halves 96-111 px (mean 103) give 13.9-14.5 | ok |
| 3025 | 0033 | baguette size | 52 | Three loaves 335/380/409 px give 45/51/55 | ok (instance ambiguous) |
| 3029 | 0035 | core speed 0-0.83 s | 13.4 | Left edge moves 620 px, core 568-580 px: 12.8-13.2 cm/s | ok |
| 3030 | 0035 | thumbnail width | 1.3 | Nail extent ~83 px gives ~1.5 (nail boundary unclear) | ok (within 15%) |
| 3031 | 0035 | core displacement | 11.2 | 10.7-11.0 | ok |
| 3032 | 0036 | bill length | 156 | Aspect 1407/603 = 2.33 gives 155 mm | ok |
| 3033 | 0036 | bottom hand 0-1.4 s | 0.176 | Fingertip f0 (44,4000) to thumb tip f35 (1368,1780): 2585 px, 0.208. Visible-centroid: 0.176 | FLAG (convention) |
| 3034 | 0036 | bottom hand 1.72-2.6 s | 0.249 | Thumb tip 2492 px / bill corner 2478 px: 0.316. Visible-centroid: 0.272 | FLAG (convention) |
| 3035 | 0036 | top hand 1.4-2.2 s | 0.237 | Fingertip 2059 px: 0.289. Knuckle template + 3-frame extrapolation 2015 px: 0.283. Visible-centroid: ~0.246 | FLAG (convention) |
| 3159 | 0056 | rider height | 1.57 | Rider 610 px / 1.9 s gives 0.0082 m/px. Height ~190 px gives 1.56 | ok |
| 3160 | 0056 | tree spacing | 13.0 | 990 px: naive 8.1. Perspective ×~2 (base 66 vs 134 px below horizon) gives ~16 | convention (agent in between) |
| 3161 | 0056 | leftmost tree height | 10.0 | 685 px: naive 5.6, perspective 10.6-11.2 | convention |
| 3239 | 0067 | accel at 0.17 s | 14 | Cap-edge second difference at f5: 106-143 px/f², giving 12.0-16.2 | ok |
| 3240 | 0067 | v at 0.17 s | 2.9 | Central difference at f5: 784-796 px/f, giving 2.95-3.00 | ok |
| 3241 | 0067 | v at 0.20 s | 3.2 | Central difference at f6: 861 px/f, giving 3.25 | ok |
| 3242 | 0067 | acorn width | 7.4 | Cap 50%-coverage extent 508-583 px (height 637 px = 8 cm) gives 6.4-7.3 | ok (within 15%) |
| 2050 | 0010 | shooter height | 173.8 | f0: 332 px tall, held ball 46.7 px, giving 171 | ok |
| 2051 | 0010 | ball v at 2.00 s | 552.3 | Raw ~30 px/f + ~4 px/f pan, vy ~ -12.5 px/f: 1086 px/s, giving 564 (raw 506) | ok |

## Rows checked in depth: internet_0036 hands (3033-3035)
The agent eyeballed mixed endpoints. One end was a palm or hand-centre point. The other was the small piece of hand
visible at the frame edge, which is the fingertips: the hand enters at f0 and leaves at f55 (top hand) and f65 (bottom hand).
The question times are exactly the first and last frames in which any skin is visible.
- A rigid point on the hand gives consistent results across routes:
  - 3034: auto-segmented thumb tip 2492 px; manually read bill right corner (the bill moves rigidly with the hand) 2478 px. Both give 0.316 m/s.
  - 3035: fingertip 2059 px; knuckle template track plus extrapolation 2015 px. These give 0.29 / 0.28.
  - 3033: fingertip 2585 px gives 0.208.
- A "centroid of the visible hand" convention gives 0.176 / 0.272 / ~0.246.
  This is what a mask-based or click-on-visible-blob annotation would produce, and it is close to the current values.
- No fix proposed. The gap comes from the annotation convention, not a demonstrable measurement slip.
  With about a 50/50 prior on the convention, the expected score change from switching is about 0.
  If a later stage decides the ground truth tracks a fixed point, the values are 0.208 / 0.316 / 0.287.

## Other notes
- 0056 tree rows are convention-limited: naive 2D scale vs perspective differ by about 2x. The agent's answers sit near the perspective values. Left unchanged.
- 0008 speedboat: single-scale answers kept. A depth-aware scale would give 24.6 m/s and 4.3 m.
- No unit slips, wrong-object scales or wrong-interval errors were found in any clip.

## Fixes
None.
