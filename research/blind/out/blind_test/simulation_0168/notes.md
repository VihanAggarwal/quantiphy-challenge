# simulation_0168 - notes

Scene: static Blender camera at a crossroads at night. Road A runs from far-right to near-left (VP at x=2647, y=540).
The bike, followed by the police VW T5 van, rides toward the camera in the far lane of road A. The bike crosses road B,
which runs parallel to the building's front facade (VP at about x=-3250).

## Camera
- Verticals are exactly vertical, so pitch is 0 and the horizon is at y=540.
- Focal length: the orthogonal vanishing points of road A and road B (and of the building's side and front facades)
  give f = 2665-2683 px. I used f = 2667 px (Blender 50 mm lens on a 36 mm sensor). The aspect ratios of the van rim
  ellipses also fit f of about 2667 and rule out about 3150.
- Depth convention: range (Euclidean distance). The optical-axis Z convention would need dZ = 2.33-2.54 m in 0.5 s,
  but the given value is 2.665 m.
- Camera height from the bike's speed (5.52 m/s, linear fit of the wheel-contact track over 8 frames) is
  h = 1.186 m. The depth values with the origin at the wheel midpoint give 1.180 m. I used h = 1.185 m.
  Every metric quantity scales linearly with h.

## Measurements
- Road B (crossed by the bike), curb face to curb face along road A: left-block corner e=10.96 m,
  building-side curb base e=19.95 m, so **8.99 m**. Confidence medium; the ground truth may define the edges differently.
- Road A (bike and van), curb to curb: far curb base c=-8.68, near curb face c=-1.98 (corrected for a curb height of
  about 0.086 m), so **6.70 m**. The outer edges of the painted edge lines are 6.27 m apart. Confidence medium.
- Bike wheel diameter: rim-centre and tire-bottom intensity profiles at frames 72 and 79 give 0.709-0.722 m,
  so **0.716 m**. Confidence medium-high.
- Bike length: weighted wheelbase 1.08 m plus wheel diameter 0.716 m gives **1.79 m**. The image extents at frame 79
  give 1.775 m. The basket does not reach past the front tire. Confidence medium.
- Van tire diameter: 8 wheel measurements (frames 48, 60, 70, 79, front and rear) range 0.698-0.726 m,
  median 0.719 m, so **0.72 m**. Confidence high.
- Van speed: the front-wheel ground track over frames 48-79 is linear at 6.858 m/s. The licence-plate template track
  over frames 13-75 is also linear (acceleration about 0), so the speed is constant. Scaled to the bike speed prior,
  this gives **6.87 m/s**. Confidence high.
- Van length: wheelbase 2.99 m (same as a real T5). Front overhang to the plate is 0.83 m (plate line fitted at
  c=-6.80; the far tire confirms the centreline). The rear body corner and bumper on the near side plane are
  0.4-0.55 m behind the rear axle. Total 4.2-4.45 m; answer **4.4 m**. A real T5 is 4.89 m. Confidence medium-low.
- Van width: solving for both mirror tips at frame 48 gives a width of 2.30 m including mirrors, at a mirror height
  of 1.38 m. The body width is about 1.85-1.90 m (tire faces +/-0.885 m from the centreline). The answer, **2.25 m**,
  leans toward the axis-aligned bounding box including mirrors. Confidence medium-low.
