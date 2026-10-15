# simulation_0205: magnifying glass dropped onto a pedestal desk (typewriter, revolver)

## Camera (fixed, 2124x1080, 24 fps, 30 frames)
- Vanishing points: desk long edges, short edges and vertical leg edges (Hough segments plus sub-pixel silhouette fits) fitted jointly (vpfit.py).
  This gives f ~ 2595-2642 px, tilt 13.2-13.5 deg down, roll ~0, desk yaw 29.6 deg relative to the camera.
- Free fall of the glass (track2.py, fitglass2.py): range 4.2401 m at t=0, g=9.8, tilt 13.4 deg. Fitting the vertical pixel track gives
  f = 2648 px with 0.13 px rms and release at t0 = -0.002 s, i.e. at rest at frame 0.
  Two independent routes agree within about 1%. Adopted f ~ 2625-2645 and tilt 13.4 deg.
- Depth convention: Euclidean range fits. The near corner (3.593 m) and the front-right corner (5.009 m), both taken as range, put the desk-top plane
  at the same height (h = 1.265-1.272 m below the camera). Optical-axis Z would make them disagree by 4.5%.
  The glass back-projected at t=0 and at t=0.5 shows a vertical drop of 1.07 m with less than 1 cm horizontal shift. That is consistent with free fall.
  "Far right" corner = the right-most (front-right) corner. The back-right corner would be at about 5.7 m.

## Desk (deskfit.py, lip.py, chord.py)
- Rectangle fitted to the back and right silhouettes and the front and left top-edge lines, then scaled with the corner ranges:
  top surface 2.43-2.48 m x 1.046-1.062 m. The fitted angle is 90.4 deg and opposite sides are equal.
- Moulded lip overhang beyond the top surface is about 1.6-2 cm per side (from the lip tips). The chord between the two depth-given corners is 2.45-2.50 m.
- Length ~2.47 m and width ~1.08 m, as AABB including the lip and assuming the desk is axis-aligned in the world.
  Caveat: if the desk is rotated 29.6 deg in the world, the world AABB would be about 2.69 x 2.16.

## Typewriter (tw3d*.py)
- Base-plate bottom corners back-projected onto the desk plane: 0.376 m (along the desk long axis) x 0.320 m (front-back).
  It is aligned with the desk, and the keyboard rows point to the desk vanishing point.
- The platen knobs, assuming left-right symmetry, span about 0.40 m. Length taken as ~0.39.
- Height: the paper-table top is at b ~0.64 by symmetry, giving z = 0.175-0.19 m. Taken as 0.188.

## Glass speeds (speed.py)
- Measured 3D backward-difference speeds at frames 3, 6 and 8: 1.047, 2.287, 3.088 m/s.
- Model g(t - dt/2) with Blender semi-implicit substeps (offset 0.019 s): 1.041, 2.266, 3.083. The exact model g(t - 1/48) gives 1.021, 2.246, 3.06.
- Answers: 1.04, 2.27, 3.08.

## Confidence
- Speeds: high (within 2%).
- Desk length and width: medium-high (about 2-3%, plus the axis-alignment assumption).
- Typewriter length and width: medium (5%).
- Typewriter height: medium (5-7%).
