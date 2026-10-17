# Audit sim2_11: family simulation_0233 (0231, 0232, 0233, 0233_segmented)

Classroom scene. The prior in all clips is "speed of the black cat = 0.714 m/s".
- 0231 and 0232 come from the same front camera (wall-floor line at y=952, ceiling line at y=171.5). The camera is level, with the horizon at y≈541. 0231 shows the chalkboard and 0232 shows a bare wall. The paper airplane follows the same path in both clips; I tracked it, and the left edges match to within 3 px frame by frame.
- 0233 and its segmented twin come from a camera looking straight down. The principal point is at about (960,540): the table legs point radially toward it. The cat walks along +x at row y≈530.
- The cat animation is synchronised across all clips. The nose shows the same jump at frames 10-11 and the same stall at frames 12-13 in both views.

## Scales (my own measurements)
- Front cat: the dark-mask centroid and edges move 8.85-8.96 px/frame (0231 and 0232). That gives 0.00334-0.00336 m/px at the cat's depth. The paws are at row 743.
- Front geometry, without using the focal length: table-top front edge y=763 and front-leg floor contact y=1027 give (Hc-Ht)/Hc = 0.457. The cat gives Hc-Ht = 0.680 m. So Hc = 1.49 m and Ht = 0.81 m.
  - Wall scale = Hc/411 = 0.00362 m/px. The agents used 0.00345-0.00348; mine is about 4% higher.
  - Table front-edge scale = 0.00306.
  - Chair back-leg scale (floor y≈1005) = 0.0032.
- Top view: the nose moves 13.32-13.35 px/frame, so the scale at the nose plane (about 0.24 m above the table) is 0.002232 m/px. I found the camera distance D above the table three ways:
  - The table legs show a radial ratio of 0.866 together with the leg inset seen in the front view (3 cm). That gives D≈5.2 m.
  - The chalkboard's top and bottom edges in the top view (y=60 and y=212), with their front-view heights (2.33 and 0.78 m), give Zfloor≈5.64 m, so D≈4.8 m.
  - The tail tip moves faster than the nose (14.0 vs 13.33 px/frame), which fits D≈5.
  - So f_top≈2060-2220 px.

## Row table (all rows are scored; none is a stated fact or an earlier audit fix)
| qid | clip | quantity | current | quick check (mine) | diff | verdict |
|---|---|---|---|---|---|---|
| 736 | 0231 | chalkboard height | 1.52 | 438 px x 0.00362 = 1.59 | +4% | ok |
| 737 | 0231 | chair width | 0.48 | backrest 150 px x 0.00324 = 0.486 | +1% | ok |
| 738 | 0231 | table length | 2.07 | 700 px x 0.00306 = 2.14 | +3% | ok |
| 739 | 0231 | ceiling height | 2.71 | 780.5 px x 0.00362 = 2.83 | +4% | ok |
| 740 | 0231 | plane speed t=1 | 5.55 | 69-71 px/frame, fitted path, 5.55-5.60 (cat-plane depth assumed) | 0-1% | ok |
| 741 | 0231 | plane acc t=1 | 2.6 | speed falling, magnitude 2.4-3.3 (noisy), sign negative | ~ | ok (see sign note) |
| 742 | 0231 | plane speed t=1.25 | 4.85 | 4.89-4.93 | +1% | ok |
| 743 | 0231 | plane acc t=1.25 | 2.8 | magnitude 2.2-3.1 | ~ | ok (see sign note) |
| 744 | 0231 | cat length | 0.615 | dark tail-to-nose 0.613; bbox with paws mean 0.653 (0.61-0.72 over the walk cycle) | 0 to +6% | ok |
| 745 | 0231 | cat height | 0.47 | 143 px x 0.00335 = 0.48 | +2% | ok |
| 746 | 0231 | chalkboard length | 5.0 | 1368 px x 0.00362 = 4.95 (agent file said 4.73) | -1% | ok |
| 747 | 0231 | clock diameter | 0.383 | 111-112 px x 0.00362 = 0.40 | +5% | ok |
| 748 | 0232 | chair width | 0.48 | same chair and camera, 0.486 | +1% | ok |
| 749 | 0232 | table length | 2.05 | 2.14 | +4% | ok |
| 750 | 0232 | ceiling height | 2.63 | 2.83 | +7% | ok |
| 751 | 0232 | plane speed t=1 | 5.41 | same path as 0231: 5.55-5.60 | +3% | ok |
| 752 | 0232 | plane acc t=1 | 2.9 | 2.4-3.3 | ~ | ok |
| 753 | 0232 | plane speed t=1.25 | 4.84 | 4.89-4.93 | +1% | ok |
| 754 | 0232 | plane acc t=1.25 | 2.7 | 2.2-3.1 | ~ | ok |
| 755 | 0232 | cat length | 0.62 | 0.604-0.65 | ~0 | ok |
| 756 | 0232 | cat height | 0.48 | 0.48 | 0 | ok |
| 757 | 0232 | clock diameter | 0.385 | 0.40 | +4% | ok |
| 758 | 0233 | cat length | 0.75 | perspective-corrected tail-to-nose 0.65-0.67; with paws about 0.68-0.70 | -7 to -13% | close to the threshold; no fix |
| 759 | 0233 | chair width | 0.50 | top view 0.476-0.488; front 0.486 | -3% | ok |
| 760 | 0233 | chair length (y) | 0.545 | top view 0.53 (D 4.8-5.2) | -3% | ok |
| 1966 | 0233_seg | cat length | 0.75 | same as 758 | -7 to -13% | close to the threshold; no fix |
| 1967 | 0233_seg | chair width | 0.446 | 0.48 | +8% | ok (the twin has 0.50) |
| 1968 | 0233_seg | chair length (y) | 0.462 | 0.53 | +14% | close to the threshold; one route only; no fix |

## Investigations
1. Cat length: top clip 0.75 vs front clips 0.615/0.62.
   - The front view shows the tail held almost upright. Its tip is about 0.475 m above the table and the nose about 0.24 m.
   - In the top view the raised tail tip is closer to the camera. It is pushed outward from the principal point, and the cat sits 400-900 px left of it.
   - Evidence: the tail tip moves faster than the nose in the image (13.98 vs 13.35 px/frame). The apparent length shrinks from 340 to 322 px as the cat approaches the image centre.
   - The 0233 agent took the whole nose-to-tail-tip pixel length (335 px) at the head-plane scale, so its length is inflated.
   - I projected the front-view 3-D silhouette into the top camera, for every synchronised frame, over D = 4.5-6 m. The top-clip cat's tail-to-nose x-extent comes out at 0.646-0.668. Its silhouette is about 5-9% longer than the front-view cat's (0.613). The same 6% excess appears in the nose-to-rump distance measured in frames of travel (18.2 vs 17.2 frames), which needs no camera-distance correction.
   - So the top clip looks slightly larger. It could be a real difference or a definitional bias in the masks.
   - Route A (front bbox) gives 0.61-0.65. Route B (top, corrected) gives 0.65-0.70 depending on whether paws are included. The current 0.75 is 15-22% above A but only 7-14% above B, so it does not clearly differ by 15% or more from both routes. **No fix.**
   - If the family is harmonised later, 0.67 is the value I would use for 758/1966.
2. Chair twins (759/760 vs 1967/1968): the twins should carry identical answers.
   - Width: both views give about 0.48. In the top view, the backrest's lower-left corner is the leftmost point and its upper-right corner the rightmost. 0.50 and 0.446 are both within 8%.
   - Length (y-extent): the backrest top edge (y=502, 0.865 m high, so Y=-0.088) to the front feet (y=703 on the floor). That gives 0.529-0.535 for D 4.8-5.2, and 0.47 if the camera were treated as orthographic. The segmented agent evidently used one scale for everything, which explains its 0.462.
   - I have only one route here (the front view cannot resolve the depth), and the error is under 15%. **No fix.** If harmonised, use 0.53 for 1968 (or the 0.545 already on 760).
3. Plane: depth is unknown and there is no shadow cue. The top clip does not show the plane. All four plane values assume the cat's depth plane, as the agents did. My pixel tracks reproduce their speeds to within 3%.
4. Sign convention, outside this audit's scope: the plane is slowing down at both 1 s and 1.25 s. If labels are signed "change of speed magnitude", they would be negative, about -2.6 and -2.8. Both agents answered positive magnitudes. I changed nothing here; this needs a project-wide decision.

## Fixes proposed
None. No scored row met all three conditions: two routes agreeing within 8%, the current answer at least 15% away, and a concrete reason it is wrong. Three rows come close: 758/1966 (0.75 → about 0.67) and 1968 (0.462 → about 0.53).
