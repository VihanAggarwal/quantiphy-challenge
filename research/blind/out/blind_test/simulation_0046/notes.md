# simulation_0046 - notes

Scene: static Blender camera, 1920x766 @33 fps. Blue bicycle and rider ride left on the street. A person walks left on the far sidewalk.
Background: photo lab with a telephone booth (left), green wooden house (centre) and stone house (right). The pink bicycle is static.

## Camera / scale
- Median background, then diff masks. The front tyre outer edge is fit with circle and ellipse fits on clean arcs (60-225 deg), half-max edges.
- Wheel diameter: D(t=1) ~ 98.9 px, D(t=2) ~ 93.85 px. This uses 1/D linear in time across the clean frames 36-44 and 54-70.
- f from wheel + range (Euclidean): 1892 / 1874, so f ~ 1883 px (about a 35 mm lens). The optical-Z convention would give f ~ 1923.
  The bike is consistent with both conventions. Sizes and bike speed are nearly independent of the convention.
- Vanishing points:
  - Street lines (curbs, cornices): VP1 ~ (-14750, ~335).
  - Near-sidewalk slab joints: VP2 ~ (1180+-15, 312-335). This gives tan(yaw) ~ 0.117.
  - Verticals: pitch ~1.3 deg.
  - VP1 x VP2 gives f ~ 1880-1900, consistent with the wheel route.
- With tan(yaw) = 0.117, f = 1883 and the Euclidean convention, the bike's 3D path from the ranges is exactly parallel to the street (dz_w = -0.016 m over 4.85 m).
- Ground model: horizon ~335 (312-358 tested).
  - Camera height above the street is 1.76 m, from the bike contact rows.
  - Curb face is 20.5 px, which gives c = 0.14 m. The far sidewalk sits 1.62 m below the camera.

## Answers
- 1190 bike speed 1-2 s: P(t) from the ranges and the hub-midpoint pixels. The displacement is 4.835-4.885 m and the motion is constant velocity (fit rms 7 mm). Answer 4.83 (allows ~1% for a possible pixel-aspect effect). High confidence.
- 1187 bike height: handlebar top (~449.5-451) to wheel bottom, scaled by the vertical wheel diameter, gives 0.974-0.984. Answer 0.985. Medium-high.
- 1188 bike length: front tyre to rear tyre/fender, about 238.5 px in frames 61-70. The wheel-ratio route gives 1.64 and the 3D route with yaw foreshortening gives 1.69. Answer 1.66. Medium.
- 1183 person height: 245 px at gait peaks.
  - From the ground plane (feet row 559.4 on the sidewalk), Z ~ 13.7, which gives 1.78 m.
  - The given human depth (14.77 / 15.18) is NOT consistent with the visible person. The given ranges increase 0.40 m/s, while pixel height and feet row show the person walking almost parallel to the street (dZ ~ 0.1-0.15 m/s). Euclidean visible ranges would actually decrease.
  - The given depth would give 1.84 (Euclidean) or 1.89 (optical Z).
  - Answer 1.80, a hedge. Medium.
- 1182 person speed at 1.0 s: the head/torso template track gives ~5.15 px/frame (4.9 at frame 33). The visible ground-plane geometry gives 1.22 m/s. Using the given depths: 1.29 (optical Z) and 1.33 (Euclidean). Answer 1.24. Medium.
- 1184/1185 telephone booth:
  - Roof top at y = 152.3. Bottom ~547, partly hidden by the pink bike; the result is insensitive to this.
  - Front plane z_w ~ 13.5 (on the sidewalk near the curb).
  - Height = (vb - vtop)/(vb - vh) x sidewalk camera height, giving 2.98-3.06. Answer 3.02.
  - Roof front width is 146 px (77-223), giving 1.15-1.26 (1.185 at vh 335). The body without the roof is 1.10. Answer 1.17. Medium.
- 1186 pillar distance: the doors are the green-house and stone-house doors. Pillar world x positions:
  - Green stair pillars: -1.68 and -0.12.
  - Stone stair pillars: 3.31 and 4.98.
  - The door pilasters line up with these.
  - In optical-axis depth the stone door is nearer (15.3 vs 15.9); in Euclidean range the green door is nearer (15.9 vs 16.4). Visually the stone house looks nearer: lower stair base and larger door.
  - If stone is near: stone-left to green-right = 3.42-3.47 m. If green is near: green-left to stone-right = 6.67 m.
  - Answer 3.6, hedged toward the smaller value because the relative-error scoring is asymmetric. Low-medium.
- 1189 first-step height:
  - Green house: riser 19.5-20.5 px at Z 14.8, giving 0.153-0.161.
  - Stone house: 19-19.8 px at Z 14.25, giving 0.144-0.150.
  - Answer 0.155, which covers both. Medium.
