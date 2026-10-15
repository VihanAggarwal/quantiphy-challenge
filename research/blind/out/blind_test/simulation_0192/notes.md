# simulation_0192 - box drops onto truck roof (fixed camera, 120 fps)
- Camera pitch 0 (wall verticals exactly vertical), so horizon at y=540.
- Box tracked by HSV colour mask per frame. It falls from frame ~1 and lands at frame ~61.
- Free-fall fits (y = y0 + A(t-t0)^2): top silhouette (front-top edge) 2032 px/s2, bottom (back-bottom edge) 1827, mid 1935; t0 ~0.008 s.
  Scales: front 207.4 px/m, back 186.5 px/m, centre ~197 px/m.
- Box width = 282.5 px front face / 207.4 = 1.36 m (medium-high confidence).
- Box height = 217.5/207.4 (top above horizon) - 14/186.5 (bottom) = 0.97; the start frame gives 0.98. Answer 0.975 (medium-high confidence).
- Speeds: a*(t - t0 - 1/240) gives 1.84 / 3.80; local poly fit gives 1.81 / 3.85. Answers 1.86 / 3.83 (high confidence).
- Truck width = 567 px at an unknown depth (truck rear is in front of the box front, so width <= 2.74 m).
  Assumed truck-rear scale ~231 px/m, giving 2.45 m (low-medium confidence).
