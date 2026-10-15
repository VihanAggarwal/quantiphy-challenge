# simulation_0021 — notes

Scene: fixed camera looking squarely at a white brick wall (no yaw or roll; window rows are identical left and right). The camera is pitched UP by about 3.9 deg: vertical edges converge upward, with the vertical vanishing point about 22150 px above the image centre (fitted on 5 long pilaster edges). A person (1.87 m) walks left to right behind a fire hydrant (x~93) and a streetlight (x~189). 89 frames at 30 fps, 1080x1080.

## Measurements
- Median background, then the person mask from frame differencing. Subpixel tracks of head and torso edges (work/vel.csv, work/torso.csv).
- Person: head top at row 650 (mid-stance), sole at about row 866, so H_px is about 216. The sole row stays constant across the clip, so the person walks parallel to the wall.
- Hydrant: top of the cap dome at row 754.3. Front-bottom of the base flange at 890.5, half-width 30.5 px.
- Streetlight: top of the finial at row 327.5 (x 196.5). Front-bottom of the base at 891.5, half-width 27 px. The finial-to-base lean matches the vertical vanishing point.

## Depth convention
- The given distances are Euclidean range, not optical-axis Z. With base origins, the range ratio of hydrant to streetlight (1.0195) matches the ground-row geometry (1.021). The Z convention would predict about 1.006.
- With base origins, the hydrant and streetlight bases come out at the same height (within 4 mm). With centre origins they would be 3 cm apart. So both origins are at the base.
- The person's pelvis range together with the static ranges suggests the person's feet sit about 4-5 cm below the plane of the static bases (sunk model). The joint fit includes this offset e.

## Camera (joint least-squares fit: person ranges at t=0 and 1, pixel rows, static ranges, vertical vanishing point)
- f is about 1512-1529 px (HFOV about 39 deg), pitch about 3.9 deg, camera about 1.85-1.88 m above the static base plane.
- Pelvis scale k = z/f is about 0.0086-0.0087 m/px.

## Answers
- 1096 speed at 1.0 s: the pelvis moves almost purely laterally (Y constant). The average over 0-1 s from the depth pair and the pixel track is about 1.68 px/frame, or 0.43-0.44 m/s. Frame 30 is just after mid-stance, where the trunk's local velocity is about 1.45-1.5 px/frame (0.38-0.39 m/s). The head reads about 1.85 px/frame. The person also speeds up later in the clip (2.5 px/frame by frame 85). Answer 0.40 m/s. Confidence: medium (true value probably 0.36-0.47).
- 1097 hydrant height: back-projected from the base centre (placed from its range) to the dome top. 1.006-1.018 m across fits; without the sink term it would be 1.03-1.04. Answer 1.01 m. Confidence: medium-high.
- 1098 streetlight height: same method, 4.34-4.41 m (4.43-4.49 without the sink term). Answer 4.38 m. Confidence: medium-high.
