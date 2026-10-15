# simulation_0186 — gift box dropped onto a ramp, then sliding down it (A3SC, 24 fps, 40 frames)

## Camera calibration (fixed camera)
- Pitch and roll are zero: the vertical wall corner is exactly vertical in the image. Back-wall mortar rows converge at VP (-5123, 540), and 4 rows fit with 0.24 px rms. So the horizon is y = 540 = cy.
- Perpendicular horizontal direction: side-wall brick rows give a VP at about x = 1646–1780 (mean 1720), the platform plank seam gives about 1711 and the platform edge about 1683. I used VP_perp = (1711, 540).
- f^2 = (1711-960)(960+5123) gives **f ≈ 2137 px** (HFOV about 48.4°).
- The two ramp long edges meet at x ≈ -5200, the same x as the wall VP. So the ramp runs parallel to the wall, sloping down at 28.5° and coming toward the camera.

## Track and 3D reconstruction
- Box mask from a median background and frame differencing; I used the mask centroid (the bbox centre gives the same results).
- Frames 0–8: free fall from rest (x constant, released at about frame -0.1). From frame 9 the box slides along the ramp line through the landing point.
- **Depth convention check:** with the range (Euclidean) convention, the reconstructed range at t = 0.5 s is 9.741, matching the given 9.741 exactly. Under the optical-axis Z convention it would be 9.796. Range convention confirmed.
- Physics consistency at f = 2137:
  - Free-fall acceleration is 9.72 m/s^2, matching g = 9.81 with Blender's default damping (about 9.74).
  - Ramp acceleration from a quadratic/cubic fit is 3.20–3.22, close to the prior of 3.18 (within 1.2%).
- The final scale is a compromise between the prior and gravity calibrations (about 0.995).

## Answers
- Q1434, acceleration at 0.2 s: the box is in free fall, so I answered g with damping, **9.75** (measured 9.72). Confidence high.
- Q1435, speed at 1 s: backward difference at frame 24 is 3.22 (raw and smoothed), so **3.21**. Confidence high.
- Q1436, speed at 1.5 s: backward difference at frame 36 is 4.81–4.83, so **4.80**. Frame 39 was excluded because the box is clipped at the image bottom. Confidence high.
- Q1437 / Q1438, box size: a cuboid silhouette plus ribbon-centreline fit over 10 frames gives:
  - Local box dims of 0.400 along the ramp × 0.379 across × 0.375 along the normal. The box is aligned with the ramp; yaw is within about 2°.
  - The bow rises about 0.15–0.17 m above the top face.
  - The box is spawned tilted 28.5°, so the world AABB at frame 0 is 0.537 along the wall, 0.41 perpendicular to the wall, and 0.545 vertical without the bow. With the bow it is 0.626 vertical (about 0.60 on the ramp).
  - The size convention is ambiguous (local vs world AABB, bow included or not), so I hedged:
    - **length 0.42**: local about 0.39–0.40, AABB 0.41 or 0.537.
    - **height 0.575**: local + bow about 0.535, AABB without bow 0.545, AABB with bow 0.60–0.63, local body 0.375.
  - Confidence medium-low, because the convention is uncertain. The measurements themselves are about ±3%.
