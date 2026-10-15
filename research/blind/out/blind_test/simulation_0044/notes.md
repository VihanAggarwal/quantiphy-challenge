# simulation_0044: eagle over a beach with a rock (S3MC)

## Scene
1080x1080, 24 fps, 72 frames. Fixed camera. An eagle flies left to right at about 10.6 px/frame. Its shadow falls on the sand about 235 px to its right. A large rock sits at the top of the frame.

## Method
- Background = median of all frames. The eagle and its shadow were segmented by difference from that background.
- Body-axis track: for each frame I took the mask row (along the motion axis) with the longest span, giving a body centre per frame. I fitted a constant-velocity 3D line to this track (frames 1-67), with |P(1s)| = 175.3081 and |P(2s)| = 172.9881. Reprojection rms is 0.49 px.
- Eagle length in pixels: the dark body is 16.8 px at half-maximum. With the light head and tail tips it is about 18 px, at d of about 175. The body is foreshortened by sin(76 deg). This gives f of about 4050 px (135 mm on a 36 mm sensor) and HFOV of 15.2 deg.
- Camera tilt: the image track and the depth info are consistent with level flight. That puts the camera about 38 deg from nadir with no roll; the far side is at the top of the image. This was checked independently from the wing asymmetry: each wing disappears in turn during the flap cycle. That implies the eagle is seen about 33-36 deg off vertical across the wings, which the level-flight model predicts (33.8 deg).
- Shadow: I fitted the sun direction and the eagle-to-shadow ray length. The sun elevation is about 29 deg, and the eagle is about 6.6 m above the sand. The camera is about 146 m above the sand.
- Rock: the extremes in image x are 386 (at y=195; its lit side wall at the base) and 885 (at y=50). I intersected these rays with the ground plane, raised by about 2 m for the widest part of the rock. Width is measured along the camera x axis, which is horizontal and assumed to be world X.

## Answers
- 1172, speed at 1 s: |V| = 11.18 m/s. Lateral speed is 10.9 m/s and radial speed is -2.66 m/s. Confidence is medium: the result scales with f. For an eagle length of 17-19 px it ranges 10.6-11.8.
- 1173, wingspan: I measured each wing's maximum projected half-span from the body axis. Each half reaches about 21.5-22 px in every flap cycle, giving about 43.5 px at d=175 and 1.88 m. Confidence is medium (range 1.77-1.99).
- 1171, rock width: 24.8 m. Confidence is low to medium. The range is 23.4-26.2 over the eagle-length uncertainty, plus or minus 2% for roll and the ground estimate. If the camera were nadir instead, it would be about 22.4 m. "Width" is ambiguous; the extent along the other horizontal axis is about 21-29 m.
