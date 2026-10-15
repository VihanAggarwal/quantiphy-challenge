# simulation_0011 — bird / falling nest / house / cart (Blender, 1920x1954, 24 fps, 60 frames)

## Camera
- Static camera. Vanishing points from the house: facade horizontals (4 long beam edges + sills) give VA ~ (-1800, 1283);
  side-wall beam (slope 0.158, both edges) and roof-plank edges (0.244-0.255) give VB ~ (2510, 1283);
  60 LSD vertical segments give a vertical VP at y ~ -12800 (x ~ 942).
- Horizon y = 1283 -> camera pitched UP ~8.5 deg, no roll. Principal point at image centre is consistent with the
  orthocentre of the 3 VPs.
- f from (VA,VB) orthogonality = 2046 px; f from horizon x vertical-VP = 2053 px. Gravity cross-check from the falling
  nest (alpha-matte centroid, parabola fits, pixel acc ~1100-1250 px/s^2, noisy because the nest tumbles) gives
  f ~1950 (z-depth convention) or ~1780 (Euclidean-range convention). Used f = 2040 px, depth = optical-axis Z
  (range convention would make gravity and VPs disagree by ~13%; z-convention by ~5%).
- Camera height from ground plane: nest landing 2.38 m, cart wheel contact 2.24 m, house origin (footprint centre) 2.30-2.40 m -> h ~2.30 m.

## Answers
- 1058 bird avg speed 0.5-1.0 s: bird body track (background-subtraction mask centroid, cubic/quartic smoothing over flap
  cycle), straight-line 3D path through the t=0 / t=1 depth points (46.654 / 43.970 m); depth progress tied to lateral
  progress (bird is accelerating). |P(24)-P(12)|/0.5 = 6.1-6.45 m/s (linear-in-time depth gives 5.8). Answer 6.1. Confidence medium.
- 1059 door height: doorway 204 px (y 1150.5-1354.8), door leaf ~197 px. Intersected with the facade plane (ground-plane
  reconstruction, h=2.3): 5.34 m (doorway) / 5.29 m (leaf). House-origin based (footprint centre at Z=63.6): 5.3-5.55.
  Answer 5.3. Confidence medium.
- 1060 wheel diameter: near wheel outer rim, vertical extent 169.3 px (1260.7-1430), nearly circular (170 px wide).
  Hub depth: cart origin Z=33.235 minus half axle track (~1.4 m, from far-wheel offset) -> 31.8 -> 2.60 m; ground plane
  h=2.3 -> 2.66 m; range convention would give ~2.39. Answer 2.55 (hedged). Confidence medium.
- 1061 eave-to-eave width: front bargeboard tips at (1043,1090) and (1610,1082), intersected with facade plane:
  16.8 m (h=2.31; 16.3-17.3 for h 2.24-2.38). Answer 16.6. Confidence medium-low (house origin/ground uncertainty).
- 1062 bird body length: tail-to-beak extents along the flight heading (-35 deg, i.e. toward camera), over 20+ frames:
  mean 2.49 m incl. blur/mask dilation -> ~2.35-2.5. Answer 2.4. Confidence low.
- 1063 wingspan: far-wing tip extents in wings-level frames (7, 24) and upstroke frame 54 give semi-span ~3.0-3.2 m with
  heading -35 deg (sensitive to heading); max wings-up silhouette height 1.80-1.87 m consistent across frames 2/19/36/54.
  Answer 5.8 (blend of geometric ~6.0-6.4 and bird proportions ~2.2x length). Confidence low.

Scene is scaled ~2.5x real life (door 5.3 m, wheel 2.6 m, bird ~2.4 m long) — consistent across objects.
Scripts in scr/ (nest3.py, vpfit.py, vpV.py, housemeas.py, cart3d.py, bird2.py, birdgeo.py, birdspeed.py).
