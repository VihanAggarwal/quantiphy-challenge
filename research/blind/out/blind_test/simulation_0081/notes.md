# simulation_0081 (S2MX, top-down view, 24 fps, 29 frames; frames 0 and 1 identical)

Scene: camera looks straight down at a grey floor. A walker (white shirt) moves +x along image y~437;
a cyclist on a cyan bike with a rear basket moves -x along image y~640. Prior: bike length = 1.7 m.

## Scale and camera
- Cyan mask gives the bike's front and rear tips with subpixel edges. Pixel length is 382.2 px at the image centre,
  with a slight trend of 0.0071*(x_f-960) (the rear tip is slightly higher than the front tire).
  Scale at the front-tip height (~0.35 m): s_f = 223.2 px/m. Rear tip: 224.8 px/m.
- Parallax (positions relative to the front tip, regressed on x_f) shows strong perspective. Handlebar slope 0.0358,
  basket 0.0211, rider head 0.069. This gives camera height H ~ 19 m (16-21), f ~ 4160 px, hFOV ~ 26 deg.
  Walker head (h ~ 1.66 m) scale is ~240 px/m.

## Answers
- Q85 bike speed: front and rear tips move at a constant 47.25 px/frame, which gives 5.08 m/s (both tips agree).
  Confidence: high.
- Q84 walker speed at 0.5 s: dark-hair head blob tracked. Its mean is 13.49 px/frame, or 1.35 m/s.
  The gait oscillation puts the frame-12 backward difference at ~12.3-12.7 px/frame (1.26 m/s); the shirt track
  agrees, 4-6% below its mean. Answer 1.29, a hedge between the pelvis-bone instantaneous value and the mean.
  Confidence: medium.
- Q86/Q87 distances: ground positions come from the pinhole model. The walker's pelvis is taken under the head,
  0.04 m behind it, at Y = -0.43 m. The bike origin is taken at the AABB centre (front tip + 0.85 m) at Y = +0.447 m.
  - Frame 12: dX 4.37, dY 0.88, horizontal 4.46 m.
  - Frame 24: dX 1.13, dY 0.87, horizontal 1.43 m.
  - The height difference between pelvis (~1 m) and bike origin (0-0.9 m) is unknown. With dz 0.45 the distances
    are 4.49 and 1.50; with dz 1.0 they are 4.57 and 1.75.
  - Answers: 4.5 (confidence high) and 1.52 (medium-low; it depends on the origin convention and on the
    frame/time alignment, since the gap closes by 0.27 m per frame).
