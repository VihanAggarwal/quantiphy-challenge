# simulation_0293 notes
Scene: static camera, drone with black cylindrical column rising vertically out of a wheeled box at constant speed.
Scale: template-matched drone+column (frame 70 template) per frame; linear motion 7.110 px/frame (170.63 px/s) from frame 2 on
(frames 0-1 static). Prior 0.96 m/s -> 0.005626 m/px.
- 1023 length (x-extent = diameter): column edges x 1289..1376.5 at frame 70 -> 87.5 px -> 0.492 m. Confidence: high (unless "length" means vertical).
- 1024 height: column from y 485 (under drone plate) to 663 (bottom) -> 178 px -> 1.00 m. Confidence: medium-high (hidden part inside drone unknown).
- 1025 displacement 0.5-1.0 s: constant speed, 0.96*0.5 = 0.48 m; track gives 85.2 px -> 0.480 m. Confidence: high.
