# simulation_0109 — two red blood cells (3D Blender, 1080x1080, 24 fps, 72 frames)

## Measurement
- Cells segmented by redness r-(g+b)/2 > 67 (half of ~134 contrast), hole-filled; per-frame centroid + equivalent-circle diameter
  (trackL.txt / trackR.txt). Frame 31 is a render glitch (excluded); frames >=63 clipped by top edge (excluded). Halo appears after ~frame 31
  but stays below threshold.
- Constant-velocity projective model u=(a+bt)/(1+ct), v=(d+et)/(1+ct) fits the left track with 0.11 px rms (right: 0.10 px).
  Left c=Vz/Z0=0.0683, right c=0.0705.

## Camera (principal point = image centre)
- Range convention verified: track gives Z2/Z1=1.064 but depth ratio is 1.092 -> depth_info is Euclidean range, not optical-axis Z.
- Route A (range ratio t=1/t=2 + track foreshortening): f = 1503-1519 px (frame-range dependent).
- Route C (range at t=1 + speed prior 4.7833 for the left cell): f = 1500.5 px.
- Blender default 50 mm / 36 mm sensor at 1080 px => f = 1500 px exactly. Adopted f = 1500 (HFOV 39.6 deg).
- With f=1500: left-cell speed reproduces 4.7833 m/s and range at t=2 = 24.037 (given 24.0333).

## Answers
- 1378 diameter: D = s_px * Z / f, left cell face-on disc. Median over frames 1.636 m (t=0 1.639, t=1 1.632, t=2 1.642;
  max-extent (112 px vertical) at t=1 gives 1.640). Answer 1.636 m. Confidence: high (~2%).
- 1377 centre-to-centre distance at t=1: right-cell depth needs an assumption: same diameter as left -> 3.02 m;
  same speed as left -> 3.07 m. Answer 3.04 m (average). Confidence: high-medium (~2%), assuming centre-to-centre
  (surface gap would be ~1.40 m).
