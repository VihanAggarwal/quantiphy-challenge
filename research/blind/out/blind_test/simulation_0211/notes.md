# simulation_0211 - black cat walking along wall; bench, lamp, vase, floor mirror in corner

## Camera model
- Static Blender camera, 1920x1080, 24 fps, 50 frames.
- Floor/wall baselines fitted with subpixel edges: left wall y = 908.98 - 0.07504x (rms 0.09 px), right wall y = 563.5 + 0.1288x; corner at (1694.9, 781.8). Corner line is vertical, so pitch is about 0.
- Level camera (horizon y=540): orthogonal wall vanishing points give VP1 x=4917, VP2 x=-182.5, f = 2126 px (HFOV 48.6 deg).
  - Cross-check: the cat's smoothed track speed is 0.940 m/s and constant only for horizon ~540 (it drifts for 520/560). Matches the 0.94 prior.
- Camera height H from the cat ranges (t=0 4.199, t=1 4.481), with the origin on the floor: 0.776. Checks:
  - closest bench leg: model 5.675 vs 5.69 given.
  - mirror bottom-centre (AABB bottom centre between floor edge and top): model 6.37-6.40 vs 6.407 given.
  - Scale factor k ~1.005 adopted, so H = 0.780.
- The ranges follow the Euclidean (range) convention. The optical-axis Z convention gave inconsistent H.
- The cat walks parallel to the left wall: paw contacts lie on one line through VP1 within ±1.5 px.

## Measurements (wall-aligned frame a along wall, b toward wall; wall at b=4.895)
- Cat: mask by background difference with shadows removed. Extents projected onto the cat's vertical path plane b=4.02.
  - Length (a-extent, rear paw/tail to nose): frame 0 0.706, median over frames 0.706 (range 0.67-0.75).
  - Height (floor to tail tip): frame 0 0.495, median 0.486.
- Bench: legs at the floor (front-left and back-left at the same a, 0.31 m apart in b). Top board front edge/thickness.
  - Top surface height 0.455*k = 0.457.
  - Top a-extent 3.505..4.524 = 1.019*k = 1.024. The top overhangs the splayed legs.
- Lamp: base front-bottom (1370,661) on the bench top, giving centre Z 5.72 (b 4.52).
  - Shade bottom rim 192.4 px wide, giving D 0.508.
  - Rim back at v 495, top front at v 399, giving shade height 0.248 and lamp top 1.154. Lamp height 0.697.
- Vase: foot (1546,655) on the bench top (b 4.53); lip front at v 470; height 0.520.
- Mirror: bottom front edge on the floor (b 4.55). Frame side edges are consistent with a top-front at b about 4.745 (not rotated).
  - Height of the top edge: 1.437*k = 1.444.
  - Width along the wall: 0.628*k = 0.631. Reported as "length"; the depth extent is only about 0.23.
- Cat distance: straight constant-speed path. r^2 = D^2 + a(t)^2 fitted to r0, r1 and the measured Δa = 0.94 m/s (the track is linear at 0.47 m per 0.5 s).
  - r(0.5) = 4.317, r(1.5) = 4.687. The model-based track with a fitted origin offset gives the same values.
  - Note: the given ranges imply the cat origin sits about 0.15 m behind the mask centroid (hips/root).

## Confidence
- Distances 1603/1604: high (±0.5%).
- Bench height and length, mirror height: high-medium (±2-3%).
- Lamp and vase: medium (±3-4%; depends on the bench-top plane).
- Mirror "length": medium. Interpreted as width along the wall; the alternative (frame length ~1.47) is possible.
- Cat length and height: medium. They depend on which pose or frame the GT bounding box used; frame-0 animated pose reported.
