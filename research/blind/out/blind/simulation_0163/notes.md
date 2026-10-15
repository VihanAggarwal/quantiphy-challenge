# simulation_0163 (S2MC, bowling lane, 24 fps, 1920x1080, 51 frames)

## Scene / camera
- Fixed camera looking across the lanes (lanes run exactly horizontal in image: lane lines constant y to <1 px over 1250 px => no yaw/roll), pitched down.
- Vanishing points: depth (Y) direction from end-wall lines -> horizon v_h ~207 (x~960); vertical VP from 4 end-wall vertical edges (rms 0.1 px) -> v ~17,900.
  => f ~2400 px, pitch ~7.9 deg (HFOV ~44 deg).
- Independent checks of f: (1) ball silhouette off-axis elongation (width 83.6 px at left edge vs 79.3 near centre) is flat only for f~2400;
  (2) back-projected ball-return arches are perfect semicircles centred on the floor (Zc~0) only for f~2400.
- Ball scale: gradient-edge widths corrected for off-axis elongation -> f*D/Z = 79.35 px (std 0.44) for D = 0.21 m
  => 0.0026465 m/px along the lane at the ball depth (ball moves parallel to image plane, centre y constant, size constant).
- Camera height from ball centre row vs horizon: H ~1.28 m; ball depth ~6.3 m.

## Motion (ball origin = centre)
- Tracked frames 3-25 (impact with pins ~frame 26) by background subtraction (edges + mask centroid).
- Fit x(t) = quadratic + sinusoid in rolling phase (x/R; texture rotation bias, period ~5 frames); residual rms 0.3 px; best R_px ~39.7 (rolling without slip, consistent with D).
- Backward-difference speed: v(frame 11.5) = 50.80 px/f, v(23.5) = 47.90 px/f; deceleration 0.240 (t=0.5) / 0.245 (t=1) px/f^2.
- 398 speed@0.5s = 3.227 m/s; 400 speed@1s = 3.042 m/s; 399 acc@0.5s = 0.366 m/s^2; 401 acc@1s = 0.374 m/s^2 (magnitude of deceleration).

## Sizes
- 402 pin height: 4 front-row pins (top/base subpixel), full pinhole model with floor plane, base-front vs axis offset (r_base~0.037 m) corrected:
  0.3256 m (per-pin spread <0.001; without offset correction 0.332). Answer 0.326.
- 403 ball-return opening: black semicircular arch at the end of the ball-return hood (end-wall plane X~1.58 m). Back-projected contour =
  semicircle radius 0.172 m centred on the floor; height (top above floor) 0.172 m (near arch; other arches 0.163-0.172, lower resolution).

## Confidence
- Speeds: high (~2-3%). Accelerations: medium (small deceleration, +-10-15%). Pin height: medium-high (~3%).
- Opening height: medium (geometry solid; risk is which object/definition the GT uses, e.g. full-circle cutter would be 2x).
