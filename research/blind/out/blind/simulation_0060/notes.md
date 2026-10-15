# simulation_0060 — method and measurements

## Camera model (2160x1080, 24 fps, static camera)
- Road-direction vanishing point from the two long curb lines (rms 0.25 px): VP_Z = (1208.6, -43.5).
- Vertical vanishing point from 9 poles/lamp posts: VP_V = (1065, 8588).
- Principal point at the image centre, so f = sqrt(-(VP_V-c)·(VP_Z-c)) = 2167.6 px (pitch ~15.1 deg down, roll ~0.1 deg, yaw ~3.4 deg).
- Scale (camera height h) from the prior. I tracked the van's side panel (chained template, sub-pixel) and projected it onto the van's side plane
  (Z = 3.747 h, from the tyre contacts, which are constant across frames). The fit was X(t) quadratic, giving 0.7637 h/s^2 (rms 0.1 mm) => h = 4/0.7637 = 5.236 m.
- Checks against depth_info, all consistent:
  * Van: X1^2-X2^2 = d1^2-d2^2 puts the origin within 6 cm of the van's bbox centre. Origin-height/width residual is plausible (W/2 ~1.0-1.2 m).
    The same check, run with different f, independently selects f ~2150-2170.
  * Bike: ranges match a constant-Z track (Z=22.77). The origin sits 0.41 m behind the bike centre at both times, height ~0.85 m.
  * Pedestrian: the feet-on-sidewalk positions (sidewalk ~0.1 m) match the pelvis ranges (Z=33.50 at 0.58 s, 34.70 at 1.58 s).
  * Taxi: the sign-point range is 26.20 vs 26.23 at 0.58 s.
- Measured road width (curb to curb) 11.86 m. The cross road is 12.1 m.

## Answers
- 1343 taxi average speed 4.12 m/s: taxi roof sign colour-segmented in every frame and projected onto plane Y=1.53. That height was calibrated
  at frames 26/28 so the sign lies on the car centreline relative to the wheel contacts. Smoothed path length 12.1 m over 70 frame intervals => 4.15.
  Rear-tyre contacts at frames 56-71 give 4.14. Small reductions for the origin offset and the duplicated first frame. Medium confidence.
- 1344 lane width 6.2: there are no lane markings. Curb-to-curb width is 11.86 m. The traffic (purple car, green car, taxi's final lateral position)
  is consistent with 2 lanes of ~5.93 m. The answer leans to a single lane. Low confidence (could be 11.9).
- 1345 van length 5.85: silhouette extremes (rear-near corner at f36-40, front-near corner at f62-68), combined via the tracked translation,
  give 5.72-5.84, plus a small allowance for bumper rounding. Wheelbase 3.74 m. Medium-high confidence.
- 1346 taxi length 5.38: measured wheelbase 2.90 m (f26) = Crown Victoria (2.913). Overhangs measured roughly (front ~1.0, rear ~1.4) => ~5.3-5.4.
  Medium confidence.
- 1347 taxi height 1.63: roof-sign top 1.61-1.62 m in 6 rear-view frames, 1.62 in side view f6. Medium confidence (assumes the sign is part of the bbox).
- 1348 bicycle wheel diameter 0.65: horizontal and vertical tyre extents at f40 (wheel contact Z=22.77) give 0.64-0.66. Medium-high confidence.
- 1349 pedestrian average speed 1.20: feet ground positions f0-4 vs f48-60 give 1.21. Pelvis ranges give 1.20 between 0.58 and 1.58 s. High confidence.
- 1350 pedestrian height 1.79: head top to feet at f0/f4/f52 gives 1.80/1.81/1.79. High confidence.
- 1351 bike average speed 5.32: chained track frames 4-51 on plane Z=22.77 gives a constant 5.35 m/s (per-frame 5.32-5.38).
  Small allowance for the duplicated first frame. High confidence.
- 1352 green car width 1.95: mirror-tip span 2.00 m at mirror height ~1.0 m. Body ~1.80-1.85 (left side at X~0.05). The answer leans to mirrors.
- 1353 purple car width 1.87: front corners/tyres give 1.70-1.72, mirrors ~1.9 (Mercedes W123, body 1.79). Hedged.
- 1354 three stacked trash bags height 1.32: on the road at Z=51.5. Front-bottom v=187.5, top v=129.7 => 1.31-1.34. Medium confidence (far object).
- 1355 trash can height 0.78: green slatted bin on the sidewalk (s~0.1). Bottom v=309.5, front rim top v~257.5 => 0.785, diameter 0.48.
  Assumes the green bin rather than the small grey box in the road (~0.6 m).
