# simulation_0177 — elephant walking right (V2SC, 60 frames @24 fps, 1920x1080)

Prior: elephant speed = 1.424 m/s. Static camera (phase correlation on background: <0.03 px drift).

## Tracking
- Torso template matching (two templates from frame 30, sub-pixel): x moves linearly, 3.43-3.45 px/frame
  (std of per-frame diff 0.25 px), vertical drift < 2 px, no trend. 203 px total from frame 0 to 59.
- Multi-scale template matching shows no monotonic scale trend (only gait noise of +-3%), so the motion is
  roughly parallel to the image plane. The gradual change in appearance (more of the front visible at left) fits
  off-axis viewing, not a turn.
- Scale: 1.424 / (3.44*24 = 82.6 px/s) = 0.01725 m/px at the elephant.

## Q423 height
- Top of head 652-656 px (median 652). Feet bottoms run from 831 (far-side feet) to 845 (near-side feet), with a
  median of about 838. That spread fits a slightly elevated camera. Grass hides about 3 px of the feet.
- Height is about 183-190 px, call it 186 px, x 0.01725 = 3.21 m. Answer 3.2 m (confidence moderate, +-5%).

## Q424 displacement
- Constant speed along a straight line: 1.424 * 59/24 = 3.50 m. The measured 203 px * 0.01725 = 3.50 m agrees.
  Answer 3.5 m (confidence high, as long as the dataset uses first-to-last-frame displacement).
