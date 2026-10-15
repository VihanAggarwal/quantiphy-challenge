# simulation_0054 — notes

Scene: top-down (nadir) perspective Blender camera over a 2-lane road, 1080x1080, 30 fps, frames 0-90 valid (91-99 black).
Orange car (left lane) and green classic roadster (right lane) both drive downward (front at bottom).
Prior: orange car acceleration = -2.86 m/s^2.

## Scale
- Orange car tracked by frame-to-frame NCC template matching of the whole car interior (frames 16-90):
  per-frame displacement decreases linearly (rms 0.027 px/frame) -> pixel acceleration -163.7 px/s^2
  (sub-windows/edges: -161..-165; colour-mask midpoint -164; centroid -162).
- s_car = 163.7/2.86 = 57.24 px/m at the car-top feature height (~1.05 m).
- Perspective check: the two lamp posts project as radial segments from the image centre (base flange -> lantern),
  radial ratio lantern/base = 1.19 for both lamps -> lantern height = 0.16*Zc; principal point = image centre.
  Edge-vs-template speed ratios of both cars (1.0-1.5%) are consistent with camera height Zc ~ 30 m (range 22-40).
  Height correction s(z) = s_car*(Zc-1.05)/(Zc-z) applied (1-3% effect).

## Measurements
- Green car speed: template matching 22.70 px/frame (constant speed frames 27-70; 22.71 at 59->60);
  white rear-bumper edge 22.48 px/frame. -> 681 px/s / s(0.85)=56.85 and 674 px/s / s(0.55)=56.27 -> 11.98 m/s.
- Orange length: colour-mask silhouette 289-292 px (slow frames) -> 291 px / s(0.6)=56.37 -> 5.16 m.
- Green length: aligned-average silhouette 530.5 -> 828 (chrome corners) = 297 px / s(0.5)=56.17 -> 5.29 m.
- Lamp distance: base flanges at (252.5,465) and (251.5,909.5) -> 444.5 px at sidewalk height (~0.15 m),
  s(0.15)=55.5 px/m -> 8.01 m (lantern-to-lantern 528 px / 1.19 gives the same).
- Orange width: body 107.5 px (1.90 m); mirror-to-mirror 124 px (2.17 m). AABB likely includes mirrors;
  answer hedged to 2.08 m (within ~4% of mirror width, ~9% of body width).
- Green width: body 113-117.5 px (no protruding mirrors seen) -> 115 px / 56.4 -> 2.04 m.

## Confidence
- 24 green speed: high (~2%).
- 25 orange length: high (~3%).
- 26 green length: medium-high (~4%, chrome bumper extremes faint).
- 27 lamp distance: medium-high (~3%, depends on camera height for ground-vs-car scale).
- 28 orange width: medium (mirror inclusion ambiguity).
- 29 green width: medium-high (~4%).
