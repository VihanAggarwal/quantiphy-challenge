# internet_0008 — sunset, sailboat + speedboat (S2MC, 30 fps, 960x540, 529 frames)

## Scene / camera
- Static camera (horizon fixed at y~442.7 +-0.2 px in all frames). Very long telephoto: sun disc 161 px wide (0.53 deg) -> f ~17300 px.
- Sun rises ~66 px in 17.6 s, about 3x Earth's rate, so the clip is probably sped up. Ignored: GT uses video time at 30 fps.
- Sailboat moves steadily right (x 293 -> 856). Speedboat (RIB, 3 people) enters left at frame ~224, passes IN FRONT of the sailboat (frames 302-326), and exits right at frame ~350. It gets closer and grows (37 -> 45 px).

## Scale (prior: sailboat length 12 m)
- Hull body at half-level edges, rows 507-511: 87 px (start), 89 (mid), 91 (end). Mean 88.9 px.
- Full silhouette with stern fittings and bow pulpit: ~100-106 px.
- Used L = 94.5 px (between the two definitions) -> 0.1270 m/px. Single planar scale, because the clip is labelled 2D and has no depth_info.

## Measurements
- Sailboat centre: linear fit 32.26 px/s (endpoints agree: 32.23). Speed falls slowly, ~34 -> ~29 px/s.
- Speedboat bow (leading edge) from frames 225-346: 231.8 px/s. Frames 240-345, fully visible: 236.6 px/s. Pixel speed rises 6.6 -> 9.3 px/frame as it approaches. Used 236 px/s.
- Speedboat length: blob/hull ~40-41 px mid-track (37 early, 44-47 late, including some blur and spray). Used 41 px.

## Answers
- 2044 sailboat average speed = 32.26 * 0.1270 = 4.10 m/s. Confidence medium-high: the main uncertainty is pixel length L, about +-6%.
- 2045 speedboat average speed = 236 * 0.1270 = 30.0 m/s. Confidence medium. This uses the single scale. A depth-aware scale (speedboat ~0.82x as far, from waterline-below-horizon geometry) would give ~24.6.
- 2046 speedboat length = 41 * 0.1270 = 5.21 m. Confidence medium. Depth-aware would give ~4.3 m.
