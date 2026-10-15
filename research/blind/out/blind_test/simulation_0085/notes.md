# simulation_0085 notes (2D top-down sim, prior: car acceleration 4.03 m/s^2)

Scene: fixed camera looking straight down. A Cybertruck-like car and a cyclist both move left (-x). 1920x1080, 72 frames, 24 fps. The render looks 2x upscaled.
Frame 0 is a duplicate of frame 1. Positions fit t = n/24, with the car starting from rest at t=0 (quadratic vertex at n ~ -0.05).

## Scale
- Car pixel track: frame-to-frame SSD registration of the car band (rows 585-880) with subpixel parabola; cross-checked against the front/rear edge tracks and 14 individual feature tracks.
- Velocity is linear for frames 1-35: a = 0.8895 px/frame^2 = 512.3 px/s^2. Acceleration rises to ~1.35 px/f^2 around frames 50-56, then falls to ~0.2 by the end. The average over the whole clip is also ~0.887.
- Scale at car-roof height: m/px = 4.03/512.3 = 0.007866. Check: car length 723.4 px gives 5.69 m, which matches a real Cybertruck (5.683 m).
- Perspective: rear and front faces show parallax (k ~0.024 and 0.017 per px of offset). Tyre features move about 1.2% slower than roof features, so the camera distance is roughly 35-45 m.
  Bike wheel-height features therefore get a scale factor of about 1.02 relative to the car registration.

## Measurements
- Car length: silhouette at centred frames 52-55 = 723.4 px, giving 5.69 m.
- Car width: mirror to mirror 315.0 px (stable across frames), giving 2.465 m. Tyres are 268 px (2.13 m); body is 254.5 px (2.00 m).
  Answer 2.42 is hedged slightly toward the mirror-inclusive bounding box.
- Bike: front/rear wheel tips from a red-channel drop threshold. Length near the image centre = 213.4 px, giving 1.71 m.
  Speed = 26.665 px/frame (constant, residual rms 0.12 px), giving 5.13 m/s.
- Car speed at 1.5 s (backward diff, frames 35-36): fit 31.62 px/f, giving 5.97 m/s. Constant-acceleration theory gives 5.96.
- Distances use bounding-box centres. Car centreline y = 727.4, bike y = 383.8, so dY = 2.73 m.
  - t = 1.0 s: dX = 5.41 m, giving 6.06 m.
  - t = 2.0 s: dX = 4.45 m, giving 5.22 m. A small origin height difference would add about 0.02 m.

## Confidence
- 115 car speed: high.
- 111 car length: high.
- 109 bike speed: high-medium (depends on the height scale factor, ±1%).
- 110 bike length: medium-high.
- 113/114 distances: medium (depends on where the origins are).
- 112 width: medium (depends on whether the bounding box includes the mirrors).
