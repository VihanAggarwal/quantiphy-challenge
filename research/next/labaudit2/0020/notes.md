# Lab audit round 2: family 0020 (captured_0020, 0020s, 0020x; one event, one label set)

Input: `../inputs/0020.json` (24 scored D3 rows = 8 questions x 3 renders). Only test inputs were used (frames, prior, depth_info).
No labels were used, and no row had a round-1 fix. Round 1 is in `research/next/labaudit/0020/notes.md`; its `tracks.json` and the
vanishing-point script were reused read-only. Frames are read in memory and nothing is dumped. Crops are in `img/`.

| script | what it does |
|---|---|
| `common.py` | video loader, capture clock, back-projection (f 711, pp 640/360) |
| `track2.py` | my own 2D tracker (x-render green-screen / s-backdrop foreground + colour), writes `track2.json` |
| `crops.py`, `crops2.py` | zoom crops with the centroid marked (`img/crops_o_*.png`, `img/z_*.png`) |
| `lm.py` | small Levenberg-Marquardt solver (scipy is not in the venv) |
| `ballfit.py` | Route A: constant-g 3D fits (fixed VP gravity or free direction; anchored or not), label-style values |
| `resid.py` | residual patterns, free \|g\|, joint jar+toy fit with a shared free gravity direction |
| `rsfit.py`, `distfit.py` | tests of rolling shutter and radial distortion as causes of the gravity anomaly (neither works) |
| `sizes.py` | Route B: apparent-size ranges against the fit ranges |
| `motion.py` | the motion-row table (both routes, all renders, both clock variants), writes `motion_table.json` |
| `mc.py` | label-noise Monte Carlo and the score-optimal constant |
| `toylen.py` | static check: toy and jar silhouette extents (x render) |

## Scene, tracks and clock
- The near person (range 1.58 m) throws the white jar up toward the far person (3.237 m). The far person throws the yellow
  pineapple toy (the "carrot" in depth_info) to the near person. Both objects leave the hands at video 14-15 (the hand still
  touches both at video 14). The toy is caught at video 24-25 and the jar at video 27-28.
- My tracker agrees with round 1: median offset 0.6-1.9 px. The largest are 5.5 px on the toy at o16, s15 and x14, where round 1
  caught a hand or crown pixel. The three renders agree to under 1.7 px at video 14, 15 and 19.
- **Dropped frame between video 11 and 12 (confirmed).** The jar step 11->12 is (29.3, -93.0) px, against (19.0, -35.6) before
  and (10.1, -53.3) after. The toy step is (-35.9, -16.7), against (-9.6, +2.4) and (-20.1, -16.8). Half of each double step
  falls between its neighbours in both components, for both objects.
  - Mapping: c = k + [k>=12] + [k>=36].
  - t = 0.60 / 0.64 / 0.80 s is capture 15 / 16 / 20, which is video 14 / 15 / 19.
  - The variant without this drop (video 15 / 16 / 20) was run as a sensitivity check only.

## Depth routes for the unstated ranges (c16, c20)
- **Route A, fixed gravity.** The direction comes from the vertical vanishing point. I re-ran round 1's seam fits: the seams near
  x 1130 and x 960 have slopes -0.146 and -0.034, and they meet at (906, 1536). That is a camera pitch of about 29 deg.
  - This geometry is physical. A ~10 deg pitch would put the camera about 0.3 m above the floor.
  - The fit is anchored at the stated range plus the object radius (3.5 cm jar, 4 cm toy). Residual rms is 1.8-2.0 px.
- **Route A, free gravity direction.** The jar and the toy each prefer a down vector of about (0.21, 0.96, 0.17), or about 10 deg
  pitch. This is the same direction for both objects, and rms falls to 0.8-1.6 px.
  - Unanchored joint fits with this direction reproduce the stated ranges to 1-2% on o and x (jar 1.988, toy 2.645, against
    2.009 and 2.670).
  - Unanchored fixed-VP fits overshoot by 4-9% (toy 2.86-2.93).
  - A rolling-shutter row delay (fitted Tr 12-27 ms) does not remove this anomaly. Neither does radial distortion (k1 has an
    unstable sign and rms does not improve).
  - Cause unknown (track bias from the tumbling toy, drag?). I treat fixed and free as two bracketing variants of Route A.
- **Route B, apparent size** (sqrt of blob area, scaled from c15).
  - Jar: dR16 is +5 to +12 cm raw and +8 cm smoothed, against +2.6 to +4.5 from Route A.
  - Toy: unreliable. The toy turns from side-on to end-on after video 17, so its area stops shrinking.
    - Route B gives dR20 of only -11 to -15 cm, against -39 to -48 from Route A.
    - That would put the toy at about 2.3 m at the catch, about 0.9 m beyond the near person's torso. Route A gives 1.80-1.89 m,
      or about 0.5 m of arm reach, which is plausible.

## Motion rows (one label for all three renders; drop@c12 clock)
For the label-style value, the clicked centre at video 14 / 15 / 19 is back-projected. The range is the stated value at c15 and the
route's surface range at c16 and c20. The speed is a forward difference on the 25 fps clock. Percentages are current relative to
label-style.

| row (qids o/s/x) | current | label-style A fixed-g | label-style A free-g | Route B (size) | physical (A fixed / free) | MC-optimal (noise-aware) | verdict |
|---|---|---|---|---|---|---|---|
| jar v(0.60) (2355/2363/2371) | 383.0 | 334-344 (+11 to +15%) | 343-355 (+8 to +12%) | 356-462 raw, 388-394 smooth | v_inst 352-356 / 368-373 | 343-346 | OK under the bar. Flag: about 11% high |
| toy v(0.60) (2354/2362/2370) | 274.9 | 321-327 (-14 to -16%) | 268-286 (-4 to +3%) | 191-375 (unreliable) | 345 / 288-302 | 292-299 | OK |
| jar disp 0.60-0.80 (2357/2365/2373) | 57.1 | 55.1-56.0 | 55.7-57.0 | 52-54 raw, 66-67 smooth | 56.3-57.4 / 57.0-58.0 | 56.0 | OK (0-3%) |
| toy disp 0.60-0.80 (2356/2364/2372) | 50.4 | 59.8-59.9 (-16%) | 53.5-54.3 (-6 to -7%) | 40-51 (unreliable) | 60.6-60.8 / 54.3-54.8 | 56.5-57.1 | OK under the bar. Flag: about 11% low |

- In the no-drop clock variant, toy v changes by +1 to +4%, toy disp is 57-62, and jar disp is 50-54. Jar v falls to 291-316.
  That variant is excluded by the step analysis, and it moves no row past the bar toward a fix.
- The MC (`mc.py`) covers click sd 2-3 px, ToF sd 1-3 cm and a 50/50 mix of fixed/free gravity:
  - jar v: the current answer scores 0.885 in expectation, against 0.93-0.97 at about 345.
  - toy disp: the current scores 0.894, against 0.955-0.964 at about 56.7.
  - toy v: the current scores 0.83-0.89, against 0.83-0.91 at about 295 (negligible gain).
- No motion row meets the bar of two agreeing routes plus a >=25% gap. The largest gaps to any agreed value are 11-16% (jar v)
  and 6-19% (toy disp). Route B is too noisy to agree with Route A for the toy.

## Static rows (re-check)
| row (qids o/s/x) | current o/s/x | my routes | verdict |
|---|---|---|---|
| distance between the people (2353/2361/2369) | 235.4 / 240.2 / 236.4 | Click grid with the stated 1.58 / 3.237 m: 236-250. Round-1 floor route: 236-246 | OK (<6%) |
| toy height (2350/2358/2366) | 15.9 / 14.3 / 14.4 | x-silhouette length at video 15-17 (free flight, fit ranges 2.4-2.6 m) is 15.4-20.0 cm, depending on the blur deduction (exposure fraction 0.5: 15.4-17.7; 0.3: 16.6-18.6). Video 20-23 (foreshortened): 12.8-16.2. Round 1: 14.2-18.2 | OK. s/x may be about 10% low, but the routes spread more than 6% |
| jar height (2351/2359/2367) | 7.9 / 8.4 / 8.4 | Extent along the axis at video 20-22, deblurred: 8.4-10.6 cm, including about 1 cm of halo | OK |
| jar diameter (2352/2360/2368) | 6.7 / 7.1 / 7.1 | Width across the motion at video 15-17 and 20-22: 7.5-9.1 cm, including halo (1-2 px a side, about 0.6-1.3 cm) | OK |

## Result
**No fixes for family 0020.** All motion rows are within the bars.
- Flagged for the policy level only, if lab-noise bases are ever rebuilt from measured tracks:
  - jar v(0.60): about 345 instead of 383, on all renders.
  - toy disp 0.60-0.80: about 56.5 instead of 50.4, on all renders.
- Each would gain about 0.05-0.08 per row under my noise model, but neither meets the 25% bar.
- Static rows agree with round 1.
