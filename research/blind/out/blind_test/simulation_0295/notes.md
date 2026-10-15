# simulation_0295 (V2SC, butterfly, prior speed 0.32 m/s)
Method: static camera; median background + diff mask + blue-hue mask (track.py, body.py). Butterfly flies right->left at
roughly constant depth (wings-up apparent width 385-398 px at frames 9/30/51, so no visible depth change), flap period ~21 frames.
Pixel speed from same-phase centroid differences (lags 20-22 and 42 frames, blue centroid / dark body / diff centroid):
30.2-31.0 px/frame -> ~30.6 px/frame = 735 px/s at 24 fps. Vertical bobbing of the body is small.
Scale = 0.32 / 735 = 4.35e-4 m/px.
Q1028 wing length: forewing span with wings flat, measured on zoomed crops near the image centre (frame 41: 422 px; total 425 px),
frame 0 approx. 407 px (one pair). Taking 420 px gives 0.183 m, so the answer is 0.182 m. Medium confidence, since "length" could mean
something else (for example a single wing, which would be about half). Perspective parallax between the wing pairs is visible at the frame edges.
Q1029 displacement 0.5->1.0 s: straight, constant-speed path -> 0.32*0.5 = 0.16 m (pixel check: 12 frames * 30.6 px * 4.35e-4 = 0.16). High confidence.
