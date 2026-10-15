# simulation_0228 notes
Top-down static camera, 1920x1080, 50 frames @24 fps. Cat walks +x on paving; pink swim ring drifts +x in pool (accelerates then stops).
Scale: cat centroid (gray<40 mask) linear fit 5.456 px/frame = 130.9 px/s -> 1.041/130.9 = 0.00795 m/px (cat plane, ~ground).
Perspective: raised chair backrests show radial displacement ~3.7% relative to seats -> camera height large vs objects; seat/water plane corrections ~1-2%.
- 710 cat length incl tail: silhouette bbox mean 107.4 px (max 111), +~1.5 px antialias -> ~108.5 px -> 0.865 m (conf: medium-high)
- 711 chair width: seat x-extent 195 px for all 3 chairs (backrest top 202-205 px is perspective-magnified); /1.015 for seat height -> ~192 px -> 1.53 m (conf: medium; width = shorter horizontal dim, length ~335 px)
- 712 paving stone width: joint pitch 144.6 px (10 joints), minus ~3 px joint gap -> ~142 px -> 1.13 m (conf: medium; stones 145x263 / 145x525 px)
- 713 ring length: brightness mask (gray>50) bbox 143.5 x 133 px -> longest 143.5 px -> 1.14 m (conf: medium)
- 714 ring speed t=0.5 s (frame 12): quadratic fit of centroid, backward-diff-equivalent velocity 8.45 px/frame (raw backward 8.34) -> 202.8 px/s -> 1.62 m/s (conf: medium)
Scripts in work/.
