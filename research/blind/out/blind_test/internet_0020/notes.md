# internet_0020: bottle picked off a bathroom tray

## Clip
- 4096x2160, 19 frames. Container timing is 19.6 fps, but the dataset says 25 fps and I used 25 for every velocity. At 19.6 fps the velocities would be about 0.78x.
- The camera barely moves. ORB features on the left half of the frame show a drift of at most 27 px in x and 14 px in y and a scale change under 0.1%, which is small next to the bottle's 100-170 px/frame motion.

## Scale
- Picked bottle: a clear rectangular perfume bottle with a silver cap. In frame 0, where it is static, the cap top is at y=1187 and the base at about y=1805, so it is 620 px tall (+-10). The cap top edge looks the same in frames 3 and 8.
- k = 11.7/620 = 0.01887 cm/px.

## Camera geometry, used only to check perspective
- The tile grout lines converge downward, putting the vertical vanishing point at y ~ 35000. The tray side edges give a depth vanishing point at about (1633, 375).
- Together these give f ~ 4900 px (horizontal FOV ~45 deg), a downward pitch of about 8 deg and a camera about 28 cm above the tray.
- The tray front edge is about 1.17x closer to the camera than the bottle. The sink silhouettes are about 1.09-1.14x closer, and the pump bottle about 1.03x closer.

## Sizes
For each size I give the 2D value (pixel ratio at the bottle's scale) and the depth-corrected 3D value, then hedge toward 2D.
- **Pump bottle (2101):** 913 px gives 17.2 cm in 2D and about 16.7 cm in 3D. Answer: **17.0**.
- **Tray width (2100):** the front edge runs from x=1225 to about 2995 in frame 0, 1770 px. That gives 33.4 cm in 2D and about 28.5 cm in 3D. Answer: **32**.
- **Sink height (2099):** the sinks run off the bottom of the frame.
  - In 2D, rim top (y~990-1000) to the base at the silhouette edge (y~1976-2046) is 989-1046 px, or 18.7-19.7 cm. Rim top to the frame bottom is 1160-1173 px, or 21.9-22.1 cm.
  - In 3D the silhouette heights are 871-950 px, about 15-16 cm, which fits a typical vessel sink.
  - Answer: **18.5**, a hedge between these. Confidence is low.

## Motion
- **Tracking:** I tracked the hand point gripping the cap with DIS optical flow. It stays on the cap through frame 14; I checked this with overlays.
- **Base:** the bottle's lower end comes from aligned differences against frame 18, where the bottle is gone (lowest masked row). The cap-to-base distance stays at about 560 px through frames 0-14, as it should for a rigid bottle.
- **Centre:** the bottle centre is the base plus L/2 along the bottle axis. For frames 15-16 I took the tilt from the masks (about 25-30 deg).
- **Speed profile:** the bottle accelerates steadily. Per-frame centre speeds in cm/s: 4, 5, 10, 17, 25, 31, 36, 36, 44, 56, 55, 62, 68, 81, 67, 88.
- **Velocity at 0.50 s (2103):** frame 12.5 falls in the frame 12->13 interval. The centre moves about 145-155 px there (68 cm/s for the centre, 73 for the cap, 68.5 for the base). A central difference at frame 12 gives about 66. Answer: **70**.
- **Average velocity (2102):** over frames 0-16 (the last frame where the bottle centre is in view), displacement and path length both give 42-43 cm/s. Counting only from the start of the lift (frame 2-3) gives 48-51. Answer: **44**.

## Confidence
| qid | Answer | Confidence |
|---|---|---|
| 2103 | 70 | medium |
| 2102 | 44 | medium-low (unknown averaging window) |
| 2101 | 17.0 | medium-high |
| 2100 | 32 | medium |
| 2099 | 18.5 | low (sink bottom out of frame; unclear whether ground truth is 2D or 3D) |
