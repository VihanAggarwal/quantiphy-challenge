# simulation_0022 — boat moving left and slightly toward a fixed camera (960x960, 75 frames, dataset fps 24)

## Measurements (scripts in work/)
- Tracked the hull by red threshold, and the bow and stern by subtracting a static background. The background combines frame 0 (x<805) and frame 74 (x>=805).
- Bow tip x(t): 831.5 at f0 down to 483.8 at f74. It moves about -4.6 to -4.86 px/frame, and the speed-up is fully explained by perspective. A constant-acceleration fit gives acc ~ 0, so the speed is constant.
- The stern is visible from f35 onward. Projected length s(f36)=285.2 px and s(f48)=287.7 px. Growth is 0.215-0.233 px/frame (diff- and red-edge methods).
- Mast column x(t) was tracked. The mast top is at row ~391.4 (f24) and ~389.6 (f48), with about 1 px noise because sky contrast is low.
- The waterline (hull meets reflection) is at 679.9 (f24) and 682.4 (f48). Vertical extent at f48 is about 292.5 px.

## Geometry / scale
- Fitted a 3D constant-velocity rigid-boat model. Parameters: f, X0, Z0, vx, vz, mast offset. Inputs: bow, stern and mast image tracks, plus the Euclidean distances D(1s)=148.7451 and D(2s)=146.9726 to the boat centre. Boat length L=10 m from the prior. Heading is tied to the velocity direction, or offset by dphi.
- Euclidean range fits the length-growth signal much better than the optical-axis Z convention (sse 26-30 vs 53-58).
- f is about 4270-4710 px (hFOV ~11.7-12.8 deg). The spread comes from the unknown stern shape (rounded stern vs transom half-width 0-1.3 m) and a heading offset of 0 to -4 deg. The length-growth data mildly prefer a dphi of about -3 deg or a small transom.
- Velocity is about 23 deg off the image plane, toward the camera. Radial speed is 1.77 m/s and transverse about 3.6 m/s.

## Answers
- 1099 speed at 1.0 s: across variants |v| = 3.86-4.18 m/s, central about 4.0. Answer **4.0 m/s**. Confidence medium-high (about ±4%).
- 1100 height: visible extent (mast top to waterline) times Z/f gives 9.1-10.0 m across variants, central 9.5. Added a small allowance for keel or forefoot below the waterline: the stem is still curving at the waterline. Answer **9.6 m**. Confidence medium (about ±5%). Main risks: the scale (stern geometry, heading) and how deep the hull sits under water.
