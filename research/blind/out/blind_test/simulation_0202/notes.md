# simulation_0202 — magnifying glass dropped onto a desk (Blender, 24 fps, 2124x1080, 30 frames)

## Camera / scale
- Glass falls from rest at frame 0 (top of frame), lands between frames 10 and 11, bounces, and is still by about frame 23.
- Tracked the handle-axis centre in each frame (background subtraction; masks checked on overlays). The per-frame
  displacements fit s_k = g(k^2+0.1k)/1152 (Bullet semi-implicit Euler with 10 substeps) with rms 0.07 px.
  B/A of about 0.10 was measured, not assumed. A pure 0.5 g t^2 model fits worse (rms 0.7 px).
- Focal length from the fall (g=9.8, range 4.2401 m at t=0): f = 2664-2678 px, depending on pitch. Orthogonal desk
  vanishing points give f of about 2659. Adopted f = 2668 (HFOV of about 43 deg; a 45 mm lens on a 36 mm sensor would be 2655).
- Pitch: horizon from desk VP_B (-462,-102), the vertical VP from desk legs (y of about 11800), the chord between the
  t=0 and t=0.5 glass positions, and the right angle of the desk corners all agree on theta = 13.4-13.55 deg. Roll is about 0.
- Depth convention: range (Euclidean) is consistent. Under Z, the two desk corners would differ in height by 10 cm.
- Desk plane is 1.262 m below the camera (from the near and far-right corner depths, which agree to within 1.4 cm).
- Room back wall / floor line is parallel to the desk front, so world axes are probably aligned with the desk.

## Sizes
- Table: top-surface corners N(699,876.5), FR(1985,638), BL(470,684). L = 2.45 (direct from depths) / 2.42 (on-plane) -> 2.44.
  W = 1.03 (on-plane, theta 13.45) -> 1.035. Confidence: L high, W medium-high.
- Typewriter: base plate corners FL(1003,757), FR(1158,706), BL(863,713) projected onto the desk plane give 0.36 x 0.32 m
  (right angle 88 deg), rotated 18 deg relative to the desk axes. The carriage top is about 0.185 m above the desk
  (excluding the handwritten letter in it, which would make it about 0.31).
  World AABB (desk-aligned) is about 0.455 x 0.43; local dimensions are about 0.37 x 0.33.
  Answers hedged toward the AABB: length 0.43, width 0.41, height 0.19. Confidence: medium (AABB vs local, and whether the paper is included).
- Paper next to the glass (left of the resting glass, under the right side of the typewriter): front edge 0.196 m along
  desk x, side edge 0.31 m along desk depth. About A4 (0.21 x 0.297), which supports the calibration.
  Width = short side, about 0.21. Confidence: medium (if width means the desk-depth axis, it would be about 0.31).

## Speeds (backward difference, |p(k)-p(k-1)|*24)
- Model: s_k = g(k^2+0.1k)/1152, so v_k = g(2k-0.9)/48. This is confirmed by direct 3D reconstruction of the pixel track
  (raw: 1.044, 2.272, 3.087).
- t=0.125 (k=3): 1.042; t=0.25 (k=6): 2.268; t=0.333 (k=8): 3.084. Confidence: high.
