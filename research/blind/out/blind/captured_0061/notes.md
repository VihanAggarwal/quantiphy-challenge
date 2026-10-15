# captured_0061 (lab, 1280x720, 24 fps, 49 frames)

Scene: a woman throws a soccer ball, which bounces and flies out of the frame at the bottom left at about 1.1 s. She dribbles and tosses
a basketball, which ends near the camera at 2.0 s. A 55 cm class yoga ball is rolled from the camera toward her, and she grabs it.

## Method
- Pinhole camera: f = 711 px, principal point (640,360). Frame = t*24, interpolated between frames.
- Ball edges come from radial half-max profiles on |frame - median background| (soccer, yoga) or on the R-B "orange" signal
  (basketball), followed by a robust circle fit. The off-axis ellipse stretch is corrected: r_t = r/((1+1/cos(theta))/2).
- Depth convention: the depth_info values are surface Z at the clicked centre, so the centre is at Zc = Zs + R*cos(theta). Evidence:
  1. The basketball anchor at 1.6 s gives D = 24.0 cm, which is the size of the size-7 Wilson ball.
  2. Gravity: a projectile fit of the basketball (frames 37-47) together with its size gives R = 0.119, which agrees with the anchor.
  3. The yoga speed at 0.6 s comes out at 2.3-2.55 m/s (prior: 2.51).
  4. The camera height from the rolling yoga ball (H = 3.50 R_y = 0.97 m) agrees with the basketball's bounce height.
- Speeds are forward differences [t, t+0.04 s] of the SURFACE label point on smooth fitted trajectories (free flight with
  g = 9.8, Z linear in t).

## Answers
- 3047 yoga D = 55.5 cm. At t=0.6 the yoga ball has r = 84.2 px, depth 2.133, so R = 0.2776. (high confidence)
- 3048 soccer D = 21.5 cm. The vertical (tangential) extent is about 75 px at 0.6 s, giving 21.5. The 0.9 s anchor gives
  about 20.4, and a gravity-based depth gives about 23. (medium confidence)
- 3050 basketball-yoga distance at 2.0 s = 1.24 m. Surface-to-surface it is 1.21, centre-to-centre 1.35. Basketball surface
  point (-0.457, 0.742, 1.635); yoga surface point (-0.068, 0.639, 2.782) with r = 65.5 px at frame 48. (medium confidence)
- 3052 soccer v(0.6) = 1.62 m/s and 3053 v(0.9) = 2.10 m/s. Fitted on the label anchors (VZ = -1.17 m/s). (medium confidence)
- 3054 basketball v(1.1) = 4.4 m/s. This is the free fall after release (VY of about 4.3, VZ of about -0.9). (medium-high confidence)
- 3055 basketball v(1.6) = 0.8 m/s. This is near the apex, so VZ (-0.6 to -0.9) dominates. (low-medium confidence)
- 3049 and 3051: the soccer ball is NOT visible at 2.0 s (it leaves the frame at about 1.1 s). I assumed the label holds its last
  labelled position (somewhere in 0.9-1.1 s). That gives a soccer-basketball distance of 0.82-1.0 m (answer 0.9) and a height
  above the floor of 0.49-0.97 m (answer 0.65). (low confidence)
