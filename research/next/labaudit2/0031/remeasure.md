# 0031 independent re-measure (second measurer): qids 2523, 2529, 2534

All three ask for the velocity of the tennis ball at 1.6 s in cm/s. captured_0031, 0031s and 0031x are the same
footage (s and x are SAM re-renders with the background replaced) and have identical depth_info, so they share
one label and get one answer.

Scripts are in `remeasure_b/`: track.py, edgefit.py, table.py, fcal.py, motion.py, vel.py, plane.py, steps.py,
combine.py. Frames and crops are in remeasure_b/frames/ (about 11 MB).

## Scene
- The camera is level and about 17 cm above the table top, looking along the 76 cm side of the table. The 60.3 cm
  side runs across the image. The yellow tennis ball (6.7 cm) and the white ping-pong ball (4.0 cm) start at rest
  near the back edge. Both are pushed at video frame ~15 and roll toward the camera. The tennis ball reaches the
  front edge and falls at video frame 42-43; the white ball is still rolling at the end of the clip.
- Frame-drop map from capture (25 fps) to video (24 fps). Template matching of ball patches gives a double-length
  step at video 35->36 for both balls (tennis 5.15 px against 2.4/3.6 px for its neighbours; white 3.13 px against
  1.74/2.23 px). This fits nearest-rounding resampling: capture = k for k<=11, k+1 for 12..35, k+2 for 36..48.
  So t = 1.6 s is capture 40 = video 38, and the forward difference 40->41 is video 38->39, a single step.

## Focal length for this clip
- Table rectangle PnP with an unknown f (60.3 across, 76 deep): best f is about 775 px, with reprojection error
  0.9 px. f = 711 gives 3-6 px errors. Swapping the table dimensions fails (error over 6 px).
- The ToF anchors give the same value, but only if the object names are swapped (see the next section).

## depth_info names are swapped relative to the visible objects
At t = 1.6 s (video 38) the yellow ball is plainly the nearer one: its contact point is lower in the image, and
its image radius is 25.6 px against 12.4 px for the white ball.
- Tennis ball centre: 103.8 cm by size and 103.0 cm by the ground plane. Its surface is therefore at about 1.00 m,
  which matches the value stated for the **white** ball (0.994 m).
- White ball centre: 126.0 cm by size and 123.2 cm by the ground plane. Its surface is at about 1.22 m, which
  matches the value stated for the **tennis** ball (1.19 m).
- With the names as written, the two balls give f = 931 and f = 629 and are not consistent with each other. With
  the names swapped, they give f = 782 and f = 750, which agree with the table's 775.
- Conclusion: in the label pipeline, the object called "tennis_ball" has the white ball's depth at 1.6 s.

## Speeds (label-style: surface point along the clicked-centre ray, capture clock)
Two routes, each run on all three renders and on the median across renders:
1. Size route: sub-pixel circle fit to the upper silhouette arc, then range from the angular radius with f = 775
   (ToF-consistent), then the surface point at (Rc - R_ball) along the centre ray.
2. Ground-plane route: the ball centre lies on the plane z = R_ball above the table top, with camera pose from the
   table PnP. This route is table-anchored and nearly independent of f: 711, 745, 775 and 805 all give the same
   speeds within 1 cm/s.

| ball | ground route | size route | raw single forward difference 40->41 |
|---|---|---|---|
| tennis (yellow) | 61.5-64.3 | 60.5-64.4 | 46-62 (noisy) |
| white | 44.2-45.7 | 43.4-47.9 | 34-69 (noisy) |

Physical tennis speed at 1.6 s: about 63 cm/s. The label-style surface-point value is about 62.5 cm/s. Speed is
roughly constant from capture 22 to 43; I see no clear deceleration. Physical white-ball speed: about 45 cm/s.

## Answer
- If the label's "tennis ball" track is the yellow ball, so that only the depth_info text is swapped:
  **62.5 cm/s** for all three qids.
- If the annotation object keys are swapped (the same track feeds both depth_info and the velocity label), the
  "tennis ball" label is the white ball's speed, **about 45 cm/s**.
- The current answers of 71.8 and 77.5 look like the yellow-ball speed scaled by the misattributed 1.19 m anchor
  (62 x 1.19 / 1.00 is about 74). They are probably too high under either hypothesis.
- A hedge of about 53 would score about 0.85 under either hypothesis. Committing to 62.5 scores 1.0 or about
  0.64; committing to 45 scores about 0.74 or 1.0.
- Labels come from single-frame forward differences of the clicked ToF points. At about 2.5 cm of motion per
  frame, a few cm of ToF noise makes the label itself very noisy.
