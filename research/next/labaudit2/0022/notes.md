# Lab audit round 2: family 0022 (captured_0022, 0022s, 0022x; one event, one label set)

Input: `../inputs/0022.json` (18 scored S3 rows = 6 questions x 3 renders). Only test inputs were used (frames, prior, depth_info).
No labels were used. Round 1 is in `research/next/labaudit/0022/notes.md`.
Scripts are in `scripts/`; frames are read in memory, nothing is dumped. Crops are in `img/`.

| script | what it does |
|---|---|
| `track.py` | ball blob centroid on each render, written to `track.json` |
| `table.py` | edge-line fit, corners, PnP; writes `plane.json` and `img/table_fit.jpg` |
| `plane_check.py`, `plane_traj.py` | plane-model ranges and trajectory |
| `motion.py` | label-style and physical values |
| `mc.py`, `mc_mix.py` | label-noise Monte Carlo and the MRA-optimal constant |
| `accel.py` | physical acceleration |
| `static.py` | table size from the vanishing-point plane and the stated-range scale |
| `zoomc.py`, `crop.py`, `peek.py` | visual checks |

## Scene and clock
- A table top sits on a fixed single pole; its corners are static across frames.
- The ping-pong ball rests at the far edge until video frame 11. It is released at video 11-12 with a push.
  - It slows from about 2.5 to 1.45 cm per capture frame. This is the slide-to-roll transition.
  - It then rolls toward the near edge, speeding up slowly (~7 cm/s^2), and leaves the table at video 46-47.
- The o, s and x tracks agree to within about 0.5 px. The zoom crops (`img/zoom_*_a.png`) confirm that the centroid sits on the ball centre.
  In x frames 0-12 the tracker picks up the table edge on alternate frames, so x is used only from video 14 on.
- **Dropped frame between video 35 and 36 (confirmed).** The image step is 11.5 px, against 5.7 and 6.1 px for the neighbouring steps.
  A drop after video 11 can't be seen because the ball starts moving in that interval.
- Mapping used: capture c = k + (k>=12) + (k>=36). So t = 0.6/0.8/1.2/1.6 s is capture 15/20/30/40, which is video 14/19/29/38.
  The variant without the drop after video 11 (video 15/20/30/39) was run as well and changes nothing material.

## Geometry
Table top: edge lines were fitted to the x-render mask boundary and to the top-to-front-face gradient (residual sd 0.16-0.44 px).
The corners are the line intersections, because the real corners are rounded: FL (281.3, 416.9), FR (600.5, 361.5), NR (671.3, 513.3), NL (224.2, 613.9).

| check | result |
|---|---|
| Vanishing points | orthogonal at f = 711 (\|d1.d2\| = 0.000) |
| PnP, 76.0 x 60.3, f 711 | reprojection error 0.9 px; normal (0.044, 0.872, 0.488); plane at 0.888 m |
| Swapped side assignment | 32 px error, so it is excluded |
| Ball surface range, plane model (centre 2 cm above the top) | 1.729 / 1.664 / 1.532 at t 0.6 / 0.8 / 1.2 |
| Stated ranges | 1.751 / 1.687 / 1.526 |

- A plane scale of x1.013 reproduces the t 0.6 and 0.8 ranges exactly.
- **The t = 1.2 reading is then 2.6 cm closer than the plane predicts.** This is the usual ToF scatter.
  Because of it, the stated approach rate from 0.8 to 1.2 s (1.61 cm per frame) is about 25% faster than the plane rate (1.29).
- sin_psi is 0.55 at 0.8 s and 0.60 at 1.2 s. The emulator used 0.51-0.55, which is right.

## Motion rows (one label for all three renders)
The label-style value is computed noise-free: the clicked centre is back-projected and the speed is a forward difference on the 25 fps clock.
The stated range is used at c15, c20 and c30. Other frames use one of three depth routes:
- **A1**: interpolation and extrapolation of the stated ranges.
- **A2**: the stated range plus the plane's change in range.
- **A3**: the absolute plane range, scaled x1.013.

Physical values come from the plane model with local quadratic or linear fits. Ranges cover o/s/x and both clock mappings.

| row (qids o/s/x) | current o/s/x | label-style A1 / A2 / A3 | physical | emulator policy on measured speed | verdict |
|---|---|---|---|---|---|
| v(0.8) (2389/2395/2401) | 50.9 / 50.9 / 52.2 | 46-47 / 41-43.5 / 43.5-48 | 39.3-40.8 | 49-52 (base 40-42.3) | OK. MC-optimal 50-53.5, so the current value is at the optimum. |
| v(1.2) (2390/2396/2402) | 57.3 / 55.0 / 58.4 | 47-49 / 41-47 / 36-40 | 41.3-43.4 (42.3 central) | 48.8-49.2 (base 42.3) | Soft. Not proposed (see below). |
| a(1.2) (2391/2397/2403) | 30 / 30 / 30 | -17 to +245, depending on the depth route | 4-10 (linear fits of plane speed; ~7 central) | n/a | Leave: the routes disagree (see below) |
| disp 0.6-1.6 (2392/2398/2404) | 47 / 47 / 47 | 45.4-45.8 / 43.4-43.9 / 41.4-42.0 | 41.1-42.4 | n/a | OK (3-14% above the label-style value, under the bar) |

### v(1.2), why it is not proposed
- The current 57.3 comes from Claude's direct 55 times the emulator's 1.04 (o). The s render has 55.0 and the x render has 58.4.
  The base of 55 is 30% above the measured 42.3. The ball speeds up only about 6% between 0.8 and 1.2 s, while the base values jump from 43 to 55.
- Against the noise-free label-style value (~43.5, A2) the current is 26-34% high.
- The value I would actually put in is noise-aware, and it is ~49:
  - `labnoise/emulate.row_model` (sz 2 cm) applied to the measured 42.3 gives 48.8-49.2.
  - `mc_mix.py` gives an MRA-optimal value of 47.5-51 over click 2-3 px, ToF 1-3 cm, base reading stated or noisy, and next-frame range A2 or A3.
- The current is only 12-19% above 49, so it misses the 25% bar.
- The expected gain of 49 over the current is +0.003 to +0.026 per row. 49 loses 0.013 if both readings are noisy with sz 3 cm.
- Flagged for the policy level only. If the lab-noise base is ever rebuilt from measured speeds, this row should be ~49 on all three renders.

### Acceleration
- The plane-based physical acceleration is 4-10 cm/s^2.
- The stated-depth-only route (average speeds 0.6-0.8 and 0.8-1.2) gives ~26, because of the 2.6 cm-close reading at 1.2 s.
- Forward-difference label emulation is dominated by the depth choice: from -17 up to 245.
- No two routes agree, so this is unchanged. The current 30 is consistent with the stated-depth route.

## Static rows
Route A takes the plane orientation from the vanishing points (aspect free) and the scale from the stated ball ranges (`static.py`).
At f 711 it gives 77.2 x 60.2 with the t 0.6 or 0.8 anchor and 75.8 x 59.1 with the t 1.2 anchor.
Route B is the PnP prior of 76.0 x 60.3.

| row | current | route A | route B | verdict |
|---|---|---|---|---|
| table width (2393/2399/2405) | 59.6 | 59.1-60.2 | 60.3 | OK (<2%) |
| table length (2394/2400/2406) | 74.5 | 75.8-77.2 | 76.0 | OK (2-3.5%) |

## Result
No fixes. v(0.8), displacement and the table rows agree with the measurements within the bars.
v(1.2) is high, but the gap to a noise-aware answer (~49) is 12-19%, which is below the 25% bar. It is flagged for the policy level only.
The acceleration routes disagree, so it is left at 30.
