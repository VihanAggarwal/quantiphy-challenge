# simulation_0178 (2D sim, two elephants walking right, static camera)
- Scale: big elephant pixel speed 7.035 px/frame (template track 7.035, rump-edge fit 7.034; linear over 60 frames) -> 168.8 px/s;
  prior 2.313 m/s -> 0.013700 m/px. Both elephants' feet at y~690-692 (horizon ~641) -> same depth, same scale.
- Masks: clean background composed from frames where each pixel is unoccupied; features = rump edge, front edge, centroid, top, bottom.
- 425 small speed @1s: ~6.10 px/f (quadratic fits of rump/front/centroid at frame 24: 6.07-6.11; linear 6.13) -> 2.006 m/s. Conf: medium-high.
- 426 big height: top ~464, feet ~691 (+~2 px grass occlusion) -> 228 px -> 3.12 m. Conf: medium.
- 427 small height: top ~540 (536-544 gait), feet ~692 -> 154 px -> 2.11 m. Conf: medium.
- 428 big displacement frame0->59: 415 px -> 5.69 m (= 2.313*59/24). Conf: medium-high.
- 429 small displacement: 361.5 px -> 4.95 m. Conf: medium-high.
