# simulation_0166 - bike + police van crossing an intersection (static camera, 1920x1080, 24 fps, 80 frames)

## Geometry
- Camera static, level: vanishing point of main-road edge lines = (960.5, 539.5) = image centre -> zero pitch/yaw/roll.
  The cross street (where bike and van ride, left->right) is parallel to the image plane: bike pixel size and speed are constant along the track.
- Bike pixel speed (template matching, frames 35-75, linear fit): 21.026 px/frame = 504.6 px/s.
  Scale at bike plane s_b = 5.52 / 504.6 = 0.010939 m/px.
- Bike tyre ground contact row 739.45; horizon 539.5 -> camera height H = 199.95 * s_b = 2.187 m.
- Van near-side tyre contact row 745.8 -> van near face is closer: Z_van/Z_bike = 199.95/206.3 = 0.969, s_van = 0.010602 m/px.
- Focal length (only for sanity checks): van front-face foreshortening at frames 22-25 gives Zn/Zf = 0.953, so f is about 3700 px
  if the van is 1.9 m wide. Assuming the cross street is as wide as the main road gives about 3850 px. The two routes agree, so the bike is about 41 m away.

## Answers
- 389 bike wheel diameter: outer tyre 66.4 px (horizontal and vertical edge profiles, frames 44-71) * s_b = 0.726 m. Confidence high.
- 390 road width (the main road the bike crosses): curb base lines have X/H = -1.568 (left) and +2.527 (right), so width = 4.095 H = 8.96 m.
  (Outer paint to outer paint = 8.74 m; inner paint = 8.26 m. The cross street, using f of about 3750, is about 9.1 m, which is consistent.) Confidence medium.
- 391 bike length: rear tyre outer edge to front tyre outer edge 161.8 px * s_b = 1.77 m. Confidence high.
- 392 police van length: rear bumper 752.7 to front bumper 1185.5 at frame 66 (van centred, no end faces visible) = 433 px * s_van = 4.59 m
  (4.74 m without the depth correction). Wheelbase 275.5 px = 2.92 m, which is consistent with a VW T6 (3.0 m). Confidence medium-high.
- 393 van tyre diameter: horizontal outer extent 73.0 px (rear) and 74.7 px (front), so 74 px * s_van = 0.785 m. Confidence medium.
- 394 van speed at 1 s: wheel template tracking gives a constant 27.03 px/frame over frames 27-79. The front-edge track over frames 21-28 shows the
  same constant motion, so there is no acceleration. 27.03*24*s_van = 6.88 m/s (7.10 m/s without the depth correction). Confidence medium-high.
