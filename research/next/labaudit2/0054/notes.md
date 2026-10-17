# Lab audit round 2, family 0054 (captured_0054a/as/ax, 0054b/bs/bx): 71 scored rows, all D3

This family has no S3 rows. Scripts are in `scripts/`. Frames were read straight from the mp4s, and crops went to the session
scratchpad, not to this folder. No labels were used. The only inputs were test depth_info and priors.

## Setup checks (own measurements)
- **Timing.** 49 frames at 24 fps from a 25 fps capture. There are double steps at video 11->12 and 35->36 in both cameras
  (orange ball: a 15/31.5/16.5 px, b 24/53/24 px; green ball: a 47/132 px). So capture(k) = k for k<=11, k+1 for 12..35,
  and k+2 for k>=36. On this map, t=1.0 s is video 24 = capture 25. t=1.5 s is video 36 = capture 38, and capture 37 is a
  dropped frame. t=0.5 s is video 12 = capture 13, and capture 12 is dropped.
- **Camera b gravity.** The vertical VP from 11 wall-seam segments gives pitch 31.3 and roll -7.9 (round 1 had 29.9 / -6.5).
  Camera a is level (pitch 0-1). Free-direction joint fits put a at -5 and b at 31.8 / -10.5. These are weakly constrained.
- **Small-ball ballistic fits.** I fitted g=9.81 and f=711 to my own tracks: a from ax SAM components plus raw-a yellow
  segmentation; b from bx components plus my own background-subtraction colour split for video 21-26, where bx merges or
  drops the balls. The fitted ranges at 1.0 s reproduce the stated ToF:
  - a: white 3.108 vs 3.107, green 3.03 vs 3.073 (stated surface + R).
  - b: green 1.38 vs 1.365, white 1.35 vs 1.269.
  - The rms residual is 0.8-1.1 px.
  - A similarity alignment of the a and b trajectories has a 6 cm rms residual and a scale ratio of 1.12. The two cameras'
    metric scales differ by about 10%, which is why b-route speeds come out about 8-10% below a-route speeds.
- **Bounces.** Triangulating with the a<->b alignment (`tri.py`):
  - The green ball is at floor height at capture 39 (video 37). It sits 7 cm above the free-flight extrapolation, and b
    shows a sharp ball with a contact shadow at b37. Contact is at about 1.547 s.
  - The white ball is still in free flight at capture 39 (within 1 cm of the parabola) and touches the floor at capture 40.
- **Off-axis sizes.** The soccer ball sits at 37 deg off-axis in a. Its size only agrees with the floor plane (H about
  0.86 m from the small-ball bounces) and with b's stated 3.254 m at 2.0 s when the pinhole off-axis factor is included
  (tangential = f D / (r cos th)). That gives D about 19-20 cm in both cameras.
  - My first naive size range for the soccer in a (2.25 m) was wrong. The floor-plane range is 2.6-2.9 m.
  - The colour segmentation of the orange ball in raw a misses its dark top: 59 px measured against 70 px by eye at rest.
    I used no orange sizes from a.

## Motion rows
Label-style values use the clicked (tracked) centres, the stated range at the stated frame, the fit/size range ratio for
other frames, and the forward difference on the 25 fps clock.

| row | renders: current | a-route | b-route | physical | verdict |
|---|---|---|---|---|---|
| orange displacement 0.5->1.0 | a/as/ax 0.865-0.870, b/bs/bx 0.80 | 0.852 (cap13) / 0.883 (cap12), with stated 2.3557 / 1.81 | 0.775-0.833, with b-stated 2.24 / 1.81 | - | OK |
| soccer displacement 1.0->1.4 | 0.37 x3, 0.446, 0.444, 0.384 | floor plane 0.44-0.60 | off-axis sizes anchored at 3.254: 0.38-0.42 | - | OK (routes disagree; all current values inside) |
| soccer v(0.5) | 0.02 x3, 0.033, 0.148, 0.013 | ball at rest under the hand (centre moves < 1 px) | occluded | ~0 | label is click/ToF noise; cannot be judged |
| green v(1.0) | 1.85, 1.81, 2.17, 2.25, 2.29, 2.19 | 2.45-2.55 (fd 2.33-2.47) | 2.12-2.14 (fd 2.11-2.15) | 2.2-2.5 | OK (max 21% off) |
| white v(1.0) | 1.745, 1.70, 1.72, 2.22, 2.25, 2.14 | 2.18-2.30 (fd 2.26-2.43) | 1.79-1.85 (fd 2.06-2.11) | 2.1-2.5 | OK (a renders 21-23% below the physical about 2.2: under the gate) |
| green v(1.5) | a 4.30, as 4.11 (r1), ax 5.42, b/bs/bx 4.11 (r1) | 38->39 across the bounce: 2.98 (triangulated) / 3.12 (horizontal continuity); 37->38: 4.89-4.95 | 38->39: 2.5-2.65; 37->38: 4.46-4.54 | v(1.52) 4.7-5.0 | **ax 5.42 -> 4.11** |
| white/pink v(1.5) | a 5.92, as 4.748, ax 6.70, b/bs/bx 4.748 (r1) | 38->39: 4.91-4.99; 37->38: 4.41-4.48 | 38->39: 4.47-4.62; 37->38: 4.02-4.16 | v(1.5) 4.3-4.6 | **ax 6.70 -> 4.75, a 5.92 -> 4.75** |

- **Green 1.5 s.**
  - The label pair is most likely capture 38->39, because t=1.5 maps to video 36 = capture 38, and round(37.5) is also 38.
    That pair crosses the floor contact at about 1.547 s, so the label-style value is about 2.5-3.1. The 37->38 pair
    (int() convention) gives about 4.5-4.95.
  - The current ax value 5.42 is above every label-style value from either camera under either convention: the maximum is
    4.95, and the in-flight speed just before contact is about 5.2 (a) or 4.9 (b).
  - Setting ax to 4.11, the round-1 family hedge, gives a better score under both conventions.
  - The other green rows, at 4.11 and 4.30, are hedges, not clear errors, so I left them. If the 38->39 convention is
    accepted, the whole family would score better at about 3.0-3.3.
- **White 1.5 s.**
  - There is no bounce inside either pair. The a and b routes agree within 10% at about 4.75 (38->39).
  - ax 6.70 is 41% above that value, and above the white ball's in-flight speed just before contact (5.3-5.6).
  - a 5.92 is 24.6% above 4.75, just under the per-row gate. All renders share one label, and the family value 4.75 is
    already on 4 renders, so I apply the event fix to it too. It is 19-21% above a's own route (4.95) and 32% above the 37->38
    value (4.45).

## Static rows

| row | current | route 1 | route 2 | verdict |
|---|---|---|---|---|
| orange diameter | 23.2 | basketball stated in 0035 | - | OK |
| soccer diameter | 18.36 x3, 19.0 x2 | b at 2.0 s with stated 3.254: 18.7-19.4 (minor 42.4-43 px, with or without 1 px halo) | a floor plane plus off-axis: 18.7-19.8 | OK |
| white diameter | a 6.70, as 7.72, ax 6.42, b 6.75 (r1), bs 6.54, bx 7.01 | white/green ratio across blur in ax masks: 0.99-1.03, so 6.6-6.9 | b ratio 1.03, so 6.9; b absolute after halo correction 6.4-6.9 | **as 7.72 -> 6.8** (12-13% high) |
| orange-soccer distance 1.0 s | a 1.556, as 1.46, ax 1.55, b x3 1.325 | a: orange 1.81, soccer floor-plane 2.65-2.79: 1.40-1.50 | b with b-stated 1.81: 1.30 (matches current b). With b's true orange range (2.64-2.72 surface): 1.48 | OK |
| green-white distance 1.0 s | 0.163, 0.147, 0.151, 0.141, 0.172, 0.138 | a stated ranges at clicked centres: 0.159 (3 px jitter p10-p90 0.139-0.182) | b stated: 0.138 | OK (routes 14% apart) |

- **White diameter, as 7.72.** This value equals a blur- and halo-inclusive mask extent. The same mask measurement reads
  the green tennis ball (6.7) at 7.7 cm in ax and 7.0 cm in bx, while the white/green ratio is 0.99-1.03 in both cameras.
  The other five renders are within 6% of 6.8.
- **b depth_info.** b's "orange at 1.0 s = 1.8100" equals a's value; b's sizes put the ball at about 2.7 m. The current b
  distance 1.325 matches the label-style value computed with that 1.81, so I left it alone: if b has its own label, that
  label used this depth.

## Fixes

| qid | render | row | current | new |
|---|---|---|---|---|
| 2863 | ax | pink (white) ball velocity 1.5 s | 6.70 | 4.75 |
| 2840 | a | pink (white) ball velocity 1.5 s | 5.92 | 4.75 (event value; 24.6% off, applied as a family fix) |
| 2862 | ax | green ball velocity 1.5 s | 5.42 | 4.11 (family hedge) |
| 2847 | as | white ball diameter | 7.72 | 6.8 |

## Near misses (not changed)
- a, as and ax white v(1.0), at 1.70-1.75, sit 21-23% below the physical forward difference of about 2.2. Camera a's own
  label-style value is 2.18-2.30.
- bs green-white distance, 0.172, is 25% above the b route (0.138) but only 8% above the a route (0.159).
