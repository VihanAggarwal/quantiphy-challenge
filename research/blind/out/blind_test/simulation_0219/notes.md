# simulation_0219 (V2MC, 2D side view, 24 fps, 50 frames)
Scene: a big tracked robot drives to the right at a constant 51.9 px/frame (measured on its tank side). A small robot walks left in front of it. Camera faces the wall squarely. The parking-line vanishing point is about (965, 545), so the horizon is near the image centre.

Scale comes from the speed prior. Because px speed is proportional to 1/depth, I measured px speeds of features at different depths:
tank side 51.86, near nozzle 51.35, far nozzle 46.16, tread plate and wheel posts 50.76, handle 49.26, drill tip about 53.8 px/frame.
- Scale = 5.924/(v*24): tread 0.004863 m/px, handle 0.005011, near nozzle 0.004807, drill 0.00459.
- The nozzle end ellipses give f of about 2500 px. With that f, the parking space depth comes out at about 2.5 m, which is consistent.
- Camera height h = (894.5 - 545) * 0.004863 = 1.70 m, from the near-tread ground contact at y = 894.5.

Answers:
- 641 length: rear nozzle at X = -0.71 m, drill tip at X = +2.23 m, giving 2.94 m. Confidence medium-high.
- 642 height: handle top at y = 272.5 and tread bottom at y = 894.5, each scaled at its own depth, giving 3.07 m. Confidence medium-high.
- 643 parking space long side (along the wall): the near-line span of 1241 px at y = 908, times h/(908 - 545), gives 5.82 m. The free-fit vanishing point gives 5.9 m. Confidence medium.
- 644 road wheel diameter: 69.5 px * 0.004863 = 0.338 m. Confidence medium; it is unclear which wheels count as "tires".
- 645 small robot speed: torso track is about 8.65 px/frame near t = 1 s. Ground contact is about y = 963 (planted feet range 955-972), so scale = h/(963 - 545) = 0.00407 m/px, giving 0.845 m/s. Confidence medium; gait makes the speed vary by about 10%.
- 646 small robot height: head top about 662 to sole about 963, so 301 px * 0.00407 = 1.22 m. Confidence medium.
