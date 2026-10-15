# internet_0047 — top-down basketball rolling across gym floor (30 frames, 1920x1080)
Method: camera has small handheld jitter (dy up to 22 px), so I estimated it with phase correlation on the bottom strip and aligned all frames to frame 29.
I then built a median background and tracked the ball by background subtraction (centroid).
Ball pixel speed around frame 15 is 76.4 px/frame (76.7 px/frame by backward difference), which gives 2292 px/s. The prior of 2.94 m/s then gives 0.001283 m/px.
Measurements (px): ball vertical extent ~226 (the horizontal extent is blurred); red line centres at ball rows are at 238 and 1737 (~1500); white line centre is at ~1196;
the left red line to the white line is ~960; line widths are 44-48 (~46); the ball centre at t=0 is ~102 (extrapolated, because the ball is partly out of frame).
Displacement between 0.1 s and 0.3 s is 6 frames x 76.4 px = 458 px.
Answers: diameter 28.9 cm (med); red-red 1.92 m (med-high); ball-white 1.35 m (low: the reference time and point are ambiguous;
centre-to-centre at t=0 gives 1.41 and edge-to-edge gives 1.23); displacement 0.588 m (high); left red to white 1.23 m (med-high); line width 5.9 cm (med).
Note: the scale is about 15-20% larger than real-world sizes suggest (ball 24 cm, court lines 5 cm). I kept the prior's scale.
