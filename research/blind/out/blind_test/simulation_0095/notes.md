# simulation_0095 (A2MX, 2D, 24 fps, 72 frames, 1920x1080)

Scene: plain grey background. An Air China A320-type airliner (side view) flies left at constant speed and leaves the frame at about frame 32. A Cybertruck-type pickup (side view) starts from rest and accelerates to the left over the whole clip. Frames 0 and 1 are identical. Prior: car acceleration = 10 m/s^2.

## Method
- Per-pixel median background (plane-free frames for the upper half; complementary halves for the car band). Diff masks and subpixel edges are based on coverage and half-contrast.
- Scale: quadratic fit of the car trajectory (frames 2-71).
  - bbox centre: a = 290.1-290.7 px/s^2 (rms 0.36 px).
  - Template on the car's near side: 293.5 px/s^2. The near side sits about 1 m closer to the camera, so it is magnified by about 0.8% at Z of about 130 m.
  - Adopted origin a = 291 px/s^2, so s = 29.10 px/m (0.03436 m/px).
- Plane velocity: template and edge tracking of centreline features (nose tip 73.01, fin top 72.96, tail logo 73.03, tail cone 73.19 px/frame) gives 73.02 px/frame (1752 px/s). Features on the near side of the fuselage move 74.15 px/frame and the near engine about 76.3, which is the expected perspective parallax. Speed is constant, so v(0.5 s) = 60.2 m/s.
- Perspective check: the fuselage-side parallax (d/Z = 0.0153) and the fuselage half-width (about 57 px) give f of about 3700-3900 px (HFOV about 28 deg). Engine parallax (d/Z = 0.044) fits A320 proportions. Car Z = f/s, about 130 m.
- Same-depth check: at the car scale the car comes out at 5.63 m (Cybertruck 5.68 m) and the plane at 37.8 m (A320 37.57 m). Both are real-scale at one shared scale, so the 2D single-scale assumption is used.
- Car length: the coverage-edge length is smallest near the image centre at 164.2 px; it grows to about 171 px at the edges from end-face perspective. The near-corner magnification correction (about 0.5%) gives 163.3-164.2 px, so 5.63 m.
- Car height: coverage height is 54.37 px. Removing the perspective spread (near tyres lower, far side of the roof higher, about 1.1 px) gives 53.2-54.4 px, so 1.85 m.
- Plane length: nose tip (half-crossing of the low-contrast grey nose) to the end of the APU tail cone, measured on centreline points at the same time: 1100 +/- 2 px, so 37.8 m.
- Plane height: fin tip at y = 170.0. The lowest visible point is the far nacelle at 496.8 and the near nacelle sits at 491.5. Converting both to origin depth with d/Z = 0.044 gives about 494.1. Height is 324-327 px, so 11.16 m.

## Answers
| qid | quantity | answer | confidence |
|-----|----------|--------|------------|
| 164 | plane speed | 60.22 m/s | high, if plane and car share a depth |
| 165 | car length | 5.625 m | high |
| 166 | car height | 1.849 m | medium-high (perspective and AABB of the wheels) |
| 167 | plane length | 37.8 m | high, if same depth |
| 168 | plane height | 11.16 m | medium-high |

The main risk: the plane and the car might sit at different depths. Geometry cannot decide this, because nothing ties the two objects together. It is ruled unlikely because both come out at real-world size on the same scale.
