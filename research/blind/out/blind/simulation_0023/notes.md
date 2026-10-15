# simulation_0023 — boat + eagle (960x960, 24 fps, 75 frames, static camera)

## Scale (focal length) from the eagle prior
- Eagle tracked by median-background subtraction (work/track_eagle2.py). Flap period ~24-25.5 frames; t=1 (f24) and t=2 (f48) are the same flap phase.
- Eagle origin pixels t=1 ~(469.5,382.5), t=2 ~(741.8,377.8) (global fit: linear 3D motion + Fourier flap terms, work/fitglobal.py).
- |r2*ray2 - r1*ray1| = 11.84 m with r1=116.0475, r2=108.2756 -> f ~ 3408 px (raw same-phase centroids give 3390). HFOV ~16.1 deg.
- Constant-velocity 3D model reproduces the whole eagle pixel track (residuals = flap oscillation only).
- Eagle velocity (camera frame) ~ (8.6, 0.15, -8.1) m/s -> heading ~43 deg from image plane, toward camera.

## Boat
- Cabin template track (sub-pixel) is perfectly explained by constant 3D velocity (residual <0.3 px over 75 frames).
- Speed: V = r2*ray(f48) - r1*ray(f24) with boat ranges 103.157/106.0906 -> |V| = 4.03 m/s (4.02-4.04 for f 3390-3425; radial part dominates so insensitive to f). Backward difference at t=1 equals this (uniform motion). -> 4.03 m/s.
- Heading = V direction (-47 deg from optical axis): moving left & away, bow at left. Cabin faces (port side & back) equal pixel widths -> square cabin, consistent with this heading. Structure-from-known-motion places rudder and cabin corner consistent with that centreline (cabin half-width 0.8 m).
- Height: mast top row ~305 (f24), hull bottom / waterline ~626.5 -> 321 px at mast depth z~103.6 -> 9.75 m; +small allowance for possible draft/antenna tip -> 9.85 m.
- Length: bow tip (195,515) and stern on the centreline vertical plane through the origin. Bow->rudder = 9.92 m; stern overhang beyond rudder (rounded cruiser stern, silhouette extreme at x=445) adds ~0.2-0.4 m -> ~10.2 m (range 9.9-10.4).

## Eagle sizes
- Wingspan: max x-extent of silhouette per flap cycle (51-52 px at z~110-113) / sin(angle between wing axis and view ray) (0.64-0.66), minus anti-alias and tip-chord effects -> ~2.4 m (level-wing frames give 2.25-2.4, under-detected thin tips; drooped frames 2.4-2.6).
- Length: wings-up frames, tail (light strip) to white head at bottom of V: 16.5-18.5 px -> 0.75-0.78 m along body axis (factor 0.73-0.78) -> ~0.8 m.

## Confidence
- 1101 boat speed 4.03: high.
- 1102 boat height 9.85: medium-high (draft unknown).
- 1103 boat length 10.2: medium (stern centreline point inferred; assumes length = hull length along heading).
- 1104 eagle length 0.8: low-medium (tiny target, ~17 px).
- 1105 wingspan 2.4: medium.
