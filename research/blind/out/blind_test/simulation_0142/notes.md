# simulation_0142 — notes

Scene: static, level camera (floor-line VP at (959.5, 539.1), the image centre). A man walks left to right parallel to the image plane,
at constant depth. 80 frames at 24 fps.

## Scale from prior (walking speed 1.693 m/s)
- Median background, then background subtraction gives the man's mask. Torso/head/whole-body centroid x is linear in time:
  18.90 px/frame (453.6 px/s); residual std 4-5 px from arm swing.
- Foot plants: near foot 904, far foot 898 (sole bottom y). Pixel strides 471.5 / 464 per 24.8-frame cycle give a mean of 18.86 px/frame, which agrees.
- Scale at the man's depth: s = 1.693/453.6 = 0.003732 m/px.

## Camera / floor
- Ground under the pelvis at y≈900 gives camera height h = s*(900-539.1) = 1.347 m. Wall-floor junction y=800.0 gives Z_wall = 9.08 m.
- Floor depth lines are x=a*y+b through the VP, with Δa between neighbours = 0.445. Tile width = Δa*h = 0.599 m.
- Transverse grout rows (891, 925, 967, 1019) have constant Δ(1/(y-y_h)) = 2.53e-4. With square tiles this gives f ≈ 1758 px (HFOV 57°), which is plausible.

## Answers
- 335 man height: head top 414 (highest in gait) to ground 900, about 486.5 px, so 1.815 m. Rest pose may be 1-2% taller. Answer 1.82 (good confidence).
- 336 distance: 1.693 m/s * 79/24 s = 5.57 m (80/24 gives 5.64). Answer 5.6 (good confidence).
- 337 tile: 0.60 m (good confidence).
- 338 ceiling: low confidence. The plank ceiling is a tilted plane: the plank lines converge at y≈955-975, and the plank period is linear in y. It rises toward
  the camera at about 13.5° (tan≈0.24). Anchor: the ceiling rests on the window-header beam (top edge y=289.5). The beam sits at the top of window posts that lean back
  (post offset ratio 1.051, so Z≈9.5 m). Ceiling height: 2.70 m at the beam, 2.80 above the wall-floor line, and 3.39 m at the top of the frame / 3.41 m
  directly above the man's path. The white ribs reach the ceiling at about 3.35-3.4 m near the man's depth. The opening jambs at the frame edges hint at a front wall at about 4 m,
  so the hall may be symmetric with a ridge of about 3.4 m above the walking line. Hedged answer 3.3 (covers ridge 3.4; wall 2.7-2.8 within about 20%).
