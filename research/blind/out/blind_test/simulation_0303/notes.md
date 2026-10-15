# simulation_0303: plane receding (V3SX), prior speed 22.16 m/s, d(1s)=102.67 m, d(2s)=121.83 m

## Method
- 72 frames, 2560x1440. Frames 0 and 1 are duplicates. Frame index = t*25; this was confirmed below.
- Silhouette: the dark plane against the sky (gray < 110). KLT features (fwd/bwd checked) were tracked over 71 frames.
- Pure-translation model: every body point moves on a line toward a common vanishing point (VP), with
  p_j(i) = VP + D_j/(1 + c_j i). A grid search over the VP gave (-748, -477) px, with rms 0.43 px and bootstrap std about 1.5 px.
  This means the motion is straight-line, constant velocity, with no rotation.
- Focal length: three routes using the frames at t=1 and t=2 (25 and 50):
  - chord |p2-p1| = 22.16 m with d1, d2 -> angle 5.706 deg -> f = 3472 px (centroid);
  - angle between the line of sight and V at t1 (33.14 deg) and t2 (27.43 deg), using the VP -> f = 3482 and 3484 px.
  - The 24-fps alternative (frames 24 and 48) is inconsistent: 3404 vs 3519/3551. The 25-fps mapping holds.
  - Adopted f = 3470 (HFOV about 40.5 deg).
- Depth of each tracked point: Z_j = (Vz/25)(1/c_j + i), with Vz from the speed prior and the VP direction -> 3D point cloud.
  - Check: the 3D bbox centre of the cloud reprojects to d = 102.64 / 121.74 m at t = 1 / 2 s (given 102.67 / 121.83).
- Body frame: the lateral axis comes from symmetric winglet pairs and the front-element pair. Fore is V orthogonalised against it.
  - V is about 6-7 deg off perpendicular to the lateral axis.
  - The plane's up vector implies the camera is pitched down about 20 deg with roll about -2 deg, so the plane flies level.

## Results
- Width (wingspan, lateral extent between winglet tips): 18.42 m at f = 3470. It is 18.2-18.6 for f in 3400-3540 and 18.45 when aligned with V.
  Answer: 18.4.
- Length (fore-aft extent): from the ventral fin / tail nozzle at -8.75 to the front of the nacelles / strakes at +5.56 -> 14.3 m.
  It is 14.46 when aligned with V. A centreline nose beyond about +6 m is ruled out by the silhouette in frames 1, 25 and 70. Answer: 14.4.
- Displacement 0.5 -> 1.0 s: constant velocity is confirmed by the fit, so 22.16 x 0.5 = 11.08 m.

## Confidence
- 1473 displacement: high.
- 1472 width: medium-high. The measurement is about +/-3%. The main risk is the dataset naming the axes the other way round.
- 1471 length: medium. A hidden nose could add up to about 1 m, and the same axis-naming risk applies.
