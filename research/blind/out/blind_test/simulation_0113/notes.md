# simulation_0113 — swim ring in square pool (top-down, 1080x1080, 24 fps, 120 frames)

Method
- Fixed top-down camera; pool centred in frame. Ring segmented with colour mask (max(R,B)-G>60 & R>110,
  restricted to pool ROI), contour + ellipse fit per frame (scripts/track2.py -> track2.csv; overlay checked).
- Ring outer diameter via radial half-max crossing of chroma (72 rays, scripts/rays.py): 73.5-74.0 px in every
  sampled frame (stable). Scale: 1 m / ~73.75 px = 0.01356 m/px.
- Ring moves at constant velocity: 0.403 px/frame (global linear/quadratic fits, local fits around frame 24,
  segment averages 0.395-0.404 all agree). Speed = 0.403*24/73.75 = 0.131 m/s.
- Pool extent from intensity profiles (scripts/pooledge2.py): outer rim x 306.5-769.5 (463 px), y ~308-770.5
  (462 px); water-line inner x 313.5-765.5 (452 px), y 310.5-765 (454.5 px). Outer -> 6.26 m, inner -> 6.12 m;
  answer midpoint 6.2 m. Visible rim/inner-wall band only 2-6 px, so water-vs-rim depth effect <2%.

Answers
- 231 speed at 1.0 s: 0.131 m/s (high confidence; constant-velocity motion, scale error ~1-2%).
- 232 pool side: 6.2 m (high confidence; inner/outer ambiguity +-1.3%).
