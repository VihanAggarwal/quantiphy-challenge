# Audit sim2_18 (families simulation_0123, simulation_0262, simulation_0277)

Result: **no fixes proposed**. Every scored row (36) was quick-checked on the frames. All quick checks are within 6% of the current answer, so no row met the ">= 15% difference" trigger for an in-depth re-measure.

Scripts are in this folder: util.py, q0123.py, qfall.py, fitfall.py, q0262.py and qrac.py. The PNGs are the crops I viewed.

## Family structure found
- **0123 / 0123_segmented**: identical footage. The cup track gives 14.537 px/frame in both clips, so the scale is 9.688e-4 m/px in both. The segmented twin does not show the holder cup or the blue toothbrush, but the question refers to the same scene object, so copying the answer from the original clip is correct. "Bottom towel" in the twin is the same towel as "largest towel" in the original.
- **0261 / 0261_segmented / 0262**: same backdrop and camera, but the dropped objects differ (a mug in 0261 and a red cup in 0262). They fall at different depths, so their scales differ: mug 1.92e-3 m/px, cup 1.51e-3 m/px. The landing rows agree with this. With a level camera, the contact-row offset from eye level is proportional to px/m. Solving for both clips gives an eye level near row 1028 and a camera height of 1.234 vs 1.235 m. This is consistent, and the mug's ellipses degenerate near that row. Neither clip uses the other's object, so there is no cross-clip size check.
- **0274/0276** (top-down, studio and forest) and **0275/0277** (side view, studio and forest) are the same camera with the same raccoon motion. Pixel positions match to within a few px: 0275 and 0277 xmax at frames 0/3/6/9/12 are 864/910/968/1046/1113 vs 862/906/975/1042/1111. Pixel speeds are therefore shared:
  - top-down: about 20.6 px/frame (0274 and 0276 both measure 20.5-20.6).
  - side view: about 22.5 px/frame from 0275, with 12->24 frame displacement of about 272.5 px.

## Rows checked
| qid | clip | quantity | current | quick-check route | quick value | diff |
|---|---|---|---|---|---|---|
| 265/1832 | 0123(_seg) | rolling cup length | 0.0752 | cyan-mask bbox 78-79 px x 9.688e-4 | 0.0756-0.0765 | +1-2% |
| 266/1833 | 0123(_seg) | rolling cup diameter | 0.0436 | mask bbox width 44-45 px | 0.0426-0.0436 | -2-0% |
| 267/1834 | 0123(_seg) | toothbrush length | 0.1089 | segmented minAreaRect 115.1-115.3 px | 0.1115 | +2.4% |
| 268/1835 | 0123(_seg) | holder cup diameter | 0.0444 | cyan mask, equal-area diameter / bbox 46-47 px | 0.0444-0.0455 | 0-2.5% |
| 269/1836 | 0123(_seg) | largest towel length | 0.3628 | segmented minAreaRect 373-374 px (rot -25.7 deg) | 0.3616-0.3625 | -0.2% |
| 270/1837 | 0123(_seg) | largest towel width | 0.1792 | minAreaRect 187.5-188.9 px | 0.1816-0.1830 | +1.5-2% |
| 917/2006 | 0261(_seg) | mug height | 0.1665 | segmented mask height minimum at eye level (frames 14-15) = 88 px x 1.920e-3 | 0.169 | +1.5% |
| 918/2007 | 0261(_seg) | v(0.2 s) | 1.87 | centroid parabola a = 8.859 px/f^2 (5103 px/s^2), so 1.920e-3 m/px; backward diff at frame 5 = 40.5 px | 1.867 | 0% |
| 919/2008 | 0261(_seg) | v(0.4 s) | 3.91 | backward diff at frame 10 = 85.2 px | 3.93 | +0.5% |
| 920/2009 | 0261(_seg) | v(0.625 s) | 5.97 | backward diff at frame 15 = 129.3 px | 5.96 | 0% |
| 921 | 0262 | red cup height | 0.217 | eye-level full extent (frames 13-17) 150-153 px, minus ellipses about 1-5 px, x 1.51e-3 | 0.216-0.226 | 0 to +4% |
| 922 | 0262 | v(0.25 s) | 2.25 | red-mask top/bottom/mean parabolas a = 11.04-11.44 (mean 11.3) px/f^2, so 1.506e-3 m/px; vertex near frame 0.1-0.3; backward diff at frame 6 about 61 px | 2.16-2.25 | 0 to -4% |
| 923 | 0262 | v(0.5 s) | 4.70 | backward diff at frame 12 = 127/130 px (bottom/top) | 4.65 | -1% |
| 924 | 0262 | v(0.625 s) | 5.92 | backward diff at frame 15 = 164/163 px | 5.91 | 0% |
| 968 | 0274 | width | 0.326 | column profiles: body edge to shadow boundary 64-66 px x 0.005 | 0.32-0.33 | 0% |
| 969 | 0274 | v(1.0 s) | 2.49 | bg-subtraction centroid slope 20.61 px/f, x24-x23 = 20.6 px; scale 1.51/302 | 2.47 | -1% |
| 970 | 0274 | disp 0.5-1.0 s | 1.24 | x24-x12 = 248.4 px (xmin 250, xmax 245) | 1.242 | 0% |
| 971 | 0275 | height | 0.64 | bbox height above ground 120-142 px, gait-dependent (frame 0 = 142 px, median 125 px), x 1.51/327 | 0.554-0.656 (median 0.577) | -10 to +2% |
| 972 | 0275 | v(1.0 s) | 2.48 | centroid slope 22.49 px/f, x24-x23 = 22.7 px; scale 1.51/327-330 | 2.47-2.52 | 0-2% |
| 973 | 0275 | disp 0.5-1.0 s | 1.24 | x24-x12 = 272.6 px (xmin 275, xmax 270) | 1.247-1.259 | +1% |
| 974 | 0276 | width | 0.316 | crop measurement 62.5 px x 0.0051 | 0.319 | +1% |
| 975 | 0276 | v(1.0 s) | 2.53 | bg+colour mask xmin/centroid slope 20.5-20.6 px/f (same camera and motion as 0274) | 2.51-2.52 | -0.5% |
| 976 | 0276 | disp 0.5-1.0 s | 1.266 | x24-x12 xmin 250 px; twin 0274 248 px | 1.265-1.275 | 0% |
| 977 | 0277 | height | 0.61 | bbox height frames 0-12: 144/131/125/124/129 px (median 129) x 0.0047 | 0.606 | -1% |
| 978 | 0277 | v(1.0 s) | 2.44 | same camera and motion as 0275: 22.5-22.7 px/f (own centroid x24-x23 = 21.4 px) x 0.0047 | 2.41-2.56 | 0 to +5% |
| 979 | 0277 | disp 0.5-1.0 s | 1.22 | own centroid x24-x12 = 274.3 px; twin 0275 = 272.6 px; x 0.0047 | 1.28-1.29 | +5% |

## Observations (no change proposed)
- **0277 speed/displacement.** The per-clip agent used a constant 21.6 px/f nose track. The shared motion with 0275 indicates about 22.5 px/f and about 272.5 px over frames 12-24. The agent's 0.0047 m/px scale (321 px length) is about 2.7% larger than 0275's (330 px), and the two effects partly cancel. In metres the family agrees within 2-5%: speeds 2.44-2.53, displacements 1.22-1.266. This is well below the fix threshold.
- **Raccoon height (971/977).** The answers 0.64 and 0.61 differ only by the agents' gait-phase choice; the two clips have the same pixel heights. Frame-0 bbox gives about 0.655 and the gait median about 0.58. The convention cannot be resolved without labels.
- **Red cup height (921).** The 143 px rest-frame value assumed an 8 px lid-top ellipse. The lid top looks domed, and the near-eye-level extent (frames 13-17, 150-153 px) suggests 145-150 px, i.e. 0.219-0.226. The difference is under 5%, so no change.
- **0.2 s / 0.4 s frame convention (918/919, 2007/2008).** These times fall at frame 4.8 and 9.6; the agent rounded to frames 5 and 10. Floor-frame values would be 1.47 and 3.54, which are 21% and 9% lower. Continuous-time backward-difference values would be 1.79 and 3.75, within 5%. This is a convention question, not a measurement error, so no change.
- **Sizes of rotated objects in 0123 (toothbrush at 45 deg, towel at -25.7 deg).** The answers use the object's own dimensions. A world-AABB convention would give about 0.085 m (toothbrush) and 0.40 x 0.32 m (towel). I left these unchanged: there is no evidence about the convention, and the agent's choice matches Blender object dimensions.

## Fixes
None. No row had two independent routes that agreed with each other and differed from the current answer by >= 15%.
