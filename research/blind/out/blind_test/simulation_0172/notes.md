# simulation_0172 — astronaut moon-hop (S3SS)

## Scene and setup
- 2304x1296 at 24 fps, 80 frames, static camera, black sky with a lunar ground strip. The bottom 103 rows are a hard black band.
- One astronaut doing a bounding moon-walk to the right and toward the camera. The pelvis is the origin I tracked.
- Prior: height 2.2 m. Depth at t=1 s (frame 24): 18.147 m to the pelvis. The pelvis pixel at frame 24 is about (1055, 800), which gives optical-axis Z24 = 18.12 m.

## Method
1. Median background subtraction gives the astronaut and shadow masks (overlays checked).
2. **Relative depth** comes from the apparent size of the rigid backpack (PLSS). I used three measures:
   - (a) SIFT similarity transforms on the backpack region over 644 frame pairs (gaps 1-24), solved by global least squares on log-scale;
   - (b) the vertical (row-2) scale of the affine fits, which yaw does not affect;
   - (c) the backpack silhouette length measured along its edge.
   All three agree: the scale grows about 23% from frame 0 to 79, so Z goes from 19.5 m to 15.7 m. The astronaut walks along a roughly straight path about 29 deg toward the camera, then turns further toward the camera after about frame 68.
   - The SIFT consecutive-frame chain on the whole upper body drifted (+32%), and ECC over long gaps failed, so I did not use either.
3. **Pelvis pixel track**: I propagated the pelvis point from frame 24 with frame-to-frame SIFT similarity transforms of the upper body. A second track built from the backpack-edge geometry agrees.
   - The root motion has velocity kinks (keyframes) at frames 15, 30 and 61. I smoothed each segment separately with cubic polynomials and never smoothed across a kink.
4. **Focal length**: f = 3200 px (HFOV 39.6 deg).
   - The height prior with the frame-24 pose (386 px) gives f = 3180.
   - The upright pose normalised to frame-24 depth (about 385-395 px) gives about 3200-3250.
   - The frame-0 AABB hypothesis gives 3040.
   - Blender's default 50 mm lens gives 3200.
   - Uncertainty is about ±4%. It affects only the lateral and vertical components.
5. World position: X = (u-cx)Z/f, Y = (v-cy)Z/f. Speed = |p(t)-p(t-1)|*24. Acceleration = d|v|/dt from the smoothed track.

## Key velocities (m/s, x lateral / y up / z depth)
- f12: (1.38, -0.46, -0.92), speed 1.72. With the noisier silhouette-length depth rate, speed would be 1.99.
- f24: (4.11, 2.06, -2.3), speed about 5.15. The speed peaks near frame 23-24.
- f48: (1.73, -0.99, -1.1), speed 2.28. The speed is flat here.
- f72: (0.70, 0.33, -1.28), speed about 1.5. The local depth rate is 0.32-0.35 %/frame; the cubic fit gives 1.37.

## Answers / confidence
- 1407 speed t=0.5: 1.74. Medium; the depth-rate uncertainty is about ±10%.
- 1408 accel t=0.5: 0.45. Low; this is small, since the descent is decelerating while vx rises slightly.
- 1409 speed t=1: 5.15. Medium-high.
- 1410 accel t=1: 0.5. Low; the speed is near its peak, so the true value is near zero.
- 1411 speed t=2: 2.28. Medium-high.
- 1412 accel t=2: 0.15. Very low; the speed curve is flat.
- 1413 speed t=3: 1.5. Low-medium; the astronaut is turning toward the camera, so the depth component dominates.
- 1414 accel t=3: 0.9. Low.
