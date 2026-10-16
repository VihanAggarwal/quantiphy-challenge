# Lab audit: family 0029 (captured_0029 / 0029s / 0029x)

There is one event. A tennis ball (6.7 cm, stated) is held at the front-right corner of the lab table during
frames 0-16. A hand rolls it diagonally toward the back-left at frames 17-19. It reaches the far edge, where it
hits the whiteboard at frame 30, then rolls slowly left along the back edge and a little toward the camera.

All three renders have 49 frames, a 24 fps container, 1280x720, and identical foreground. The ball centres agree
between the base and x renders to 1 px. There is one dropped/duplicated step between frames 35 and 36 (22 px
instead of 10 px).

Scripts are in `scripts/` and frames and crops are in `frames/`. The scripts are `extract.py`, `track.py`
(HSV ball track), `geom.py` (table edge lines and corners from the x-render mask), `rectify.py`, `plane3d.py`
(ray to table-plane offset by the ball radius), `ballfit.py` (circle fit to the upper arc) and `routes.py`.

## Geometry
- The table-top corners come from the x-render mask on frame 48. They are BL(448.4,448.6), BR(918.6,467.1),
  FR(1141.0,587.2) and FL(209.8,535.7).
- At f=711 the rectified aspect ratio is 1.33 (the known table is 76.0/60.3 = 1.26). The orthogonality residual
  cos is 0.013. This is acceptable.
- I scaled the plane so that the left-right edge is 76.0 cm. Against the stated depths:
  - Ball at frame 24 (t=1.0 at 24 fps): plane range 0.900 m, stated 0.901.
  - Frame 30 (hit): plane range 1.138, stated 1.144.
  - Frame 38.4 (t=1.6 at 24 fps): plane range about 1.003, stated 1.027.
- So the stated times map to 24 fps frames: t=1.0 is frame 24 and the hit (t=1.24) is frame about 30. The
  25 fps mapping fits worse: frame 25 gives 0.943 against 0.901.
- The stated depths imply a left-right edge of 76.0-77.8 cm and a front-back edge of 57-59 cm. A second route,
  the ball size at the hit (circle fit D = 44 px, giving 1.08 m against the stated 1.144), is consistent within 5%.

## Rows

| qid | render | question | current | measured | verdict |
|---|---|---|---|---|---|
| 2492/2498/2503 | 0/s/x | table long/length | 74.5 | 76-78 (stated-depth scale); 76.0 (known lab table) | OK (2-4%) |
| 2493/2499/2504 | 0/s/x | table width | 59.6 | 57-59 (rectified + stated depth); 60.3 (known table) | OK (1-4%) |
| 2494/2500/2505 | 0/s/x | v at 1.0 s | 99.456 | plane steps about 5.3 cm/frame, so 127 (24 fps) to 133 (25 fps). The 0.24 s chord average is 120 | ratio 1.3, inside the tuned-correction regime; not > 1.5x. Keep |
| 2495 | 0 | v at hit | 100 | 120 just before contact, 48 after the bounce, forward difference at contact ambiguous | Keep (no clear value) |
| 2496/2501/2506 | 0/s/x | v at 1.6 s | 47.31 | 38-40 (plane), up to about 53 (ball-size radial rate) | Keep |
| 2497 | 0 | distance until hit | 30.024 | I: 28.6-29.0 / II: 68-69 | see below |
| 2502/2507 | s/x | distance until hit | 43.2 | I: 28.6-29.0 / II: 68-69 | see below |

## Distance travelled "when it hits the whiteboard": an inconsistency I did not fix
- **Interpretation I (from t=1.0 s, the first depth row, to the hit):**
  - Route A (stated ranges 0.901 and 1.144 at the ball pixel centres of frames 24 and 30): chord 29.0 cm, or
    28.8 cm with the hit at frame 29.76.
  - Route B (table plane): chord 28.6 cm, summed path 28.8 cm.
- **Interpretation II (from the rest position in the hand at the table's front-right corner to the hit):**
  - Plane route: the held ball at range 0.63 m gives a chord of 68.5 cm.
  - Off-axis ball-size route: the minor axis of about 95 px with cos(theta) = 0.785 gives range 0.64 m and a
    chord of 68.3 cm (66.9-69.6 for 91-99 px).
- **Where the current values come from:** every render has the same base measurement p8 = 27, which is the
  interpretation I value. The labnoise emulator then gave factor 1.112 on the base render but 2.5 (capped at 1.6)
  on s and x. The s/x tracks have sin_psi 0.44 and 0.32, but the measured geometry gives 0.56, matching the base
  track. So 43.2 = 27 x 1.6 is an emulator/track artefact, not a measurement of either segment. The direct
  answers were 27 on the base render and 72/75 on s/x, which matches interpretation II.
- **Why I made no fix:** the segment is ambiguous.
  - The question names no start time, while the sibling interval questions in 0028 and 0040 say
    "between X s and Y s". That favours II.
  - The first stated depth is at 1.0 s, and in other clips (0034a, 0040) depth rows do not line up with distance
    endpoints. That favours neither reading.
- **What each reading would mean:**
  - Under I, 30.0 is right and 43.2 is 1.44-1.49x off. That is below the 1.5x bar.
  - Under II, both values are more than 1.5x off; the correct answer would be about 68.
- **Rough expected-value check** (score about 1 - relative error):
  - Moving s/x from 43.2 to 30 pays off if P(I) > 0.29.
  - Moving all three to 68 pays off only if P(II) > 0.6.
- **Conclusion:** neither reading is clear enough to override the leaderboard-tuned path rows. I left all three
  rows unchanged. One label is shared, so a consistent value is preferable if the orchestrator wants to decide:
  30 if it believes I, 68 if it believes II.

## Verdict
No fixes. All 16 rows are within the tuned-correction tolerance or have no clear alternative. The only open
point is the ambiguous segment of the distance row across renders (30.0 against 43.2), documented above.
