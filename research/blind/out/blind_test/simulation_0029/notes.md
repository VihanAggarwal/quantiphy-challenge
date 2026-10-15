# simulation_0029 — eagle + red fishing boat, fixed camera, 960x960 (upscaled from 480), 24 fps, 75 frames

## Camera / scale
- Prior: eagle speed 12 m/s. Depths (range convention) eagle 139.70 m (t=1) -> 147.16 m (t=2); boat 133.96 -> 131.26 m.
- Eagle tracked by background subtraction (sky median); flap period ~24 frames so t=1/t=2 are same flap phase.
  Smooth projective fit x(t)=(a+bt)/(1+ct)+flap harmonics: x(1)=234.9, x(2)=409.95 (dx=175 px), y~528-531.
- Solve |P(2)-P(1)| = 12 m with P = d * ray(u,v,f), principal point (480,480): f = 2650-2658 px (range), hFOV ~20.6 deg.
  Using the Z convention instead gives f=2538. Range chosen: (a) documented, (b) eagle & boat velocities come out
  anti-parallel within 0.2-0.3 deg with range (both move along one world axis), versus 1.5 deg off with the Z convention.
  Constant-velocity line through P(1),P(2) reproduces eagle x at frames 0 and 74 within 1-2 px. Using f = 2654.
- Horizon (vanishing point of both motion directions) ~ y 625-631 => camera pitched up ~3 deg, about 2.5 m above water.

## Boat speed (qid 1122)
- Template match of whole boat (multi-scale, subpixel): centre 486.0 -> 423.7 px between frames 24 and 48; motion is
  constant velocity (extrapolation to frames 0..72 matches within 0.2 px).
- V = (-3.08, -0.16, -2.73) m/s -> |V| = 4.12 m/s (f 2600-2700 gives 4.17-4.08). Confidence: high.

## Boat height (qid 1120)
- Mast antenna top y~487 (t=1) / ~482.75 (t=2); visible hull bottom (dark bilge band / forefoot) ~679.5.
- 192.5 px * 133.85/2654 = 9.71 m; t=2: 196.75 px * 131.16/2654 = 9.72 m. Bilge turn is visible so draft is small;
  added ~0.1 m allowance for faint antenna tip / possible submerged keel -> 9.8 m. Confidence: medium-high.

## Boat length (qid 1121)
- Heading = direction of motion, 48.7 deg from line of sight (bow toward camera-left); extent change across video
  (+4.7% in metres) matches the predicted change of viewing angle, so the hull is rigid and aligned with its motion.
- Bow stem tip x=403.7 (t=1) / 338.0 (t=2); stern centreline (rudder 555 / stern pole 557.5 at t=1).
  3D back-projection along heading: bow 5.39 m ahead of track point, stern 4.76-4.93 m aft => L = 10.1-10.3 m.
  Visible-side transom corner (566.5) fits a stern half-width ~0.8 m at the same station. Answer 10.2 m. Confidence: medium.

## Eagle length (qid 1119)
- Eagle seen from rear-left quarter (~50 deg); body length mostly hidden in silhouette. Wing geometry
  (V-pose height ~1.05 m, flat-wing width ~1.45-1.6 m) => wingspan ~2.1 m (real-eagle scale).
- Widest row at V junction 14 px (0.73 m) / sin(53.5 deg) => ~0.91 m; eagle proportions (L ~ 0.42-0.45 x span) => 0.88-0.95 m.
- Answer 0.9 m (body beak-to-tail). Confidence: low-medium (assumes "length" = body length along heading, not wingspan).
