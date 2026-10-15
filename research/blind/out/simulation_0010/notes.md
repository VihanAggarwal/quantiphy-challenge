# simulation_0010 - notes

Scene: fixed Blender camera, 1920x1954, 59 frames @24 fps. A crow-like bird flies left->right in front of a timber-framed
gable house (crossed gable beams), a wide two-wheeled hand cart sits on the right (handles on the ground).

## Calibration
- Bird length 1.19 m = beak-to-tail extent. Measured it by hand on 12 clear frames: 135-153 px, median L*Z = 4920 px*m
  -> f = 4140 px (HFOV about 26 deg). Bird depth comes from the given ranges converted to optical-axis Z: Z0 = 34.20, Z1 = 33.94.
- Ground geometry (assuming flat ground and zero roll):
  - Bird shadow: the shadow's image x-velocity is 1.04x the bird's, so the shadow is at Z = 32.6 m (image row v = 1228).
  - Horizon: lines parallel to the house long axis / cart axle (right eave rafter line, the two wheel-bottom points, the
    two handle-tip points) meet near v = 975-1050, central ~990. This is consistent with the cart-origin depth check
    (the wheel midpoint lands at the given cart range). The camera is about level (pitch about -0.1 deg) at height about 1.9 m.
  - House facade base (v = 1174) -> facade Z about 42 m (41.5-43 for horizon 975-1000). The given house range (55.08 m) is the origin,
    about 12 m behind the facade, so the house is a long house. Used Z_facade = 43.0 (slight hedge toward the origin prior);
    eaves taken 0.3 m in front of the wall. House yaw about 3.3 deg (long-axis vanishing point x about 724).
  - Cart: near wheel depth Z about 28.3 (origin Z 29.94 minus half of the about 3.1 m track).

## Answers
- 1053 eaves width: tips at x = 80 and 1026 (946 px) on the facade plane -> 9.72 m. Confidence medium-low (facade depth is
  the main risk: if the facade were at the origin range it would be about 12.4 m).
- 1054 door height: door leaf/opening 275-281 px (277 used) at the facade -> 2.87 m. Same risk as 1053.
- 1055 cart max height: rear top corners at v = 1011, wheel bottom at v = 1266.7, Z = 28.3 -> 1.75 m (h + (v_h - v_top) Z/f
  also gives 1.73). Confidence medium.
- 1056 wheel diameter: near wheel rim 205 px tall at Z 28.3 -> 1.40 m. Confidence medium.
- 1057 bird speed 0.5-1.0 s: smoothed over one flap period (17 frames; the centroid bob comes from the wings, the tail y
  stays flat). du is 256-265 px over 12 frames (centroid, beak, tail), plus a small depth change -> 4.29 m/s. Confidence
  medium (scales with the bird-length calibration, about 4%).
