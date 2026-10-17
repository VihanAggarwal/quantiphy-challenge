# Audit internet_11 (internet_0045, 0047, 0052, 0061, 0062)

All five clips are singleton families, so there was no cross-clip size transfer to check. I quick-checked all 30 scored rows from the frames with my own scripts (in this folder: t45/d45, t47b/t47c/l47/fb47, t52, t61b-e, t62).

## Scales (independent re-measurement)

| clip | prior | my route(s) | my scale | agent scale |
|---|---|---|---|---|
| 0045 | roll v = 107.3 cm/s | white-mask track: lateral px speed grows 55 to 70 px/frame as the roll approaches. Over f18-28 it is 66.7 px/frame; over the whole path, f4-30, it is 62.8 | 0.0535 to 0.057 cm/px | 0.0535 |
| 0047 | ball v(0.5 s) = 2.94 m/s | stabilized (phase-corr) colour-diff centroid: 77.5-77.8 px/frame at f15; template match f12-18: 79.2; f13-17 centroid: 76.4. Speed is constant within +-3% over f3-19 | 1.26 mm/px (+-2%) | 1.283 |
| 0052 | avg rider speed 2.91 m/s | stabilized diff-mask leading edge: 1010 px / 54 frames = 561 px/s | 0.00519 m/px | 0.00518 |
| 0061 | g | rebound parabola f48-56: 31.1-32.8k px/s^2 (resid < 14 px); fall f40-44 body centre: about 29.7k (noisy) | 0.0306-0.0316 cm/px | 0.0302 |
| 0062 | g | dark-mask parabola f67-79: lead 10.3-10.5k, centroid 10.37-10.47k px/s^2, vertex t = 2.200 s | 0.000942 m/px | 0.000945 |

## Row table

| qid | quantity | current | quick check (my route) | diff | verdict |
|---|---|---|---|---|---|
| 3084 | roll diameter (cm) | 8.0 | see note A: 7.4 (physical, if the back objects are life-size) / 11.7-12.0 (prior read as the 3D speed) / 10-14 (2D) | n/a | no fix (structural ambiguity) |
| 3085 | green bottle h | 30.6 | 573 px x 0.0535-0.057 = 30.7-32.7 | <7% | ok |
| 3086 | PET bottle h | 22.8 | 425 px -> 22.7-24.2 | <7% | ok |
| 3087 | bowl h | 9.7 | 185 px -> 9.9-10.5 | <8% | ok |
| 3088 | bottle distance | 13.1 | centres 243 px -> 13.0 (edge gap 103 px -> 5.5) | 1% | ok (centre convention kept) |
| 3089 | kettle-plate | 53.7 | bbox centres 1006 px -> 53.8 (kettle body centre: 50.0) | <7% | ok |
| 3096 | ball diameter (cm) | 24.22 | 226-228 px x 1.26 = 28.5 | 15% | FIX -> 28.5 |
| 3097 | red-red (m) | 1.609 | centres 1500 px (row 550-600) -> 1.89 | 15% | FIX -> 1.89 |
| 3098 | ball-white (m) | 1.131 | t=0 centre-centre 1104 px -> 1.39; edge-edge 969 px -> 1.22 | 7-19% | FIX -> 1.33 (hedge, same as agent's at my scale) |
| 3099 | displacement 0.1-0.3 s (m) | 0.4928 | template f3->f9 461 px, linear fit 458 px -> 0.58 | 15% | FIX -> 0.58 |
| 3100 | left red-white (m) | 1.031 | centres 238 -> 1203 = 965 px -> 1.22 | 15% | FIX -> 1.22 |
| 3101 | line width (cm) | 4.944 | red 46-49 px, white 42, horizontal red 44 -> 46 px -> 5.8 | 15% | FIX -> 5.8 |
| 3129 | rider height | 1.65 | 310-317 px x 0.00519 = 1.61-1.65 | <3% | ok |
| 3130 | tree distance | 8.6 | trunk centres about 1050 px; horizon 640-680 from parked-car heights; ground-plane ratio 1.36-1.48 (with and without the raised-planter correction) -> 7.4-8.1 m (2D would give 5.4) | 6-16% | no fix (horizon-sensitive) |
| 3131 | sign height | 0.48 | panel 70.5 px x ratio 1.31 -> 0.48 (standard 18 in = 0.457) | 0-5% | ok |
| 3132 | sign width | 0.32 | 46.5 px -> 0.316 (standard 12 in) | 1% | ok |
| 3133 | scooter height | 1.08 | about 210 px -> 1.09 | 1% | ok |
| 3134 | wheel-to-wheel | 1.05 | outer extents 202 px -> 1.05 | 0% | ok |
| 3195 | acorn width | 8.1 | cap 265-268 px -> 8.1-8.5 | <5% | ok |
| 3196 | acorn height | 8.0 | no stem 283-292 px -> 8.6-9.2; with stem about 338 px -> 10.3-10.7 | 8-15% / 25% | no fix: the stem convention is ambiguous and the no-stem route is under 15%. Note B |
| 3197 | v(1.40 s) | 1.68 | v = g (1.40 - t0), t0 = 1.217-1.230 s from the fall fit -> 1.67-1.79 | <=6% | ok |
| 3198 | gap at 1.40 s | 21.1 | pixels 713 px -> 21.8-22.5; kinematic (contact about 1.50 s) 21.7-22.7 | 3-7% | ok |
| 3199 | gap at 1.80 s | 20.7 | rebound parabola: bounce 1.51 s, apex 1.7285 s -> 20.9 cm; px 683 px -> 20.6-20.9 | 1% | ok |
| 3200 | disp 1.30-1.40 | 11.9 | 0.49 x (2.7 - 2 t0) -> 11.9-12.9; px 400 px -> 12.2-12.6 | <8% | ok |
| 3201 | wallet long | 21.1 | corners 219-226 px -> 20.6-21.3 | <3% | ok |
| 3202 | wallet short | 13.1 | 135-142 px -> 12.7-13.4 | <3% | ok |
| 3203 | v(2.5) | 2.88 | g x 0.300 = 2.94; px 3130 px/s -> 2.95 | 2% | ok |
| 3204 | corner-floor at 2.5 s | 0.77 | lead x 754 to floor 1545-1580 -> 0.745-0.78; kinematic (impact 2.693 s) 0.75 | 3% | ok |
| 3205 | disp 2.2-2.5 | 0.443 | 0.5 g 0.3^2 = 0.441; px 464-475 -> 0.44-0.45 | 0% | ok |
| 3206 | v(2.6) | 3.85 | g x 0.400 = 3.92; px 4175 -> 3.93 | 2% | ok |

## Fixes proposed (internet_0047, all 6 rows; one cause)

The current 0047 values are exactly the agent's prior-scaled answers multiplied by 0.83801: 28.9 -> 24.2186, 1.92 -> 1.6090, 1.35 -> 1.1313, 0.588 -> 0.4928, 1.23 -> 1.0308 and 5.9 -> 4.9443. So the clip was rescaled until the ball is a standard basketball (24.2 cm) and the lines are 2 in wide. That contradicts the stated prior, which is exact.

- Over frames 3-19 the ball moves at a constant 76.4-79.2 px/frame. I measured this two ways: a colour-difference centroid after phase-correlation stabilization, and template matching. With v(0.5 s) = 2.94 m/s this gives 1.26 mm/px (+-2%).
- The current displacement of 0.493 m over 0.1-0.3 s implies 2.46 m/s, but the prior says 2.94 m/s at 0.5 s and the pixel speed is the same at both times. So the current answers are internally inconsistent with the prior by 16-19%.
- Real-world cues (floorboards 52 px, ball 24 cm, 2-in lines) do say the physical world is about 0.85x the prior's world. That is exactly why the current answers were rescaled. Under the task premise that the prior is exact for the clip and sets the scale, the labels follow the prior.
- Caveat: if a validated rule (for example a basketball identity transfer) deliberately set 24.22 cm, 3096 and 3101 are the rows most likely to be annotator reference sizes. 3097-3100, the distances and displacement, are the most robust part of this fix: they follow the prior even if only the reference object was physical.
- No perspective correction was applied: the ball-centre scale is used for the floor (2D, D2 category). A 3D reading of the prior would make the floor rows about 8% larger still (camera about 1.9 m, ball centre 0.14 m above the floor).
- Measured |current - new| / new is 14.7-15.3% for most rows (18.7% for 3098 under the centre convention). Treat the six rows as one decision about the scale.

New values: 3096 28.5, 3097 1.89, 3098 1.33, 3099 0.58, 3100 1.22, 3101 5.8.

## Note A (0045 roll diameter, not changed)
- The camera is low and roughly level: the roll's centre stays 0.97-0.99 D below the optical axis, and the camera is about 1.5 D above the desk. The roll approaches the camera: its face grows from 190 px (f4) to 267 px (f27).
- The back objects are life-size at 0.0535 cm/px: wine bottle 30.6, 0.8 L T-fal kettle 17, PET bottle 22.8. That implies the prior was computed in 2D at the back-object depth. The physical roll would then be about 7.2-7.5 cm, which supports the current 8.0.
- If instead the prior is the true 3D speed, the roll's own size-change geometry gives D = 11.7-12.0 cm (robust to the focal length 1300-1700), and a standard toilet-roll core read from the hole ratio gives about 10.8 cm. But then the bottle would be about 46-55 cm.
- 2D labelling (same-frame px diameter x 2D scale) would give 12.7-13.7.
- No two routes agree against the current value with a concrete error, so no fix. This is the least certain row of the item.

## Note B (0061)
- The camera is not exactly perpendicular to gravity: the acorn's body width shrinks about 12% during the fall (f36 -> f44), so the acorn recedes. Sizes taken at the hold position could therefore be up to about 10% smaller than the rebound-derived scale gives.
- The width (8.1) and height (8.0) are left as they are. 8.0 is below the no-stem value at the agent's scale (8.9), but within this depth uncertainty.
- The 3D kinematic rows (v, gaps, displacement) depend only on t0 and the contact times, and they agree with the current values.

## Disk
Work folder is about 18 MB (crop PNGs and scripts). I wrote no frame stacks.
