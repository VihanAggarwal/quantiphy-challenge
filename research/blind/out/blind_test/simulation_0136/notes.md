# simulation_0136 (S2MC, front view of kitchen counter, 24 fps, 60 frames)
Scale: blue cup isolated width (frames 7-28 HSV mask) = 118.5 px = 0.087 m -> 7.342e-4 m/px.
- 328 toaster length: red mask x 52-486 = 434 px -> 0.319 m (planar scale; toaster sits further back, so may be underestimated). Confidence medium.
- 329 cup speed t=1s (frame 24): bbox-centre backward diffs frames 22-26 ~36.9,35,33.2,31.4,30 px/frame (decelerating) -> 33.2 px/f -> 0.585 m/s. Confidence medium-high.
- 330 cup speed t=2.25s (frame 54): cup partly off-frame & tilting; centre diffs frames 40-51 ~25.1 px/f, left-edge 50-55 ~24.4 -> 24.8 px/f -> 0.437 m/s. Confidence medium.
