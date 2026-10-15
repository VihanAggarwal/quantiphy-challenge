# simulation_0309 (dragon flying away from a static camera; 2880x1440 with black bars, content 2560x1440, 24 fps, 72 frames)

## Method
- The camera is static (median background diff is about 0). The dragon's hip/tail-base was tracked frame to frame with template matching (work/tmpl.py). Overlays were checked visually; the track is smooth and stays on the hip.
- 3D model: the origin moves along a straight line at constant velocity with |V| = 1.29 m/s (prior). Depth info r(1s) = 5.2108 and r(2s) = 6.3261 (range or Z). The principal point is the content centre (1440, 720). Focal length is a free parameter, fitted by LM to the 71-frame image track (work/fit.py, fit2.py). A sinusoidal wing-flap bob (period about 1.09 s, about 40 px) was added to the tracked point.
- Focal estimates: Z-convention, linear origin: 3565 px; range convention: 3448 px; bobbing-origin variants: 3330-3400; direct two-ray solve from hip pixels at t=1 and t=2: 3529 (Z) / 3367 (range). The Z-convention value is close to Blender's default 50 mm lens (3556 px, hfov 39.6 deg). Adopted f of about 3500 px (hfov of about 40 deg). The flight direction in camera coordinates is about (-0.415, -0.306, 0.857), which implies about 20 deg camera pitch if the flight is level.
- An independent check of the projective image track gives t0 = -3.82 s, against -3.67 s implied by the depth info. These are consistent.
- Q1 body length: the head and tail-tip pixels in frames 1-17 were reconstructed in 3D by intersecting their rays with the dragon's sagittal plane (span of the flight direction and world up), cross-checked by projecting onto the flight-axis line (work/recon.py, tailtip.py). Tail tip is about -0.55 to -0.63 m behind the origin, with the most extended at frames 1-6. The front of the head (horns/head tip) is about +0.21 to +0.35 m ahead. Snout-to-tail-tip is about 0.90-0.98 m with f=3565, about 0.93-1.0 m with f=3450. Answer: 0.96 m. Sanity check: the measured wingspan in glide frames is about 1.45 m, giving a span/length ratio of about 1.5.
- Q2 displacement 0.5 s to 1.0 s: constant speed, straight path, so 1.29 x 0.5 = 0.645 m. A bobbing-origin variant gives 0.62-0.63.

## Confidence
- 1486 (body length 0.96 m): low-moderate. The snout is hidden in this rear view, the tail swings, and it is unclear whether ground truth is an AABB at some frame or the rest pose. Expect +/-15%.
- 1487 (0.645 m): moderate-high if the origin moves at constant speed, which the prior implies.
