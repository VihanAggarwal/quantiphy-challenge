# 0062 independent re-measurement (whiteboard width, shopping-bag width)

Measurer: independent second pass. I did not read any other file in this folder; all of my scripts, crops and
intermediate files are in `remeasure_work/`. I used no labels, no paid API and no Table 6 sizes.

Qids: 2924/2932/2940 (whiteboard width; renders o/s/x) and 2926/2934/2942 (blue shopping bag width; o/s/x).
The three renders show one event and share one set of labels, so each quantity gets one value for all three.

| qid(s) | quantity | answer | current (o/s/x) | confidence |
|---|---|---|---|---|
| 2924, 2932, 2940 | whiteboard width | **61.0 cm** | 45.9 / 48.3 / 48.3 | medium-high |
| 2926, 2934, 2942 | blue shopping bag width | **35.5 cm** | 12.1 / 30.2 / 21.3 | medium (which side counts as "width" is ambiguous) |

## Scene
- Camera is static (1280x720, 24 fps, 49 frames). It looks down at a carpeted corridor floor, pitched about 39 deg down and
  rolled about 7 deg.
- Whiteboard: a white rectangular board lying flat on the floor, with two hanger clips on one long edge. It is still in
  frames 0-16, where its near corner is cut off by the image bottom. It slides away from the camera in frames 17-48
  (probably pulled). There is a dropped frame between frames 35 and 36 (the centroid step doubles).
- Blue tote bag ("MARINE"): lies flat and still. The handles attach on its long edge (the opening).
- Intrinsics used: f = 711 px with the principal point at the image centre. depth_info is treated as range.

## Floor plane (scale-free), three routes
1. **Board rectangle across frames (main route).** I fitted 4 edge lines per frame at the 50% crossing between board
   and carpet on the o render, frames 20-48 (25 frames). I then solved jointly for one floor normal plus the board L/h
   and W/h so that the board's size stays constant while it travels from range/h 1.2 to 1.8.
   Result: n = (-0.114, 0.765, 0.634), L/h = 0.4607 (sd 0.0018), W/h = 0.3285 (sd 0.0013), aspect 1.40. With f
   free the fit gives f = 732 and aspect 1.38, so f = 711 is consistent.
2. **Static board, frames 0-15 averaged.** Sub-pixel edge fits; the far-right corner is extrapolated from two visible
   edges. With the route-1 normal: far 0.462, near 0.456, left 0.330, right 0.3225 (units of h). The corner angle is
   89 deg. The unblurred board therefore agrees with the moving-frame fit, so motion blur is not inflating it.
3. **Room lines.** The left and right wall baselines give the corridor vanishing point. The route-1 normal is 0.06 deg
   from perpendicular to the corridor. Corridor x carpet-stripe vanishing point gives a normal 1.5 deg from route 1.
   The wall panel seams give a normal 5.6 deg away. I rejected that one: the seams sit in the image corner, and that
   normal makes the board's size vary 3-5x more across frames. Rectified top views (`top_board_o05.png`,
   `top_board_o44.png`, `top_bag_pair.png`) show square corners for both the board and the bag.

## Scale (camera height h) from the stated ranges, with the route-1 normal
- Board centre range 2.815 m at t = 1.4 s (frame 33.6) gives h = 1.899. Frame 33 gives 1.912 and frame 34 gives 1.891.
- Bag body centre (832, 330) at range 3.307 gives h = 1.821 (bag surface plane).
- Mario at 2.016 gives about 1.74, or about 1.80 after its centre height.
- White box at 2.082 gives about 1.61, or about 1.66 after its centre height.
- Trashbin at 2.303 gives 0.95. This is inconsistent; the trashbin is clearly the farthest object, so this depth is
  probably wrong.
- A depth-only plane fit leaves 7-14 cm residuals, so the stated depths carry a few percent of noise. The board's own
  depth reads about 4% "farther" than the static objects imply.
- Velocity prior check: 1.9339 m/s implies h of about 2.3. This is consistent with the known inflation of the noisy
  motion labels (about 1.2x), so I did not use it for scale.

## Whiteboard width (2924, 2932, 2940)
W = 0.3285 h (short side; the long side is 0.4607 h).
- Route A, board's own depth, which is what the label's ToF clicks see: 0.3285 x 1.899 = **62.4 cm**.
  Per-frame scaling at frames 33/34 gives 62.8 / 61.8. With f = 732 it gives 61.8.
- Route B, bag-depth scale (static, no timing issue): 0.3285 x 1.821 = **59.8 cm**. The long side is then 83.9 cm.
- Physical cross-check, assuming the same board appears in captured_0029. There a white board stands right behind
  the 76.0 x 60.3 cm lab table. At the table's back edge it spans 494 px against the back edge's 467 px. The ball
  contact range of 1.144 m puts the board about 1 cm behind that edge. That gives a long side of 80.5-82 cm, so
  W is about 58 cm at aspect 1.40. This suggests a board close to A1 (84.1 x 59.4). It is weaker evidence, because I
  cannot confirm it is the same board.
- **Answer: 61.0 cm.** This is the middle of 59.8-62.4 and within 2.5% of either scale. The current 46-48 cm is 22-25%
  low. That aspect (about 1.8) cannot come from this board: the board rectifies to 1.40 in 26 frames, and the static
  frame agrees.

## Blue shopping bag width (2926, 2934, 2942)
- I fitted the body edges on a B-R "blueness" image of the median frame, excluding where the handles attach
  (`bag_fit_overlay.png`, residual rms about 0.4 px). Corners are L(769.9, 313.7), T(822.7, 293.8), R(896.2, 347.5) and
  B(842.5, 371.5).
- On the floor plane the sides measure 0.1956 / 0.1935 h (side edges) and 0.2505 / 0.2471 h (opening and bottom
  edges). The corner angles are 88-91 deg.
- Route 1, edge fit at h_bag = 1.821: short side **35.4 cm**, long side 45.3 cm.
- Route 2, hand-picked corners: 33.9 / 35.2 (long side 44.4). The SAM mask with the handles cut off gives a median
  across-slice extent of 36.4 (long side 46.9); SAM masks run about 1 px generous.
- The carpet-stripe normal (n_cc) gives 36.6 x 45.2.
- The handles stick out 26.5 cm beyond the opening edge. From the bottom edge to the handle tip is 62 cm. The body
  diagonal is 57.1 / 57.9 cm.
- **Answer: 35.5 cm.** This is the short in-plane side of the body: width < length, and the length is the 45 cm
  opening edge.
- Semantic risk: if the annotators' "length" included the handles (bottom to handle tip, 62 cm), then "width" would be
  the 45 cm opening edge. I judge that less likely, roughly 30%. A thickness/gusset reading (about 12 cm) cannot be
  seen on a bag lying flat.

## Files
`remeasure_work/`:
- Board: `board_fit.py`, `joint_fit.py`, `static_board.py`, `static_geom.py`, `scale.py`, `route2_board.py`
- Room lines: `seams.py`, `corridor.py`, `carpet.py`
- Bag: `bag_edges2.py`, `bag_dims.py`, `bag_handle.py`, `bag_route2.py`
- Cross-clip check: `c29_*.py`
- Shared: `lm.py` (numpy LM solver, because scipy is not installed in .venv)
