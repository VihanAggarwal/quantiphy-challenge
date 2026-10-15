# simulation_0133 — apple rolls down a rod ramp, off a counter, onto the floor (2D side view, prior g = 9.8 m/s^2)

Method
- Static camera, no pitch (table left edge exactly vertical at x=582 from y=940..1660). Apple size constant
  (~62-64 px) on table, in flight and on floor -> motion is in one fronto-parallel plane -> single m/px scale.
- Apple tracked per frame by saturation mask (s>90), checked against background-difference masks (frame 0 as bg).
- Free flight frames 36-47: parabola fit of centroid y(t): g_px = 6360 px/s^2 (range 6348-6369 over windows; rms 0.16 px),
  vertex at frame 34.44 (y=886), vx = 429.4 px/s constant. Scale s = 9.8/6360 = 0.0015409 m/px.
- On the table the apple's bottom is hidden by the counter front edge (camera ~ at counter height), so centroids
  for frames <=34 are biased; used apple top (ymin) + radius instead.

Measurements / answers
- 315 apple diameter: silhouette extents 61-66 px (bg-diff th 30), mean ~63, eq-diam 62.5 -> 63.5 px -> 0.098 m. Conf: medium (AABB def / rotation).
- 316 table height: apple centre drop table->floor = 639.7 px (top-based) / 643 px (horizon at 960 + front face 906.5..1662 geometry) -> 641 px -> 0.988 m. Conf: high.
- 317 horizontal speed leaving table: 429.4 px/s in flight (14.5 px/frame rolling just before edge) -> 0.662 m/s. Conf: high.
- 318 horizontal displacement in flight: flight time from vertex (f34.44) to centre reaching floor-rest height 1525 = 0.448 s (= sqrt(2h/g) with h=0.988) -> 192.5 px -> 0.297 m. Conf: medium-high (definition of start/end).
- 319 speed at 1.2 s (frame 36, backward diff p36-p35): (14.3, 7.5) px/frame -> 485 px/s -> 0.747 m/s; frame-35 convention would give ~0.67-0.70.
  Answered 0.74 (slight hedge). Conf: medium (apple just leaving edge; timing convention sensitive).
