# simulation_0190 (S2MS, 120 fps, 1920x1080)
Scene: box-body truck seen from directly behind (camera on truck centreline, pitch 0: verticals exactly vertical, horizon y=540).
Truck body lifts vertically (bumper/chassis static, body width constant -> pure vertical translation). Cardboard box on roof also rises, but
with its own (lagging, non-rigid) profile; box apparent width constant 281.5 px -> no depth motion.

Scale: box front-face width 281.5 px (S>45 mask edges 805.8..1087.3) = 1.33 m -> 0.004725 m/px at box front plane.
Assumed box front face flush with body rear edge (box bottom coincides with roof edge; box cannot be nearer). Same scale used for truck.

- 461 truck height t=0: roof top edge y=338.5, ground at rear landing-leg feet y~1041 -> 702.5 px -> 3.32 m. (medium; depends on box depth assumption)
- 462 truck width: body 661..1228 px = 567 px -> 2.68 m. (medium; if box sits further back on roof, truck is smaller)
- 463 box height: front face top 163.8 to roof edge 338.5 = 175 px (0.83 m); open flap tip at y=145 adds 19 px (0.91 m) -> 0.90. (low-medium)
- 464/465 box speed: template-matched vertical track of box face, local quadratic fits (h=8..40 frames) -> 18.6 px/s @1s, 25.0 px/s @2s
  -> 0.088, 0.118 m/s. (high; independent of depth assumption)
