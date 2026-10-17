# Lab audit round 2: family 0037 (captured_0037, 0037s, 0037x; one event, one label per question)

Input: `../inputs/0037.json`, 18 scored S3 rows (6 questions x 3 renders). I used only the frames and the test
`prior` / `depth_info`: ping-pong ball 4 cm; stated ranges at t = 1.0 s of ball 1.055, card 0.679, poker tower 0.905,
cup 0.845, tape 1.038 and jar 1.008 m. No labels were used. Round 1 is `../../labaudit/0037/notes.md` (no fixes). The jar
re-measure by the second measurer is `remeasure.md` and `m2/` (9.0 cm).

**Result: 6 fixes in 2 label groups (both ping-pong speeds), applied to all three renders:**
- v(1.0 s) goes to **72 cm/s**.
- v(1.4 s) goes to **95 cm/s**.

The gates are met on the s rows (2691, 2692). The o and x rows are included because the label is shared; on their own
they are 18-20 % low, which is under the 25 % bar (details below). No static row changes.

Scripts are in `scripts/`; nothing is dumped and frames are read in memory.
- `track.py`: blob track for all 3 renders. Output `track.json`.
- `capsule.py` (with `nm.py`): capsule fit (a motion-blurred disc), giving the centre and diameter. Output `capsule.json`.
- `plane.py`: table PnP 76.0 x 60.3 cm, f = 711 / 725 / 735. Output `plane.json`. At f = 711 the camera is 0.165 m
  above the table top.
- `ballistic.py`: per-hop 3D fits, g = 9.8 along the table normal.
- `bouncefit.py`: a joint piecewise-ballistic fit. The bounce points lie on the table plane (centre 2 cm up), so the
  scale comes from both the plane and gravity.
- `dropcheck.py`: test of where the dropped frame is.
- `motion.py`: label-style forward differences, by the size route and the gravity route.
- `mc.py`, `mc_mix.py`: label-noise Monte Carlo.
- `static.py`, `static2.py`: static re-check.

Outputs: `motion_out.txt`, `dropcheck_out.txt`, `mc_out.txt`, `mc_mix_out.txt`, `static_out.txt`. Crops are in `img/`.

## Scene and clock
- The ping-pong ball is thrown from behind the cup at v11-12. It travels left and toward the camera, hopping on the table:
  - bounce behind the poker tower at c20.4;
  - bounce just behind the tape's right side at c29.2;
  - bounce beside the jar at c37.5;
  - bounce at c45.3.

  The tape and tower occlusions in the composite match the fitted 3D positions.
- **Dropped frames.** The capture clock is c = v + (v>=12) + (v>=36).
  - In the raw track, the step v35->v36 is 38 px. The whole-ball centre of v35 gives 35 px. The neighbouring steps are
    14-15 px.
  - The joint fit of hops B, C and D gives an rms of 0.61 px with the drop before v36 (or before v37: the same rms,
    because v36 is not used). With the drop before v35 the rms is 4.2 px, and with no second drop it is 3.9 px.
  - When g is left free, the fit returns g = 9.6-9.7.
  - The drop before v12 follows the 24-frame period. It cannot be seen here, because the ball is still in the hand.
- **Times.** t = 1.0 s is c25 = v24, so its forward difference is v24->v25. t = 1.4 s is c35 = v34, so its forward
  difference is v34->v35.

## Ball geometry (x and s renders agree within 0.5 px)
- **Hop B (v21-27, t = 1.0 s at its apex c24.8).**
  - The per-hop gravity fit puts the range at c25 at 1.063-1.09 m (f 711) and 1.10-1.13 (f 735). The stated surface
    range is 1.055, which is a centre range of about 1.075. The fit agrees with it.
  - The capsule diameter is 27.6-28.0 px, which is 4.1-4.2 cm at that range.
  - The fit predicts the bounces at c20.4 and c29.2. Those match the image bounces.
- **The ball approaches the camera.** The capsule diameter is 27.6 px in hop B, 31.5 in hop C and 35.4 in hop D.
- **Range-rate at c25, the uncertain part.**

  | route | range-rate at c25 (cm/s) |
  |---|---|
  | size line over the clean frames v22-40 | -38 |
  | hop-B gravity fit, v21-27 | -37 to -41 |
  | joint plane + gravity fit (whole-ball v35) | -53 to -65 |
  | joint fit, other frame sets | -40 to -50 |
  | within-hop size slope (noisy, ±10) | -15 |

- **Hop C (v30-35; t = 1.4 s is 1.6 frames after the apex at c33.4).**
  - At v35 the jar lid is drawn over the ball, so the blob centroid (485.5, 394.5) is about 7 px too high.
  - The frame difference shows the whole motion-blur streak, which runs over the lid (`img/v35_zoom.png`). Its centre
    is (483.1-483.9, 401.2-402.4) in o and x. The hop-C model predicts (483.2, 401.0).
  - A clicker sees this whole streak, so I use the whole-ball click.
  - The range at c35 is 0.917-0.927 from the joint fit, and 0.926 (centre) from the size route anchored at 1.055.
    That puts the ball in front of the jar, which matches the composite.

## Motion rows (cm/s; label = |P(c+1) - P(c)| x 25, with clicked centre and surface range)

| qids (o/s/x) | question | current | label-style (noise-free) | physical | verdict |
|---|---|---|---|---|---|
| 2685 / 2691 / 2697 | v at 1.0 s | 59.0 / **48.5** / 58.1 | click v24 (639.5,351.5) at stated 1.055; click v25 (626.3,357.7) at 1.055 + dR. See the routes below this table. | \|V(c25)\| 61-80 (hop-B fit 60.6-63.2; joint 64-80) | **fix -> 72** |
| 2686 / 2692 / 2698 | v at 1.4 s | 76.6 / **55.1** / 75.9 | Whole-ball v35 click: **95.8** (size ranges 0.906 / 0.891) and **99.0** (gravity range 0.979). Joint-fit model forward difference: 98.5-99.3. Zero-radial lower bound: 92-99. The occluded-centroid click would give 70-77, which is below the physical speed, so that click is ruled out. | \|V(c35)\| 82.5-87 | **fix -> 95** |

Routes for the v(1.0 s) label-style value:

| route | label-style value |
|---|---|
| size range-rate | **65.8** |
| hop-B gravity fit | 64.5-67.4 |
| joint fit | 75-84 |
| zero radial motion (hard lower bound for a noise-free label) | 53.3-54.7 |

### Why the current values are wrong
- The label is shared, but the answers differ by render. All three use the same base, 41 / 60 (the VLM geometry,
  p8). Each is then multiplied by a per-render label-noise factor from `research/labnoise`:
  - o/x factors: 1.44 / 1.28;
  - s factors: 1.18 / 0.92.

  The s factors differ only because the agent's s-render track had a different motion direction (sin_psi 0.68 / 0.55
  against 1.0). One label cannot have two expected values.
- **The bases are too low.**
  - At 1.0 s, the clicks v24 -> v25 are 14.4-15.0 px apart at the stated 1.055 m. That alone gives at least 53 cm/s
    with no radial motion. On top of that the ball moves 37-65 cm/s toward the camera.
  - At 1.4 s, c35 -> c36 is the descent just after the hop-C apex. The vertical speed at c35.5 is about 0.84 m/s. The
    step is 28.8 px at about 0.91 m, which gives at least 92 cm/s.
  - The s answers are below these hard lower bounds by 10 % (48.5 against 53) and 40 % (55 against 92).

### Gates
- **(a) Two independent routes agree within 12 %.**
  - At 1.4 s: the size-range forward difference is 95.8, the gravity-range one is 99.0, and the joint model gives 98.5-99.3.
  - At 1.0 s: the size route gives 65.8 and the gravity hop-B route gives 64.5-67.4. The joint fit gives 75-84, which
    is within 12 % of the chosen 72.
- **(b) The current answer is at least 25 % off.**

  | qid | current | proposed | difference | gate |
  |---|---|---|---|---|
  | 2691 (s, 1.0 s) | 48.5 | 72 | -33 % (-26 % even against the lowest route, 65.8) | passes |
  | 2692 (s, 1.4 s) | 55.1 | 95 | -42 % | passes |
  | 2685 / 2697 (o, x; 1.0 s) | 59.0 / 58.1 | 72 | -18 / -19 % | fails on its own |
  | 2686 / 2698 (o, x; 1.4 s) | 76.6 / 75.9 | 95 | -19 / -20 % | fails on its own |

  The o and x rows are included only because the label is shared. The orchestrator may drop them if it applies the
  gate per row.

### Choice of 72 / 95 (`mc_mix.py`)
The Monte Carlo is a mixture over the route scenarios, with 2 px click jitter and ToF noise sigma_z of 0-3 cm per click.
For 1.4 s, 25 % of the weight is on the occluded-click case. The table gives expected MRA per row; the noise columns
are sigma_z = 0 / 1 / 2 / 3 cm.

| answer | sigma_z 0 | 1 cm | 2 cm | 3 cm |
|---|---|---|---|---|
| v1.0 = 72 | .84 | .73 | .66 | .60 |
| v1.0 = 59 (o/x now) | .75 | .70 | .63 | .56 |
| v1.0 = 48.5 (s now) | .63 | .61 | .54 | .48 |
| v1.4 = 95 | .86 | .83 | .77 | .70 |
| v1.4 = 76.6 (o/x now) | .80 | .75 | .68 | .60 |
| v1.4 = 55.1 (s now) | .57 | .55 | .49 | .43 |

The MRA-optimal constants are 69-77 at 1.0 s and 91-102 at 1.4 s. The proposed values sit between the noise-free
label-style values and the physical ones, rounded slightly up for noise inflation (the same convention as 0040).

**Risk.**
- For 1.0 s: a radial speed of only about 15 cm/s (the noisy within-hop size slope) would make the label about 56. In
  that case 72 scores up to 0.15 below 59 at sigma_z = 0, about 0.04 below at 1 cm, and slightly above 59 at
  2 cm or more (`mc_out.txt`).
- For 1.4 s: if the labeller clicked the visible blob above the lid, the label would be about 76. In that case 95
  scores 0.0-0.19 below 76.6.

## Static rows (re-checked; `static2.py`, edges read from colour profiles on the x median)

| qids (o/s/x) | question | current | route A (stated range) | route B (table plane) | verdict |
|---|---|---|---|---|---|
| 2681 / 2687 / 2693 | cup height | 14.82 / 14.75 / 14.75 | 14.6-15.0 (f711); 14.1-14.5 (f735). Rim at 377-381, contact at 503.5 | 14.1-14.6 | OK |
| 2682 / 2688 / 2694 | poker tower height | 10.42 / 10.41 / 10.41 | 10.2-10.6 (f711); 9.9-10.3 (f735). Apex 416, feet 496-499.5 | 9.5-9.7 | OK (0-8 %) |
| 2683 / 2689 / 2695 | glass jar height | 9.1 | (m2 cylinder fit 8.95-9.07; round 1: 9.0-9.2) | | OK |
| 2684 / 2690 / 2696 | tape width | 10.64 / 10.29 / 10.50 | 72.5 px wide: 10.6 at 1.038 and 11.1 at the axis range (f711); 10.2 / 10.8 (f735) | round 1: 10.25-10.49 | OK (diameter reading). The front band is 4.7-4.9 cm, which is 48 mm tape. Round 1's open risk about the "width" meaning stays as it was. |

## Result
- **18 rows checked. 6 fixes:**
  - 2685 / 2691 / 2697 (v at 1.0 s) go to 72;
  - 2686 / 2692 / 2698 (v at 1.4 s) go to 95.
- The s rows carry the gate. The o and x rows follow from the shared-label rule.
- Static rows unchanged.
