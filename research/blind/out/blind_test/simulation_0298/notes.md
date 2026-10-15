# simulation_0298 - fire truck, top-down view, moving left at constant speed
- Segmentation: max-channel difference from the uniform purple background; per-frame bounding box (thresholds 20/40/70 checked).
- Constant speed: centroid moves 26.09 px/frame (frames 0-47); edge slopes range from 25.8 px/frame (bottom edges) to 27.0 px/frame (top rear edge), so there is a mild perspective effect.
- Scale: v = 11.18 m/s -> 0.4658 m/frame. Pixels per metre are taken per edge height from its slope (55.5 at the bottom, 56.3 at the cab top, 57.6 at the rear top).
- Length: the front and rear edges are converted with their own scales -> 9.40-9.59 m across frames and thresholds; answer 9.47 m. A single scale gives 535 px * 0.01785 = 9.55 m. Confidence: high.
- Width: the y extent including the side mirrors is 188-190 px -> 3.3-3.4 m; answer 3.37 m, on the assumption that the bounding box includes the mirrors. The body alone (~159 px) would be about 2.84 m. Confidence: medium.
- Displacement 0.5-1.0 s: constant speed x 0.5 s = 5.59 m. Confidence: high.
