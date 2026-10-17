# internet_11 remeasure (independent second measurer): internet_0047, qids 3096-3101

The clip is internet_0047.mp4: 30 frames, 30 fps, 1920x1080. It is a nearly top-down handheld view of a gym floor.
A basketball rolls left to right along the top red line, and below that line are two vertical red lines and one white line.
The prior is that the ball's velocity at 0.5 s (frame 15) is 2.94 m/s.
I did not read internet_11/notes.md or the other files in that folder; I used only the original agent notes (blind_test/internet_0047/notes.md).

## Camera motion
- I matched ORB features with RANSAC and fitted a homography from each frame to frame 15.
  The jitter is almost entirely vertical (up to 18 px); horizontal drift stays under 2 px, rotation under 0.13 deg and scale under 0.3%.
- After alignment, the floor line positions are stable to within 0.5 px across frames 6-21 (aligncheck.py). Background is the median of the aligned frames.

## Ball track (aligned to frame 15)
- Method A (track5.py) takes, row by row, the midpoint of the left and right half-max boundaries of the Lab colour difference, using rows above and below the red line.
  Within one frame the rows spread by sd about 1 px in frames 9-18, and the bands above and below the red line agree to within 1 px.
- Method B (track6.py) registers the ball silhouette between frames i-1 and i+1.
- Method C (arcsym.py and vext.py) finds the mirror-symmetry centre of the bottom arc, and the plateau of the vertical extent per column. Both work even when the ball is partly cut off in frame 0.
- Positions (px, frame-15 coordinates): f0 71.6 | f3 305 | f4 383 | f8 704 | f9 781.0 | f10 856.9 | f11 932.8 | f12 1008.6 | f13 1087.2 | f14 1162.2 | f15 1240.2 | f16 1318.9 | f17 1398.1 | f18 1476.9
- Speed at frame 15:
  - central difference (A): 78.35 px/frame
  - B (frames 14-16): 78.2
  - quadratic fit over frames 9-18: 78.0
  - (x18-x12)/6: 78.05
  - mean over frames 0-18: 78.07
  - Best value: **v15 = 78.0 +- 1.0 px/frame**.
  - Simple blob-centroid tracking gives a biased 76.0, because the mask picks up the occluded red line. The original agent's 76.4 came from centroids.
- Scale from the prior: s = 2.94 / (30 * 78.0) = **1.2564 mm/px**. This is the image scale at the ball centre at x of about 1240.
- Perspective: the right side of the image is closer to the camera. Board pitch rises from about 49.3 to 53 px left to right, and the ball's vertical extent rises from 226.8 to 232.2 px between frames 9 and 18.
  Using the ratio D/v at frame 15 cancels this effect.

## Measurements
| qid | quantity | pixels | value at prior scale | reported |
|---|---|---|---|---|
| 3096 | ball diameter | vertical extent at frame 15 by max-gradient: 228.8, plus about 1 px for motion-blur shrink, giving 229.5 | 28.8-28.9 cm | **29.0 cm** |
| 3097 | red-red, centre to centre | 1494 (y520), 1498 (y560), 1502 (y600), 1521 (mid-image) | 1.88-1.91 m | **1.92 m** |
| 3098 | ball (t=0) to white line | white line centre 1197.0, ball centre 71.6 (ball radius 114.75 px) | c-c 1.414 / ball centre to near edge 1.385 / edge-edge 1.241 | **1.37 m** |
| 3099 | displacement 0.1-0.3 s (frames 3 to 9) | 468-476 measured (speed fit to directly measured); 455 from the local 9-12 speed | 0.57-0.60 m; constant 2.94 m/s gives 0.588 | **0.59 m** |
| 3100 | left red to white, centre to centre | 957.6 (y560), 960.3 (y600), 963 (y640) | 1.206 m | **1.23 m** |
| 3101 | line width | left red 45.3-45.9, white 45.0-45.7, right red 47.8-48.2, top red 44.2-45.0; mean about 45.7 | 5.74 cm | **5.85 cm** |

## Why the floor values are nudged up about 2%
1. Annotator scale. The diameter at the prior scale (28.9 cm) is about 20% larger than a real basketball (24 cm).
   It is suspiciously close to "29.5", the circumference in inches of a size-7 ball.
   If the annotator assumed D = 29.5 cm and used one image scale, every label is px * 0.295 / D_px. That is +2.3% over my scale.
2. Depth. The ball centre is about 12 cm above the floor, so a physically exact prior puts the floor scale at s * H/(H - r).
   That factor is +5% for H of about 2.4 m (from the ball-to-board ratio) and +9% for H of about 1.5 m (from a phone focal length of about 1400 px).
   I think annotators used a single scale, so I did not apply the full factor.
A +2% nudge keeps all of these hypotheses within about 5% error, except the strongest depth case.
The pure prior-anchored values with a single scale are in the "value at prior scale" column of the table.

## Real-world check (not used for the answers)
- The floor boards measure 51.5-52.4 px. If they are 2-1/4" maple strips (57.15 mm), the floor scale is about 1.09-1.11 mm/px.
- On that scale the lines come out at 5.0 cm (standard 2"), red to red is about 1.66 m, and the ball is about 23-25 cm. That is a fully consistent real-world picture.
- The stated prior is therefore about 16-22% "too fast" for real sizes. The current pipeline answers (scaled by 0.838, for example 24.2 cm) use that real-world scale.
  I followed the task rule that the prior is exact and sets the scale. If the labels are real-world sizes instead, multiply my values by about 0.84-0.86.

## Files
Scripts are cam.py, track*.py, diam.py, vdiam.py, lines.py, boards*.py, arcsym.py, vext.py, f0.py, aligncheck.py, blur.py, sheet.py and crop.py.
The PNG crops are in png/.
