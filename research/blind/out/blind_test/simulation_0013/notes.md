# simulation_0013: bird, falling nest and cart (Blender, 1920x1954, 54 frames, fps 24)

## Scale: focal length from the nest falling under gravity (prior g = 9.8)
- The camera is static. I used a median background, plus frame 53 as a nest-free background, and tracked the nest as a dark blob. Centroid estimators: core mask, moments, alpha matte and ellipse.
- The nest is on the branch until about frame 20, falls from about 21 to 40 while tumbling, and lands at frame 41 (frames 41-53 are identical).
- Vertical pixel acceleration in the clean window (frames 29-38, not overlapping the trunk) came out between 5.0 and 6.8 px/frame^2 depending on the method:
  - plain quadratic fits: 5.0-5.6, biased by the tumbling wobble
  - velocity end points: 6.1-6.8
  - parabola plus a shared wobble sinusoid: 5.9-6.6
  - time from release (about frame 21.5, y≈343, v≈13 px/frame) to landing (y≈1748 at about frame 40.9): about 6.1-6.4
  - Adopted a = 6.15 ± 0.4 px/frame^2, which is about 3540 px/s^2.
- Nest depth: the Euclidean distance at t=1 is 4.895 m and the nest is about 772 px off-axis, so Z ≈ 4.42 m. The nest's apparent size stays about the same through the fall, so Z is roughly constant.
- This gives f = a·Z/g ≈ **1600 px** (HFOV about 62°), with an uncertainty of about ±8%.
- Cross-checks:
  - Nest landing contact (y=1888), the cart wheel ground contact (y=1141) and a near-wheel depth about 1 m in front of the cart centre give a horizon at y≈979. That means the camera is level and about 2.2 m high, which is consistent.
  - The bird's 3D heading is near-profile (it is seen side-on), which requires f below about 2500 and rules out a long-lens "realistic size" scale (f about 10000 would make the bird fly 60° toward the camera).
  - The objects are about 2.5-6x larger than their real-world counterparts, but the physics is self-consistent.

## Q1064: bird speed at t=1.0 s (frame 24)
- I fitted a smooth trend (cubic) plus flap harmonics (period about 17.4 frames) to the bird centroid. At frame 24: (1285, 743), image velocity (19.5, -1.0) px/frame.
- Velocity perpendicular to the line of sight = d·|du/dt|·fps = 9.50 m/s, with d = 34.077 m.
- Radial velocity from the depth change: -1.883 m/s (average over 0-1 s).
- Speed = √(9.50² + 1.88²) ≈ **9.7 m/s**.
- Confidence: medium. It scales about as 1/f, and the radial term adds ±0.2.

## Q1065: bird body length
- Beak-to-tail length in pixels grows over time from about 105 to about 150-155 px as the bird gets closer and turns side-on.
- Taking the maximum side-on length of about 152-155 px at frames 42-44, where Z ≈ 29.3 m (depth extrapolated linearly), gives L ≈ 2.8-2.9 m. Answer: **2.85 m**.
- Confidence: medium-low. Scales with 1/f; the tail is faint in places.

## Q1066: cart wheel diameter
- The near wheel's outer rim fits a circle with R = 100 px centred at (1935, 1041), partly outside the frame. The vertical extent is about 941-1141.
- Cart centre: Euclidean distance 26.342 m at r≈950 px, so Z ≈ 22.65 m. The near wheel plane is about 1 m closer (half the track width), so Z ≈ 21.65 m.
- D = 200·21.65/1600 ≈ **2.7 m**.
- Confidence: medium-low. Scales with 1/f, plus ±3% from the half-track assumption.

Scripts: bg.py, nest*.py, alpha.py, ell.py, fitoff.py, wob.py, track.py, birdfit.py, birdlen.py, wheel.py, final.py
