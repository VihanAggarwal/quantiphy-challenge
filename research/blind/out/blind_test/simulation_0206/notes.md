# simulation_0206 — typewriter falling onto a desk (3D Blender, 24 fps, 2124x1080, 30 frames)

## Camera
- Typewriter free fall (frames 0-10), keyboard tracked by chained template matching (sub-px).
  A 3D free-fall fit with g=9.8 m/s^2 and range 4.32 m gives f/R = 629 px/m, so f = 2717 px.
  The fit also gives the vertical vanishing point at about (971, 10706), so the pitch is about 15.0 deg
  (rms 0.04 px in y).
- Cross-checks:
  - The pitch comes out at exactly 15 deg when f = 2724.
  - Desk edges, back-projected, are orthogonal to within about 1-2 deg at f of about 2650-2750.
  - The desk is yawed 29.6-29.9 deg relative to the camera, which suggests the camera is set at (75, 0, 30) deg and the desk is aligned to world axes.
  - The paper sheet rectangle back-projects to 90.2 deg and the letter corner to 90.1 deg.
  - The range change from 4.32 to 4.50 at t=0.5 matches the measured fall.
- Model used: f = 2724, pitch 15 deg, roll about 0 (also checked with the roll-0.5 deg variant).
- Desk-top plane is about 1.36 m below the camera, measured along the vertical. Evidence:
  - The FL corner at range 3.593 gives 1.339.
  - The gun origin at range 4.704 sits at about 1.346, plus some offset for its thickness.
  - The front-right corner, if it is the "far right" one at 5.009, gives 1.39.
  - The typewriter landing time and its range at t=0.5 are consistent with about 1.36.
- The given "far right" range of 5.009 does not fit the back-right corner, which would be about 5.5. I treated it as roughly the front-right corner.

## Answers
| qid | question | answer | basis | confidence |
|---|---|---|---|---|
| 1574 | table length | 2.36 | desk-top corners on plane h=1.36: 2.32-2.36, plus about 3 cm moulding | medium |
| 1575 | table width | 0.94 | same: 0.92-0.94, plus about 2 cm | medium |
| 1576 | typewriter length | 0.39 | local side-to-side extent 0.33-0.40 (carriage); world AABB at frame 0 is about 0.40-0.43 (yaw about -14 deg vs desk) | low-med |
| 1577 | typewriter width | 0.32 | local depth about 0.29 (base edge at rest, on desk plane); AABB at frame 0 is about 0.34-0.37 | low-med |
| 1578 | typewriter height | 0.19 | paper-rest top above the base: 0.18-0.19 (rest and flight agree) | medium |
| 1579 | speed t=0.125 | 1.10 | backward difference frames 2 to 3 of the 3D fall track (v0 = 0.08 m/s, a = 9.8) | high |
| 1580 | speed t=0.25 | 2.32 | frames 5 to 6 | high |
| 1581 | speed t=0.333 | 3.14 | frames 7 to 8 | high |
| 1582 | paper width (next to typewriter) | 0.20 | sheet 0.187 x 0.282 m, rotated 5 deg from the desk; AABB short side is 0.21. If "width" means the Y size, the answer would be about 0.29 | low-med |
| 1583 | letter under gun, length | 0.24 | visible short side 0.132 m along the desk depth; the long side is hidden under the gun (at least 0.10). The paper under the keys measures 0.125 x 0.25, so the letter is assumed to be the same asset | low |

Scripts are in work/. They use a small built-in Levenberg-Marquardt solver because the venv has no scipy.
