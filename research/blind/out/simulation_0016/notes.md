# simulation_0016: notes

Scene: a top-down (nadir) Blender view of an atrium. The 1080x1080 render is padded into a 1920x1080 frame (x 420-1500). The scene has a central sculpture on a square pedestal, two 4-cushion benches (left and right), two side pedestals and one person walking toward +y at about 1.3 m/s.

## Camera
- Floor tile seams are equally spaced: rows every 131 px and columns every 140 px, with no perspective change across the frame. The image plane is therefore parallel to the floor (tilt < 0.3 deg).
- The nadir is about the image centre (960,540). Evidence: the vertical edges of the top pedestal converge there (scale ratio about 1.09), and the side faces of the two benches are symmetric (7 px each on the inner side).

## Scale (floor-plane px/m, k_floor)
- Head template track (long-term average) moves 4.89 px/frame. The gait period is 17 frames per step and 34 frames per stride.
- The head's shadow on the floor, matched across exactly one stride (34 frames), moves about 130.8 px while the head moves 165.5 px. That gives s = Z_floor/Z_head = 1.27. Floor-plane speed is 3.85 px/frame, so 1.3 m/s gives k_floor = 97.7 px/m.
- The stance-foot displacement per stride is 134-136 px. At 1.3 m/s x 34/33 s this gives k_floor = 100.8 (the animated feet may slide a little).
- Depth route: assume the bench and pedestal origins sit on the floor and use Euclidean distance. Then H = 9.967 m (the pedestal is at the nadir) and bench R = sqrt(d^2 - H^2) = 3.695 m / 3.579 m. Bench centres projected to the floor are at 368.6 px / 354.9 px, so k_floor = 99.8 / 99.2.
- Adopted k_floor = 99.0 px/m (spread about +-1.5%).
- Inconsistency: the person's distances (9.24 -> 9.14 m) fit neither Euclidean distance nor optical Z with plausible human proportions. They were not used for scale.

## Heights (from sun shadows; sun vector calibrated on the person's head shadow and checked against the bench shadow x-extent)
- Bench seat top: shadow edge offset 22.7 px, so h/H = 0.052 (about 0.52 m).
- Central pedestal top: shadow edge offset 30.5 px (y) gives h/H = 0.065; the right edge gives 0.078. Adopted 0.068 (about 0.68 m).

## Measurements (top-face outlines, px)
- Central pedestal outer square: x 881.5-1037.5 = 156, y 461.5-617 = 155.5.
- Bench seat: width 75 (left 533.5-608.5, right 1297.5-1371.5); length 235 (y 427.5-662.5). Both benches are identical.

## Answers (size = px * (1 - h/H) / k_floor)
- 1498, pedestal width: 156 * 0.932 / 99 = 1.469 m. Confidence: medium (k_floor +-2%, pedestal height +-1%).
- 1499, bench seat width: 75 * 0.948 / 99 = 0.718 m. Confidence: medium.
- 1500, bench seat length: 235 * 0.948 / 99 = 2.249 m. Confidence: medium.
