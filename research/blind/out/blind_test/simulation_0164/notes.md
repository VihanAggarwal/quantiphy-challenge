# simulation_0164 (bowling ball rolling down lane into pins), 24 fps, 1920x1080, 66 frames

## Camera (static)
- LSD line segments. Lane-direction vanishing point VP1 = (5640, 209), from 15 long lane/gutter lines with residuals under 1.5 px.
  The ball's own image track passes through it (it meets y=209 at x of about 5690).
- Cross-direction VP2 = (-284, 210), from the wainscot line and the masking-unit top edges. Vertical VP3 = (976, 17832).
- The orthocentre of the three VPs is (973, 542), which is the image centre, and f = 2399 px (about 2390 with pp=(960,540)).
  Three VP pairs give the same value, so f ~ 2395 px (HFOV ~44 deg, about a 45 mm lens). No roll; pitched down ~7.9 deg (horizon y=209).

## Scale conflict (important)
- Ball edge-fit diameter at t=0.5 s (frame 12): 84.2 px (circle fit to edges against the lane). With f=2395 and D=0.21 m,
  the ball centre is 6.24 m from the camera. depth_info says 9.391 m, which is a factor of 1.505.
  Matching depth_info would need f ~3650 px, and the VPs rule that out decisively.
- Ball-scale world: ball 0.21, pin ~0.33, lane width 1.40 m, camera 1.20 m above the lane (realistic).
  Depth-scale world (x1.5): ball 0.316, pin 0.50, lane 2.1 m (oversized).
- Chose the PRIOR scale (prior stated exactly true; depth likely affected by a camera-space or camera-scale issue).
  If the GT instead follows depth_info, all answers are x1.505.

## Ball track
- Blue-mask tracking, then a sub-pixel edge circle fit (frames 6-38).
- 3D: ball centre on a line parallel to VP1 at constant height. Camera is 1.096 m above the ball centre and the line is 5.94 m out
  in the cross direction (medians of size-based positions, frames 6-33). Size-based and line-based distances agree within ±1%.
- Position along the lane is the closest point to each frame's ray. Quadratic and exponential (damping) fits, rms 2.4 mm.
  - v(0.5) backward diff = 3.37 m/s; v(1.0) = 3.19 m/s. Both are robust to f ±100 px and the principal point (±0.03).
  - Decay rate k ~0.11/s (like RB damping ~0.1): a(0.5) ~ -0.37, a(1.0) ~ -0.355 m/s^2.
    These depend on VP1 x (±0.03 for ±50 px). Size-based route: -0.52 (biased by early-frame D).

## Pin height
- Front 4 pins at t=0: apex y ~482-484, base contact line y 584-586, 102 px.
- Ground-plane intersection (lane at 1.201 m below camera) puts them 7.9-8.0 m away. Vertical extent 0.331 m,
  minus ~0.003 m for the base-front-edge vs base-centre offset, gives 0.328 m.
- Ratio cross-check with the ball at frame 36 agrees (~0.33).

## Confidence
- Speeds: measurement ±2%, but the scale-hypothesis risk is large (x1.5 if GT follows depth). Medium.
- Accelerations: ±10-15% measurement, plus the same scale risk. Low-medium.
- Pin height: ±2% measurement; prior-consistent. Medium.
