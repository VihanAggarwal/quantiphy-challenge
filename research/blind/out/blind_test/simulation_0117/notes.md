# simulation_0117: tennis ball falling in front of a door with a smart lock (2D sim, gravity prior)

## Scale from gravity
- Ball tracked by background subtraction (median background) over 19 frames at 24 fps. It drops from rest at t=0 (centre y ~10 px), x = 1017 px stays constant.
- Quadratic fits of y(t), frames 3-18: centre a = 6314 px/s^2 (rms 0.5 px), top edge 6293, bottom edge 6329. Used 6315 px/s^2,
  so s_ball = 9.8/6315 = 1.552e-3 m/px.
- Ball diameter: about 43.5 px (difference-mask half-max 43.2, ellipse fit 43-45, visual 43.3), giving **0.0675 m**. This matches a real tennis ball
  (6.5-6.9 cm), and the result does not depend on the ball's depth. Confidence: high.

## Door and lock pixel extents (median background)
- Door frame outer edges: x 697-1430 (733 px), y 356-1838 (1482 px; 1838 is the floor line). Inner panel: x 714-1410 (696 px), y 373-1838 (1465 px).
  The vertical groove at x = 822 splits a narrow side strip from the leaf (leaf alone is 822-1410, 588 px).
- Electronic lock: y 1035.5-1224.7 (189 px), x ~825-866 (~41 px).

## Depth: the ball is in front of the door plane, so the door scale is not the ball's scale
- The spotlight beam on the door and the ball's own illumination show the ball's lit band is narrower in image space than the wall's lit band.
  The ball's soft shadow is displaced outward from the beam centre. Both give a ball-to-shadow image mapping slope m ~ 1.39 about the light's
  image point (943, 1180). So the light sits in front of the camera, and m = rho(1-lambda)/(rho-lambda), where rho = Zball/Zwall.
- Penumbra fit in the plateau frames gives a light apparent radius of ~200-230 px. Beam edge widths are about 200 px horizontally and 265 px
  vertically; under Cycles spot attenuation per sampled point these give an emitter smear radius of ~120 px, so lambda ~ 0.5-0.6 and
  rho ~ 0.80-0.85 (plausible range 0.7-0.95).
- Real-size priors: a smart lock is usually 0.33-0.42 m long, which points to rho 0.73-0.85. A 2.3-2.7 m door points to rho 0.85-1.
  The camera height (878 px below horizon) is 1.36/rho m.
- Chosen rho = 0.88 as a hedge, so the wall scale is s_wall = s_ball/0.88 = 1.764e-3 m/px.

## Answers
| qid | quantity | px | value | confidence |
|---|---|---|---|---|
| 241 | ball diameter | 43.5 | 0.0675 m | high |
| 242 | door height (bbox incl. frame, 1465-1482 px) | 1476 | 2.60 m | medium-low (depth ambiguity; 2.27 if coplanar) |
| 243 | door width (frame 733 / panels 696 px) | 720 | 1.27 m | low (depth plus which parts are "door"; leaf only would be 1.04) |
| 244 | lock length | 189 | 0.334 m | medium-low |
| 245 | lock width | 41 | 0.072 m | medium-low |

Scripts are in scripts/ (track, fit, measure, shadow*, beam, edges, penfit, elong, hwidth).
