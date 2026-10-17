# Lab audit round 2: family 0010 (captured_0010 / 0010s / 0010X; one event, labels shared)

Input: `../inputs/0010.json`, 18 scored D3 rows (6 questions x 3 renders). Round 1: `../../labaudit/0010/notes.md` (no fixes).
I used test inputs only: frames, `prior` (g = 9.8; the same red ball is stated as 7 cm in captured_0027) and
`depth_info` (surface ranges 1.706 / 1.344 / 1.4605 / 1.784 / 1.717 / 1.350 m at t = 0.3 ... 1.8 s). No labels.
f = 711 px, principal point (640, 360). Frames are read from the mp4s in memory; only crops and plots go to `img/`.

**Result: 5 fixes.**
- a(0.6), all three renders: 2.82-2.90 -> **6.8**.
- v(0.6), o and X: 0.433 / 0.388 -> **0.692**. This is the value s already has.

All other rows stay as they are.

## Scripts (`scripts/`)
| script | what |
|---|---|
| `track.py` | Ball centroid per frame in s (red on green), o (red hue) and X (non-white blob, string opened away). Output in `track.json`. |
| `size.py` | Sub-pixel half-max width (R-G) per frame, s render. Output in `size_s.json`. |
| `xcircle.py` | Circle fits to the s and X outlines. Output in `circ.json`. |
| `stringline.py` | String line per frame. Output in `string_s.json`. |
| `pend3d_v2.py`, `pend3d_v3.py` | Spherical-pendulum fits on the capture clock (RK4 plus a hand-written LM; there is no scipy). |
| `geo.py` | Sphere-geometry route. |
| `size_route.py` | Size-only local fits. |
| `final_rows.py` | Label-style values for every route. |
| `pipeline_emul.py` | Emulates how the current answers were made. |
| `mc.py`, `mc_fix.py` | Label-noise Monte Carlo and expected MRA. |
| `clock_check.py` | Tests the dropped-frame placement. |
| `plot_range.py` | Draws `img/range_vs_capture.png`. |
| `pend3d.py`, `label_style.py` | Early versions, superseded. `pend3d.py` fits all frames with a free pivot: the pivot lands 23 px under the string top and the fit gives g = 8.7 at D = 7. `label_style.py` uses a running-median pivot. |

## Clock
- **Drop before video 12.** The u step at video 11->12 is 8.7 px, against 4.7 before and 2.5 after.
- **Drop before video 36.** The v step at 35->36 is 24.5 px, against 9.1 and 14.5.
- So capture c = k + (k>=12) + (k>=36).
- **Pendulum-fit check** (`clock_check.py`, video 0-31). With the drop before video 12 the fit gives u/v rms 0.37/0.40 px. The drop placed at 11, 13 or 14, or no drop (24 or 25 fps), gives 0.79-0.91 / 0.57-1.29 px.
- **t = 0.6 is c15 = video 14.** The forward difference is video 14->15. The acceleration uses video 14, 15 and 16.
- **t = 0.3 is c7.5.**
  - Rounding half-up gives c8 (video 8); the `treal` convention gives c7.
  - The stated 1.706 cannot separate the two, because the anchors scatter by 2-3 cm, which is about one frame of radial motion.

## Geometry and scale
- **Pivot.** The string lines of video 5-28 meet at (640.3, 234.1) with 0.42 px rms. For video 33-48 they meet at (635.8, 235.9): the hand moved about 1 cm around video 29-33. The models are therefore fitted on the first period (video 0-31).
- **Three independent scale sources agree within 3%:**
  - g = 9.8 fixed gives D = 6.80-6.96 cm;
  - D = 7 cm fixed gives g = 10.09;
  - the stated anchors give D = 6.99 and g = 10.08.
- **Turning points:**
  - near-side turning at c18 (0.72 s), from the u max, v min and size max (video 16-17) and from every fit;
  - far-side turning at c3 and c33;
  - period 1.20 s.
- **Sphere route.** Ball centre on |C - P0| = L along the click ray. The anchors and the sizes both give d0 = 1.52 m and L = 0.346 m.
- **Anchor pattern.** The stated anchors deviate from the pendulum fits in a near/far pattern: near side -2.6 to -3 cm, far side 0 to +3 cm. The half-max size ranges match the anchors without that pattern (c15 -0.3, c23 0.0, c30 0.0, c38 -1.8, c45 -2.3 cm). So the offset is smooth and systematic (fit amplitude or ToF). It persists from frame to frame, which supports the "persist" label emulation: stated range at c0 plus the route's radial change.

## Rows (label style = forward difference of clicked s-centroid points on the 25 fps clock, stated range at c0 plus the route's radial change)

| qids o/s/X | question | current o / s / X | dynamic pendulum (10 variants) | sphere geometry | size-only (s-circle / half-max) | physical (pendulum) | verdict |
|---|---|---|---|---|---|---|---|
| 2194/2200/2206 | v(0.6) | 0.433 / 0.692 / 0.388 | 0.688-0.703 (dR -2.63..-2.69 cm/frame) | 0.579 (dR -2.16) | 0.64-0.77 / 0.79-1.05 | FD 0.69-0.71; instantaneous 0.81-0.84 | **fix o, X -> 0.692** |
| 2196/2202/2208 | a(0.6) | 2.83 / 2.82 / 2.90 | 6.68-7.09 | 5.54 | 6.9-8.3 / 8.4-11.2 | FD 6.6-7.1; instantaneous 6.4-6.6 (g sin(theta) near the turning point) | **fix all -> 6.8** |
| 2193/2199/2205 | v(0.3) | 1.51 / 1.24 / 1.48 | c8: 1.34-1.37; c7: 1.14-1.16 | c8 1.34; c7 1.11 | c8 1.12-1.26; c7 1.04-1.17 | FD c8 1.32-1.37, c7 1.16-1.21 | leave: within 25% under c8; the c7/c8 frame is unresolved |
| 2195/2201/2207 | a(0.3) | 4.89 / 4.89 / 5.02 | 5.7-6.3 | 6.8-7.1 | 1-5 (far-side size fits unstable) | 5.8-6.4 | leave: 18-22% low, below the bar |
| 2192/2198/2204 | ball diameter | 7.0 | D fit 6.8-7.0 | - | f x width / range ~7.0 (round 1) | same ball as 0027 (7 cm prior) | OK |
| 2191/2197/2203 | string length | 35.0 | L (pivot to ball centre) 0.329-0.340 | 0.346 | - | string only (L - r) 0.30-0.31 | leave: OK under the centre convention (+1..+6%); +13..+17% if the label is the string only. The convention is unknown, so this is not a clear error. |

### Why the current v(0.6) and a(0.6) are wrong
The current answers come from the pipeline's 3D track. In `qp/geometry.py` the range is "piecewise-linear in time" between
the depth_info anchors. Here those anchors are 0.3 s apart, which is a quarter of the pendulum period.

**What the interpolation does near the turning point.** Between t = 0.6 (1.344) and t = 0.9 (1.4605) the interpolated range rises by +1.55 cm per frame from c15 on.
In fact the ball keeps approaching until the turning point at c18. Every route gives a radial step c15->16 of -2.2 to -3 cm,
and the u, v and size extrema all sit at video 16-17 (`img/range_vs_capture.png`).

**Emulation** (`pipeline_emul.py`: s clicks, ranges interpolated linearly between the anchors, capture clock):
- v(0.6) = 0.442 and v(0.3) = 1.506. The pipeline's own geometry values are 0.45-0.47 and 1.43-1.48. These are the
  current o/X values; the s render's 0.692 is the labnoise x1.6 rule.
- The radial acceleration at the near turning point is lost. Near c15 the ball moves almost along the line of sight:
  the image step is 4.4 px (0.8 cm), against a 3D step of 2.7 cm. So the pipeline's a(0.6) of 2.8 keeps only part of
  the true acceleration of about 6.8 m/s^2. That true value equals g sin(theta) at the turning point, with theta0 of
  about 44 deg.

### Bar check
- **v(0.6), (a) route agreement.** The dynamic route (0.69-0.70) and the size s-circle route (0.64-0.77) agree within 12%.
- **v(0.6), (b) gap.** Against the lowest route (sphere, 0.579), o 0.433 is -25% and X 0.388 is -33%. Against 0.69 they are -37% and -44%.
- **a(0.6), (a) route agreement.** The dynamic route (6.7-7.1) and the s-circle route (6.9-7.7) agree within 12%.
- **a(0.6), (b) gap.** Even against the lowest route (5.54), the current values are 48-49% low.
- **Frame-difference direction does not matter.** Backward and central per-frame differences at c15 give 0.82-0.95 m/s and 6.4-7 m/s^2, so the current values are also too low under those.
- **The renders share one label.** So the v fix aligns o and X with s (0.692), and the a fix covers all three renders.

### Expected MRA item score (`mc_fix.py`; pendulum track, radial steps x0.85-1.2, iid click jitter and ToF noise)
| label noise | v(0.6): 0.388 / 0.433 / **0.692** | a(0.6): 2.83 / 2.90 / **6.8** |
|---|---|---|
| none (smooth label) | 0.50 / 0.60 / **1.00** | 0.40 / 0.40 / **1.00** |
| 1 px, 0.5 cm | 0.52 / 0.58 / **0.75** | 0.33 / 0.33 / **0.53** |
| 2 px, 1 cm | 0.49 / 0.53 / **0.60** | 0.19 / 0.19 / **0.44** |
| 2 px, 2 cm | 0.44 / 0.46 / **0.48** | 0.12 / 0.12 / **0.31** |
| 3 px, 3 cm | 0.40 / 0.42 / **0.48** | 0.06 / 0.07 / **0.21** |

**Risk: the round-1 "0.3 s chord on the stated grid" hypothesis.**
- Under it, v(0.6) = 0.39 and a(0.6) = 3.07, which is what o/X currently hold. The fix would then score 0.2 (v) and 0 (a).
- That hypothesis contradicts the stated label model, which is per-frame clicks with forward differences on the capture clock.
- In 0014 the stated prior acceleration (4.6) matched the one-frame forward second difference (4.49-4.57). It did not match a chord.

## Not changed, with reasons
- **v(0.3).** The label pair is c7->8 or c8->9, and the anchor cannot decide. Under c8 every current value is within
  -10..+14% of 1.34. Under c7, o (1.51) and X (1.48) would be 27-31% high, but only under that unresolved convention.
- **a(0.3).** All three routes put it at 5.7-7.1, so the current 4.9-5.0 is 18-30% low. Against the main route (dynamic, about 6.1) it is only about 20% low, under the 25% bar. A hedge to about 6 would be a small +EV change (MC: 0.48 -> 0.54 at low noise). It is not a clear error.
- **String length.**
  - Pivot to ball centre is 33-35 cm. The string alone is 30-31 cm.
  - The current 35 fits the centre convention. Under the string-only convention it is 13-17% high.
  - The convention cannot be settled without labels, so I flag it here and leave it.
