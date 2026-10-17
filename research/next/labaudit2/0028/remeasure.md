# 0028 second measurer: qids 2475 and 2481 (ping-pong ball velocity at 1.3 s)

Independent measurement. I did not read labaudit/0028 or other notes in labaudit2/0028. The only outside input I used was the
general 25->24 drop pattern noted in other families (0039, 0036): capture = k + (k>=12) + (k>=36).
Scripts and crops are in `remeasure_work/`: track2.py, fit3d.py, bounce.py, size2.py, velocity.py, and the PNGs.

## Scene
- All three renders (o, s, x) use the same camera and pixel geometry. The x render has a black background, so I tracked the ball there.
- The camera is about level. Fitting the table's side edges puts the horizon (vanishing row) at y of about 349-351 (cy 360).
  The camera sits about 17 cm above the table top.
- The ball is released from the hand at about video 21 and bounces near the BACK edge of the table at capture 27.2
  (centre y 420.8). The apex is at capture 32.87 (video 32 = capture 33, y 300.9, x 749.7).
  The second bounce is at capture about 38.6, and the ball reaches its third apex at video 42.
- Drops: within arcs video 21-25, 27-35 and 37-45 the second differences are uniform (about 7.3-7.9 px per capture-frame squared in arc 2),
  so there is no drop inside them. The x step from video 35 to 36 is 3.66 px against about 2.0 px for its neighbours, which fits the capture-37 drop.
  So video 31/32/33 = capture 32/33/34. t = 1.3 s means capture 32.5, and the max-height frame is capture 33 (1.32 s).

## Depth and Vz near the apex (the crux)
- ToF anchors (labeller): 1.557 m at t=1.1 and 1.4115 m at t=1.3. The trend is -0.63 m/s (27->33) or -0.73 m/s (28->33).
- g route (3D ballistic fit, f=711): arc-2 Z is about 1.45-1.49 at the apex, which agrees with the ToF. Vz is poorly constrained (-0.38 or 0.0, depending on which frames are used).
- Size route: the mask-coverage width grows about 0.25-0.38 px per frame over arc 2, giving Vz of -0.4 to -0.65 m/s.
  The apex-2 to apex-3 width ratio is about 1.157 (x, s and o renders), and arc-3/arc-2 g-scale is 0.82, giving a mean Vz of -0.44 to -0.60.
- Bounce-on-table-plane route: Z2/Z1 is 0.88-0.94, giving -0.25 to -0.4 m/s. This route is very pixel-sensitive near the back edge (about 2 cm per px), so I gave it low weight.
- Combined estimate: Vz is about -0.58 +- 0.12 m/s. Vx is about 0.0-0.03 m/s (from the x drift of 2.0 px per frame, mostly perspective expansion).
  Vy is about 0.05 m/s at capture 33.

## Result (both qids share one label: same event, renders o and s)
Label style, P = ToF_surface_range * ray(click), forward difference times 25:

| Vz (m/s) | capture 32->33 | capture 33->34 |
|---|---|---|
| -0.50 | 53 | 54-56 |
| -0.58 | 60-61 | 62-63 |
| -0.65 | 67-68 | 68-70 |
| -0.73 (pure ToF trend) | 75 | 76-77 |

- The transverse part of the step is only about 0.5-1.1 cm (vertical step of 3-4 px near the apex). The label is dominated by the range step (about -2.3 cm).
  ToF noise of 1.5-2 cm per reading, about 2-3 cm on the difference, therefore controls the label: plausible labels run from 45 to 95 cm/s.
  Simulation: the noise inflates the median by about 2-5 cm/s, while the relative-error scoring favours shading lower. Net, about 62.
- Physical speed at t = 1.32 s is about 55-58 cm/s (range 45-65), almost all toward the camera.

**Recommended: qid 2475 = 62 cm/s, qid 2481 = 62 cm/s (confidence low).** The current 93.4 is high, unless the ToF difference at that step was unusually large.
