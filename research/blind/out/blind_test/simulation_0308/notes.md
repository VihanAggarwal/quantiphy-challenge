# simulation_0308 — whale (V3SC, DS: depth + speed prior)

## Inputs
- speed prior 1.67 m/s; distance to whale origin 33.7307 m (t=1 s), 35.1624 m (t=2 s); 2560x1440, 24 fps, 72 frames; fixed camera.

## Geometry from prior
- Straight line, constant speed: p(t)=p1+1.67(t-1)w. From d1, d2: p1.w = 28.696 m (radial 1.42 m/s,
  angle of the line of sight to the motion = 31.7 deg); the line's perpendicular distance from the camera h = 17.728 m.

## Image measurements
- Blowhole tracked with a fixed multi-scale template (rms 0.4 px; dark-blob centroid used as a cross-check):
  195.8 px in 71 frames along the direction (-0.869,-0.494), about 66 px/s, slowly falling (projective).
- Vanishing point of the motion (V) on the blowhole track line, three cues:
  shadow-head track convergence about (-653,-624); floor-texture foreshortening horizon y about -680, giving (-755,-680);
  "origin inside the body" plausibility gives about (-500..-650). Image deceleration alone gave a closer V (r about 1550),
  which cannot reach h=17.7 for any f, so I treated it as biased.
- For each V, f was solved so that the reconstructed blowhole (ray intersected with the vertical plane through the axis)
  moves rigidly at 1.67 m/s (no drift in s between frames 9 and 71). This gives f of about 3300 to 5200 px (camera pitch
  about 16 deg, roll 0).
- Reconstruction (axis line at h=17.728 through the body centre at frame 48 (1300,575)):
  snout (front of the grey translucent rostrum, (915,350) at frame 48) on the mid-plane;
  fluke tips at mid-stroke frames 48/52/56 on the horizontal plane where the two tips are laterally symmetric
  (fluke span about 5 m).
  Snout to fluke tips = 20.1-20.2 m (V=-500,-536), 20.4-20.5 m (V=-653,-624), about 20.8 m (V=-755,-680).
  Snout to tail notch (tail bent down at frame 48) = 18.5-19.1 m.
  This length is nearly independent of f and V, because the scale comes from speed x travel time across the image.

## Answers
- 1484 whale length: 20.3 m (world AABB length along the motion axis, snout to fluke tips). Medium confidence (about ±10%).
  Remaining risks: the AABB convention or a world-axis misalignment; whether the grey rostrum belongs to the mesh;
  the origin lying off the body axis (about ±4%).
- 1485 displacement 0.5 to 1.0 s: 0.835 m (1.67 m/s x 0.5 s). The reconstructed blowhole gives 0.836-0.841 m. High confidence.
