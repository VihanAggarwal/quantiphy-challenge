# simulation_0247 (V2MS, 2D planar, fps 30, 75 frames)
Scene: fantasy deer (horns, tail) walking right in profile; rabbit hopping right in front of it. Static camera, motion purely horizontal in image.
Scale: deer pixel speed by chained template matching of 4 body patches (torso/neck/chest/rump, gaps 1/3/6):
590-612 px over 74 frames -> mean 8.13 px/frame = 243.9 px/s. Prior 1.277 m/s -> 0.005236 m/px.
- Q1630 rabbit avg speed: HSV saturation mask centroid 969.8 -> 1542.3 px over 74 frames = 232.1 px/s -> 1.215 m/s;
  rabbit slightly nearer camera than deer midline (-~1.5%) -> 1.20 m/s. Confidence medium-high.
- Q1628 rabbit length: horizontal extent incl. pale face ~81 px (frames 0 and 74) -> 0.424 m -> 0.42. Confidence medium.
- Q1629 deer length: tail tuft to face-plate extent 544/570/595/606 px (frames 0/36/54/74), ~575 px -> 3.0 m
  (without tail ~440 px = 2.3 m; chose AABB including tail). Confidence low-medium.
