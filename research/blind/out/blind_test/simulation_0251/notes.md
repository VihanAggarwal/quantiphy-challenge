# simulation_0251 (S2SS, 24 fps, 1920x1080, 51 frames)
Scene: static camera, gray studio backdrop; star-patterned soccer ball rolls left->right at constant image row
(contact y~580, size constant ~48 px across the whole clip) => constant depth, single planar scale.
Scale: ball diameter measured on zoomed crops and on a motion-aligned average silhouette: 47.5-49 px -> 48 px.
  0.344 m / 48 px = 7.17e-3 m/px.
Track: background (median) subtraction, left/right silhouette edges per frame; robust quadratic fit
  L(f) = -0.0854 f^2 + 33.65 f - 42.6 (rms 0.46 px); right edge fit agrees within ~0.5 px/frame.
  Ball decelerates steadily (~0.17 px/frame^2, ~ -0.7 m/s^2).
Backward-difference px/frame (avg of L,R fits): t0.5 31.6, t1 29.7, t1.5 27.8, t2 25.8.
Answers (x24 fps x scale): 0.5s 5.44, 1s 5.10, 1.5s 4.78, 2s 4.44 m/s.
Confidence: medium-high; main uncertainty is ball diameter in px (+-3%).
