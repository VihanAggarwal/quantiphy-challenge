# Lab audit, family 0018 (captured_0018, 0018s, 0018x; one event, one label set)

Scripts: `scripts/common.py`, `scripts/measure_box.py`, `scripts/track_small.py`, `scripts/measure_all.py`.
Images: `montage_{o,s,x}.png`, `montage_drop.png`, `box_fall_tiles.png`, `right_fall_tiles.png`,
`grid_box_{o,x}_f10.png`, `grid_boxland.png`, `grid_lfeet.png`, `grid_lshoe_avg.png`, `grid_tennisland.png`,
`ball_bounce.png`, `crop_*.png`, `ref_0062_*.png`, `ref_0020_*.png`.

## Scene
49 frames at 24 fps (2.04 s), 1280x720. The o, s and x renders have identical geometry (edge correlation gives a 0,0 shift).
Left person = far person (3.130 m); right person = near person (2.002 m), feet cut by the bottom edge.
The left person holds a white printed box (the same prop as the 0062 "white box", with a red end face and a black logo) and the soccer ball.
The right person holds the tennis ball (on her extended arm) and the yellow pineapple toy (in her near hand).
The right person releases at about frame 27 and the left person at about frame 30. The pineapple and tennis ball land at about frame 36
and bounce. The soccer ball lands at frames 39-40 and rebounds (in the air at frame 48). The box lands on its end
at frames 41-43, topples, and lies flat at frames 47-48.

## Camera / depth convention check (independent of the stated depths)
The floor height comes from the tennis ball (6.7 cm prior from other clips). Its width is 20 px, so z = 2.38 m at floor contact (bottom v = 614, frame 36),
which gives h = 0.851 m (zero pitch; verticals in the room are vertical). The floor model then predicts:
- left feet (v 572): z 2.854. The stated far-person range 3.13 at the torso gives z 2.930 (range reading, +2.6%), against 3.13 for the z reading (+9.7%).
- soccer ball contact (v 575): z 2.814. The stated 2.80 gives a centre z of 2.75-2.84.
So the "range" convention and f = 711 hold here.

## Time base (rows at 3.0 s and 3.4 s)
The clip ends at 2.04 s, and the earlier dead-end note (PROBES.md) found the video runs in real time (g ~ 8.9 in video time).
12 questions x 3 renders ask for t = 3.0 s (distances between objects) and t = 3.4 s (velocities). The offset of the trimmed
window is unknown. If the window ends at the drop, the objects are still held at 3.0 s and falling at 3.4 s.
If it starts at 0, they are on the floor or bouncing. The two scenarios give different values for every
row, and neither can be measured. Not touched. This includes all speed rows, per the brief.

## Static rows (current answers; my measurements)
| row | current o/s/x | measurement | verdict |
|---|---|---|---|
| left person height | 168/168/168 | 404 px (173-577): 166.5 (range z 2.93), 162.2 (floor z 2.85), 177.9 (if z reading) | ok |
| right person height | 164/164/164 | top 102, floor model: 150-153 (range), 158-166 (z reading); leaning, feet cut | ok (within ~8%; not >=15%) |
| two people distance | 230/230/229 | 226.7 (stated ranges, torso centres), 212 (feet on floor model), 242 (z reading) | ok |
| box length | 21/21/21 | 52.5 px: 19.9 (floor z 2.69), 20.0 (ball range), 20.4 (feet h), 20.7 (ball surface) | ok (~5%) |
| box width | 8/**11**/9 | 20 px (470.2-490.0, both renders): 7.56 / 7.62 / 7.77 / 7.87; aspect 0.381 x 21 = 8.0; z-reading upper bound 8.3 | o ok, **s wrong**, x borderline |
| soccer ball diameter | 18.36/18.36/18.54 | 45 px: 17.4 (centre range), 18.0 (surface range), 18.0 (floor-contact z) | ok |
| tennis ball diameter | 6.7 (fact) | 20-21 px at z 2.3-2.4, consistent | ok |
| yellow toy height | 15.89/17.16/16.41 | 55 px; depth between torso and tennis-ball hand (in front of extended arm): 15.1-15.9 (z 1.95-2.05), full bracket 13.9-18.0 | ok |
| left shoe length | 22/22/22 | near shoe heel(348,571)-toe(400,577): 24.9-25.6 with floor plane, 20.7-21.2 if parallel to image; depends on a 6 px dv | ok (cannot exclude 22) |

## Fix
Box width, 0018s (qid 2316): 11 -> 7.8.
- Route 1: the held box occludes the ball-holding forearm, so it is no farther than the ball (stated range 2.80, centre-or-surface).
  With z 2.71-2.80 and 20 px, the width is 7.6-7.9 cm.
- Route 2: the box lands on its end at v 585. The floor model, calibrated by the tennis ball's known size, gives z 2.69 and 7.56 cm.
  Calibrated by the left person's stated range instead, it gives 7.77 cm.
- Route 3: the pixel aspect ratio (0.381) times the current length (21) gives 8.0 cm.
  Even the most generous depth (the far person's 3.13 taken as z) gives only 8.3.
- The current value is a raw:direct VLM guess on the s render. The three renders, which share one label, got 8 / 11 / 9.
  An 11 cm visible face would need z ~ 3.9 m, behind the person.
- The visible face is the printed main face (ECO print and black logo, the same face that is the top face in 0062), and the cross-section is close to square (0062 end face), so no hidden 11 cm side exists.
0018x (qid 2335, 9) is 13-15% above 7.8, at the edge of the 15% rule. It is not proposed as a fix. If the family is harmonised to
one label, 7.8 is the value. 0018 (8) is fine.
