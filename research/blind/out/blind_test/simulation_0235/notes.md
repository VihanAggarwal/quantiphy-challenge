# simulation_0235 (S2MS, 2D planar view, 24 fps, 1920x1080, 50 frames)
Scene: basketball bounces vertically in front of a green gym wall (windows above); trophy on pedestal to the right.
Scale: ball diameter 106 px (colour mask, consistent all frames) -> 0.282/106 = 0.00266 m/px at ball depth.
Depth correction (level camera, horizon ~y=540): ball floor contact y=918, wall base y=904 -> wall 1.038x farther -> 0.002763 m/px on wall.
Trophy axis contact ~y=928 -> 0.974x -> 0.00259 m/px.
- 768 trophy height: top 505.5 to bottom ~928-937 (~423-431 px) -> 1.10 m (medium confidence: depth/what counts as trophy)
- 769 pane length: black opening 196 px -> 0.542 m (medium: opening vs frame-incl period 247 px -> 0.68)
- 770 pane height: 148 px -> 0.409 m (medium; period 199 px -> 0.55)
- 771 green section height: y 442-903 = 462 px -> 1.277 m (medium-high)
- Motion: subpixel centroid track (mask cut to 108 px below top to exclude floor reflection), local quadratic fits (w=4..6).
  Ball is keyframed (accel ~2 m/s^2, not g). Bounce at frame 24.
- 772 v(0.5s)=1.007 m/s, 773 a=1.99 m/s^2 (speeding up), 774 v(1.5s)=1.08 m/s, 775 |a|=1.87 m/s^2 (slowing). High-medium confidence.
