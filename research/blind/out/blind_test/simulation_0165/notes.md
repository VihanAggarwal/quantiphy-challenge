# simulation_0165 — bike crossing an intersection (2D, static camera)

Prior: bike speed = 5.52 m/s. 1920x1080, 24 fps, 80 frames.

## Geometry
- Static camera. Main-road vanishing point from 4 white-line edges (sub-pixel row fits) = (960.2, 539.55), i.e. the image centre:
  zero pitch/yaw, and cross-street edges are horizontal image rows. The bike moves purely horizontally (wheel centre y constant at 705.7/706.5,
  wheel size constant), so the bike stays at one depth (fronto-parallel motion). One planar scale applies.
- Bike track: circle fits to the outer tyre edges in frames 34-67. Wheel-centre pixel speed: rear 20.997 px/frame, front 21.014 px/frame (resid sd 0.15 px)
  -> 21.01 px/frame = 504.2 px/s -> s = 5.52/504.2 = 0.010947 m/px.

## Measurements
- Wheel outer (tyre) diameter: 66.3 px (circle fits, both wheels, ~frames 41-63, range 65.9-66.7) -> **0.726 m**.
- Bike length: wheelbase 95.03 px + one diameter 66.3 px = 161.3 px (bg-subtraction mask extent 161.5-162 px); nothing on rider/basket sticks out past the tyres -> **1.766 m**.
- Road width (main road the bike crosses, curb base to curb base): radial profiles from the VP give the curb bases at dx/dy = -1.562 (left) and +2.530 (right).
  Camera height H = s*(y_contact - y_vp) = 0.010947*(739.2-539.55) = 2.186 m. Width = (2.530+1.562)*H = **8.94 m**.
  Other options: between the outer edges of the white edge lines 8.72 m, between their inner edges 8.28 m.

## Confidence
- 386 wheel diameter: high (~3%).
- 388 bike length: high (~3%). If the GT box includes something outside the tyres it would be a bit larger.
- 387 road width: medium. The main uncertainty is what counts as the road (curb-to-curb asphalt is used here). Only curbs/sidewalks included would change it (+~1.5 m).
