# internet_0054 independent remeasure (qids 3145-3150)

Prior: average speed of scooter rider = 4.9 m/s. Clip 3840x2160, 94 frames @30 fps.
I did not read ../notes.md or ../work/. I read only the original agent notes
(research/blind/out/blind_test/internet_0054/notes.md). Scripts are in scripts/ (originally run from the scratchpad).

## Camera motion
Phase correlation on clean background ROIs (left hedge x50-900, right hedge x3150-3750, building).
Pan: scene drifts +32 px in x over the clip, the same at hedge and building depth, so this is rotation.
Small roll change: dy is +0.8 on the left and +19 on the right at f93, about 0.35 deg.
Rider positions were stabilised to frame 0 with the mean hedge shift (shifts_clean.txt).

## Rider speed (sets the scale)
Median-background subtraction on the stabilised band, then white-shirt centroid per frame (rider_track2.txt).
- Shirt centroid: linear fit -16.58 px/frame; net (x93-x0)/93 = -16.68 px/frame.
  By thirds: 16.1, 16.3, 17.2. The rider gets ~3% closer and slightly faster toward the left.
- Front wheel read by hand at f15/32/48/64/80: 16.5 px/frame over f15-80.
- Unstabilised raw value: 16.22 px/frame.
- Adopted 16.6 px/frame = 498 px/s, giving s_r = 4.9/498 = 0.00984 m/px at the rider's ground row (wheel contact y ~ 1125.5, stabilised).

## Ground plane / horizon (depth correction for benches and canopy)
- Route A: fit a pinhole camera to the court centre circles (outer 12 ft, inner ~4 ft; radii left free except the outer one).
  Best f = 2960 px, which is about 28 mm equivalent and plausible for an iPhone.
  Pitch 3.3 deg, roll -0.09 deg, horizon y ~ 910. The fit is consistent at f0, f47 and f93.
- Route B: the centre line's half-max width is linear in image row (rms 0.17 px) and reaches zero at y = 870-875.
  This does not depend on the model.
- Adopted y_h = 890 +- 20.
- Benches' front legs and the pergola's centre post stand at y ~ 1086-1087, against the rider's y ~ 1125.5.
  Depth factor (1125.5-890)/(1086-890) = 1.20, ranging 1.185-1.224 across the horizon range.
  So the benches and pergola front are ~20% farther away than the rider.

## Pixel measurements (stabilised frame-0 coords; rider values normalised to row 1125.5)
| item | px | frames / notes |
|---|---|---|
| person, cap top to soles on the deck | 281, 285.7, 288.5, 290, 290 -> normalised mean 286.4 | f15, f32, f48, f64, f80 |
| scooter, ground to handlebar grip top | 189-192 -> 190.5 | 5 frames; the hand hides the bar, so the grip top was estimated at ~935 |
| scooter wheels, outer extent | 177, 179, 181, (186) -> ~179.5 | |
| scooter wheels, centre to centre | 140, 141, 145.5, 145 -> ~142.6 | |
| benches, front face (legs/arm scrolls) | 278, 274, 271, 274 -> 274 | ground row 1086 |
| canopy, foliage extent | x 880 to ~2718 = 1838 | right edge merges with background trees, +-10 px |
| canopy, ground to top of foliage mass | 1087 - 515 = 572 | sprigs reach 502 |

## Results (prior-anchored, scale at each object's own depth)
| qid | item | value | 2D (no depth correction) | real-world alternative* |
|---|---|---|---|---|
| 3145 | person height | **2.82 m** | 2.82 | 1.78 |
| 3146 | bench length | **3.24 m** (3.19-3.30) | 2.70 | 2.09 |
| 3147 | canopy height | **6.73 m** (6.64-6.85) | 5.63 | 4.34 |
| 3148 | canopy width | **21.6 m** (21.3-22.0) | 18.1 | 13.9 |
| 3149 | scooter height | **1.87 m** | 1.87 | 1.19 |
| 3150 | wheel-to-wheel | **1.58 m** (mid of c-c 1.40 / outer 1.77) | same | 0.89-1.12 |

*Real-world alternative: the scale comes from the court circle, assuming the standard 12 ft basketball centre circle (inner/outer ratio measured 0.33).
That gives 0.00623 m/px at the rider, which puts the rider at 3.1 m/s.

## Major flag: the prior conflicts with real-world size by a factor of ~1.6
- With the 4.9 m/s prior, the rider is 2.82 m tall and the scooter is 1.87 m tall.
- The court geometry (a standard 12 ft circle), the scooter (an M365-class scooter is ~1.14 m tall) and normal human height all agree on 0.0060-0.0063 m/px at the rider. That scale implies a true speed of ~3.0-3.1 m/s.
- I report the prior-anchored values, as the rules require.
- If the ground truth uses physical sizes, every answer is ~1.57-1.64x too high.
- If the ground truth was produced as 2D pixels x (4.9 / pixel speed), then the benches and canopy have no depth correction. For those, use the 2D column.
- The depth-corrected and 2D values differ by ~20% for 3146-3148. They are identical for 3145, 3149 and 3150.
