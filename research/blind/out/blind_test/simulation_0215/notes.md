# simulation_0215 (top-down Blender living room, cat walks left->right)
Scale: cat tracked (dark-pixel blob, head edge + centroid) 10.98 px/frame over 44 frames -> 263.6 px/s;
prior 0.94 m/s -> 0.003566 m/px at cat height.
Perspective: top-down camera at principal point (960,540) (wall corners radial). Camera height H estimated ~10-13 m
(wall visible to >=0.23H at frame edge, lamp bulb parallax, mirror top/bottom width ratio 1.22 consistent); applied
scale correction s(h)=s_cat*(H-h)/(H-0.1) with H=12 and guessed object heights (bench .45, stand .5, vase .65,
lampshade .9, sofa .5, carpet 0). Corrections are only 2-7%.
Pixel extents (frame 0): cat 197 (tail straight), bench 287x114, TV stand 442x123 (right end under lampshade, ~uncertain),
lampshade 150, vase 72.5, mirror bottom edge 160 / top edge 195 (both give ~0.575 m), carpet 477 (vertical diameter),
sofa 886x477.
Confidence: medium-high for carpet/bench/lamp/vase/mirror; medium for stand length (occluded end), cat (tail pose), sofa.
