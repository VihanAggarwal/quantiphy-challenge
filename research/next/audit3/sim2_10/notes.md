# Audit sim2_10 (family simulation_0243..0247 + segmented twins)

All 31 rows scored, all "agent measurement or pipeline" (no stated-fact rows).
Prior in every clip: antelope/deer speed = 1.277 m/s. Same horned "antelope"/"deer" model + hopping rabbit.

## Family structure (verified on frames)
- 0243, 0244, 0245 (+0243_seg, 0245_seg): SAME side camera, 1080x1920, same antelope animation.
  Antelope nose track 0243_seg 6.50 px/f, 0245_seg 6.52 px/f (centroid, left edge and right edge all 6.52).
  -> 195.6 px/s -> s = 0.006529 m/px. Rabbit feet and hooves on the same row (y~1548) -> same depth.
  0244 = 0243 + rabbit (the 0244-0243 frame difference isolates the rabbit, which follows the 0245_seg trajectory exactly).
  0243_seg antelope width per frame = 0245_seg width except f0-11 (tail hidden by left bushes) -> same pose.
- 0246: top-down perspective camera (1920x1080). 0247/0247_seg: elevated oblique camera.
- Rabbit hop timing (13-frame cycle, peaks at f7,20,33,46,59) and antelope gait (width maxima f10,30,50,69) are identical
  in 0245, 0246, 0247 -> same scripted motion. Rabbit average = 87.35 px per 13 f in 0245 = 6.72 px/f -> 1.316 m/s.

## Key measurements
- Antelope side view (0245_seg mask, thr 245): height median 421 px (p10-p90 417-423) -> 2.75 m;
  x-extent median 488 px (472-503) -> 3.19 m.
- Rabbit side view: x-extent median 71 px (thr 230: 70, thr 252: 76) -> 0.465 m; height median 62 px (66 at thr 252) -> 0.405-0.43 m.
- 0246 top view, template tracks of antelope parts: head 9.65, mid-torso 9.20, rump 9.11, tail tuft 8.38 px/f; rabbit 8.59 px/f.
  The speed rises with the height of the part: this is perspective from the overhead camera. Ground-level scale is 1.277/(8.38*30) = 0.00508 m/px.
  Same-motion route: 1.316/(8.59*30) = 0.00511 m/px (agrees within 0.6%).
  Check: perspective-corrected antelope length (nose at head scale, tail at ground scale, principal point x=960)
  = 3.22 m median, which matches the side view's 3.19 m. Using one mid scale gives 3.12 m; the agent's 2.90 m used a head-level scale.
- 0247: tail-tip (near ground) left-edge slope 7.44 px/f -> ground scale 0.005722 m/px; same-motion rabbit scale
  1.316/(7.66*30) = 0.005727 (agree). Rabbit 7.66 px/f -> 1.315 m/s; deer centroid 7.88 px/f (torso is nearer the elevated camera).

## Row table (quick check = my independent value)
| qid | clip | quantity | current | quick check | diff | verdict |
|---|---|---|---|---|---|---|
| 817 | 0243 | antelope height | 3.03 | 2.74 | +10.6% | below threshold. Agent px speed 175 px/s is wrong; the true value is 195.6 |
| 818 | 0243 | antelope length | 3.50 | 3.19 | +9.7% | below threshold, same cause |
| 819 | 0243 | left tree height | 10.0 | 7.7 (k=1) .. 10.4 (k=1.4) | ? | unresolved (tree depth unknown) |
| 820 | 0244 | antelope height | 2.71 | 2.74 | -1% | ok |
| 821 | 0244 | antelope length | 2.78 | 3.19 | -12.8% | below threshold. Tail tip missed (430 px vs 488 px) |
| 822 | 0244 | left tree height | 10.2 | 7.7..10.4 | ? | unresolved |
| 823 | 0244 | rabbit speed | 1.306 | 1.316 | -0.8% | ok |
| 824 | 0244 | rabbit height | 0.43 | 0.405-0.43 | ~+3% | ok |
| 825 | 0244 | rabbit length | 0.47 | 0.465 | +1% | ok |
| 826 | 0245 | antelope height | 2.779 | 2.75 | +1% | ok |
| 827 | 0245 | antelope length | 3.196 | 3.19 | 0% | ok |
| 828 | 0245 | rabbit speed at 1 s | 1.399 | 1.316 avg (instantaneous value can't be resolved) | +6% | ok |
| 829 | 0245 | rabbit height | 0.43 | 0.405-0.43 | ok | ok |
| 830 | 0245 | rabbit length | 0.463 | 0.465 | 0% | ok |
| 831 | 0246 | antelope length | 2.903 | 3.22 (persp.) / 3.19 side | -9.5% | below threshold. Head-level scale used |
| 832 | 0246 | rabbit speed at 1 s | 1.257 | 1.309 (ground scale) / 1.316 (same motion) | -4.5% | ok |
| **833** | 0246 | rabbit length | 0.397 | 0.467 (92 px x 0.00508) / 0.465 side | -14.6% of new, +17% of current | **FIX -> 0.465** |
| 1628 | 0247 | rabbit length | 0.42 | 0.463-0.481 (81-84 px x 0.00572) | -9..-13% | below threshold |
| 1629 | 0247 | deer length | 3.0 | ~3.15-3.2 | -5% | ok |
| 1630 | 0247 | rabbit avg speed | 1.2 | 1.315 (ground scale) / 1.316 (same motion) | -8.8% | below threshold. Deer-torso scale used |
| 1977 | 0243_seg | deer height | 2.7 | 2.74 | -1.5% | ok |
| 1978 | 0243_seg | deer length | 2.9 | 3.19 | -9% | below threshold |
| 1979 | 0243_seg | tree behind deer (same left tree) | 7.4 | 7.7..10.4 | ? | unresolved. 7.4 is under the k=1 bound of 7.7 |
| 1980 | 0245_seg | deer height | 2.735 | 2.75 | 0% | ok |
| 1981 | 0245_seg | deer length | 3.187 | 3.19 | 0% | ok |
| 1982 | 0245_seg | rabbit avg speed | 1.317 | 1.316 | 0% | ok |
| 1983 | 0245_seg | rabbit height | 0.43 | 0.405-0.43 | ok | ok |
| 1984 | 0245_seg | rabbit length | 0.463 | 0.465 | 0% | ok |
| 1985 | 0247_seg | rabbit length | 0.42 | as 1628 | -9..-13% | below threshold |
| 1986 | 0247_seg | deer length | 3.0 | as 1629 | -5% | ok |
| 1987 | 0247_seg | rabbit avg speed | 1.2 | as 1630 | -8.8% | below threshold |

## Fix proposed
- Q833 (0246 rabbit length) 0.397 -> 0.465.
  - Why the current answer is wrong: 0246 is an overhead perspective view. The agent's scale 0.004364 m/px (9.75 px/f from a torso+head template)
    belongs to the antelope's head/back plane, about 1.7-2 m up and nearer the camera. The rabbit is at ground level, where the scale is 0.00508 m/px.
  - Route A (within the clip): 92 px top-view extent (orange body + pale head card, median of 7 zoomed frames; agent 91 px) x 0.00508 = 0.467.
  - Route B (same object, side view 0245/0245_seg): 71.3 px x 0.006529 = 0.465.
  - Route C (same motion): rabbit-plane scale 0.00511 x 92 = 0.470.
  - The routes agree within 1-3%.
  - Borderline: the change is 17% of the current value but 14.6% of the new value.

## Changes below the 15% threshold (concrete causes found, not proposed as fixes)
- 0243 (Q817 3.03, Q818 3.5): wrong antelope px speed (175 vs 195.6 px/s). Values on the family scale would be 2.74 and 3.19.
- Q821 (0244 antelope length 2.78): tail tip missed. 3.19 by the identical-pose segmented twins.
- Q831 (0246 antelope length 2.903): perspective. 3.22 when corrected.
- Q1628/1985 (0247 rabbit length 0.42) and Q1630/1987 (rabbit avg speed 1.2): the deer-torso scale was used for the ground-level rabbit.
  The ground scale gives about 0.465 m and 1.315 m/s.
- Trees (Q819 10.0, Q822 10.2, Q1979 7.4): same tree, inconsistent answers. Base hidden by bushes. Horizon is about y 1390, so the camera is about 1.0 m up.
  Height = 0.00653*(1023k+157): k=1 gives 7.7, k=1.2 gives 9.0, k=1.4 gives 10.4. The tree is behind the antelope (the horn occludes it), so k>1 and 7.4 is too low.
  The tree depth can't be measured, so no fix. A family-consistent value would be about 9-10.

Scripts: s/*.py. Small CSV tracks: *_t245.csv, top46.csv. Crops viewed are in png/.
