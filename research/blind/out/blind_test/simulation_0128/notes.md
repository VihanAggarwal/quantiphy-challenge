# simulation_0128 — notes

Video: 1920x1080, 24 fps, 38 frames. Static camera. Red ball falls vertically from rest near the image centre
(x~962); an orange Toyota forklift drives right (accelerating, ~120 px total) at the lower left. Prior: g = 9.8 m/s^2.

## Scale (from the falling ball)
- Ball centroid tracked per frame (red-colour mask, alpha-weighted centroid). Quadratic fit over frames 2-37:
  a = 609.3 px/s^2 (rms 0.14 px); sub-ranges give 607-611. Vertex at frame 0 (dropped from rest).
  No sign of damping (early/late halves agree).
- s = 9.8 / 609.5 = 0.01608 m/px (at the ball's plane).
- Same-plane check: the forklift tyres meet the ground at y=1056.4. Extrapolating the ball's fall, its bottom would reach
  that line between frames 38 and 39, just after the clip ends. If the ball were much farther away than the forklift, it would have
  passed its own floor line long before the end, so it is taken to be in the forklift's plane (the 2D design).
- Perspective is weak (telephoto-like): no far-side wheels are visible, and the counterweight top shows as only a ~5 px strip.
  The background hangar is a strongly perspective backdrop that does not match the camera.

## Ball diameter (qid 295)
- The chroma (V) integral across the centre row gives a 23.2 px chord. V-coverage gives 23.4 px vertically.
  An edge-local half-max circle fit on colour distance gives 23.6 px (biased up by a halo). An inner-referenced
  alpha width gives 22.4 px (biased low by limb darkening). Adopted 23.3 px -> 0.375 m.
- Confidence: medium-high (±3%).

## Forklift length (qid 296)
- Rear edge 125.5 px (frame 0; difference against frame 37, constant to ±0.5 px after shift correction across frames 0-34).
  Fork tip 539.4 px (frame 0; half-level of the orange chroma). Shift from multi-part template tracking: 120.2 px at frame 37.
- Image extent 413.9 px. Removing a small perspective term (near-side rear corner and far-side fork tip, W/f ~0.009) leaves ~408.8 px.
- 408.8 * 0.01608 = 6.57 m (uncorrected 6.66). Confidence: medium (the same-plane assumption is the main risk).

## Forklift height (qid 297)
- Top of the overhead guard is at 813.8 px; the tyre bottom is at 1056.4 px; extent 242.6 px. The mast top (824) is lower than the guard.
- Perspective correction ~3.3 px -> 239.3 px -> 3.85 m (uncorrected 3.90). Confidence: medium.

The forklift comes out ~1.95x real size (3.4 m x 2.1 m), so the scene is scaled. That is acceptable given the prior defines the scale.
