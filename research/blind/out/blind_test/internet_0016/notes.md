# internet_0016: overhead drone view of a basketball court (2160x3840, 91 frames, 30 fps)

## Scene
- The camera looks straight down from a drone, with zoomed or telephoto framing. The line positions drift by 3 px or less over the 3 s, so I treat the camera as static.
- The questions concern the bottom half of the court. The player in black (black shirt, bare arms) has just shot the ball. The ball hits the rim at t=0, falls, bounces at about frame 13 and is caught by the player in black at about frame 28. The player in white (white shirt, dark hair) stands at the left lane line. A third, shirtless person at the top basket is not involved.

## Scale
- Prior: inner court (key/paint) width = 4.88 m.
- Bottom key line centres are 638 px apart at y=3400 (outer edges 649 px, inner edges 628 px). I used 640 px, so scale = 4.88/640 = 0.007625 m/px.
- Check: the key length from the end-line inner edge to the free-throw line outer edge is 777 px, which gives 5.80 m (the FIBA value) at 7.46 mm/px. The sideline-to-sideline width / key width ratio is 3.07, matching 15/4.88. The scale is therefore isotropic to within about 1%, and the top key is about 4% smaller because of slight tilt/perspective (not relevant here).

## Measurements (image plane; the dataset's 2D convention)
- Frame-differencing masks with the shadow cut off, cross-checked by hand on gridded zooms:
  - player in black, frame 0: (1037, 3212)
  - player in white, frame 0: (749, 3536)
  - player in black, frame 15: (1059, 3274)
- Ball: template matching (NCC above 0.95 except frame 0 at 0.83, where the ball overlaps the rim).
  - Frames 0 to 13: about (+3, -8) px per frame. Per-frame step sizes are 6.5, 7.5, 8.1, 8.7, 9.2 ... px.
  - Ball at frame 15: (1142.1, 3435.1).
- Rim centre from a ring fit: (1064, 3567).

## Answers
- 2080, distance between the two players at t=0: 433.5 px, which gives **3.31 m**. Head-to-head the distance is 442 px (3.37 m). Confidence: medium-high.
- 2081, ball speed at 0 s: a quadratic fit of the image track gives 6.3 to 7.3 px/frame at t=0, i.e. 1.44 to 1.67 m/s. The forward difference over frames 0 to 1 gives 1.49 m/s, and the mean over frames 0 to 5 gives 1.83 m/s. Answer: **1.62 m/s**. Confidence: medium-low.
  - Caveat: the ball is falling from rim height, so its true 3D speed is about 5 m/s. The image-plane value follows the 2D labelling convention.
- 2082, ball to player in black at 0.5 s: 181 px, which gives **1.38 m**. Measured to the head instead it is 1.13 m. Confidence: medium.
- 2083, basket (rim centre as seen in the image) to player in black at 0.5 s: 293 px, which gives **2.23 m**. Confidence: medium.
  - Caveat: the rim's ground projection is about 80 px closer than its image position (the backboard and rim are displaced outward by perspective; camera height is about 60 m). A ground-projected answer would be about 1.6 m.
