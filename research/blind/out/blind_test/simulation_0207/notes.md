# simulation_0207 (A2MC, typewriter free fall onto desk, 24 fps, 2124x1080)
Scale: typewriter falls straight down at constant depth (in-air width constant at about 290 px). Template-tracked features fit a parabola:
paper-rest bars a=11.98 px/frame^2, centre badge 12.08, key centroid 12.43 (front, noisy). Origin a taken as 12.05, so m = 9.8/(12.05*576) = 1.412e-3 m/px at the typewriter depth.
Camera geometry: the table side edges (fitted per row, residual <1 px) meet at the horizon y=546.6 with VP x=1070, so the camera is level.
Table width in px W(y)=3.796*(y-546.6), so table length L = 3.796*h (h = camera height above the table top).
h comes from the typewriter landing row: front-bottom row 1022.5, with the footprint centre about D/2=0.175 m behind it, so the centre row is 546.6+450.8 and h=0.637 m.
f is about 2300 px (brass disc ellipse 2500, ashtray 2170, paper=A4 assumption 2240).
Answers:
- 546 table length = 3.796*0.637 = 2.42 m (medium confidence, +-3%)
- 547 typewriter length: in-air width 290 px at the front base edge, times m times Z_f/Z_c (0.946) = 0.388 (medium)
- 548 height: landed top/bottom rows and in-air silhouettes give 0.169-0.186, so 0.176 (medium-low)
- 549 paper width: AABB x is about 0.225 and y (depth) is about 0.30-0.32 (f-dependent). The naming is ambiguous, so I hedged at 0.27 (low)
- 550 letter under the gun: x-extent from world corners on the table plane = 0.270 (medium)
- 551-553 speeds = backward pixel diffs of the fitted parabola (release offset about 0.17 frame), converted via g: 1.09, 2.32, 3.13 m/s (high)
