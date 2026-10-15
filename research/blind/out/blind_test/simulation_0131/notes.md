# simulation_0131: hot air balloon rising (V2SX, 24 fps, 1080x1080, 97 frames)

Prior: balloon speed is 4 m/s. Q308 asks for the width and Q309 for the height.

## Observations
- The background is a uniform sky (BGR 197,168,139) and the camera is static. The balloon rises straight up: the axis column stays at 539.5 and nothing drifts in x.
- The silhouette's maximum width at 50% contrast is 356.13 px. It stays constant within 0.05 px over the whole clip, so depth is constant. The camera is level (pitch below about 0.02 deg relative to the motion) and the motion is parallel to the image plane.
- There is strong perspective parallax. Texture on the front of the band moves at 4.47 px/frame, texture near the limb at about 4.1, the crown silhouette at about 4.03-4.10 (accelerating as it rises), and the basket at about 3.93-4.00. Because of this, a naive single pixel speed (about 4.05) is biased high.
- Basket edges, tracked at subpixel precision and both very linear (rms under 0.08 px):
  - The top (back) edge moves at 3.9228 px/frame.
  - The bottom (front) edge moves at 4.0022 px/frame.
  - These give an axis-depth pixel speed s = 2/(1/s_top + 1/s_bot) = 3.962 px/frame, with half-depth to distance ratio beta = 0.0100.
  - Check: the basket's apparent height shrinks by 7.53 px over the clip, against 7.55 px predicted. This also confirms the horizon is near y=540.
- If the basket is square (30.04 px wide), f is about 1486 px (horizontal FOV about 40 deg), D is about 62 m and r/D is about 0.12. The crown-acceleration model (f about 1500) and the band-front parallax (s about 3.947 at f about 1485) agree with this.

## Computation
- The scale at the axis depth is (4/24)/3.962 = 0.042065 m/px.
- Width: 356.13 px x 0.042065 x sqrt(1 - 0.12^2), where the last factor corrects for the limb tangent, gives **14.87 m**.
- Height: at frame 0 the crown top is 35.7 px above the horizon (a near-horizontal view, flat-crown correction of about 0.3 px). The basket's front-bottom edge is 432.42 px below the horizon, times (1 - beta), giving 428.09 axis-px. The total is 463.8 px x 0.042065 = **19.51 m**. The height runs from the envelope top to the basket bottom.

## Confidence
- Width: high, about ±2%. Other plausible choices for s (3.94-4.04) give 14.6-14.95 m.
- Height: high, about ±2.5%. The range is 19.2-19.6 m. It assumes the AABB includes the basket.
