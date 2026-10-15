# simulation_0245 (2D sim, antelope + rabbit walking right, static camera, 1080x1920, 75 frames @30fps)
Scale: antelope speed prior 1.277 m/s. Antelope torso template tracking: anchored-template 195 px/s, chained 191.4 px/s
(per-frame 180-213 px/s gait oscillation) -> 193 px/s -> s = 0.006617 m/px. Both animals' feet on same ground row (~1548) -> same depth, one scale.
- 826 antelope height: horn tip y~1125 to hoof y~1548 = ~420 px (408-423 over frames) -> 2.78 m. Conf medium.
- 827 antelope length: tail tip x~73 to nose x~555 (f0), 320->805 (f38) = ~483 px -> 3.20 m. Conf medium.
- 828 rabbit speed @1s: orange-mask centroid track (bg = composite of first/last frames), backward diff around f30 ~7.05 px/f -> 1.40 m/s
  (rabbit average 6.7 px/f -> 1.33). Conf medium.
- 829 rabbit height: 63-68 px (ears up) -> 65 px -> 0.43 m. Conf medium.
- 830 rabbit length: 67-82 px (stretched during hops) -> 70 px -> 0.46 m. Conf medium-low.
