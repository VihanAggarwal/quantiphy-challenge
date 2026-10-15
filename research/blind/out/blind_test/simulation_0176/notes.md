# simulation_0176 notes

Scene: a static camera (1920x1080, 24 fps, 40 frames) watches a T-tail jet (CRJ-like) fly right to left past a rock stack on a sand island.
I measured with a pinhole model and principal point (960,540).

## Camera
- The nose tip of the plane (left end of the transparent radome outline, from background subtraction) is at (1069,156) in frame 12 (t=0.5) and (377.5,173) in frame 24 (t=1.0).
- With the given nose distances (284.98, 305.627) and |dP| = 153.582*0.5 m, the RANGE (Euclidean) convention gives f = 2693 px (HFOV 39.2 deg).
  The optical-axis-Z convention gives f = 2827.
- Checks:
  - (a) The perspective curvature of the nose track over frames 10-30 fits the range convention (rms 1.2 px, best f about 2700-2800 even without the speed prior). It does not fit Z (rms 4 px, independent of f).
  - (b) A frame offset of 0 (t=0.5 at frame 12) fits best.
  - (c) The sky-brightness horizon is at y of about 540, so pitch is 0. The vanishing point of the plane's flight direction (yaw 10.66 deg) lies on the tilted far edge of the sea plane (slope 0.0246). So the plane flies along a world axis, and its AABB length equals its body length.

## Q1415, plane length
- I fitted the rightmost silhouette point (the far horizontal-stabiliser tip) over frames 10-30.
- Model: nose - L*axis +/- w*lateral, with the axis along the velocity. Result: L = 47.75 m, semispan 5.9 m, rms 0.87 px.
- A single-frame check (467 px at frame 12) gives about 48 m.
- Answer: 47.8 m. Confidence: medium-high.

## Q1417, rear (main) wheel diameter
- From frames 22-30 the two main gears are separated (fitted: 26.2 m behind the nose, half-track 2.75 m).
- I measured the half-max silhouette extent perpendicular to the projected axle direction, because a cylinder's width there equals D.
- 18 measurements give D = 1.195-1.273 m, median 1.228.
- Answer: 1.23 m. Confidence: medium.

## Q1416, stone cliff height
- Pitch is 0, so the horizon is at y=540. The rock's front-right base touches the sand at y of about 1018, and the stone top (where the trees grow) is at y of about 624. Trees reach y of about 522.
- The footprint spans the base rows 975-1018. With the rock origin at range 296.35 (Z about 294), the camera is about 49.7 m above the sand and the front contact is at Z of about 280.
- Visible stone height is about 40.6 m (range 39.7-42 for front contact Z between 275 and 285). Including the trees it would be about 51.6 m.
- Answer: 42 m (stone only, nudged up for possible embedding in the sand). Confidence: low-medium; the biggest risk is whether the vegetation is in the AABB.
