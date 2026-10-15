# simulation_0311 (LaFerrari driving away, static elevated camera)
- Camera: vertical VP from 2 poles (1289,12055); motion VP from taillight tracks (-1112,-858); lateral VP from taillight pairs (~9600,-836).
  Pairwise orthogonality gives f = 4151/4161/4231 px; orthocenter ~ image centre -> f ~4190 (HFOV ~34 deg). Rim ellipse aspect ratios confirm f >= ~4190 (not 3550).
- Car: pure translation (stable lateral VP), near-constant speed 3.84 W/s (W = taillight separation), slight accel ~0.05 W/s^2.
- Depth info inconsistent with the image geometry for any in-car origin (range ratio 1.30 vs <=1.235 achievable). Using ranges + motion direction
  with in-car origin: displacement 6.6-6.9 m/s; triangle inequality gives v >= 5.37 m/s. Car proportions (rear width ~1.11 W) with real LaFerrari width
  give scale ~1.75-1.85 m/W -> v ~6.7-7.1. Chosen scale 1.76 m/W.
- Answers: v(1s)=6.7, v(2s)=6.8 (medium-low confidence); length 4.85, width 2.05 from LaFerrari proportions scaled to H=1.15 (medium);
  accel 0.1 m/s^2 (low confidence, near-constant speed).
