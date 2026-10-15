# simulation_0163 — bowling ball rolling into pins (side view, fixed camera)

## Scene / geometry
- 1920x1080, 24 fps, 51 frames. Ball enters at frame 1 from the left, rolls left->right along the lane, hits the pins at frame ~27.
- Lane lines are exactly horizontal in the image (fitted slope ~1e-4), so the lane direction is parallel to the image plane. The ball's image y stays at 657-659 for frames 2-26, so its depth is constant and px -> m along the path is one linear scale.
- Horizon from receding end-wall/panel lines: y ~207 (VP x ~ 960). Vertical-edge convergence gives f ~2400-2700 px. Off-axis elongation of the ball gives f ~2300-2350 px. Camera pitch is ~7.5-8.5 deg and camera height ~1.29 m in prior units.

## Scale
- On-axis horizontal ball diameter (the ellipse minor axis = 2fr/Z): 79.3 px (gradient edges, fitted with the off-axis model) and 78.8-79.3 px (coverage at 50%). Used 79.2 px for 0.21 m, i.e. 0.0026515 m/px at the ball's depth.

## Motion (Q381-384)
- Ball centre per frame comes from a circle fit to subpixel side edges.
- The x track has a ~5-frame oscillation (rolling texture). A quadratic plus a rolling-phase sinusoid fits with 0.27 px rms. Speeds over 5-frame windows (one rotation) decline linearly at -0.245 px/frame^2.
- Backward difference at frame 12 is 50.83 px/frame, which gives 3.235 m/s. At frame 24 (still before impact) it is 47.92 px/frame, which gives 3.049 m/s.
- Deceleration is constant over frames 3-26: 0.243 px/frame^2, which gives 0.371 m/s^2 at both times.
- Confidence: speeds high (~2%). Acceleration medium: the smooth estimate is robust, but the GT frame-level differences could be noisy.

## Pin height (Q385)
- Full pinhole and floor model: the ball fixes Z and the camera height. Each pin's base y gives its floor distance, and its top y gives its height.
- Pixel heights: head pin 568.7 to 690.5. The near pins of rows 2, 3 and 4 were measured the same way.
- Heights: head 0.328, row 2 0.327, row 3 0.327, row 4 0.3275 m. This is insensitive to f in 2200-2600 (+-0.001) and to the horizon.
- The ball rolls about 0.1 m nearer the camera than the head pin (pocket hit), consistent with the image.
- Answer 0.328 m. Confidence high (~2%).
