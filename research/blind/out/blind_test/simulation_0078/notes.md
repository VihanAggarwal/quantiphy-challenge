# simulation_0078 - notes

Scene: fixed top-down Blender camera (looking straight down), 1920x1080, 24 fps, 72 frames. Two identical character
models (black shirt walks +x from the left edge, white shirt walks -x from the right edge) on the same row (y ~ 550).
Prior: white-shirt speed = 1.3 m/s (taken as a constant speed: no time given, round value).

## Method
- Tracked the brown hair blob of each person per frame (HSV threshold + morphology + connected components, assigned
  by surrounding shirt colour); checked with overlays. Hair blobs are the same size for both people (~56 px), so same head height.
- Head x tracks fitted with linear + 2-harmonic gait model (step period ~17 frames, same phase for both -> same walk clip,
  constant translation speeds).
  - black: 11.89 px/frame (17-frame windows: 12.14, 11.78, 11.80, 11.88)
  - white: 15.41 px/frame (windows: 15.62, 15.45, 15.41, 15.50)
- Straight-down camera: scale is uniform within the head-height plane, so the speed ratio and head-plane scale need no camera model.
  Head-plane scale = 1.3 / (15.41*24) = 0.003516 m/px (284 px/m). Head ~0.20 m, shoulders ~0.48 m (plausible).
- Perspective check: soft shadow halo centres (ground level) vs head positions give (x_g-960) = 0.874 (x_h-960) for BOTH people,
  so the principal point is the image centre and the camera looks straight down (head height / camera height ~ 0.125, camera ~13-14 m up, HFOV ~32 deg).
  The shadow pixel speed of black (10.39 px/f) = 0.874 x head speed, also consistent.

## Answers
- Q73 black speed at 1.0 s = 1.3 x 11.886/15.406 = 1.003 (same-window ratio gives 0.998) -> 1.0 m/s. High confidence, if speeds are constant
  (the instantaneous head dx at frame 24 is +16% higher, but that is the gait oscillation of the head, not the origin).
- Q74 distance at 1.0 s (frame 24): head separation 1501.8 px (instantaneous) / 1515.3 px (linear fit) -> 5.28 / 5.33 m -> 5.3 m.
- Q75 distance at 2.0 s (frame 48): 863.4 / 860.3 px -> 3.04 / 3.03 m -> 3.03 m.
  Uncertainty: the head may lead/lag the pelvis origin by a few cm (+-0.1 m in the separation). Medium-high confidence.

Scripts: work/hair.py (tracking), work/fit.py, work/answer.py, work/shadow2.py, work/shreg.py.
