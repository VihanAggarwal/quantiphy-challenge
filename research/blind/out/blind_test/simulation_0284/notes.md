# simulation_0284 (V2SS, 2D top-down view, plane flying right-to-left)
Method: frame-to-frame template chain tracking (subpixel) of the plane: 34.45 px/frame, constant (34.3-34.55) over frames 1-56; no vertical drift.
Frames 0 and 1 are duplicates (ignored). Dataset fps 25.
Scale: 22.16 m/s / 25 = 0.8864 m/frame -> 0.02573 m/px.
Extents at frame 25 (plane near image centre), from intensity edge profiles:
- length (x): nose pod tips x=1100.5 to tail pipe x=1667 -> 566.5 px -> 14.58 m
- width (y): top winglet edge y=368.5 to bottom winglet edge y=1089 -> 720.5 px -> 18.54 m
  (winglets project outward identically at left/centre/right positions -> weak perspective, real lateral extent; included)
- displacement 0.5-1.0 s: constant speed -> 0.5*22.16 = 11.08 m (pixel track confirms constant speed)
Confidence: displacement high; length medium-high; width medium (winglet inclusion adds ~ +7% vs rim-only 693 px -> 17.8 m).
