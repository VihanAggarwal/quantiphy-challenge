# simulation_0160 - billiards, top-down 2D view (S2MC), prior ball diameter 0.0757 m

## Video
- 1920x1080, 40 frames, 30 fps. Static camera looking straight down on the table.
- Only the orange-striped 13 ball moves (right to left along y~505 px). Frame 1 is a glitch (ball shown at (1305,801)).
- The video has exact duplicate frames (4=5, 9=10, 12=13, 18=19, 25=26, 27=28, 34=35) balanced by 2-step jumps, so the
  timing is jittered. Total steps from frame 2 to 39 = 37, so the timeline stays aligned overall. I rebuilt the sim frame
  index by counting steps (video 15 = sim 14, video 30 = sim 29).

## Scale
- Ball diameter in px, several methods: anti-aliased disc model fit (48.1-48.7 for the balls near the centre), soft-coverage
  area (47.8-48.1), edge profiles (48.0-48.9). Used d = 48.3 px, so s = 0.0757/48.3 = 1.567e-3 m/px at the ball-centre plane.
- Weak perspective: the cushion inner faces show as dark strips 9.5 px wide (left/right) and 5 px (top/bottom), so h/D ~ 0.0125.
  Pocket cylinders are stretched radially by the same amount. Ball ellipticity against offset from centre gives f ~ 3000 px,
  so D ~ 4.7 m. Plane corrections: rail top x0.996, cloth x1.008 (both under 1%).

## Measurements
- Outer table (rail outer edges, subpixel): 1671.6 x 916.9 px -> 2.609 x 1.431 m.
- Cloth / playing area: 1524.5 x 788.7 px -> 2.409 x 1.246 m. The inner rail-top edges (1544 x 799 px) agree.
- Pocket black disc, max width perpendicular to the radial stretch: 75.5 px -> 0.118 m.
- Ball track (background subtraction centroid). Speeds with the backward difference:
  - t=0.5: 29.05 px/frame (smooth fit in sim index, deg-4/5 polynomial and saturating-exponential fits) vs 28.35 raw video
    step -> used 28.7 px/frame -> 1.349 m/s.
  - t=1.0: 33.3 (fit) vs 33.1 (raw) -> 33.2 px/frame -> 1.561 m/s.
  - Ball speeds up (slip-to-roll with topspin), from ~15 px/frame to ~34 px/frame.

## Answers and confidence
- 372 length: we cannot tell whether the GT uses the outer bounding box (2.609) or the playing area (2.409). Gave the geometric
  mean, 2.51, which is within about 4% of both. Medium confidence.
- 373 width: outer 1.431 or cloth 1.246. Gave 1.374, 4% below outer (outer is somewhat more likely; cloth would be off by ~10%).
  Medium-low confidence.
- 374 pocket diameter 0.118 m: medium-high confidence.
- 375 speed at 0.5 s, 1.349 m/s: high confidence (+-2%).
- 376 speed at 1.0 s, 1.561 m/s: high confidence (+-1.5%).
