# simulation_0214 notes
Top-down fixed camera over a living room, 1920x1080, 50 frames at 24 fps. Black cat walks right at a steady 10.96 px/frame
(centroid of dark mask, frames 0-49), so the prior 0.94 m/s gives 0.003573 m/px at the cat-silhouette plane (about 0.2 m above the floor).
Camera height H was estimated at about 10 m (f about 2740 px, HFOV about 39 deg):
- floor mirror: top edge 197 px vs bottom edge 163 px, so z_top = 0.173H, which fits a mirror about 1.7 m tall when H is about 10
- lamp-shade and vase top openings are shifted radially by 12 and 9 px (consistent with H around 9-11)
- TV stand shows about 15 px of front face (consistent with H around 8-10)
Scale at height h: s(h) = 0.003573*(10-h)/9.8.
Pixel extents: cat 192 px (tail included); bench 287x115 (h 0.45); TV stand 485 px (symmetric about the shelf legs, right end hidden under the lamp) x 110 px top face (h 0.5);
lamp shade 150 px (h about 0.75); mirror bottom 163 px (z 0); dog 322 px including head and tail (h 0.45);
carpet 478 px (vertical; the right side is hidden under the sofa); sofa 880x473 (h 0.4).
Dog speed: HSV saturation mask centroid with a linear fit over frames +-3..6 gives 12.7 px/frame at frame 24 and 10.6 at frame 36, using s(0.5).
Confidence: cat, bench and mirror high; carpet, sofa and dog length medium; TV stand length and lamp medium-low (occlusion and assumed heights); dog speeds medium.
