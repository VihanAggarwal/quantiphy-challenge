# simulation_0149 - yellow sports car leaving a parking bay (garage), fixed Blender camera, 24 fps, 50 frames

## Camera calibration
- Vertical lines are vertical (no pitch); horizon well below image centre (lens shift).
- Hough + LSQ vanishing points: U (lights/lane direction) ~(4000-4060, 820-832), V (beams/pipes) ~(-890..-910, 823).
  f^2=(xu-cx)(cx-xv) with cx=960 -> f ~ 2370-2410; mid-pillar squareness gives 2400. Used f=2370.
- Horizon y_h ~828 (light/floor VP 827-832, rim-centre rows 826.8-830, best marking consistency at 828).
- Camera height ~ wheel-centre height (0.382 m); ground mapping Z = 0.382*f/(y - 828).

## Car track
- Rim (white wheel) of right-front (FR, frames 0-31) and right-rear (RR, 19-41): sub-pixel centre u and height h.
- Depth from rim height Z = f*D/(k*h); both wheels lie on one straight line, heading 37.7 deg = garage V axis (no rotation).
- Fitted rigid straight-line model with Blender Bezier ease s = V(3tau^2-2tau^3): t0=-0.3 fr, T=59.0 fr, wheelbase const,
  rms 0.8 px (u), 0.9 px (h). Car starts at rest at frame 0, peak speed at frame ~29.
- Scale: depth_info (range convention, documented) at t=0 for FR: model horizontal range 14.644 (k=1.5) -> factor 0.9727.
  Direct tire measurement gives k~1.48-1.59 (consistent with range conv; Z conv would need k=1.44). Range conv used.
- Speeds: backward difference |p(t)-p(t-1)|*24 -> v(12)=6.40, v(24)=9.64 m/s.
- Accel candidates: t=0.5: back 10.05 / central 9.78 / fwd 9.50 -> 9.9; t=1.0: back 3.43 / central 3.16 / fwd 2.88 -> 3.3.

## Sizes
- Car width: triangulated body points in car frame (motion model): right mirror tip b=-0.02, left mirror tip 2.115,
  front-left silhouette ~2.05-2.11, right tyre sidewall ~-0.03 (model units) -> ~2.15 * 0.9727 = 2.09 m.
  (Licence plate sits at b=1.127, ~8 cm left of mirror midline 1.049 -> plate appears offset.)
- Pillars (square, aligned U/V): corner base rows -> depth, face ends by ray intersection.
  y_h=828: near 0.95/1.07, mid 1.04/1.02, B1 1.02/1.00 -> width ~1.02 m.
- Black/yellow corner-guard marking from floor to top: near pillar 207.5 px @Z 8.56 -> 0.749 m; mid pillar 124 px @14.26 -> 0.746 m,
  118 px @14.88 -> 0.741 m -> 0.745 m.

## Confidence
- 1522/1524 speeds: medium-high (+-4%, scale convention).  1523 accel t=0.5: medium. 1525 accel t=1.0: low-medium (convention).
- 1519 width: medium (+-6%). 1520 marking: medium (+-5%, horizon). 1521 pillar width: medium (+-6%).
