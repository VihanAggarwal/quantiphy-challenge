# Audit sim2_05: family simulation_0075 (0068, 0068_segmented, 0069, 0070, 0071, 0072, 0073, 0075)

## Family structure
- All 8 clips use the same fixed nadir camera. The median backgrounds of every clip match 0073 to within 0.01 px (phase correlation), so there is one world scale for the whole family.
- The same scripted motions appear in each clip that shows them. Blob tracks are identical across clips:
  - white van: accelerates from rest at a constant rate (vertex at video frame about -1)
  - yellow car: constant speed through the right turn
  - bicycle: constant speed
  - pedestrian: constant speed
- The stated priors (van length 6 m, yellow length 5.44 m, bike speed 5.33 m/s, van acceleration 4 m/s^2) give mutually consistent pixel scales:

| Prior | Pixel measurement | Scale |
|---|---|---|
| van acceleration 4 m/s^2 | front edge 162.5 px/s^2 (all 4 clips) | 40.6 px/m at the front-edge height |
| van acceleration 4 m/s^2 | rear-bottom edge 159.9 px/s^2 | 40.0 px/m |
| yellow length 5.44 m | 217.5-220 px | 40.0-40.4 px/m |
| bike speed 5.33 m/s | blob centroid 8.88-8.95 px/frame (4 clips) | 40.2 px/m |
| van length 6 m | 243-245 px | 40.5-40.8 px/m |

  The ground scale is 40.0-40.5 px/m, with a spread of about 2%. The camera is very high (about 60-70 m), so height effects are 1-2%.

## Quick-check table (every scored row)

The quick route uses my own background-difference blobs, profiles and half-level edges, at about 40.2 px/m unless a prior-specific scale is noted.

| qid | clip | quantity | current | quick check | diff | note |
|---|---|---|---|---|---|---|
| 33 | 0068 | yellow speed @2.5s | 4.00 | 6.80-6.82 px/fr -> 4.02-4.08 | <2% | constant speed, turn done by f60 |
| 34 | 0068 | yellow length | 5.44 | stated | - | stated fact |
| 35 | 0068 | yellow width | 2.02 | 81-82 px -> 2.02-2.04 | <1% | |
| 36 | 0068 | van width | 2.32 | body 86-88 px (2.15-2.19), mirrors ~98 px (2.42) | ±5-8% | mirror ambiguity; between both |
| 37 | 0068 | van length | 6.0 | stated | - | stated fact |
| 38 | 0069 | pedestrian speed @1s | 1.20 | 2.03-2.05 px/fr -> 1.20-1.23 | <3% | |
| 39 | 0069 | van width | 2.30 | as 36 | ±5-8% | mirror ambiguity |
| 40 | 0069 | van length | 6.0 | stated | - | stated fact |
| 41 | 0070 | yellow speed @2.5s | 4.08 | 4.02-4.08 | <2% | |
| 42 | 0070 | yellow width | 1.99 | 2.02 | 1.5% | |
| 43 | 0070 | bike speed @1s | 5.33 | identical track to 0072/0073 prior (5.33) | 0 | |
| 44 | 0071 | yellow speed @2.5s | 4.09 | 4.02-4.08 | <2% | |
| 45 | 0071 | yellow width | 1.98 | 2.02 | 2% | |
| 46 | 0071 | pedestrian speed @1s | 1.24 | 1.20-1.23 | <3% | |
| 47 | 0072 | pedestrian speed @1s | 1.21 | 1.20-1.23 | <2% | |
| 48 | 0073 | van width | 2.24 | as 36 | -4%/+8% | mirror ambiguity |
| 49 | 0073 | van length | 6.0 | stated | - | stated fact |
| 50 | 0073 | dist van-bike @1s | 5.76 | box centres f24: dY 214, dX 87.5 px = 231 px -> 5.72-5.78 | <1% | |
| 51 | 0073 | dist van-bike @2s | 5.00 | f48: dY 180, dX 87.5 = 200 px -> 4.95-5.00 | <1% | |
| 52 | 0073 | van accel | 4.0 | stated | - | stated fact |
| 53 | 0073 | platform side | 1.95 | half-level 78.6-80.5 px -> 1.96-2.00 | <3% | |
| 54 | 0073 | van speed @1s | 4.13 | a*(24.5/24) = 4.08 (vertex at f -1) | 1% | |
| 55 | 0075 | yellow length | 5.44 | stated | - | stated fact |
| 56 | 0075 | pedestrian speed @1s | 1.18 | 1.20-1.23 | -2 to -4% | |
| 57 | 0075 | yellow speed @2.5s | 4.00 | 4.02-4.08 | <2% | |
| 58 | 0075 | yellow width | 1.94 | 2.02 | -4% | |
| 59 | 0075 | purple width | 1.77 | thr20 73 px -> 1.81 | 2% | |
| 60 | 0075 | purple length | 4.75 | edges 1242 to 1437.5 = 195.5 px -> 4.79-4.86 | 1-2% | |
| 61 | 0075 | bike speed @1s | 5.33 | = sibling prior | 0 | |
| 62 | 0075 | platform side | 1.97 | 1.96-2.00 | <2% | |
| 63 | 0075 | van width | 2.40 | as 36 | +1%/+11% | mirror ambiguity |
| 64 | 0075 | van accel | 3.95 | 4.0 (sibling stated) | 1% | |
| 65 | 0075 | green width | 1.80 | 74 px -> 1.81-1.84 | 1-2% | |
| 66 | 0075 | green length | 4.69 | 335.5 to 529.5 = 194 px -> 4.75-4.83 | 1-3% | |
| 1779 | 0068_seg | yellow avg speed | 3.96 | path 478 px / 71 fr = 6.73 px/fr -> 3.98-4.04 | <2% | |
| 1780 | 0068_seg | yellow length | 5.44 | stated | - | stated fact |
| 1781 | 0068_seg | yellow width | 2.02 | 2.02 | 0 | |
| 1782 | 0068_seg | van width | 2.32 | as 36 | | mirror ambiguity |
| 1783 | 0068_seg | van length | 6.0 | stated | - | stated fact |

## Fixes
None. No scored row differs from the quick check by 15% or more, so no in-depth re-measurement was triggered. The family is internally consistent:

| Quantity | Answers across clips |
|---|---|
| yellow width | 1.94-2.02 |
| yellow speed | 4.00-4.09 |
| pedestrian speed | 1.18-1.24 |
| platform side | 1.95/1.97 |

## Residual risks (not fixable under the 2-route rule)
- **White van width** (36, 39, 48, 63, 1782; answers 2.24-2.40): the body is about 2.15 m and mirror-to-mirror is about 2.42 m. Whether the GT AABB includes the mirrors is unknown. Every current answer is within 11% of either reading. The answers could optionally be unified at about 2.32, but no evidence supports a single value.
- **Distances** (50, 51) assume the object origins are at the bbox centres. A different origin convention for the bicycle could shift them by 0.3-0.5 m.

Scripts are in `scr/`. Blob tracks are stored as small JSON files. No frame stacks were saved, and the full-res background PNGs were deleted.
