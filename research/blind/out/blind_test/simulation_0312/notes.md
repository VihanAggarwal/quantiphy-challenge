# simulation_0312: red puffy star on a plain beige background (no ground cues), 72 frames at 24 fps, 1080x1080 (upscaled 2x)

## Method
- Soft alpha mask from the green-channel deficit against the uniform background (184.8). Holes filled; sub-pixel centroid and extents per frame.
- Built a parametric 3D star silhouette model: a regular 5-point star polygon (R, inner ratio q, 2D tip rounding c), extruded by T0 and Minkowski-rounded by b. It is rendered with a pinhole camera (4x supersampled, Gaussian blur) and fitted jointly over 16-17 frames by Nelder-Mead.
- Fit result: the star has a FIXED orientation (a rotating-star model gave only about 0.9 deg/s). The camera is level (roll -0.2 deg) and pitched down about 18.4 deg. The star stands upright, yawed about 64 deg from the view axis. The change in its look comes from the change in viewing direction.
- f is about 1459 px (FOV about 40 deg), from star height 0.2 m plus the depth anchors (Z convention). Under the range convention f is about 1428.
- Per-frame depth from model scale fits. World height of the star is constant, so the motion is planar (horizontal). The trajectory in the ground plane is a near-perfect circle (rms 1 mm), radius about 5.1-5.3 m, at constant angular rate 0.402 rad/s. So this is uniform circular motion.
- Depth convention: the measured Z48/Z24 is about 1.262-1.270, between Z (1.274) and range (1.256), so the evidence is ambiguous.

## Answers
- 1631 average speed: omega*r = 2.127 (Z conv, f=1459) / 2.098 (range conv, f=1428); other routes give 2.06-2.16. Displacement/time would be about 1.99. Answer 2.08 (confidence: medium-high).
- 1632 width: W/H = 1.042 (fit4) to 1.061 (free x-scale fit); regular star geometry gives about 1.05. Answer 0.21 m (medium-high; assumes star axis-aligned in world).
- 1633 thickness: T/H = 0.10-0.139 across model variants, best fits 0.133-0.139. Answer 0.027 m (medium).
