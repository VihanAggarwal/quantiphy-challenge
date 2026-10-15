# simulation_0014: nest falls from tree; house + hand cart (static camera, 1920x1954, 24 fps, 73 frames)

## Scale chain
- The camera is static. The only moving object is the nest, which slides off a branch (frames 0-33) and then falls freely (about frames 33-49). It lands near (457, 1765) at frame 50.
- Nest track: background subtraction (frame 72 background, with frame 0 used where the nest finally lands), an AND with a darkness mask, then closing. Overlays were checked (frames/ov1, ov2).
- Free-fall fit: a 3D projective model with a pitched camera, gravity 9.8, constant depth, and fixed f and horizon. It gives f/D_fall = 338 px/m from the centroid (bbox-mid gives about 317). Corrected for Blender's default rigid-body damping, this becomes about 343 px/m. A naive image parabola gives about 6.0-6.5 px/frame^2.
- Horizon y_h is about 1108, from the house front and side vanishing points (VPs). The camera is pitched up about 4.5 deg. The vertical VP is near x=948, so there is no roll and cx is about 960.
- Focal length:
  - With the documented Euclidean range and the nest at constant depth from t=1 (centroid (158,423), R=5.630), gravity gives f of about 1600.
  - The flat-ground check (cart wheel contact against the nest landing spot, plus nest size roughly constant) is consistent with Euclidean range at f of about 1600. With the axial convention it is off by about 15%.
  - House VPs are noisy because the beams and posts are rustic. The side VP is at x of about 1241. The front VP offset K is between 9.5k and 15.5k. The VP pairs give f of about 1640-2150, with a central value near 1870.
  - The vertical-VP long edges give about 1800.
  - Final choice: f = 1700 px with Euclidean depths. This is weighted toward the self-consistent physics solution and hedged toward the VPs.
- House: the origin is assumed at the footprint centre. The roof runs along the side direction from Z to 1.49 Z (from the eave-line VP ratio), which puts the front gable plane at about 44.5 m. A ground-plane check (house base y of about 1184 against the cart wheel contact) gives the same value.
- Cart: the far and near wheels have depth ratio of about 1.20, from wheel size 95/77 px and shaft-tip contacts. The origin is placed midway between them, which puts the near-wheel plane at depth of about 24.2 m. The cart's long axis is parallel to the house front.
- Script: work/recon.py intersects the measured image points with the reconstructed 3D planes.

## Measurements (frame 72) and answers at f=1700
| qid | item | pixels | answer | confidence |
|---|---|---|---|---|
| 1067 | door leaf height | 950->1175 (225 px) on front plane | 5.96 -> **6.0 m** | medium-low (f uncertainty ±12%, house-origin assumption) |
| 1068 | wheel diameter | 190 (h) x 185.6 (v) px, near wheel | **2.62 m** | medium-low |
| 1069 | eaves width | left tip x=311, right tip x=1041 (front gable), plane rotated about 9.6 deg | **20.2 m** | medium-low |
| 1070 | cart max height | box top-right corner y=1017 vs wheel contact 1249 | **3.27 m** | medium-low |
| 1071 | cargo box height | about 85-87 px perpendicular to box axis (box tilted 14 deg) | local 1.20; world AABB would be 2.32. Answered **1.25 m** (local interpretation) | low |
| 1072 | cargo box length | top edge 4.44, bottom edge 4.84, horizontal extent 4.71 | **4.7 m** | medium-low |

## Sensitivity
- The alternative hypothesis (axial depth, f about 1880) gives values about 9% lower: door 5.44, wheel 2.45, eaves 18.3, cart 3.05, box H 1.12, box L 4.4.
- The pure-physics Euclidean solution (f about 1600) gives values about 6% higher.
