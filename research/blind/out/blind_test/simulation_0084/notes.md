# simulation_0084 - notes

Scene: fixed top-down camera over a uniform grey ground plane, 1920x1080, 24 fps, 72 frames. Frames 0 and 1 are the same image,
so motion starts at frame 1. Two copies of the same low-poly pickup model (Cybertruck-like):
- the yellow car drives left (y about 468-583);
- the black/white car drives right (y about 581-695).
At the last frame the two cars sit side by side. Both cars move at constant speed (template tracking residuals < 0.1 px).

## Measurements (work/track.py, work/sub.py, work/fit.py, work/tips.py)
- Yellow car: bbox-centre speed 9.91 px/frame; template speed 9.955 px/frame.
  Front (inner) edge moves at 9.841 px/frame and rear (outer) edge at 9.982 px/frame, so there is a mild perspective effect
  (about 1.4 % scale change across the car's height; the camera is roughly 50-80 m up).
- Black/white car: bbox-centre speed 13.85 px/frame; template speed 13.93 px/frame. Speed ratio BW/yellow = 1.398.
- Length at matching mirrored positions (same |offset| from the image centre): BW / yellow = 0.998, so the two cars are the same size.
  The BW car centred under the camera measures about 264.5-265 px long.
- Width over the mirror tips, using 50 % crossings on luma profiles over many frames: yellow 114.7 px, BW 114.1 px.
  The yellow axis from body edges (526.1) agrees with the mirror midpoint (526.08).
- Axis rows: yellow 526.1, BW 638.0, so the cars are 111.9 px apart laterally.

## Scale
The speed prior of 5.07 m/s means 0.21125 m/frame:
- the scale at the origin height is about 46.75 px/m;
- the bbox-centre coordinates have a scale of 9.9115/0.21125 = 46.92 px/m;
- the scale at mirror height is about 46.95 px/m.

Check: 265 px / 46.7 = 5.67 m, which matches the length prior given in Q108, so the two priors agree.

## Answers
| Q | Answer | Method | Confidence |
|---|--------|--------|------------|
| 102 | yellow length 5.67 m | Equals Q108's exact prior; the speed-prior route gives 5.66 | high |
| 103 | yellow width 2.44 m | 114.7 / 46.95. Mirrors are included because they take the body paint, so they are part of the body mesh; without mirrors it would be about 2.07 m | medium |
| 104 | BW length 5.66 m | 0.998 x 5.67 | high |
| 105 | BW width 2.43 m | 114.1 / 46.95, mirrors included | medium |
| 106 | distance at t = 1.0 s (frame 24) 23.98 m | dx = 1119.7 px / 46.92 = 23.87 m, dy = 2.38 m | medium-high |
| 107 | distance at t = 2.0 s (frame 48) 11.95 m | dx = 549.5 px / 46.92 = 11.71 m, dy = 2.38 m | medium |
| 108 | BW speed at 1.0 s 7.09 m/s | 5.07 x 1.398. The length-prior route gives 7.09 as well | high |

Q106 and Q107 assume the origin is the body centre. If the time-to-frame mapping is off by one frame, each distance changes
by ±0.51 m, because the cars close at about 12.2 m/s.
