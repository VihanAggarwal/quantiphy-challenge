# simulation_0116 — football dropped in front of blue warehouse wall (fire escape, yellow doors)

Video: 1386x1920, 32 frames @ 24 fps, static camera, wall roughly fronto-parallel (vertical lines stay vertical).
Prior: g = 9.8 m/s^2.

## Scale from gravity
- Ball segmented per frame (median-background difference + R/B chroma to drop the soft wall shadow).
- Bbox mid-point track (top+bottom)/2 fits y = 225.5 + 0.5*a*t^2 with release at t0 = 0.00 s (rest at frame 0),
  a = 1808 px/s^2 (subsets 0-16 / 16-32 give 1805 / 1810; rms 0.55 px). The top edge alone gives a biased
  1786/1707 split because the silhouette height changes with viewing elevation.
- s_ball = 9.8/1808 = 0.005420 m/px (at ball depth).

## Camera
- Vanishing point of depth lines (platform side edges) ~ (708, 984). The football rings are seen edge-on at y ~ 970-985 (horizon),
  from below at the top of the fall and from above at the bottom; the ball does NOT rotate.
- Ring sagitta vs. image height fits f ~ 900-1000 px (HFOV ~ 70 deg). Z_ball = f*s_ball ~ 5 m.

## Football (qid 236, 237)
- Tip-to-tip vertical extent at frames 21-23 (ball centre at the horizon, so no off-axis stretch vertically): 61-63 px -> 62.2 px.
  Cross-check: ring spacing 47 px + spheroid fit with ring radius gives ~63 px.
- Equator width (R/B chroma edges, all frames): 36.2 px raw; horizontal off-axis stretch 1/cos(theta_x), tan(theta_x) ~ 337/920 -> x0.94 -> 34.0 px.
- Length = 62.2*0.00542 = 0.337 m; width = 34.0*0.00542 = 0.184 m.

## Middle yellow door (qid 238, 239)
- Outer yellow frame incl. transom: middle door top 823.4, left 647.3, right 807.4 (width 160.1 px); bottom hidden behind
  the platform floor, so height taken from the identical, fully visible bottom door: 1375.4 -> 1735.8 = 360.4 px.
- Door is on the wall plane, behind the ball. Ball must clear the base rail and casts a strong contact shadow -> centre ~0.2 m
  in front of the wall; Z_wall/Z_ball ~ 1 + 0.2/5.0 = 1.04 (uncertain, 1.02-1.07).
- Height = 360.4*0.00542*1.04 = 2.03 m; width = 160.1*0.00542*1.04 = 0.90 m (plausible 2.0 x 0.9 m door).

## Speed at 0.5 s (qid 240)
- Free fall from rest at frame 0 confirmed. Backward difference at frame 12: g*(12^2-11^2)/(2*24) = 4.70 m/s
  (pixel route: 36 px/frame * 0.00542 * 24 = 4.7).

## Confidence
- 240 speed: high (+-2%).
- 236 length: medium-high (+-4%, tip edges are dark-on-shadow).
- 237 width: medium (+-4%, depends on f for the off-axis correction).
- 238/239 door: medium (+-5%; ball-to-wall gap estimated, door assumed to be the whole yellow frame incl. transom).
