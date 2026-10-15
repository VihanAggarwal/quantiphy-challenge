# simulation_0030 - eagle length (qid 1501)

Scene: static camera, 960x960, 75 frames at 24 fps. An eagle flies left to right across the sky at about y=270-295 px
and leaves the frame at about frame 38. The neon sign named in depth_info is not visible.

## Track
- Median-background subtraction plus a darkness mask give the eagle blob for frames 0-37 (work/track.py).
- Wing flapping shifts the centroid with a period of about 26 frames. I removed it with poly2 + sinusoid fits and with
  displacements taken one full period apart. Pixel speed is about 15.7 px/frame near frames 0-12 and about 15.1 later.
- Smoothed origin displacement from frame 0 to frame 12 (t=0 to 0.5 s) is about 184-189 px horizontally and about 4 px vertically.

## Scale (pinhole model with depth_info and the speed prior)
- Over 0.5 s at 12 m/s the chord is 6 m. The range changes by 25.328 - 24.899 = 0.429 m, so the lateral move is about 5.985 m.
- Solving for f gives f = 762 px with the range convention (HFOV 64 deg) or 795 px with the Z convention.
  Either way the scale at the bird is the same, about 0.0317-0.0319 m/px.
- Cross-check: a constant-speed arc model fitted to the whole track (depth constraint enforced) gives f = 741-772 px
  and Z/f = 0.0328 (frame 0), 0.0324 (frame 6) and 0.0323 (frame 12).
- Adopted scale: about 0.0322 m/px for frames 0-12 (about +/-2%).

## Size
- Taken as "length" = world AABB extent along the flight direction (beak to tail), which is about the image x-direction.
- Sub-pixel widths from column darkness profiles: frame 0 is 21.8 px (50% threshold), 23.2 px (30%) and 25.2 px (15%).
  Frames 6-7 (on axis) are 22-24 px. Frames 10-16 (wings down) are 19-22 px. The body line seen with the wings raised
  (frames 0 and 22-26) is about 21-22 px.
- Later frames get wider (26-33 px) because the wing depth extent projects into x off-axis (u*dZ/Z), so I did not use them.
- Adopted extent about 24 px x 0.0322 m/px = 0.77 m.
- The raised-wing height of about 31 px suggests a wingspan of about 2 m. That is plausible for an eagle, and the
  length is plausible too (0.7-1.0 m).

## Answer
- 1501: 0.77 m. Confidence is moderate. The scale is good to about 3%. The pixel extent is uncertain by about 10%
  (pose and threshold). The main risk is the definition: if "length" meant the largest AABB dimension (the wingspan),
  the answer would be about 2 m.
