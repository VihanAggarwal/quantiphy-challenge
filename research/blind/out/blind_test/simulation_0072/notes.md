# simulation_0072 — notes

Scene: top-down (nadir) fixed camera over a road crossing, 2160x1080, 24 fps, 72 frames (frames 0 and 1 identical).
Bicycle rides straight up the vertical road (x~918 px); pedestrian walks +x on the lower-right sidewalk (y~844 px).

## Method
- Median background, |frame - bg| masks; intensity-weighted centroids per frame (scr/track2.py).
- Bicycle: linear fit of centroid y over frames 1-71 gives 8.92 px/frame (8.88-8.93 for sub-windows; quadratic term negligible, so speed is constant).
  Blob top/bottom edges give 8.87-8.89 px/frame. Used 8.91 px/frame. Scale = 5.33 / (8.91*24) = 0.0249 m/px. The bike is ~64 px long, about 1.6 m, which is plausible.
- Pedestrian: centroid of the bright white-shirt pixels (torso, which sits over the pelvis) gives a global slope of 2.047 px/frame.
  Gaussian-smoothed (sigma 2) backward velocity at frame 24 is 2.02 px/frame (2.05 around it); used 2.03 px/frame.
- Ratio: 2.03/8.91*5.33 = 1.214 m/s.
- Perspective: the lamp posts show radial pole lines with length/r = 0.060, so H is about 17.7x the lamp height (about 50-90 m).
  The shirt plane is about 0.45 m higher than the bike centroid plane, which gives a correction of about -0.5 to -1%. Result: about 1.205.

## Answer
- 47: 1.21 m/s (confidence: good, ~5%; the main risk is pelvis gait oscillation at exactly t=1.0 s)
