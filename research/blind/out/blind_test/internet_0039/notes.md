# internet_0039 - overhead drone shot of a freestyle swimmer between two lane ropes

## Setup
- 2160x3840, 72 frames. The dataset fps is 25, which I used: frame = round(t*25), so t=1 s is frame 25 and t=2.33 s is frame 58.25.
- The container fps is 18.54 (2725/147), and one frame in about every 10 is a duplicate (frames 1, 11, 20, 30, 40, 50, 60 and 70).
  - If the ground truth used 18.54 fps, speeds would be 0.74x and the acceleration 0.55x.
  - "2.33 s" is exactly 70/30 or 56/24 frames, so a 30 or 24 fps source is also possible. I kept 25 fps as the workflow instructs.
- The camera is almost static (nadir view, drone hovering).
  - Phase correlation on the rope float pattern gives a vertical drift of about 3 px over 58 frames, which is negligible.
  - The ropes slowly diverge toward the bottom of the frame (slight tilt change, about 2%), so I ignored it.

## Scale
- Swimmer length, measured from the cap top to the lowest foot on zoomed crops with a ruler (12 frames):
  - about 1000 px in frames 0-19
  - about 1050-1060 px in frames 25-58
  - about 1080-1095 px in frames 64-69
- I used L = 1030 px for 1.68 m, giving s = 1.631 mm/px. Uncertainty is about +/-3%, depending on which frame an annotator used.
- Rope centre lines come from robust line fits to red-float pixels in each frame.
  - Separation at the swimmer's rows is about 1372-1385 px. I used 1378 px.
  - Lane distance = 1378 * 1.631e-3 = 2.25 m. This is a plausible 2.25 m lane.

## Track (full-res y, px)
| Tracked point | t=0 | t=1 s | t=2.32 s |
|---|---|---|---|
| Cap (template matching) | 2088.0 | 1613.2 | 985.3 |
| Trunks (dark-blob centroid, pelvis proxy) | 2502.6 | 2055.2 | 1438.5 |
| Bbox centre (head top to feet) | 2522 | 2082 | 1450 |

- I extrapolated by +4.8 px (0.25 frame) to reach t=2.33.

| Interval | Cap | Trunks | Bbox | Mean | Speed |
|---|---|---|---|---|---|
| 0-1 s (px/s) | 474.8 | 447.4 | 440 | 454 | 0.741 m/s |
| 1-2.33 s (px/s) | 475.7 | 467.3 | 479 | 474 | 0.773 m/s |
| 0-2.33 s (px/s) | 475.3 | 458.8 | 462 | 465.5 | 0.759 m/s |

- Acceleration: dv = 20 px/s = 0.033 m/s.
  - Divided by the time between interval midpoints (1.165 s): 0.028 m/s^2.
  - Divided by the full 2.33 s span: 0.014 m/s^2.
  - The quadratic fit to the head track gives a slight deceleration; the fit to the trunk track gives +0.003 m/s^2.
  - I answered 0.02 m/s^2.

## Confidence
| Question | Value | Confidence |
|---|---|---|
| 3046 | 0.741 m/s | medium |
| 3047 | 0.773 m/s | medium |
| 3048 | 0.759 m/s | medium |
| 3049 | 0.02 m/s^2 | very low (the signal is smaller than the tracking noise; the fps convention is a further risk) |
| 3050 | 2.25 m | medium-high |

- For 3046-3048, the main risk is the fps convention, followed by which pixel length the annotator used for the swimmer's height.
- For 3050, the main risk is which frame the annotator used to measure the swimmer's pixel height.
