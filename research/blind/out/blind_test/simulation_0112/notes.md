# simulation_0112 — red Porsche 930-style car crossing a rusty girder bridge (side view, static camera)

Prior: car speed = 6.66 m/s (origin, assumed on car centreline). fps 24, 1080x1080, 55 frames.

## Geometry found
- Camera is level with the bridge deck: deck front-top edge at row 540.0 (= image centre); tyre contacts ~539.
  Car moves exactly parallel to the image plane (constant height and roof row in every frame).
- Perspective is visible (front face of car visible at left, rear face at right, far-side wheels peek out), so
  near-side features and centreline features move at different image speeds:
  - near tyre silhouettes (circle fits of all frames): rear 28.286 px/frame, front 28.18 px/frame
  - bumper-tip extremes fitted with a 3D rounded-end model (u = max_z (U - K z^2)/(1+z)), joint R+L fit, rms 0.42 px:
    centreline speed v_c = 26.662 px/frame -> scale at origin depth s_c = (6.66/24)/26.662 = 0.010408 m/px
  - near tyre depth / centreline depth = 26.662/28.28 = 0.9445 (consistent with a 930 track and f ~ 1500 px, Z ~ 15.6 m;
    far-tyre extremity at frame 47 predicted 978 px vs observed ~979).

## Answers
- Length (230): centreline tip-to-tip length from the model fit 413.85 px * s_c = 4.307 m -> 4.31 (raw silhouette 422.5 px is inflated by near corners). Confidence high.
- Height (228): roof top row 411.8 (subpixel, dark-background frames) to contact 539.4 -> 127.6 px * s_c = 1.328; small
  silhouette-tangent correction (-0.4%) -> 1.325. Confidence high.
- Wheel diameter (229): circle fits, rear r = 33.75 px, front r = 32.68 px, scaled at the tyre's own depth (0.2775/v_tyre):
  rear 0.662 m, front 0.644 m -> mean 0.653. Confidence medium-high (front/rear differ 3%).
- Bridge thickness (227): front face 540.0 -> 616.5 = 76.5 px, but the bridge front face is nearer than the car.
  Depth ratio Z_bridge/Z_car from water reflections (flat mirror, camera horizon 540):
  A = deck-edge reflection offset (row 861 -> 320.8), B = car-roof reflection offset (y_r + y_d - 1080 = 285 lum / 292 red,
  minus ~2% roof-edge correction). Ratio 0.87-0.92, used 0.885 -> 76.5 * 0.010408 * 0.885 = 0.705 -> 0.71.
  Confidence medium (ripple-blurred reflection edges; plausible range 0.69-0.74).
