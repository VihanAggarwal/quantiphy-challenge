# simulation_0118 - toy car on table (top-down Blender view, 1080x1080, 121 frames @24 fps)

## Scale
- Camera looks straight down; disc images as a circle (258.6 x 258.9 px), so no tilt. Toy car moves along image +x at constant speed.
- Template matching of the car (3 different reference frames) gives a linear track with 2.6143 px/frame (rms 0.13 px).
  The body-end edges (saturation half-max, frames 10-120) move at 2.6167 / 2.6155 px/frame -> v = 2.615 px/frame = 62.76 px/s.
- Prior 0.05 m/s -> s = 7.967e-4 m/px at the car's height. Car apparent length does not change as it moves from x_rel=-380 to -70 px,
  so the front face never shows: narrow FOV / large camera distance. The car-to-table height correction is under 0.5%, so I used
  s_table ~ 7.975e-4 m/px.

## Measurements
- Displacement (246): 313.0 px between first and last frames -> 0.249 m. Constant speed for 5.0 s -> 0.25 m.
- Car length (247): body 126.4 +- 0.6 px (saturation edges, 22 frames, checked on a zoomed overlay) -> 0.1007 m.
- Disc (248): ellipse fit to the outer rim, diameter 258.8 px -> 0.2064 m.
- Book (249): an exact rectangle rotated 4.35 deg in the image, 214.9 x 154.0 px. Its image-axis AABB is 226.1 x 169.7 px.
  Length is 0.1714 m from the sides or 0.1803 m from the AABB. I answered between them (0.176), within about 3% of either.
- Table (250, 251): edges fitted to a parallelogram, sides 867.8 x 665.8 px, rotated ~6.2 deg, with a 0.9 deg shear (that suggests a
  rotated mesh with non-uniform object scale, so obj.dimensions = world AABB if the object rotation is 0).
  Image-axis AABB is 929.2 x 764.0 px. World axes = image axes, because the car is aligned with and moves along the image x axis.
  - Length: 0.741 m (AABB) / 0.692 m (sides). Answered 0.72, within 4% of both.
  - Width: 0.609 m (AABB) / 0.531 m (sides). Answered 0.59, leaning toward the AABB convention.

## Confidence
- 246: high. 247: high. 248: high (+-2%). 249: medium-high (depends on the convention, hedged). 250: medium-high (hedged).
  251: medium (the AABB and side conventions differ by 15%).
