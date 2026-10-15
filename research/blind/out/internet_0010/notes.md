# internet_0010: basketball shot, handheld 4K camera, 30 fps, 97 frames

Prior: the basketball diameter is 24 cm. The scale comes from the ball's pixel diameter at each depth.

## Camera
- The camera is handheld and pans. The background moves about -2 half-res px per frame (about -4 full-res px per frame) around frame 60, with small tilt and roll.
- I estimated camera motion two ways: chained frame-to-frame similarity transforms (cam.py) and direct registration of each frame to frame 60 (cam2.py).
- The backboard and the far red building show the same small residuals after stabilisation, so parallax is negligible and the motion is rotation-dominated.

## Ball (fit.py, fit2.py, radial.py)
- I tracked the ball by template matching and refined the centres in the clean sky frames (48-52 and 75-77) with sky-colour-distance segmentation.
- Diameter from a sub-pixel radial half-max edge fit is 46.4 px at frames 48-49 (just released, at the shooter's depth), 46.0 px at frames 50-52 and 45.8 px at frames 75-77. The ball recedes only slightly.
- Gravity check: the stabilised vertical acceleration is 1860-1880 px/s². At 24/46.2 cm/px this is 9.7 m/s², close to g. This confirms the scale.
- At frame 60 (t = 2.00 s), the stabilised trajectory fit (y quadratic, x linear or quadratic) gives these speeds:
  - Backward difference: 1053-1073 px/s.
  - Instantaneous: 1040-1059 px/s.
  - Without camera compensation, the speed would be about 960 px/s, which gives about 500 cm/s. This is the alternative if the ground truth ignored the camera pan.
- Answer: 1062 px/s × 24/46.15 = **552 cm/s**. Confidence: medium. The camera-compensation convention adds up to 10% uncertainty.

## Shooter (grey tank top, dark shorts; face is privacy-blurred, hair top visible)
- Upright frames give these heights from hair top to sole:
  - Frame 0: 674.5 to 1009, so 334.5 px.
  - Frame 16: 677 to 1009, so 332 px (walking).
  - Frame 20: 677 to 1010, so 333 px.
- His feet are at the same image y in frames 0 and 34-42 and the camera's vertical drift is about 0, so he stays at the release depth. The scale is therefore 24/46.4 cm/px.
- Held-ball rough check (frames 0-4, 16-20): about 45 px. That would give about 178 cm.
- Answer: 335 px × 24/46.4 ≈ 173.3 cm, plus a small upright allowance, so **174 cm**. Confidence: medium-high.
