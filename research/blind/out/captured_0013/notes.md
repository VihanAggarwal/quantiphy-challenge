# captured_0013 (lab, 1280x720, 24 fps file, 49 frames)

Camera: f = 711 px, principal point (640,360). The ball rolls down a tilted white board (the "slope") toward the camera,
reaches the desk at about frame 39, rolls across the desk and drops off its front edge at about frame 44.

## Key findings
- **Timing:** the file is a 25 fps capture converted to 24 fps by dropping frames, so frame k shows source frame round(25k/24).
  Source frame 37 is dropped between file frames 35 and 36. A constant-acceleration fit of the ball's position along the slope
  has a residual of 1.7 mm with this timing, against 9 mm or more for uniform 24 or 25 fps.
- The fitted acceleration is 3.62 m/s^2 when the distances are read as Z-depth and 3.69 when they are read as ranges. The prior
  says 3.0. A difference of about 1 mm in the second difference of clicked positions explains the gap, so the prior was treated
  as a noisy label and not used for scale. Two independent checks support the measured geometry: the ball's diameter on the slope
  and on the desk agrees (7.04 vs 7.03 cm), and its speed on the desk, measured from its apparent size (about 1.47 m/s), matches
  the speed at the bottom of the slope.
- **Z-depth vs range:** the vanishing points of the desk sides (708,364) and of the notebook sides (745,365) give a near-level
  desk horizon at v ≈ 364. With that horizon, the camera height above the desk agrees across objects only if the distances are
  ranges, which suggests they are Euclidean ranges. Answers hedge between the two readings where they differ.

## Answers
| qid | quantity | answer | basis | confidence |
|---|---|---|---|---|
| 2345 | cup height | 14.7 cm | Rim at v = 367.0. The bottom is hidden by the pen, so it is taken from the desk plane at the cup's front depth: v ≈ 452–455. Range reading gives 14.75, Z reading 14.5–14.9. | medium |
| 2346 | pen length | 14.0 cm | Ends at (520.5, 454.8) and (579.5, 462.6), assumed lying on the desk. The plane model gives 13.8–14.5. The given pen distance of 1.175 m is about 4% farther than the plane model and would give about 14.4. | medium-low |
| 2347 | cookie diameter | 8.2 cm | Horizontal width 49.8 px at a distance of 1.182 m (8.18 by range, 8.28 by Z). | good |
| 2348 | notebook width | 9.6 cm | Left-right extent of the front edge: cover 77 px, pages 74 px, at Z_front ≈ 0.90–0.91 m. Gives 9.4–9.9. | medium |
| 2349 | desk width | 60.5 cm | Front corners (419.7, 496.7) and (949.7, 500.3). Given distances as Z give 64.1, as ranges 59.0; plane-based depths give 60.0–60.7. | medium |
| 2350 | slope length | 30.3 cm | Board top edge at v = 353.3 (1.345 m) to bottom edge at v = 463.3 (1.104 m). Z reading 29.7, range reading 30.5. | good |
| 2351 | ball diameter | 7.0 cm | The ball resting and rolling on the slope plane (frames 24–35) gives 7.02–7.08. On the desk (frames 39–42) it gives 6.9–7.2. | good |
| 2352 | ball speed at 1.5 s | 118 cm/s | From the fit, v = a(t − 1.199). The forward difference over 1.50–1.54 s in source time gives 1.16 (Z) to 1.19 (range) m/s. Using source frame 37 or 38 instead gives 1.09 or 1.27. A prior-consistent reading (a = 3.0) would give about 0.96. | medium |
