# 0035 second measurement: qids 2644 / 2653 / 2662

Question: displacement of the basketball between 0.4 s and 0.9 s (captured_0035b, bs and bx renders; one set of labels).
The current answer for all three is 71 cm.
I did not read any other file in research/next/labaudit/0035/. My scripts and crops are in `remeasure_work/`.

## Result

| qid | video | my value (cm) | plausible range | confidence |
|---|---|---|---|---|
| 2644 | captured_0035b  | 84 | 80-87 (alternative scenario: ~105) | medium |
| 2653 | captured_0035bs | 84 | same | medium |
| 2662 | captured_0035bx | 84 | same | medium |

Every scenario I can build puts the answer above 71: label-consistent 80-87, physical centre-to-centre ~97, and the worst case for the depth reading ~105.
71 cm would need the ball at 0.4 s to read about 2.75 m, which is closer than the ball's own front surface.
The gap from 84 is 1.18x, which is below the 1.5x "gross" threshold. If this row is treated as a guarded motion row, that is the orchestrator's decision.

## Facts established (b, bs and bx renders are pixel-aligned; I checked all three)
- The video is 24 fps but has frame drops before video frames 12 and 36: frame-difference spikes of about 2x. The same happens in 0035a. So the source was 25 fps with one frame dropped per second.
- t=0.4 s falls at video frame 9.6-10. The basketball rests on the floor at the far person's foot from frame 0 to 10, at centre (828.7, 279.9).
  The kick contact is in frame 11; the ball moves from frame 12. I checked this by eye in the crops `bb_crops.png` and `rest_pixel.png`.
- t=0.9 s falls at video frame 21.5-21.6. The ball centre is at (671-672, 392-393): (677.6, 386.3) at frame 21 and (667.1, 397.0) at frame 22.

## The 0.9 s depth label (2.7777 m) is not the ball's surface
- The apparent size of the basketball (SAM2 mask in the x render; ellipse fit to edges in the b render) gives a centre range of about 2.58 m at 0.9 s, so a surface range of about 2.47 m. The label says 2.7777.
- Calibration of the size-to-range constant on static basketballs whose depth is stated in other clips:
  - 0053x: label 2.925, size-based surface 2.907.
  - 0052x: label 1.9365, size-based surface 1.919.
  - Result: k = (range + R) * eqd * cos^1.5 = 166.1, which is f*D with f = 716. This is consistent with f ~711. In both clips the ToF reads the front surface of a static ball to within 1%.
- Camera a (0035ax, a different take) is normal: the basketball at 0.6 s has label 2.27 and size-based surface 2.25. At 1.6 s, 2.412 against 2.36.
- In camera b, all four moving-ball labels fit "ToF read the floor behind the ball":
  - I fitted a floor plane (normal plus height) to the four labels taken as floor-behind ranges. The 1.4 s pair is read as basketball 2.602 and soccer 2.373.
  - Result: n = (0.144, 0.815, 0.562), camera about 1.69 m above the floor, pitched about 34 deg down. Label residuals are 0.1-0.8%.
  - Independent checks:
    - The two baseboard lines come out at 88 deg in 3D. They were traced straight with rms under 1 px, so lens distortion is negligible.
    - The plane predicts the resting ball's centre at 3.20 m. Its calibrated size gives 3.22 m.
  - The alternative readings of the labels as surface ranges (either 1.4 s assignment) give baseboard angles of 44-81 deg and resting-ball ranges of 3.6-4.0 m. Both contradict the size measurement, so I rejected them.
  - Likely mechanism: a time offset between RGB and depth (or an equivalent fault) in take b only, larger than about 0.15 s. The slow soccer ball at 1.4 s also reads floor.

## Route 1: apparent size of the resting ball
- The ball is static for 10 frames; the mask is clean. eqd = 54.7 px, minor axis 54.3 px; the b-render edge fit gives minor 54.0 and major 57.3. Off-axis cos = 0.961.
- Front-surface range: 3.108 m from eqd (k = 166.1) and 3.080 m from the minor axis (k' = 166.75, calibrated the same way).

## Route 2: floor plane, no ball size used
- The ray through the resting-ball centre meets the plane at height R from the label fit plus orthogonality. Front-surface range: 3.089 m (2.99-3.18 over the near-optimal normals).

## Displacement from the labels
GT = |rho_0.4 * u(828.7, 279.9) - 2.7777 * u(click at 0.9 s)|, with f = 711 and the principal point at the image centre.

| rho_0.4 | frame 21 | frame 21.5 | frame 21.6 | frame 22 |
|---|---|---|---|---|
| 3.108 (size, eqd) | 81.0 | 83.8 | 84.3 | 86.5 |
| 3.080 (size, minor) | 79.6 | 82.4 | 82.9 | 85.2 |
| 3.089 (plane) | 80.0 | 82.8 | 83.4 | 85.6 |
| 3.443 (floor behind the resting ball) | 102.4 | 104.8 | 105.3 | 107.3 |

- Changing f across 705-717 moves these values by less than 0.5 cm.
- Physical centre-to-centre displacement, with both centres on the plane: 94-101 cm (about 97 at frame 21.6). For reference only; the GT uses the labels.

## Main risk
The answer depends on whether the 0.4 s depth label read the resting ball (about 3.09 m, giving about 84 cm).
- This holds under a negative time offset, the "outlier" reading of the 0.9 s label, or a single early depth frame.
- If the depth for take b comes from a later time, the reading is the kicking foot (about 3.15-3.25 m, giving 86-90 cm) or the floor (about 3.44 m, giving about 105 cm).
- Even in the worst case, 84 is closer to the truth than 71.
- Other uncertainties: frame 21 vs 22 for 0.9 s (±3 cm), and the click position (±1-2 cm).

## Files (remeasure_work/)
`ballfit.py`, `width.py`, `maskfit.py` (basketball tracks), `greenmask.py` (0052/0053 calibration), `soccer*.py`,
`plane*.py`, `fbfit.py`, `surffit.py` (plane hypotheses), `final.py` (numbers above). PNG crops and contact sheets are also there.
