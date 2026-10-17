# Audit sim2_02: family simulation_0236 to 0249 (horses, rabbit, house)

All 70 rows are scored, and every row's prior is "speed of the back (brown) horse = 0.874 m/s".
Scripts are in this folder (seg48.py, seg39.py, track49.py, front.py, rab40.py, house_top.py, prof.py, snap.py).

## Family structure (verified on frames)
- Front camera (level, about 1.0 m high). The portrait clips 0236 (brown horse only), 0238 (+ front horse) and 0240 (+ front horse + rabbit)
  are the same camera and the same take as the landscape studio clip 0248/0248_segmented. The landscape sensor is the portrait one
  shifted by exactly 420 px in x and in y: rabbit centroid f0 613 vs 1032-420, f48 913 vs 1333-420, back-horse feet 628+420 = 1048 vs about 1046.
  So 0248_segmented (clean white background) gives the true pixel extents and tracks for all four front clips.
- Top cameras: 0237 (brown only), 0239/0239_seg (+ front horse) and 0241 (+ rabbit) are one nadir camera (s = 0.01366 m/px at horse-back height).
  0249 (studio, top view) is a lower nadir camera (s = 0.00821 m/px).
- The motion is identical across takes: the back horse is 3.21 px/f in every front clip and 2.667 px/f in every top clip.
  Front/back speed ratio in the top views is 1.73 to 1.76. Rabbit/back is 1.70 (0249).

## Scales and depth factors (front camera)
- s_b = 0.874 / (3.21 * 24) = 0.011345 m/px (0248_seg back horse; slopes from centroid and from both edges agree, 3.21 to 3.22).
- The feet rows on the clean mask are back 628, front 632.5 and rabbit 636 (landscape), with the horizon at 540 for a level camera.
  - Front-horse scale factor: 88/92.5 = 0.951.
  - Rabbit scale factor: 88/96 = 0.917.
- Top-view lateral offsets are front horse 1.23 m (0239_seg) or 1.24 m (0249) and rabbit 2.19 m (0249). With f about 2640 px these give
  factors of 0.959 and 0.928. The speed-ratio route (front px ratio / top ratio) gives 0.953 and 0.922.
- Adopted factors: front horse 0.955, rabbit 0.922.
- House model, solved jointly from the 0239_seg top-view outline and the 0236 front-view pixels:
  - Inputs: main gable apex/eave radial ratio 1.162, cross 1.088; main eaves 700 px (top), front eaves 727 px (front); cross ridge 624 px wide at y = 292.
  - Results: front gable plane at 1.031 times the horse depth; front cam f about 2640 px; top cam f about 2520 px at about 35.6 m.
  - Main eaves are at 4.98 m and the front gable apex at 9.23 m. Cross-wing eaves are at about 7.3 m and the cross ridge at 9.77 m.
    The cross ridge is the house top.
  - Bounding box: X = 8.51 m (main eave flare), Y = 7.52 m, Z = 9.77 m (9.23 m if only the front apex counts).
    The cross-wing X extent is 8.20 m, so in the top view it only looks wider because it sits higher.

## Quick check of every row (one route; family / clip scale)
| qid | clip | quantity | current | quick check | diff |
|---|---|---|---|---|---|
| 776 | 0236 | brown H | 1.87 | 1.86 (164 px) | +1% |
| 777 | 0236 | brown L | 2.07 | 2.10-2.17 (184-191 px) | -3% |
| 778 | 0236 | house H | 8.88 | 9.77 (front apex 9.23) | -9% |
| 779 | 0236 | house W | 8.22 | 8.51 | -3% |
| 780 | 0236 | window H | 1.22 | 1.27 (108 px) | -4% |
| 781 | 0236 | window W | 0.75 | 0.785 (66.5 px) | -4% |
| 782 | 0237 | brown L | 2.08 | 2.02 (148 px top) | +3% |
| 783 | 0237 | house W | 7.85 | 7.52 (Y) | +4% |
| 784 | 0237 | house L | 8.95 | 8.51 (X) | +5% |
| 785 | 0238 | brown H | 1.80 | 1.86 | -3% |
| 786 | 0238 | brown L | 2.07 | 2.12 | -2% |
| 787 | 0238 | house H | 9.99 | 9.77 | +2% |
| 788 | 0238 | house W | 9.33 | 8.51 | +10% |
| 789 | 0238 | window H | 1.39 | 1.27 | +9% |
| 790 | 0238 | window W | 0.84 | 0.785 | +7% |
| 791 | 0238 | front horse speed | 1.49 | 1.54 avg | -3% |
| 792 | 0238 | front H | 1.76 | 1.92 (177 px x 0.955) | -8% |
| 793 | 0238 | front L | 2.35 | 2.47 (228 px) | -5% |
| 794 | 0239 | back L | 2.00 | 2.02 | -1% |
| 795 | 0239 | house W | 7.60 | 7.52 | +1% |
| 796 | 0239 | house L | 9.00 | 8.51 | +6% |
| 797 | 0239 | front speed @1s | 1.55 | 1.51-1.67 (local top), 1.59 (front) | ~0% |
| 798 | 0239 | front L | 2.20 | 2.39 (175 px top) | -8% |
| 799 | 0240 | back H | 1.84 | 1.86 | -1% |
| 800 | 0240 | back L | 2.08 | 2.12 | -2% |
| 801 | 0240 | house H | 9.18 | 9.77 | -6% |
| 802 | 0240 | house W | 8.52 | 8.51 | 0% |
| 803 | 0240 | window H | 1.25 | 1.27 | -2% |
| 804 | 0240 | window W | 0.78 | 0.785 | -1% |
| 805 | 0240 | front speed @1s | 1.46 | 1.57 | -7% |
| 806 | 0240 | front H | 1.77 | 1.92 | -8% |
| 807 | 0240 | front L | 2.25 | 2.47 | -9% |
| 808 | 0240 | rabbit speed @1s | 1.37 | 1.47-1.56 | -10% |
| **809** | **0240** | **rabbit L** | **0.387** | **0.46-0.48** | **-18%** |
| 810 | 0241 | brown L | 2.00 | 2.02 | -1% |
| 811 | 0241 | house W | 7.00 | 7.52 | -7% |
| 812 | 0241 | house L | 7.80 | 8.51 | -8% |
| 813 | 0241 | white speed @1s | 1.54 | 1.57 | -2% |
| 814 | 0241 | white L | 2.35 | 2.39 | -2% |
| 815 | 0241 | rabbit L | 0.465 | 0.47 | -1% |
| 816 | 0241 | rabbit speed @1s | 1.46 | 1.52 | -4% |
| 834 | 0248 | back H | 1.889 | 1.86 | +2% |
| 835 | 0248 | back L | 2.10 | 2.12 | -1% |
| 836 | 0248 | front speed @1s | 1.634 | 1.57 | +4% |
| 837 | 0248 | front H | 1.955 | 1.92 | +2% |
| 838 | 0248 | front L | 2.46 | 2.47 | 0% |
| 839 | 0248 | rabbit speed @1s | 1.609 | 1.52 | +6% |
| 840 | 0248 | rabbit L | 0.458 | 0.47 | -3% |
| 841 | 0248 | rabbit H | 0.383 | 0.356 (34 px; 29-38) | +8% |
| 842 | 0249 | back L | 2.10 | 2.06 (251 px top) | +2% |
| 843 | 0249 | front speed @1s | 1.54 | 1.57 | -2% |
| 844 | 0249 | front L | 2.53 | 2.39-2.51 | +3% |
| 845 | 0249 | rabbit L | 0.505 | 0.47 | +7% |
| 846 | 0249 | rabbit speed @1s | 1.53 | 1.52 | +1% |
| 1969 | 0237s | brown L | 2.08 | 2.02 | +3% |
| 1970 | 0237s | house W | 7.85 | 7.52 | +4% |
| 1971 | 0237s | house L | 8.95 | 8.51 | +5% |
| 1972 | 0239s | brown L | 2.07 | 2.02 | +2% |
| 1973 | 0239s | house W | 7.60 | 7.52 | +1% |
| 1974 | 0239s | house L | 9.00 | 8.51 | +6% |
| 1975 | 0239s | white avg speed | 1.52 | 1.52 (4.64 px/f) | 0% |
| 1976 | 0239s | white L | 2.41 | 2.39 | +1% |
| 1988 | 0248s | brown H | 1.862 | 1.86 | 0% |
| 1989 | 0248s | brown L | 2.146 | 2.12 | +1% |
| 1990 | 0248s | white avg speed | 1.578 | 1.545 | +2% |
| 1991 | 0248s | white H | 1.96 | 1.92 | +2% |
| 1992 | 0248s | white L | 2.524 | 2.47 | +2% |
| 1993 | 0248s | rabbit avg speed | 1.633 | 1.565 | +4% |
| 1994 | 0248s | rabbit L | 0.458 | 0.47 | -3% |
| 1995 | 0248s | rabbit H | 0.383 | 0.356 | +8% |

## Deep re-measure (rows with quick-check diff of 15% or more): qid 809 only
- Route 1 (front, same take as 0248):
  - 0248_seg clean rabbit mask over 49 frames: median 46 px (p10 44).
  - 0240's own visible length (zoom crops at f12/f24/f36, grass hides the feet): 43-44 px.
  - Result: 43-46 px x 0.011345 x 0.917-0.928 = 0.45-0.48.
- Route 2 (top view 0249):
  - Zoomed rabbit at f12/f24 is 52-58 px (body only to hind feet).
  - 52-58 px x 0.008207 x 1.05 (the rabbit's back is about 1 m below the horse-back plane that sets the scale) = 0.45-0.50, middle 0.47.
- The family agrees: 0248 0.458, 0248_seg 0.458, 0241 0.465 (the 0249 agent's 0.505 is high).
- Why 0.387 is wrong:
  - The 0240 agent read the contact rows in grass (rabbit 1061 vs brown 1046, a 15 px gap). The clean twin shows an 8 px gap (1048 vs 1056).
  - It also used a raised horizon of 973, which gave a depth factor of 0.83 instead of about 0.92.
  - It also measured 41 px instead of 44-46 px.
- FIX: 809 changes from 0.387 to 0.47.

## Not fixed, but noted (below the 15% threshold or not resolvable)
- House naming: the top-view agents set width = Y (7.52) and length = X (8.51). If the question writer instead used width = X
  (as in the front-view clips), rows 784/796/1971/1974 would be about 19% high and 811 about 18% low. This is unresolved without labels, so no change.
- The house top is the cross-wing ridge (about 9.77 m), not the front gable apex (9.23 m). 778 (8.88) and 801 (9.18) are 6-9% low.
- 0238 house and window rows are 7-10% high: that agent applied a depth factor of 1.15 for the house wall, while the joint model gives about 1.03.
- 792/806 (front horse height 1.76/1.77) are about 8% low against 1.92. 0248 and 0248_seg (1.955/1.96) agree with 1.92.
- 808 (rabbit speed at 1 s, 1.37) is 7-12% low, because of the same over-strong rabbit depth factor (0.83). It is below the threshold.
