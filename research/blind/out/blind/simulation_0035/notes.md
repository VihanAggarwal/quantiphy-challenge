# simulation_0035 (S3MC, 1080x1080, 24 fps, 72 frames; frames 0 and 1 are identical)

Scene: static camera over a lake. A small walking person on the left shore (about 42 px tall) and an eagle flying right and away across the sky.

## Scale (focal length)
- I measured the person's height in pixels by background subtraction (median background) with sub-pixel coverage-sum edges, using every frame where the whole body is detected. The height is 40.2-43.0 px, with a mean of 41.6 px; mid-stance frames reach about 42.3 px. I used h = 41.8 +- 0.5 px for 1.75 m.
- The person's range is 139.10 m, and the person sits about 7.7 deg off-axis, so depth Z = 137.85 m. That gives f = h * Z / 1.75, about 3290 px (horizontal FOV about 18.5 deg).

## Person speed (1145)
- Upper-body centroid track: x slope 1.0527 px/frame (residual rms 0.26 px; both halves agree, 1.055 and 1.057). The vertical drift is about 0.065-0.1 px/frame.
- The range is the same at t=1 s and t=2 s (139.1030 vs 139.1044 m). For a straight walk this means the motion is tangential, so the 3D speed is the pixel speed times range over f. That gives 1.05-1.06 m/s (1.062 at h=41.6 px, 1.052 at h=42.0 px).
- **Answer 1.06 m/s.** Confidence: good (about +-3%).

## Eagle speed (1147)
- Tracked the eagle's dark silhouette with background subtraction. I fitted a constant-velocity 3D straight line to the pixel track (frames 1-71) together with the ranges at t=1 and t=2.
- Residual rms is 1.2 px, which is flapping noise. The range residuals are 3 cm. As an independent check, the image-only depth-rate parameter (0.0623) matches the one implied by the ranges (0.0606).
- Velocity is about (8.45, 0.30, 7.94) m/s, giving a speed of 11.70 / 11.64 / 11.58 m/s at f = 3248 / 3277 / 3308.
- **Answer 11.6 m/s.** Confidence: good (about +-3%). The radial part comes directly from depth_info.

## Wingspan (1146)
- The heading is taken as the velocity direction, 47 deg from the optical axis, so the wing axis is foreshortened by cos(phi), where phi is the angle between the heading and the line of sight (51-55 deg).
- Flat-wing (mid-downstroke) frames 5, 30 and 31 have widths of 28.2-30.8 px (50%/25% edge thresholds), giving 2.04-2.08 m at f = 3248.
- The foreshortening model predicts the projected-width ratio between frames 5 and 30 (0.909 predicted vs 0.914 measured).
- Scaled to f of about 3290, this gives **2.03 m**. Confidence: moderate (about +-8%, mostly from the heading assumption).

## Body length (1148)
- In the wings-up (V) frames, the base of the silhouette (body plus a tail spur) is 12-16 px. Projected along the heading (sin phi = 0.71-0.79), this gives 0.64-0.86 m.
- Typical eagle proportions (wingspan/length about 2.3-2.4) give 0.84-0.88 m.
- **Answer 0.85 m.** Confidence: low-moderate (about +-15%).
