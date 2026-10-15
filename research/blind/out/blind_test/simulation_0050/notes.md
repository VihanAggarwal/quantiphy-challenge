# simulation_0050 notes

## Camera
- 1920x766, 33 fps, static camera. f was found from three orthogonal vanishing points:
  street direction VP1 (-2717,572) from 49 facade/curb lines, vertical VP (638,-24500) from 72 lines, and the perpendicular VP3 (1897,510) from booth-side and corner lines.
  Pairwise f = 1850 / 1861 / 1876. The orthocentre lands at (961,386), which matches a centred principal point.
  I used f = 1866.7 px (35 mm lens on a 36 mm sensor). Roll is 0.74 deg and pitch is 4.3 deg up.
- Bike depth_info fits the range (Euclidean) convention: both ranges give the same camera height above the road, 1.060 and 1.059 m.
  The Z convention gives a 3.6% mismatch.
  Bike origin is at the wheel-hub midpoint, with an overall scale factor of 1.0037, so camera height above the road is about 1.0635 m.
- Curb height is about 0.12 m from the image. Camera height above the sidewalk is 0.943 m. This matches the walker's prior speed of 1.236 m/s: the torso track gives a perpendicular distance of 12.43 m and the feet on the sidewalk give 12.29 m.
- The human's depth_info (15.87 -> 16.67) does not match the body. It would put the feet below road level.
  It is consistent with an origin about 6.7 m ahead of the body along the path, at the same perpendicular distance (12.33 m).
  So I used the body position from the ground plane and the prior for human sizes.

## Answers
- 1202 human height: 3D head-top to sole in the walker's plane. 1.78-1.80 at mid-stance, 1.72 at double support. Answer 1.78 (medium).
- 1203 booth height: bottom 641.2 to roof top 295.5 at the front-right corner, at Z=16.3. Gives 3.04 m (medium; the booth is large for its kind but the geometry is consistent).
- 1204 booth width: front face along the street is 1.22 (body) to 1.25 (plinth). Side depth is 1.10-1.17. Answer 1.23 (medium-low: axis ambiguity).
- 1205 pillars: near door = grey arched door (right), far door = green door.
  Urn stair pillar to green stair right post, centre to centre: 3.47 m. Door pilasters: 3.39-3.49 m for a facade at 14.0-14.4 m. Answer 3.45 (low-medium).
- 1206 bike length: front tyre to rear tyre or fender along the street, from per-frame silhouette extremes on the bike plane (d=10.68 m). Median 1.66, plus fender. Answer 1.67 (medium-high).
- 1207 bike average speed from 1 to 2 s: hub displacement 4.86-4.87, depth-based 4.84, linear fits 4.82-4.89. Answer 4.86 (high).
- 1208 bike height: handlebar top is 1.02-1.04 m above the road, near camera height. Answer 1.03 (medium).
- 1209 wheel diameter: outer tyre, from the vertical extent at t=1 and t=2 plus 3D circle fits. Range 0.64-0.66. Answer 0.645 (medium-high).
- 1210 first step riser of the grey (nearer) house: 25 px at Z=12.2, about 0.164-0.166 m. The green house gives 0.167. Answer 0.165 (high).
