# simulation_0075 — top-down intersection (S2MS), prior: white van length = 6 m

## Camera
- Nadir pinhole camera. Principal point is at the image centre (1080,540): the lamp-pole lines all point back to it within about 2 px. There is no barrel distortion: the curb lines are straight to within 0.5 px across the full width. There is chromatic-aberration fringing only.
- Perspective is weak. Height-dependent motion of the van gives the ratios below; using realistic van feature heights, the camera height comes out at about 60-70 m in scene units, so I used H≈65.
  - Ratio of hood-edge to roof acceleration: 1.017.
  - Slope of the windshield length: 0.0119.
- Cross-check: lamp poles have h/(H-h)=0.064, which makes them about 4 m tall at H=65 (plausible).
- Scale per height: k(h)=k_b*(H-0.45)/(H-h), with k_b = 245 px / 6 m = 40.83 px/m at bumper height. The 245 px is the van's bumper-to-bumper silhouette measured in frames 46-52, the frames where the van straddles the image centre. The dark bumper bands at both ends are included, and the length is stable at 244.3-245.5 px.

## Sizes (px measured at half-max edges vs median background; mirrors are included where they protrude, since the GT uses the AABB)
- Yellow length: 218.0 (F0) and 217.7 (F71), giving 216.5 after a perspective correction of about 1.5 px. That is **5.31 m**. Width: maximum at the rear fender, 79.4 px, giving **1.94 m**.
- Purple length: 1242 to 1437.5 = 195.5 px, giving 194 after correction. That is **4.75 m**. The grey band at x 1232-1241 was judged to be AO/shadow. Width with mirrors: 72.9 px, giving **1.77 m** (body only would be 70.5 px = 1.72 m).
- Green length: 335.4 to 529.6 (front plate) = 194.2 px raw. The rear end is far off-centre (offset -744), so its trunk edge is magnified by about 3 px; the corrected length is about 191.5 px, giving **4.69 m**. Width: maximum 73.7 px, giving **1.80 m**.
- White van width: mirror-to-mirror is about 99 px at h≈1.15, giving **2.40 m** (body only would be 87.3 px = 2.13 m; this is the main ambiguity).
- Square earthen platform: outer extent 79.6-81 px across three identical squares and both axes, slightly raised. Gives **1.97 m** (probably 2.0 m).

## Motion
- Van acceleration: the position fits are perfectly quadratic (rms 0.07 px). Across three features the acceleration is 0.2818-0.2866 px/frame², which converts to **3.95 m/s²** using each feature's height scale. It is constant from frame 1.
- Yellow car at 2.5 s: speed is constant at 6.82 px/frame throughout the turn (centroid and front/rear edges agree), giving 163.7 px/s / 40.9 = **4.00 m/s**. The turn is about 99% complete at frame 60.
- Bicycle at 1.0 s: the rear end is tracked at 8.89 px/frame and the front at 8.85 px/frame, constant and straight. That gives **5.2 m/s**.
- Pedestrian at 1.0 s: the shirt centroid moves at 2.03 px/frame (fits over windows 12-36 and 18-30 agree). Using the torso-height scale of 41.36 px/m gives **1.18 m/s**. Gait-phase variation in the GT pelvis speed may be ±5-10%.

## Confidence
- High: 64 (accel), 57 (yellow speed), 61 (bike), 55 (yellow length).
- Medium: 56 (pedestrian, gait phase), 60/66 (sedan lengths, bumper/trunk ambiguity ±2%), 62 (platform rim ±2%), 58/59/65 (widths: mirror and fender ambiguity ±3%).
- Low/medium: 63 (van width: 2.40 with mirrors vs 2.13 for the body).
