# simulation_0056 – notes

Scene: static Blender camera, 2048x2048, 62 frames at 30 fps. Objects: orange Kia Stinger and green Mercedes 300SL coming toward the camera on the road,
a human walking away on the sidewalk, a white fire hydrant, and two identical lantern streetlights (near/left x~800, far/right x~855).

## Camera
- The road and building lines meet at a vanishing point (VP) of about (882,1005), so the horizon is about 20 px above the image centre. Roll is about 1.4 deg (horizon slope -0.024).
- depth_info is the Euclidean range to the bbox centre (mid-height). Check: the two identical lamps give the same height with mid-origin (ratio 0.996). With base-origin they would differ by 7%.
- Camera height x f is about 3400 px*m (from the lamps; holds for any f). The sidewalk is the ground plane for the lamps, hydrant and human. The road is slightly lower.
- Focal length (main uncertainty). Independent routes:
  * Hydrant base flange ellipse (bottom arc and extremes fitted by projecting a horizontal circle): best f 1550-1600. f=1800 fits clearly worse. Holds under other horizon, roll and principal-point choices.
  * Hydrant cap top ellipse aspect (flat top): about 1600.
  * Hydrant vs lamp camera-height agreement (ground plane with flange-derived base): about 1625.
  * Sidewalk slab: 1.935 m long (does not depend on f). It is exactly 2:1 at f about 1585.
  * Human (ground-level root, stance-heel analysis): about 1500-1600.
  * Green car front-offset vs width proportions: about 1650.
  * Real-world object sizes would suggest about 1750, but the scene may be scaled.
  -> I used f = 1610 (HFOV about 65 deg). Estimated uncertainty about ±4%. All size answers scale roughly as 1/f.

## Answers (f=1610)
- 1227 hydrant height: top-plane centre y=1393.5, ground centre from the flange fit y=1772, range 4.721 to the bbox centre -> 1.045 m (1.05@1600, 1.035@1630). Medium confidence.
- 1228 streetlight height: far lamp (finial 704.4, base 1265) 4.56 m; near lamp (237.5 / about 1659, base hidden behind the hydrant) 4.54 m -> 4.55 m. Medium confidence.
- 1229 green car average speed 0-1 s: 3D model of the fog-lamp pair at t=0 and t=1 plus the ranges, moving parallel to the road. Displacement 12.08 m -> 12.08 m/s. Weak dependence on f (12.16@1550, 11.93@1750). High confidence.
- 1230 orange car width: mirror-tip pixels at t=0, 0.5 and 1 s plus the ranges, along the car's own motion VP (899,1005). Mirrors are 0.70 m ahead of the centre. Mirror-to-mirror 2.28 m. The front-fender body width is about 1.95 m. Medium confidence (also assumes the AABB includes the mirrors).
- 1231 green car width: from the fog-lamp spacing (1.64 m), the headlight-span ratio (about 1.18x) and left/right silhouette extents -> about 2.03 m. Lower confidence (±5%).
- 1232 distance between the streetlights: |r1*u1 - r2*u2| with the mid-height rays = 7.98 m. Almost independent of f. High confidence.
