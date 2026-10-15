# simulation_0304 — whale (V3SX, prior: speed 1.67 m/s; depths 33.7307 m @1 s, 35.1624 m @2 s)

## Geometry facts from the prior
- Radial (range) rate of origin between t=1 and 2 s: 1.4317 m/s. With |v|=1.67 m/s, constant-velocity line gives
  |P0|=32.32 m, P0·v=45.13; angle between v and origin line of sight ~31 deg; lateral speed ~0.86 m/s.
- The whale swims AWAY from a fixed camera, head first (head up-left, tail/flukes lower-right, strongly perspective-magnified).

## Measurements (scripts in work/)
- Background = smooth blue gradient -> cubic-poly background model, whale mask by colour distance (masks.py).
- Head template track (track_head.py): very smooth, straight image path, ~83 px/s early to ~67 px/s late (projective decay).
  Frame 0 is a duplicate of frame 1.
- Head appearance is nearly constant over the clip (scale-normalised montage), so head rotation is small.
- SIFT affine of the head vs frame 36 (sift_affine.py): scale across the body axis goes as 1/Z, along the axis as 1/Z^2
  (as expected for a line receding along its own direction). Fits give head-centre depth at t=1.5 s: 36-40 m.
- Vanishing point V of the motion fitted from the head track for each head depth (fitV.py); front point (rostrum) and
  fluke notch are collinear with V at mid-beat (frame 52) -> whale moves along its body axis.
- Whale length from the projective structure along the axis (f-independent): a point at image distance r from V has axial
  coordinate lambda = (Z_h/cos a)(r_h/r - 1), cos a = vz/|v| = 0.857. Measured rostrum and notch at frames 1,4,46,48,52,56.
  Head depth 36.5-39.5 m -> L(rostrum->notch) 19.1-19.9 m (mean over frames 19.4-19.7; tail-beat spread +-0.5 m;
  regression to straight tail ~19.1 m).
- Cross-check: requiring the origin (cone of 31 deg around v at range d) to lie on the body axis gives (f, Z_head@1.5 s) pairs
  (3300, 36.5), (3556, 38), (3800, 39.5): f ~3556 px (the 50 mm / 36 mm default Blender camera, HFOV 39.6 deg) matches the
  scale-based depth; the origin then sits about mid-body. Implied head width ~2.6 m, flukes ~4.4 m+, pectoral fin ~4.5 m+:
  coherent for a ~19-20 m humpback-shaped model.

## Answers
- 1474 whale length: 19.5 m (rostrum-to-notch ~19.0-19.7 plus small fluke-tip sweep). Confidence: moderate (about +-10%;
  relies on whale swimming along its axis and on the measured head depth; length is insensitive to focal length).
- 1475 displacement 0.5->1.0 s: 1.67 m/s x 0.5 s = 0.835 m (constant-velocity straight path; head track consistent with
  constant velocity). Confidence: high.
