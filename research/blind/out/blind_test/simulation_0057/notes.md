# simulation_0057 — notes

The scene is a top-down (nadir) Blender view of a road, 1080x1080 at 30 fps with 91 frames. An orange car drives down the left lane (+y in the image) and slows down. Two black post-top street lamps stand on the left sidewalk. Prior: the car's acceleration is -2.86 m/s^2.

## Scale from the prior
- The background was made by stitching frame 90 (top rows) and frame 0 (bottom rows). A whole-car template from frames 40, 60 and 75 was tracked with TM_CCOEFF_NORMED and parabolic sub-pixel peaks.
- A quadratic fit of y(t) gives a pixel acceleration of -164.9 px/s^2 (range -164.7 to -165.3, residual rms 0.04-0.08 px). The deceleration is constant.
- So k = 2.86/164.9 = 0.017344 m/px at the height of the template features (roof, glass and hood, roughly 1 m up).

## Perspective (this matters)
- The lamps lean radially away from the image centre. The base, collar and lantern lie on radial lines through (540,540). The lantern sits at 0.1575*H, so the camera is perspective and fairly low (FOV about 45-50 deg).
- Sub-templates on the car move at different speeds because they sit at different heights. Relative to the whole-car template: roof/antenna 1.0103, rear window 1.0035, windshield 1.000, hood vents 0.9944, nose 0.9855.
- The rear ground shadow (ratio image, car masked out, 2D shift search over frames 58-89) moves at 0.939-0.947 of the template speed. I took a ground/template ratio of 0.941, so k_ground = 0.01843 m/px and z_roof/H is about 0.07.

## Answers
- **Q31, lamp distance.** Fitting circles to the bottom rims of the bases gives (251.6,465.1) and (250.9,909.5), a separation of 444.4 px at ground level. The lantern separation (527.5 px) agrees through the factor 0.8425. 444.4 * 0.01843 = **8.17 m**. Confidence: medium-high, about ±2% from the shadow ratio.
- **Q30, car length.** I took 50% orange edges on central columns over frames 40-90: 288.7 px on average. Frame 90 gives 288-290 px; the front end is at the nose and the rear starts at about 760. Correcting for the height of the outline points (z/H about 0.022) gives 282-284 px at ground scale, so L is about **5.2 m**. Confidence: medium.
- **Q32, car width.** The body is 293 to 405.5 px; the mirrors span 283.3 to 408 px. With the lateral parallax correction this gives 1.98 m for the body and 2.19 m including mirrors. It is unclear whether the bounding box includes the mirrors, so I answered **2.13 m**, leaning towards including them. Confidence: medium-low (about ±5%).
