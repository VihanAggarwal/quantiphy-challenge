# simulation_0017 independent re-measure: qid 1657 (width of the freestanding art display panel, segmented clip)

Scripts and crops are in rm1657/: track2.py (person track), calib.py, silh.py, paint.py and edges.py. The clip `simulation_0017_segmented` is upright (not rotated) and pixel-aligned with the upright original. The figures below were measured on the median background of the original clip (rm1657/frames/orig_bg.png). The segmented median was used for silhouettes.

## Which object, and what the depth means
- The segmented clip keeps two identical display panels, one on each side of the sculpture, at about u 293-404 and 664-783.
- Both panels are about 12 m away. Their base contact is at v~611-615, with the horizon at 540 and Hc~0.97.
- The walking person, whose pelvis Z is 4.66 m, passes IN FRONT of both panels: the left one at frames 40-48 and the right one at frames 85-100. This rules out a visible panel at the stated 4.223 m.
- The 4.223 m therefore has to belong to a different instance of the panel (for example the nearest one, outside the 62 deg FOV) or to an offset origin.
- The sibling clips 0015 and 0019 label their depth "nearest freestanding art display panel" (11.874 m and 11.042 m), and there it matches the visible panel. So the scene contains several copies of the same panel asset, and the width is the same for every copy.
- The current answer, 0.37, is what you get by using 4.223 m as the depth of the visible panel. That is wrong.

## Camera (own measurements)
- Head track over frames 4-100 is linear at 251.2 px/s (rms 1.8 px). The head top stays at y 368-376, so Z is constant and the person walks parallel to the image plane.
- Speed route: 1.3 m/s gives Z/f = 1.3/251.2 = 0.005175 m/px.
- Depth-ratio route: D0 = 5.424 and D1 = 4.886 as Euclidean range to the pelvis, with the pelvis 8-12 px behind the head, give f ~ 898-902 and Z = 4.655. This agrees with the speed route to within 0.5%.
- Camera height Hc:
  - Planted near foot (striped outer side visible) has its sole at a boundary of y = 732.0. That gives 192 px * 0.005175 * (4.555/4.655) = 0.973.
  - Head top at y 368 with person height 1.87 m (stated in sibling clips 0015/0019) gives 1.86 - 0.89 = 0.97.
  - Pedestal dark box front face is 250 px wide with its bottom at y 704. A width of 1.469-1.49 m (from clips 0016, 0015 and 0019) gives Hc = 0.958-0.977.
  - Adopted Hc = 0.97 +- 0.012.

## Panel geometry (right panel; the left one is its mirror, at X -3.30Hc vs +3.20Hc, Z 12.0Hc)
- The panels are yawed with their outer ends closer to the camera. Evidence:
  - The painting's pixel height grows 110.2 -> 114.3 px across the right panel and shrinks across the left one (4.7-6.5% dZ/Z per 100 px).
  - The base contact line slopes 610.7 -> 615.1.
  - The top line slopes 464 -> 461.
- Lower base plate (the widest part), in continuous pixel coordinates:
  - FL = (663.8, 610.7)
  - FR = (780.5, 615.1)
  - end face out to u = 783.0 (rows 608-611)
- Floor points use X = (u-540)Hc/(v-540) and Z = 900Hc/(v-540). Together with the end face this gives:
  - yaw = 27 deg
  - depth of the base end face D ~ 0.15 m
  - world-AABB X-extent = (1.451 + D sin(yaw)) Hc = 1.521 Hc = 1.475 m
  - local length = 1.632 Hc = 1.58 m. The span is 1.54-1.63 for a +-0.5 px contact error.
- Height check: top line at y 462.0 at u 725, frame-plane contact at 72.6 px below the horizon. That gives H = 2.074 Hc = 2.01 m, matching the sibling panel heights of 2.01 m (0019) and 2.04 m (0015).

## Routes
1. Ground plane plus Hc from the person and speed: AABB-X 1.475 m, local 1.58 m.
2. f- and Hc-free pixel ratio width/height = 0.733 (AABB) or 0.787 (local), times the sibling panel height of 2.01-2.04 m: AABB 1.47-1.50, local 1.58-1.61.
3. Cross-check: the original 0019 agent measured the same asset from a different camera with a 1.87 m person prior, and got AABB 1.48 and local 1.56-1.57.

## Answer
- 1657: **1.52 m**. This is a hedge between the world-AABB X-extent of a panel yawed ~27 deg (1.475) and the panel's own length (1.58). Both are within 4%.
- Confidence: medium. The values are solid if the label is the visible panel's asset. The open risk is that the label belongs to an unseen panel instance at 4.223 m with a different yaw (that only matters if the label is the world-AABB X-extent).
