# simulation_0069 — notes

Scene: top-down (nadir) Blender view of an intersection, 2160x1080, 24 fps, 72 frames. White van drives up the vertical road from rest.
Pedestrian walks right on the lower-right sidewalk. Prior: van acceleration = 4 m/s^2.

## Camera / scale
- Principal point (1079.3, 540.2), from the radial lean of 8 identical lamp posts. Lean ratio 0.059 is the same for all of them, so the camera looks straight down with no tilt.
- Tracked van features with sub-pixel accuracy (column profiles and template matching). Each was fit with a constant-acceleration model (residual rms ~0.08 px):
  roof front edge 165.0 px/s^2, roof rear edge 164.98, side-window template 164.2, windshield base 163.16, hood front edge 162.47, ground shadow halo ~160-162.
  Scale at roof height: s_r = 4/165.0 = 0.024242 m/px. Each feature's own acceleration gives the scale at that feature's height.
- Perspective depth: (z_roof - z)/(H - z_roof) is 0.0156 for the hood edge and 0.0113 for the windshield. The windshield-vs-body centre offset and the shadow-halo acceleration ratio fit too. Together they give H - z_roof of about 60 m (my range 40-100). Height corrections are about 1-2%.

## Answers
- Q38, pedestrian speed at 1.0 s: the white-torso centroid moves 49.2 px/s, steady from frame 2 to 72 (local fits 48.8-49.4). Scale at torso height (~1.35 m) is about 0.02446 m/px, giving **1.20 m/s**. Confidence: high, about ±3%. Gait-phase jitter in the GT backward difference cannot be predicted.
- Q39, van width: the body silhouette runs from 788.3 to 875.0 px (86.7 px), widest at z ~0.8 m. That is consistent with the windshield centreline offset, and gives a body width of 2.14 m.
  Mirror tips at about 780 and 878.5 px (z ~1.2 m) give a width of 2.40-2.45 m with mirrors.
  It is unknown whether the GT bounding box includes the mirrors, so I answered between the two: **2.30 m**. Confidence: medium.
- Q40, van length: bumper-to-bumper. Front bumper edge was measured near the image centre in frames 36-51 and rear bumper edge in frames 52-71, converted to world positions with the bumper-height scale. The car's displacement between frames comes from the roof-edge track.
  Outer half-level edges give 6.14 m; dark-band centres give 5.97 m. The result hardly depends on H. Answer: **6.08 m**. Confidence: medium-high.
