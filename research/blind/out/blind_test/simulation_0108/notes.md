# simulation_0108 — two viruses, V2MX, 24 fps, 72 frames (frame 0 == frame 1)

Scene: plain grey background. Left virus moves straight up (~12 px/frame) and leaves the top edge around frame 50.
Right virus moves right (~13.7 px/frame) and leaves the right edge around frame 54. Neither virus rotates in the world.

## Measurements
- Core (body sphere) found by thresholding gray<150 and a 71 px morphological opening, then a circle fit
  (also on partially visible arcs). Frame 1: L centre (722.1,570.4) r=124.1; R centre (1306.8,614.0) r=139.8.
- Red spike tips tracked (65 tracks). Each tip shifts relative to the core centre in proportion to how far the
  centre is from the optical axis (beta = -q_z/f). Tips near the disc centre give beta ~0.100 (L) and 0.102 (R).
  These sit on a sphere of radius about 236 px (L) or 260 px (R). Result: **f ~ 2600-2770 px**, which matches
  Blender's default 50 mm lens on a 36 mm sensor (2667 px). Both viruses give the same f, so neither rotates in the world.
- How fast each virus grows on screen (depth motion): L grows about +5.2% from frame 1 to 36 (side tips 5.3-5.7%, ECC x-scale 5.3%,
  core radius 6.5%, projective track fit 3.9%). R stays about 0% (−0.9 to +0.6%).
  So L moves up in the camera frame and toward the camera, about 16° out of the image plane. R moves almost exactly along +x.
- 3D linear constant-velocity model in core-radius units (f=2667). Speed scale: 1.7393 m/s = |V_L| (3D).

## Answers
- Q221 v_L(1.0 s): the motion is linear (constant 3D velocity, no easing), so the speed equals the prior: **1.7393**. Confidence high.
- Q222/223 distance (origin = core centre). There are two hypotheses we cannot tell apart from the images:
  - A, same size (duplicated asset). R is about 11% closer to the camera. D(24)=5.37 (5.32-5.42), D(48)=7.48 (7.38-7.58).
    Under A the right virus's 3D speed comes out at 1.74-1.76 m/s, equal to the left's 1.739. That coincidence favours A.
  - B, same depth / coplanar motion. R is 13% larger. D(24)=5.70 (5.61-5.86), D(48)=8.15 (8.02-8.42).
    The naive 2D pixel-scale answer, 5.67-5.73 and 7.77-8.24, is close to B.
  - Submitted values hedge between the two and lean towards A: **5.50** and **7.74**.
    Each is within about 3% of A and within about 3.5% (D24) and 5% (D48) of B. Confidence medium.
- Time convention: video frame index = t*fps (24, 48). A ±1 frame shift moves the distances by about 1.5%.

Scripts: scripts/*.py (track, core, ecc, tips, link, fitf, fitf2, scalefit, sidescale, projfit, geo3d, answers, late, veltrend).
