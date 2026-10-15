# simulation_0224 (S2MC, 2D): xiangqi piece sliding down a tilted board
- Scale: piece diameter along the slope measured from the background-difference mask = 75.7 px (stable 75-76 px along the whole path, so the motion is planar). Scale = 0.097/75.7 = 1.281e-3 m/px.
- Track: piece centre from the background-difference mask, projected onto the slope direction (26 deg).
- The video has duplicated and skipped frames (dups 1,6,13,25,28,35,38,41; skips at 5,10,23,27,34,37,40). Re-indexed to the true frame index; this gives starting velocity ~0 at frame 0.
- A quadratic fit (residuals <0.7 px) gives a constant a = 0.999 px/frame^2, i.e. 0.737 m/s^2. Backward-difference speeds: 0.35 / 0.72 / 1.086 m/s at 0.5 / 1 / 1.5 s. A cubic fit agrees within 1%.
- Board length: along-slope length of the top frame = 1057 px (1.354 m). World horizontal AABB extent of the tilted board+base = 1003 px (1.285 m). Answered 1.32, between the two (low-medium confidence).
- Confidence: speeds/acc medium-high (main risk: the frame-offset ambiguity, about 8% at 0.5 s); board length medium-low.
