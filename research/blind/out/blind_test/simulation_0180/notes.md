# simulation_0180 — trolley accelerating along the back wall (static camera)

## Camera calibration (from background median of all 60 frames)
- LSD line segments -> 3 vanishing-point families: floor lines along the wall (X), floor lines into depth (Y), verticals (door frame).
- Joint fit with the principal point at the image centre: f = 2657 px (cost minimum; 2600-2700 band), yaw -12.8 deg, pitch 7.03 deg down, roll 0.
  Used f = 2666.7 px (50 mm lens on a 36 mm sensor) which fits equally well. A bird's-eye rectification gives square tiles, which confirms f and the rotation.
- First VP fit for X was biased by the platform edges; after removing them, the horizon is level and agrees with the wall lines and the door-frame verticals.

## Scale (camera height H)
- Trolley track = midpoint of the near-wheel ground contacts mapped to the floor plane. Motion is purely along world X (parallel to the wall) at constant Y.
  X(t) is an exact quadratic: rms 0.0004 H, starts from rest at t = 0.00 s, cubic term negligible. Acceleration is 0.4549 H/s^2, so the prior 1.507 m/s^2 gives H = 3.3125 m.
- Independent checks, all consistent within 0.2%:
  - Floor grid pitch: grey tiles 1.000 m, orange tiles 0.500 m.
  - Ceiling / wall top: Z = 3.99 m (about 4.0).
  - depth_info: the Euclidean range to the ground point under the cart's wheel centre is 12.588 / 12.512 m, against 12.589 / 12.513 given. So the origin is at floor level at the cart centre, and the convention is Euclidean range.

## Answers
- 1418 trolley length (X extent): rear handle tip (near end, Y = 10.737) to front castor wheel (Y = 11.16). Median over frames 0-42 is 1.105-1.112 m. **1.11** (confidence: medium-high, +/- 3%).
- 1419 trolley height: from the floor to the top of the handle (far end, Y = 11.223). The handle Y comes from symmetry plus the near/far end ray ratio. Result 1.168 m. **1.17** (confidence: medium-high).
- 1420 entrance gate height: the wooden casing post sits in the plane X = -7.83 m. Its bottom edge on the floor is at Y = 13.39, and its top corner on the same vertical line is at Z = 3.99 m (it meets the ceiling at 3.99). **3.99** (confidence: medium; the object could extend above the ceiling).
- 1421 orange tile side: the orange face measures 0.461 m (X) and 0.45-0.46 m (Y), on a 0.500 m pitch with about 0.04 m of grout. Answered **0.48** to hedge between the face (0.46) and the pitch (0.50); both are within 5%. (confidence: medium)
- 1422 / 1423 speed: constant acceleration from rest, so v = a*t. Instantaneous values are 1.507 / 3.014 m/s; backward differences are 1.476 / 2.983 m/s.
  Measured local speeds at t = 1 s and 2 s are 1.51 / 3.015 (instantaneous). Answered **1.49 / 3.0** (both conventions are within 1-2%; confidence high).
