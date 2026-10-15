# simulation_0137 notes

Scene: static camera, small gable-roof cabin centred in the frame, a bird flies left to right in an arc above it
(enters at the left edge around frame 1, apex near frame 64, still visible at frame 99). The prior is the bird's speed, 9.146 m/s.

## Tracking
- Median-background subtraction over all 100 frames, with the largest blob above y=880 taken as the bird (track.py writes track.npy).
- Pixel speed is about 19.75 px/frame (1185 px/s) and nearly constant: about 19.9 in the low part of the path and 19.6 near the top.
- After correcting for the camera geometry (below), the world speed is constant to within about 1%, so the bird flies at a
  constant speed in a vertical plane. Scale at the bird's mean row is about 0.00772 m/px.

## Camera geometry (lines.py, vlines.py, model.py)
- Vertical edges (walls, door) converge upward to a vanishing point about 19,400 px above the principal point, so the camera
  is pitched up (f*cot(pitch) is about 19,400). Horizontal lines slope about -0.005, which is a roll of about 0.29 deg.
- The ridge is shorter than the eave line (773 px vs 848 px), and the shingle period runs from 47 px at the top to about
  51 px at the bottom, so this is real perspective on a gable roof: the ridge (house centre plane) is about 9.7% deeper
  than the eave front.
- f cannot be pinned down exactly. A camera height above the house base of 1-2.5 m gives f of about 1400-2400 px
  (roof pitch 44-55 deg). The answers barely depend on f: about 1% for L and 3% for H.

## Main ambiguity: which depth plane the bird is in
- A: bird in the house's central plane (y=0, the ridge plane). L = 5.89 m, H = 3.33-3.37 m, gap to ridge = 3.10 m.
- B: bird in the eave/front plane. L = 6.41 m, H = 3.62-3.66 m, gap to ridge = 2.92-2.96 m.
- A is favoured (natural Blender setup). The final values sit between A and B, leaning toward A, so they stay within
  about 5% of both.

## Answers
- 331 path length: constant speed x clip duration = 9.146 x 99/60 = 15.09 m (100/60 would give 15.24). Answer 15.1. Confidence high.
- 332 house length (x-extent of the bounding box, including roof overhang): A 5.89 / B 6.41. Answer 6.1. Confidence medium.
- 333 house height (foundation bottom at y=983 to ridge top at y=522): A about 3.35 / B about 3.64. Answer 3.47. Confidence medium.
  Some of the house may be hidden below the grass.
- 334 bird-to-roof distance at 1 s: the bird is at (993, 126), directly above the ridge centre at y=522; the vertical gap
  to the ridge top is 3.10 m (A) or 2.95 m (B). Measured to the centre of the roof's bounding box instead, it would be
  about 3.7 m. Answer 3.2. Confidence medium-low.
