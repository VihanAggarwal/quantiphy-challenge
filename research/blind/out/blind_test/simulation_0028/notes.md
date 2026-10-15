# simulation_0028 — eagle flying past (fixed camera, Blender)

Video: 960x960, 75 frames, dataset fps 24 (frame = round(t*24)). Static camera (rock region diff ~1 grey level).
The eagle flies left to right across the sand, frames 0 to 53, and leaves the frame after t of about 2.2 s. Its shadow is visible on the sand.

## Tracking
- I built a median background over all frames. Per-frame |frame - median| gives clean eagle and shadow silhouettes (scripts in work/).
- The eagle is seen roughly from the side (camera depression about 15-20 deg at the eagle). The body/tail "bar" is horizontal and
  the wings flap above and below it. The flap period is about 25.5 frames.
- Image velocity from template matching at matched flap phases: 16.6 px/frame early, rising to 16.95 px/frame between t=1 and t=2
  (perspective: the eagle approaches slightly). The body line drifts down 0.50 px/frame.

## Scale (prior: eagle length 0.8 m)
- Beak-to-tail extent of the body bar, using low thresholds that include the faint head/beak and remove 1 px halos:
  25-26 px on downstroke frames and 27.5-29 px on upstroke frames. Adopted L_px = 27.3 +- 1.5.
- This gives f = 27.3*99.95/0.8 = 3411 px (HFOV about 16 deg, inside 8-103).

## Q1118 speed at t=1 s
- Origin assumed at the body centre: (455, 244) at t=1 and (861.8, 256) at t=2. I used the depth_info ranges, treated as the
  Euclidean range to the origin.
- P1 = (-0.73, -6.91, 99.90) m and P2 = (11.05, -6.48, 98.69) m, so |dP| = 11.85 m over 1 s. The motion is straight with
  constant 3D speed: the rise in image speed matches the perspective change. The backward difference at t=1 is therefore the same.
- Answer 11.85 m/s. Sensitivity: L_px 26 to 29 gives 12.4 to 11.2. Confidence: medium.

## Q1117 wingspan
- I fitted a rigid-wing flap model to the per-frame silhouette top and bottom extents relative to the body line.
  The far wing tip shows s*sin(phi+theta) and the near tip s*sin(phi-theta).
- Upstroke maximum: about 31 px above the shoulder. Mid-stroke total height: about 16 px, which equals 2 s sin(theta).
- I cross-checked with the shadow, where both wing shadows are visible as diverging bars at the stroke extremes.
- Result: semi-span s = 31.5 +- 2 px and theta of about 15-19 deg.
- Wingspan = 2s + shoulder gap (about 4 px), which is about 67 px. In metres, 67 * 0.8/27.3 = 1.96 m (W/L = 2.45, typical of eagles).
- Answer 1.96 m. Confidence: low-medium. The main uncertainties are the scale (L_px) and the wing semi-span.

## Notes
- Flat-ground shadow kinematics alone would suggest a steeper camera, but they conflict with the wing silhouettes.
  The beach is probably sloped, so I did not use them for the answers.
