# simulation_0280 (2D whale, prior length 19.17 m)
- Scale: frame 60 (whale fully visible, near-straight) nose x~211 px, tail tip x~3638 px -> 3427 px = 19.17 m -> 0.005594 m/px.
- Nose leading edge tracked by colour diff vs frame 0 (nose2.py). Slope near frame 24: 11.3-13.1 px/frame (quadratic fit 13.0); whole-clip mean 11.8 px/frame. Used 12.4 px/frame -> 297.6 px/s -> 1.66 m/s (med confidence; origin may not move like nose).
- Displacement 0.5-1.0 s: ~135-145 px -> 0.78 m (med).
- Height: frame-60 vertical extent tail top y~495 to flipper tip y~1430 = 935 px -> 5.2 m (varies 900-1000 px across frames, 5.0-5.6 m; low-med confidence).
