# simulation_0272 (A2SC, top-down view of phoenix flying left, static camera, 24 fps, 72 frames)
Prior: acceleration at 2.0 s = 2 m/s^2.
- Beak-tip track (leftmost saturated pixel near body row) fits x = 1470.4 - 0.2081 n^2 (n = frame), vertex at n=0.03:
  starts from rest at t=0 with constant acceleration (per-flap surges superimposed, period ~25 frames).
  a_px = 0.4163 px/frame^2 (beak); tail-tip fit 0.405 -> used ~0.4135 -> 238 px/s^2 -> scale ~0.00838 m/px.
- Segment mean speeds 5, 15, 25 px/frame over 0-24, 24-48, 48-71 confirm v proportional to t.
- Speeds: constant acceleration 2 m/s^2 from rest -> v = 2t (backward diff gives 0.958/1.958); answered 0.98, 1.97 (high confidence).
- Length: background-subtracted mask extent along x, median 430 px (stable across video -> constant height) -> 3.61 m (medium).
- Wing span: max y-extent with wings fully spread (frames 21/46/71) 608-613 px -> 5.12 m (medium; depends on pose used for AABB).
