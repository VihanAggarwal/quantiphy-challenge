# simulation_0204 (2D, A2MS)
Scale: the glass falls freely (frames 0-10). Its centroid y, taken from differencing against the last frame, fits a quadratic with a = 12.97 px/frame^2 (second differences are steady at about 12.9).
=> 9.8 / (12.97*576) = 1.312e-3 m/px. The glass is 164 px wide (0.215 m), which is plausible. It falls at roughly the depth of the typewriter and the letter.
Speeds use the backward difference of the fitted track: frame 3 -> 1.044, frame 6 -> 2.264, frame 8 -> 3.084 m/s. The raw differences agree within 0.3%. Confidence: high.
Typewriter: 314 px wide, 171 px tall -> 0.412 m, 0.224 m (medium; the height includes the paper rest and some top view).
Letter: 198 px -> 0.259 m (medium).
Table: width at the glass's depth row is about 1745 px -> 2.29 m. The table's width in pixels grows toward the camera (perspective), so this is medium-low confidence.
