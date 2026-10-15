# simulation_0073: notes

Scene: a nadir (straight-down) view of a crossroads, 2160x1080 at 24 fps, 72 frames. Video frame 0 is a duplicate of frame 1.
A white van (the "white car") and a bicycle both move up the image (-y) at x of about 832 and 918.

## Camera / scale
- Perspective camera looking straight down. The lamp poles lean radially from the image centre (1080,540), with top/base
  radius ratio of about 1.066, so the nadir is at the principal point and the ground maps by a similarity.
- I estimated camera height H at about 70 m (range 50-110) from several parallax cues on the van: the windshield crease,
  hood vs roof, rear-face growth, side-face asymmetry, and the bike template vs the wheel tips.
  Scale at height h is s(h)=s0/(1-h/H). Every answer moves less than 1% for H between 50 and 100.
- Bike: template-match track, linear over frames 1-71, 8.980 px/frame = 215.5 px/s, residual 0.24 px.
  5.33 m/s gives 40.43 px/m at the template's effective height (about 1.1 m), so s0 is about 39.8 px/m at the ground.

## Van
- Roof edges (windshield-roof crease and roof rear edge) tracked per frame. The roof midpoint fits an exact quadratic:
  y = -0.14336 n^2 - 0.28068 n + 961.67 (residual 0.06 px), so acceleration is constant.
  Roof scale is about 41.1 px/m (roof height about 2.2 m).
- Speed at 1.0 s: the backward difference at frame 24 is 7.019 px/frame, giving 4.10 m/s. Small hedge toward the
  1-frame-offset alternative (4.27), so I answer 4.13.
- Acceleration: 0.2867 px/frame^2, giving 4.02 m/s^2 (constant).
- Length: front bumper edge at frame 43 (at the image centre, y=534.7); rear-most body edge at frame 58 (at centre, y=556);
  roof displacement between them is 221.4 px at roof scale. This gives 5.92 m excluding the dark contact bands and 6.10 m
  including them. Answer 5.95.
- Width: body silhouettes at x=787.2 and 875.2 give 2.11-2.18 m after the perspective model. Thin mirror arms reach
  781.5 and 877.5, giving 2.36 m. It is unclear whether the AABB includes the mirrors, so I hedge at 2.24.
- Distances (plan, between body-centre and bike bbox-centre origins): 5.76 m at frame 24 (dY 5.34, dX 2.15) and
  5.00 m at frame 48.

## Platform
- The three brown squares are identical: top 78.2 px (77.6-79.5 over 6 edges) at s of about 40.1, giving 1.95 m.
  The dark square at the top right (72 px) is a different object.

## Confidence
Speed and acceleration: high. Distance at 2.0 s: high. Distance at 1.0 s: medium-high (origin conventions).
Length: medium-high. Platform: medium-high. Width: medium (mirror ambiguity).
