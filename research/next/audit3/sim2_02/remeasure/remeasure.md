# sim2_02 independent remeasure: qid 809 (simulation_0240, length of the rabbit, m)

Prior: brown horse (the one at the back) speed is 0.874 m/s. The video runs at 24 fps and is 1080x1920 portrait. I used frames 0-48.
I did not read ../notes.md. I read only the input json and the listed blind agent notes (0240, 0241, 0248, 0249, 0238).

## Pixel measurements in 0240
- Brown horse px speed comes from a colour-silhouette track (HSV coat mask) over frames 0-48. Torso-band centroid: 3.215 px/f. Rump edge: 3.18. Front edge: 3.26. Overall centroid: 3.19.
  I used 3.215 px/f (77.2 px/s), which gives s_b = 0.874/77.2 = 0.011327 m/px at the brown horse's depth.
  (The segmented twin 0248_seg gives 3.214-3.223, so the two agree.)
- Rabbit px speed is 6.22 px/f (iterative aligned-template stack; the edge fits agree). White horse: 5.94 px/f.
- Rabbit px length in 0240: the colour+diff mask gives a median of 40. Half-max on the aligned diff-stack gives 41.6-42.8. Visual reading of the aligned mean image gives about 43.5.
  The rabbit sits in grass and has low contrast against the wall and grass, so this underestimates (see below).
- Ground contact rows: brown hooves about 1046, white about 1050-1055, rabbit bottom about 1060-1062.

## Same-geometry twin (0248 / 0248_segmented, studio)
0248 shows the same px speeds for all three animals (brown 3.21-3.22, white 5.94, rabbit 6.23) and the same px horse sizes (brown H 164 vs about 163 in 0240; white 225 x 177 vs 222 x 175). So the camera distance and animal layout are the same as in 0240.
- Rabbit x-extent on the clean white-background segmented render, 50% coverage: median 44.2 px, mean 44.8. The mask (thr 120) gives a median of 45.0.
  Removing the bottom 12 rows (simulated grass) barely changes it (44.9), so 0240's lower number comes from low contrast and blur, not from hidden feet.
  Raw 0248 diff-threshold: 42.5-44.2. Adopted side-view px length: **44.3 +/- 1 px**.
- Contact rows in 0248_seg: brown 627, white 631-632, rabbit 635.

## Depth ratio of rabbit to brown horse (the key correction)
1. 0248_seg contact rows: Z_r/Z_b = (627-y_h)/(635-y_h). A level camera (y_h=540) gives 0.916. y_h=520-525 gives 0.927-0.930.
2. Top-down layout (0249, 0241) gives lateral offsets brown->rabbit of 2.25 m and 2.17 m, and brown->white of 1.32 m and 1.22 m. These come from centroid rows with a perspective/height correction and f=2667 px (default 50 mm on a 36 mm sensor).
   With Z_b = f*s_b = 30.2 m this gives Z_r/Z_b = 0.927 and Z_w/Z_b = 0.958. The same ratios applied to 0248's contact rows give one common horizon (about 525) for both white and rabbit.
   f is about 2667 is supported by the 0241 roof apex/eave radial ratio (1.10-1.16) together with the about 4 m gable height seen in 0240. A wide lens (f about 1200) would need a 1.5 ratio.
3. Speed transfer. Top-down rabbit/brown px-speed ratio: 0249 7.556/4.41 = 1.713, 0241 4.55/2.682 = 1.697 (raw). The rabbit is lower than the horse back, so the true ratio is about 5% higher, about 1.79.
   The side ratio is 6.22/3.215 = 1.937, so Z_r/Z_b = 0.91-0.94. White: 1.73-1.78 vs 1.85 gives 0.936-0.963, which is consistent.
   The previous ratio of about 0.83 (horizon 973 assumption) would need a true rabbit/brown speed ratio of 1.61. That is below even the raw top-down 1.70, which is itself biased low, so 0.83 is ruled out.
Adopted Z_r/Z_b = **0.925 +/- 0.012**. This implies a 0240 horizon around y of about 850 (camera pitched about 2 deg down), not 960-987.

## Result
L = 44.3 px * 0.011327 m/px * 0.925 = **0.464 m**.
- Route 2, top-down 0249 (its own brown prior): rabbit 54.3 px (diff 50%; sat 51-54) * 0.008258 m/px * height corr 1.056 = 0.473 m (range 0.447-0.489).
- Route 3, 0241 top-down: 31-35 px * 0.01357 * 1.034 = 0.435-0.49 (noisy, dark rear edge on grass).
- Route 0, 0240 pixels only (42-43.5 px): 0.440-0.456.
- Self-consistency check: rabbit L_px / rabbit px-speed is 7.11 in the side view and 7.19-7.42 in the top view. They agree within 1-4%, so the motion is shared and the sizes are consistent.

**Best value: 0.466 m** (blend of side 0.464 and top-down 0.473). Confidence: medium-high. Expected error about +/-4%: px length +/-2%, depth ratio +/-1.3%, and which frame/pose the bbox uses +/-3%.
The current answer of 0.387 is about 17% low because its depth correction assumed the horizon at 973.

Scripts are in scripts/ (rabbit.py, rab_stack.py, brown_track.py, track2d.py, seg.py, seg_halfmax.py, s0248*.py, multi_thr.py).
