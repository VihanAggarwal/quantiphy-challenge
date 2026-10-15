# simulation_0135 — notes

The scene shows a kitchen counter (toaster, wall outlet, cooktop) seen by a static camera. A blue tapered cup rolls on its side from left to right. It enters at frame 5 and leaves the frame on the right at frame 53. The video is 24 fps with 60 frames.

## Camera
- The camera is level and faces the wall. Depth-direction lines (the vent edges under the cabinet and the cooktop edges) meet at about (948, 535), which is close to the image centre, so the horizon is at y = 540.
- Focal length is about 2660 px (horizontal FOV about 40 deg). I got it by rectifying 3 cooktop burner rings into circles. The answers do not depend on f.
- For a point on the counter, depth = f*hc / (y - 540), where hc is the camera height above the counter.

## Scale from the prior
- The cup lies on its side with the closed small base towards the camera and the wide rim at the back.
- At frames 17-20 the cup points straight at the camera. There the rim projects as a circle about 133 px wide (sub-pixel edges from the background difference; the HSV mask misses the dark shaded edge and gives only 128). The rim top is at y = 828, so the rim's bottom contact point is at y = 961.
- I took "diameter = 0.087 m" to mean the rim (max) diameter. That gives 0.087/133 m/px at rim depth and hc = 0.087*421/133 = 0.2754 m.
- Caveat: real-world cues in the kitchen would suggest hc of about 0.35, which is about 1.25x larger. Examples: counter depth 1.72 hc, cooktop width 1.71 hc, outlet height 0.21 hc. If the prior instead meant the base diameter (0.217 hc) or the mean diameter (0.265 hc), every answer would scale by 1.45 or 1.19. I kept the rim/bbox interpretation because the prior is stated to be exact.

## Answers
- **324, toaster length: 0.296 m.** This is the X extent of the toaster on the counter plane, X/hc = (x - 960)/(y - 540).
  - The front-left foot reaches x = 59.5 and the front-right corner reaches about x = 476-482, both at contact y of about 929.
  - That is about 1.075 hc, so 0.296 m. Confidence is medium (plus or minus 3% from measurement, plus the scale-interpretation risk).
- **325, outlet height: 0.0569 m.** The 3-gang frame's front face runs from y = 711.3 to about 784 (73 px). Rows 784-788 look like a shadow under the frame; if they belong to the frame, the height is 76.5 px, about 5% more.
  - The wall depth comes from the counter/wall junction at y = 891.75, with a 0.5% correction for how far the plate stands off the wall.
  - Confidence is medium.
- **326, cup speed at 1 s: 0.540 m/s.** This is a backward difference at frame 24, smoothed over frames 22-26.
  - Rim-centre track: about 34.3 px/frame at rim scale, giving 0.538 m/s.
  - Base-bottom track: about 37.3 px/frame at base depth (y = 995.5), giving 0.541 m/s.
  - The cup's yaw stays about constant, so both ends move together and these agree. Confidence is medium-high (the frame/time convention could shift this by about 5%).
- **327, cup speed at 2.25 s: 0.426 m/s.** By then the cup is off-screen (last visible frame is 53).
  - From frame 30 to 53 the cup rolls at a constant speed: the rim moves 27.2 px/frame (0.427 m/s) and the base 29.2 px/frame (0.424 m/s).
  - I extrapolated that constant speed to frame 54. Confidence is medium-high, apart from the shared scale-interpretation risk.

## Scripts
- `track2.py` builds the per-frame cup track and writes `track2.csv`.
- `burners*.py` estimates the focal length.
- `rim*.py` measures the rim size.
- `outlet*.py` and `toaster.py` take the static-object measurements.
- `final.py` computes the answers.
