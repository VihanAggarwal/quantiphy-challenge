# Lab audit round 2: family 0029 (captured_0029, 0029s, 0029x; one event, labels shared)

Input: `../inputs/0029.json`, 16 scored S3 rows. None of them carries a round-1 fix (round 1 made none; see
`../../labaudit/0029/notes.md`). I used test inputs only: frames, the `prior` (tennis ball 6.7 cm) and `depth_info`.
I used no labels.

**Event.** The ball is held in a hand just right of the table's front-right corner (video 0-17). It is pushed
diagonally across the table (released at video 18-19), hits the whiteboard at the back edge at video 30, and then
rolls slowly left along the back edge, drifting toward the camera.

**Result: 3 fixes (7 rows).**

| qids | row | current | new |
|---|---|---|---|
| 2494, 2500, 2505 | v(1.0) | 99.456 | 130 |
| 2495 | v(hit) | 100 | 55 |
| 2502, 2507 | distance travelled until the hit (s and x renders) | 43.2 | 30.024 (matches o) |

The third fix depends on how the question is read. See the last section.

Scripts are in `scripts/` and crops in `img/`. Frames are read straight from the mp4s. No frame dumps were written.

## Clock (scripts/track.py, dropcheck.py)
- The o, s and x centroids agree within 1 px from video 18 on (`track.json`).
- **Drop at video 35->36: confirmed.** The ball step is 21.6 px, against 10.4 and 10.5 px for the steps on either side.
- **Drop at video 11->12: weak signal.** The ball is held, so its own step barely shows it (3.5 px against 0.8 and
  2.2). The 95th-percentile optical flow of the hand and person shows a bump: 4.35 against 1.5 before and 2.8 after.
  The stated depths support it too (see the next list).
- So capture n = k + (k>=12) + (k>=36). The asked times map as follows:
  - t=1.0 is n25 = video 24, so the forward difference is video 24->25.
  - t=1.24 ("hit whiteboard") is n31 = video 30, which is exactly the contact frame (`img/x_hit_27_34.png`).
    The forward difference is video 30->31.
  - t=1.6 is n40 = video 38, so the forward difference is video 38->39.
- The stated ranges sit at those frames:
  - Video 24: 0.901 stated, against a plane surface range of 0.882 (0.930 at video 25).
  - Video 30: 1.144 stated, against 1.142 (plane) and 1.13-1.14 (size).
  - Video 38: 1.027 stated, against 0.98-1.04.

## 3D routes (scripts/geom.py, routes3d.py, size_fit.py, size_trend.py)

| route | how | notes |
|---|---|---|
| A, PnP plane | Table-top corners from x frame 48 (`img/x48_corners.png`), 76.0 x 60.3 cm, f=711; ball centre 3.35 cm above the top | Reprojection error 5.5 px. Camera 16 cm above the top. ToF minus surface range at the anchors: +1.9 / +0.2 / +4.5 cm. |
| B, anchor plane | Plane through the three stated centres (stated range + r along the clicked ray) | 1.7 deg from A's normal |
| C, size | Sub-pixel half-level circle fit of the upper arc against the whiteboard, on the o and s renders (`sizefit.json`) | Per-frame noise about 1 px (3 cm). Post-bounce line fits have rms 1.3-1.5 cm. |

- **Size and stated depths agree at the anchors.** The o-render size-route centre range is 1.172 at video 30 and
  1.071 at video 38. The stated value plus r is 1.178 and 1.061.
- **The post-bounce size line passes through both anchors.** It is fitted over video 31-48, with slope -1.0 to
  -1.26 cm per step. It gives 1.163-1.183 at n31 and 1.067-1.078 at n40.

## Rows

| qids | row | current | label-style (the labeller's forward difference on the 25 fps clock) | physical | verdict |
|---|---|---|---|---|---|
| 2492/2498/2503 | table length | 74.5 | known lab table 76.0. The anchor-plane implied value (78-82) is ill-conditioned. | 76.0 | keep (2%) |
| 2493/2499/2504 | table width | 59.6 | 60.3 known; 54-59 from anchors | 60.3 | keep (1%) |
| **2494/2500/2505** | **v(1.0)** | **99.456** | 128 (linear interpolation of anchors), 137 (B), 143-149 (A), 156-165 (size); median of the route mix 141 | 127-135 (anchor chord to contact: 28.6-29.0 cm in 5.3-5.7 steps); 137-144 (A/B finite difference) | **fix to 130** |
| **2495** | **v(hit)** | **100** | 50 (anchor interpolation, -1.3 cm per step); 46-50 (size-trend radial step -1.0 to -1.3 cm) | after the bounce 45-50 (lateral 1.4 cm per step plus radial -1.2); just before contact about 135 | **fix to 55** |
| 2496/2501/2506 | v(1.6) | 47.31 | 50 (anchors and size, -1.2 cm per step); 40-43 (planes, -0.5 to -0.8) | 41-51 | keep (at the MRA optimum, 45-56) |
| 2497 | distance until hit (o) | 30.024 | I: chord 28.9 (2-px jitter 28.6-29.3); I as a summed path 29.6-30.7. II: 65-69. | I: 29.2-30.8 | keep |
| **2502/2507** | distance until hit (s, x) | **43.2** | same | same | **fix to 30.024** (see below) |

### Monte Carlo of the label process (scripts/mc_rows.py, mc_hit_alt.py)
The model has 2 px click jitter on both clicks. The first ToF is the stated value. The next-frame ToF is the stated
value plus the route's radial change plus sigma_z (1, 2 or 3 cm). Expected item scores at sigma_z = 2 cm, the
fitted value for balls:

| row | current answer: E[score] | proposed answer: E[score] | MRA-optimal answer |
|---|---|---|---|
| v(1.0) | 99.456: .60-.70 | 130: .72-.73 | 118-132 (125-141 at sigma_z 1 cm, 110-136 at 3 cm) |
| v(hit) | 100: .35 (.22 at 1 cm, .43 at 3 cm) | 55: .65 (.70 at 1 cm, .60 at 3 cm) | 49-57 |

- **v(1.0) robustness.** Only one case out of 12 favours the current value: linear interpolation at
  sigma_z = 3 cm, .663 against .655.
- **v(hit) robustness.** Alternative frame conventions still favour 55-60 over 100:
  - backward difference (video 29->30);
  - hit frame = video 29;
  - no drop at 11->12, so the difference is video 31->32.

  These give label medians of 52-85 and E[score] of .56-.69 for 55, against .21-.60 for 100.

### Why v(1.0) = 99.456 is wrong
- It is p8's base of 112 times the labnoise factor 0.888 (`research/labnoise/out/test_rows_cap1.6.csv`). The 0.888
  is an MRA shading factor for a wide label distribution.
- The base 112 is already 15-20% below every geometric route. That holds for the anchors alone (127-135, no table
  dimensions used) and for the PnP plane (143).
- So 99.456 sits at the 10-15th percentile of the label distribution, about 29% below the label-style median.
- Shading applied on a correct base gives about 130.

### Why v(hit) = 100 is wrong
- The value is a direct median (dmed). It describes the approach (about 135 just before contact), or a blend of
  approach and rebound.
- The labeller's forward difference starts at n31 (video 30), when the ball is against the board and its radial
  motion has stopped. It ends at n32 (video 31), when the ball is already rolling back slowly. That step is about
  1.9 cm per step, or about 50 cm/s.
- The plane routes would give 138-168 for this step. That is an artefact:
  - The image centre drops 3.4 px at video 30->31 (circle fit) and only +0.3-1.1 px per step after that.
  - The plane maps that drop to a 5-7 cm radial jump.
  - But the diameter does not change (o: 40.64 -> 40.79 px; s: 40.94 -> 39.84). A 6 cm approach would add 2.2 px.
  - The post-bounce size line goes through the hit-frame size and through both anchors.
  - The stated n31->n40 change (-11.7 cm, which is -1.3 per step) leaves no room for a 6 cm jump.
  - Friction cannot take a ball from 6 cm per step to 1.2 cm per step in one frame.
- So the ball rides about 4 mm up the board at the impact frame. The extra 2.5 px drop at a range of 1.17 m
  corresponds to that height. At video 30 the bottom of the ball sits exactly on the back-edge line; at video 31 and
  later it sits 3.8-9 px below it.

## Distance travelled "when it hits the whiteboard" (scripts/dist_rows.py, dist_decision.py)

The three renders share one label but carry 30.024 (o) and 43.2 (s and x).

**Interpretation I: from t=1.0 to the hit.**
- Both depths are stated, so the label is nearly deterministic: chord 28.9.
- If the labeller summed noisy per-frame clicks instead, the label is 29.6-30.7.
- Plane chord 29.2-30.6.

**Interpretation II: from the start, with the ball held in the hand.**
- Off-axis sphere model with the true minor axis of about 95 px. The HSV ellipse misses the shaded lower part; see
  `img/held_ball.png`.
- This gives a range of 0.63-0.66, and a chord to the hit of 65-69. The plane route from video 18 gives 65.7.

**Why 43.2 is wrong under either reading.**
- 43.2 is 27 x 1.6: the labnoise emulator's capped factor.
- The emulator treated the row as a whole-track sum of noisy per-frame differences (factor_raw 2.5) on the s/x tracks.
- 43.2 is 44-49% too high under I and 37% too low under II.

**Expected score of the three rows against p = P(I):**

| answers | p=.2 | .3 | .4 | .5 | .6 | .7 |
|---|---|---|---|---|---|---|
| current (30 / 43.2 / 43.2) | .554 | .567 | .579 | .592 | .605 | .618 |
| all 30.0 | .513 | .569 | .626 | .683 | .739 | .796 |
| all 68 | .777 | .680 | .583 | .486 | .389 | .291 |

- The current mixed set is dominated at every p. All-30 beats it for p >= 0.3, and all-68 beats it for p <= 0.4.
- Evidence for I:
  - The depth rows are exactly 1.0 and the hit.
  - The 0008/0052 audits read "initial" as the first depth row.
- Evidence for II: the plain reading of the question (no start time; 0028 and 0040 state "between X and Y").
- My estimate is p of about 0.4-0.6.
- Proposed: 2502 and 2507 -> 30.024, the same value as 2497. If the orchestrator believes II (p < 0.375), the better
  move is all three rows -> 68 instead.

## Result
| fix | qids | change |
|---|---|---|
| v(1.0) | 2494, 2500, 2505 | 99.456 -> 130 |
| v(hit) | 2495 | 100 -> 55 |
| distance | 2502, 2507 | 43.2 -> 30.024 (interpretation-dependent, as above) |

The table rows, v(1.6) and 2497 are unchanged.
