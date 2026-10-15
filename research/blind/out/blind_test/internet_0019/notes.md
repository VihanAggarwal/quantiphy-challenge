# internet_0019 — beach football lob (prior: g = 9.8 m/s^2), 40 frames @ 30 fps

## Method
- Ball tracked frames 5-38 by darkness vs. per-pixel temporal median (sky background); sub-pixel weighted centroid,
  half-max equivalent diameter (work/ball.py -> work/ball.json).
- Camera is handheld: horizon (at infinity) drifts up ~3.7 px then back (tilt); sand texture phase-correlation shows a
  ~8 px rightward pan over the clip (work/cam*.py). Pan-corrected ball x becomes perfectly linear (resid 0.18 px vs 0.63 raw),
  confirming the correction.
- Vertical parabola fit: a = 0.931 px/frame^2 raw, 0.910 camera-corrected (0.9085 also correcting ~5% ball-size growth / depth).
  Scale = 9.8/(a*900): 1.169 (raw) .. 1.196 (corrected) cm/px. Used the midpoint ~1.183 cm/px (GT likely ignores camera drift).
- Sanity: ball diameter 18.5 px -> 22 cm (standard size-5 football), adult men ~1.75 m: scale is physically consistent with 30 fps.
- All people stand at about the same depth (feet-to-horizon distance ~93 px for each, horizon roll accounted), so one scale.

## Measurements (px, frame-0 coordinates)
- Ball half-max diameter at apex: 18.5 px.
- Middle man: head top 212.7, feet ~360 -> ~147.5 px.
- Receiver (taller man with blurred face, right; heads the ball at the end): head 213.6, feet ~362 (walking stride) -> ~148.5-149 px.
- Passer (left, curly hair, kicks at ~f0-2): head top ~235 (camera-corrected, frames 15-39), feet ~360.5 -> ~125 px.
- Initial passer-receiver separation at f0: ~366 px (passer support foot / bbox centre ~465, receiver ~831).
- Ball vx: 5.32 px/f (pan-corrected) / 5.56 (raw) -> 1.91 / 1.95 m/s.
- Speed at t=1.00 s (frame 30): vx~5.3-5.7, vy~8.0-8.2 px/f -> 3.46-3.50 m/s instantaneous, 3.30-3.37 backward diff.

## Answers / confidence
- 2092 ball size 22.0 cm (medium-high)
- 2093 middle person 174.5 cm (medium; feet hidden in dark sand ±1.5 px)
- 2094 passer 148 cm (medium)
- 2095 receiver 175.5 cm (medium; walking posture)
- 2096 initial distance 4.33 m (medium; definition of body position)
- 2097 velocity at 1.00 s 3.42 m/s (medium-high)
- 2098 average horizontal velocity 1.93 m/s (high)
