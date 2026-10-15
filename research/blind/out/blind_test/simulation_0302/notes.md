# simulation_0302 - dragon flying away from a static camera (sky background, 2560x1440, 24 fps, 72 frames)

## Observations
- One dragon (wyvern type: wings are the forelimbs, two hind legs, long tail), seen from below and behind as it flies away and toward the upper-left of the frame. Frames 0-50 show it flapping and rolling. From frame ~51 on the pose is frozen (gliding) and the dragon translates rigidly. Video frames 0 and 1 are identical.
- The head is rendered as a flat grey, untextured patch with horns (in the side-on banked frames 14-20 it sits at the front of the body).

## Geometry
- Rigid phase (frames 51-71): about 170 KLT tracks fit a pure-translation model, where each point moves radially toward the vanishing point vp of the velocity (rms 0.23 px). Result: vp = (-455, -489) px (bootstrap sd < 1 px), so |vp - c| = 2115 px. Each feature also gets its own rate w = Vz/Z, which gives relative depths: head about 0.173, hips about 0.176, tail tip about 0.184, near wing tip 0.187, far wing tip 0.173.
- The head-patch track over the whole clip lies on the same line to vp, and 1/|u - vp| is linear in t with periodic flap bobbing of about ±1.5%. So the motion is constant velocity, and Vz/Z(1 s) for the head is about 0.216.
- Depth info: r(1) = 5.1661 and r(2) = 6.2783. The origin's depth ratio fits the head/shoulder depth exactly under the optical-axis-Z convention; under the range convention it sits about 0.15 m beyond the head. The evidence is weak.
- Focal length from the speed prior, using cos(beta) = Vz/1.29 and tan(beta) = |vp - c|/f:
  - range convention: Vz = 1.077 m/s, so f = 3208 px
  - Z convention: Vz = 1.112 m/s, so f = 3600 px (close to Blender's default 50 mm lens, 3556 px)

## Answers
- Q1470 (displacement 0.5-1.0 s): constant velocity gives 1.29 m/s x 0.5 s = **0.645 m**. Confidence high; this holds if the origin moves uniformly, as the track indicates.
- Q1469 (body length): from the 3D reconstruction, back-of-head to tail tip is 0.65 m (range) or 0.62 m (Z). Its extent along the flight direction is 0.58-0.60 m. Adding about 0.11 m of head (measured from the side-on frame 14) gives 0.70-0.76 m. The spine path in rest pose would be about 0.8 m. Wingspan in the frozen pose is about 1.4-1.5 m. Answer **0.74 m**. Confidence low to medium: the head is hidden, the AABB convention is unknown, and the pose differs from rest.
