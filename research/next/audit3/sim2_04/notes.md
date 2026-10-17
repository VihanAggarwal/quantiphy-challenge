# Audit sim2_04: simulation_0263-0273 (spacecraft 0263-0268, phoenix 0269-0273)

Result: **no fixes proposed.** I checked all 41 scored rows. Every current answer is within 15% of my quick check.
One soft flag (phoenix body length on the top and bottom views) is described below. It does not meet the fix rule.

## Family structure (from the frames)
| clip | object | view | twin (same camera) | prior | my pixel acceleration (px/s^2) | scale (m/px) |
|---|---|---|---|---|---|---|
| 0263 | spacecraft | top, segmented | 0266 | a=4 | nose 504-527, tail 519 | ~0.0077 |
| 0266 | spacecraft | top, snow bg | 0263 | a=4 | nose 504, tail 519 | ~0.0077-0.0079 |
| 0264 | spacecraft | side, segmented | 0267 | a=4 | nose 656, tail 677-681 | ~0.0059-0.0061 |
| 0267 | spacecraft | side, sky bg | 0264 | a=4 | nose 657, tail 681 | same |
| 0265 | spacecraft | bottom, segmented | 0268 | a=4 | nose 706, tail 680 | 0.00567 (nose) / 0.00588 (tail) |
| 0268 | spacecraft | bottom, sky bg | 0265 | a=4 | tail 678 | same |
| 0269 | phoenix | top, segmented (grey shadow) | 0272 | a=2 | beak 238.2 (P=25 flap harmonics, rms 0.7 px) | 0.00840 |
| 0272 | phoenix | top, snow bg | 0269 | a=2 | beak 238.6 | 0.00838 |
| 0270 | phoenix | side, segmented | 0273 | a=2 | beak 281.5, tail 280.9 | 0.00711 |
| 0273 | phoenix | side, sky bg | 0270 | a=2 | 277-292 (noisy bg) | 0.0071 |
| 0271 | phoenix | bottom, segmented | (none in test) | a=2 | centroid 375.8 (agent template 379) | 0.00528-0.00533 |

Motion: every clip fits a quadratic (plus flap harmonics, period 25 frames, for the phoenix) with its vertex within +-0.2 frame of frame 0.
So the motion is constant acceleration from rest at t=0. The backward-difference speeds are a*(t-1/48):
spacecraft 1.917 / 3.917 m/s, phoenix 0.958 / 1.958 m/s.

Perspective: the spacecraft nose and tail have different pixel accelerations (4-5%) because they sit at different depths.
I computed the length per part with L = (x_tail-1280)*s_tail - (x_nose-1280)*s_nose, where s = a_world/a_px of that part.

## Rows checked (all scored rows)
| qid | clip | quantity | current | quick check (route) | verdict |
|---|---|---|---|---|---|
| 926 | 0263 | width | 2.82 | y-extent 365-367 px (dark mask, shadow excluded) x 0.00766-0.00771 = 2.80-2.83 | ok |
| 927 | 0263 | v(0.5) | 1.92 | vertex -0.03 f -> 1.917 | ok |
| 928 | 0263 | v(1.0) | 3.92 | 3.917 | ok |
| 929 | 0264 | length | 5.98 | per-part scale, f12 and f48: 5.99 / 5.98 | ok |
| 930 | 0264 | height | 1.86 | y-extent 311-314 px x 0.0061 = 1.89-1.91 (no near-side correction) | ok |
| 931 | 0264 | v(0.5) | 1.90 | vertex 0.18 f -> 1.89 | ok |
| 932 | 0264 | v(1.0) | 3.90 | 3.89 | ok |
| 933 | 0265 | length | 5.74 | per-part scale, f12/f24/f48: 6.00 / 6.01 / 6.01 | ok (-4.4%) |
| 934 | 0265 | width | 2.96 | y-extent 514 px x 0.00567-0.00588 = 2.91-3.02 | ok |
| 935 | 0265 | v(0.5) | 1.92 | vertex ~0 -> 1.917 | ok |
| 936 | 0265 | v(1.0) | 3.92 | 3.917 | ok |
| 937 | 0266 | length | 5.90 | per-part scale, f0/f42/f60: 6.00 / 5.98 / 5.98 | ok |
| 938 | 0266 | width | 2.85 | 364-366 px x 0.0077-0.0078 = 2.81-2.86 | ok |
| 939 | 0266 | v(0.5) | 1.92 | vertex -0.04 f -> 1.917 | ok |
| 940 | 0266 | v(1.0) | 3.92 | 3.917 | ok |
| 941 | 0267 | length | 5.97 | twin of 0264, same nose/tail pixels -> 5.98 | ok |
| 942 | 0267 | height | 1.90 | 297-315 px (sky mask) x 0.0061 = 1.8-1.92 | ok |
| 943 | 0267 | v(0.5) | 1.92 | vertex 0.21 f -> 1.88-1.92 | ok |
| 944 | 0267 | v(1.0) | 3.92 | 3.88-3.92 | ok |
| 945 | 0268 | length | 5.97 | twin of 0265 -> 6.00 | ok |
| 946 | 0268 | width | 2.93 | 514 px -> 2.91-3.02 | ok |
| 947 | 0268 | v(0.5) | 1.92 | vertex -0.05 f -> 1.917 | ok |
| 948 | 0268 | v(1.0) | 3.92 | 3.917 | ok |
| 949 | 0269 | body length | 3.75 | f0: beak 1483 -> rod tip 1940 = 457 px = 3.84; -> faint edge-on tail ornament tip ~1990 = 507 px = 4.26 | ok, soft flag (see below) |
| 950 | 0269 | wingspan | 5.28 | max y-extent 630-632 px (f21/46/71) x 0.00840 = 5.30 | ok |
| 951 | 0269 | v(0.5) | 0.98 | vertex -0.03 f -> 0.958 | ok (+2.3%) |
| 952 | 0269 | v(1.0) | 1.98 | 1.958 | ok |
| 953 | 0270 | length | 4.10 | f0: 570 px (solid beak) to 604 px (translucent beak tip at x~1401) x 0.00711 = 4.05-4.29 | ok |
| 954 | 0270 | height | 2.90 | f0 y-extent 404 px = 2.87; median over flap ~400 px | ok (pose-dependent) |
| 955 | 0270 | v(0.5) | 0.97 | vertex -0.09 f -> 0.958 | ok |
| 956 | 0270 | v(1.0) | 1.97 | 1.958 | ok |
| 957 | 0271 | body length | 3.85 | f0: beak 1596 -> rod tip ~2304 = 708 px = 3.78; -> faint tip ~2350 = 754 px = 4.02 (a=375) | ok, soft flag |
| 958 | 0271 | wingspan | 5.30 | max y-extent 1005-1006 px x (2/375 to 2/379) = 5.31-5.37 | ok |
| 959 | 0271 | v(0.5) | 0.94 | vertex ~0.06 f -> 0.958 | ok (-1.9%) |
| 960 | 0271 | v(1.0) | 1.94 | 1.958 | ok |
| 961 | 0272 | body length | 3.61 | f0: beak 1483 -> rod tip 1940 = 458 px = 3.84; -> faint tip ~1982 = 499 px = 4.18 | soft flag: 6-14% low, not >=15% |
| 962 | 0272 | wingspan | 5.12 | max y-extent 627-632 px x 0.00838 = 5.26-5.30 | ok (-3%) |
| 963 | 0272 | v(0.5) | 0.98 | vertex 0.03 f -> 0.958 | ok |
| 964 | 0272 | v(1.0) | 1.97 | 1.958 | ok |
| 965 | 0273 | body length | 4.25 | f0: beak ~1401-1408 -> ornament tip ~2004 = 596-603 px x 0.00711 = 4.23-4.28 | ok |
| 966 | 0273 | v(0.5) | 0.98 | vertex ~0 (twin 0270) -> 0.958 | ok |
| 967 | 0273 | v(1.0) | 1.98 | 1.958 | ok |

Unscored rows 310 and 925 (0263 length 6.0) match the spacecraft family value of 6.0 m.

## Family consistency
- Spacecraft length: all three views give 5.98-6.01 m with per-part scales. The current answers (5.74-6.0) are all within 5%.
  Width: 2.81-2.86 (top) and 2.91-3.02 (bottom); the current answers are 2.82-2.96. Height: 1.86-1.90. These are consistent.
- Phoenix wingspan: the twins 0269 and 0272 give 630 vs 632 px at the same camera. With the bottom view this gives 5.30-5.37 m.
  The current answers (5.12-5.30) are consistent. A caveat that no measurement can resolve: the f0 pose has the wings raised, with a y-extent of only about 2.25 m.
  If the AABB label came from the f0 pose, all wingspan rows would be far off. Height 2.9 corresponds to the raised-wing pose, so the rows mix poses.
  I left this alone because it is a matter of label definition, not a measurement error.
- **Phoenix body length (soft flag, no fix).** The tail ends in a flat ornament (a leaf in the vertical plane at the end of a stalk).
  The side views show it clearly (tip at x~2004 at f0). In the top and bottom views it is edge-on and shows only as a faint line:
  the diff from the background is 5-10 grey levels against 0-2 in a control band, it lies on the body-axis row, and it moves with the bird at f25 and f50.
  It continues about 50 px beyond the bright rod tip. The top- and bottom-view agents stopped at the rod tip, and 0272 used a saturated-mask median of 430 px, missing part of the rod.
  The f0 x-extent including the ornament is 4.23-4.29 (side, no depth bias), 4.18-4.26 (top, slightly over-estimated because the ornament is ~0.85 m higher than the beak)
  and ~4.0 (bottom, under-estimated for the same reason). The family value is therefore ~4.2 m.
  On that basis 949 (3.75, -11%), 957 (3.85, -8%) and 961 (3.61, -14%) are probably low. 0272 is -14% against 4.2 and -9.75% to -15.7% across the 4.0-4.28 bracket,
  which does not robustly reach the 15% threshold. The pose and the inclusion of the translucent parts are also uncertain, so I propose no fix.
  If the orchestrator harmonizes the family at a lower bar, use ~4.2 for 949, 957 and 961.

## Method notes
Scripts are in scripts/: track.py/measure.py (bbox masks; background = composite of first and last frame, or the last frame), fit.py (quadratic plus flap harmonics),
xext.py/yext.py (extents), crop.py/diffcrop.py (viewed crops). Frames are read in-script; no frame dumps. The folder is ~2 MB.
