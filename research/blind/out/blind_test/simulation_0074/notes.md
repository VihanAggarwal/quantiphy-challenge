# simulation_0074 - notes

Scene: a 4-way intersection seen by a static, high Blender camera. The white car is a Chevy Express van (prior L = 6 m). The yellow taxi turns right, from road direction -B onto +A. A bicycle rides along -B, a pedestrian walks along +A on the far sidewalk, and a purple Mercedes and a green car are parked.

## Camera
- Fitted the curb lines of the road mask. VP_A = (-1283, -253.6) and VP_B = (2677, -252.4), so the horizon is at y = -253 with zero roll.
- f from orthogonal VPs (principal point at the image centre) = 1773. The lamp-post vertical VP gives about 1780-1795. Used f = 1785 (hFOV about 62 deg) and pitch 23.95 deg.
- Checks:
  - The 3 lamp posts on the far sidewalk come out equally spaced (8.02 / 8.04 m). This confirms the horizon.
  - The rear-left corner of the van is predicted within 0.1 px in frames 5-60 from the frame-71 model plus the plate track.
- Camera height h, from several routes:
  - van length prior: body plate-to-rear L/h = 0.6204, plus bumpers about 0.626, gives 9.58-9.62
  - pedestrian pelvis depth (range): h - s = 9.49, so 9.6-9.7
  - bike absolute depth: 9.5-9.6
  - Used h = 9.58.
- Depth convention: range (Euclidean) fits better than camera-Z. The pedestrian's dR is predicted at 0.827 against 0.821 given; Z predicts 0.71.
- The bike and van depth differences come out about 5% and 10% smaller than the geometry predicts. This could be a timing or interval quirk (about 22.5 frames instead of 24), so I did not use them for the scale.

## Measurements (h = 9.58)
- **Van:**
  - Tracked the license plate (z = 0.061 h). The van drives straight along the road, with lateral drift under 2 cm, from rest at constant acceleration: a = 4.03 m/s^2 (cubic and local quadratic fits give 4.02-4.05).
  - Height: the rear roof edge silhouette gives 2.25 in frames 0-30, and the rear corner gives about 2.15 in frame 71. Answer 2.22.
  - Width: body about 2.01. Mirror-to-mirror, triangulated over frames, is 2.44-2.54. The mirror mid-plane matches the plate plane. Answered 2.38 as a hedge leaning towards including the mirrors.
- **Taxi:**
  - Two-box sedan silhouette fit plus broadside extremes in frames 30-32. L = 5.60-5.63.
  - W body = 2.0. Answered 2.1 to allow for mirrors.
  - Roof about 1.47. The top of the roof sign is at 1.66-1.76. Answered H = 1.68, sign included.
  - Path from per-frame pose fits (polynomial-smoothed) is 12.5 m in 2.96 s, so the average speed is 4.22.
- **Purple car (static):**
  - Wheel contacts give wheelbase 2.99 and yaw along the road.
  - Overhangs are about 0.65 in front and 1.1 at the rear, so L is about 4.74. A single-view box fit gives 4.6.
  - Front bumper chrome spans 1.69-1.71, so W is about 1.75-1.8.
  - H = 1.42-1.51 from the box fits.
- **Pedestrian:**
  - Mask-based height is 1.95 (median) and 2.0 (p90). The depth-based check gives 1.93-2.02. Answer 1.96.
  - Linear fit of the head-top and feet tracks gives a speed of 1.22, slightly raised to 1.23 for gait sway.
- **Bicycle:**
  - Front-wheel contact track gives a near-constant speed of 5.44-5.59 (mean 5.53). The depth difference suggests about 5.3. Answer 5.5.
  - Wheel ellipse fits give a diameter of 0.62-0.665. Answer 0.65.
- **Square platform** (on the sidewalk, top at about 0.2 m): sides and diagonals give 2.03-2.07. Answer 2.05.

## Confidence
- High: platform, van acceleration (scale-linear), taxi length, purple car height.
- Medium: van height, human height and speed, bike speed and wheel, taxi speed, purple car length and width.
- Low: the van, taxi and purple car widths, because it is unclear whether the GT includes mirrors. Taxi height is also low, because it is unclear whether the roof sign is included.
