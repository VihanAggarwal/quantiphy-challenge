# simulation_0035 — person walking on shore + eagle flying (S3MC, 1080x1080, 24 fps, 72 frames)

## Camera / scale
- Static camera. Person height prior 1.75 m. Person pixel height measured per frame by temporal-median
  background subtraction + half-max edges (head top / feet bottom): median 39.8 px, p75-p90 40.1-40.4 px -> use ~40.2 px.
- Depth convention: Euclidean range fits better. Image-track curvature of the eagle (constant 3D velocity) implies
  dZ/dt ~ 7.9-8.2 m/s (same-phase 3-point solves median 7.93); Euclidean conversion of given ranges gives 7.9,
  Z-convention 7.46 -> Euclidean adopted.
- Person pelvis ~7.5 deg off-axis -> Z = 139.10*cos = 137.9 m -> f = 40.2*137.9/1.75 ~ 3170 px (HFOV ~19 deg). Range 3135-3230.

## Q1145 person average speed
- Torso/mass-centroid x regression: 25.2 px/s lateral, 1.8 px/s down. m/px at person = 1.75/40.2 = 0.0435.
- Lateral 1.096 m/s; range constant (139.1030 -> 139.1044) implies small away component (~0.12 m/s) under Euclidean;
  vertical ~0.08 m/s -> |v| ~ 1.10 m/s. Confidence: medium-high (+-4% from pixel-height ambiguity).

## Q1147 eagle speed
- Eagle segmented as dark blob vs temporal-median sky; flap period ~24 frames (so frames 24 & 48 share phase).
- 3D positions from centroids + given ranges at t=1,2 s (Euclidean): |P2-P1| = 11.8 m/s (frames 20..28 pairs: 11.67-11.94).
  Full-track constant-velocity fit with periodic flap terms agrees (11.7-11.9). Heading ~48 deg right of optical axis
  (Vx~8.75, Vz~7.9 m/s). Z-convention would give 11.55. Answer 11.8. Confidence: medium-high.

## Q1146 wingspan
- Horizontal (mid-downstroke) frames: half-max tip-to-tip horizontal extent 28.6 px (f6, D=134.5), 29.4 px (f30-31, D=141.6),
  27.3 px (f53) -> projected 1.21 / 1.31 / 1.28 m.
- Eagle is yawed (body appears elongated, cycle-to-cycle span growth c2/c1 = 1.09 implies heading ~45 deg; velocity heading 48 deg).
  Wing axis foreshortening cos(psi_rel) with psi_rel ~50-56 deg -> W ~ 2.04-2.14 m. Rigid-wing V-pose analysis suggested a
  somewhat smaller yaw (W ~1.8), so 2.1 is a central estimate. Confidence: low-medium.

## Q1148 body length
- Dark torso projected ~0.5-0.75 m horizontally (V-pose bottom band 11-13 px, upstroke frames 16-17 px); with yaw ~50 deg
  gives 0.55-0.85 m; head/tail possibly white (bald eagle) and blended with sky. Typical eagle length/wingspan ~0.42 -> 0.88.
  Answer 0.85 m. Confidence: low.
