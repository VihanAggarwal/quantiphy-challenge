# simulation_0301 - forklift + car (Blender, fixed camera, 2560x1440, 24 fps, 72 frames)

## Kinematics (image-only evidence)
- Background = frame 71 with the frame-0 patch; masks by |frame - bg| > 22-30.
- The forklift track (KLT similarity, 72 frames) is a straight line (perp std 0.06 px). Fitting x(s) = (a s + b)/(c s + 1) with s = t^2 gives rms 0.14 px and best v0 = 0.
  So the forklift is at rest at frame index 0, then has uniform acceleration (prior a = 2 m/s^2).
- The car tail-light midpoint (frames 14-52) gives the same result: s = t^2 fits with rms 0.125 px, v0 = 0.01, so the car also has uniform acceleration from rest at index 0.
- Motion vanishing points from the intersection of many point tracks: forklift (-1175,-505), car (-1100,-460). The two motions are nearly parallel.

## Camera and time base
- The rear plate on the forklift's overhead guard (top-edge lines, 0.06-0.09 deg rms) gives VP_w = (7060,-460).
  Orthogonality with VP_F gives f = 3570-3610. The car tail-light line with VP_C gives f = 3600-3700 (noisier).
- Depth anchors (Euclidean range convention; the Z convention is rejected by the car's tail-light depth-ratio test).
  - If the anchors are at frame indices 24/48, a = 2 needs f = 3300, which contradicts the orthogonality result.
  - If the anchors are at indices 23/47 (dataset t corresponds to Blender frame 24t, i.e. video index 24t-1), the anchors give f = 3510.
    Then the reconstructed AABB centres of both vehicles sit at 48-54% of L and H (origin = body centre). The two-anchor ratios are also consistent to 0.001.
  - Index-23 timing is adopted, with f = 3450-3500. Pitch is about 19.4 deg and roll is about 0.
- Car acceleration from the anchors with the centre origin: 5.05-5.10 at f = 3400-3500 (5.0 is likely the design value). Answer: 5.05.

## Speeds (backward difference, which is the dataset convention)
- Forklift: v(idx23) = 45/24 = 1.875 and v(idx47) = 3.875. If index-24 timing or the instantaneous value is used instead: 1.958-2.0 and 3.958-4.0.
  Answers 1.92 and 3.92 are within 2.5% of every variant.
- Car: a = 5.0-5.1 gives 0.9375a = 4.69-4.78 and 1.9375a = 9.69-9.88. Other variants go up to 5.07 and 10.1.
  Answers 4.82 and 9.88.

## Sizes (3D reconstruction)
- Each KLT point track and silhouette landmark is triangulated using the known metric motion T(k) = u*(a/2)*((k/24)^2 - (23/24)^2).
  The scale comes from a = 2 (forklift) or a_c = 5.07 (car), and depends only weakly on f.
- Forklift (body axes u,w,up):
  - Fork tip (leftmost-silhouette landmark, reproj 0.5 px) to the rear counterweight (dense min): L = 4.34.
  - Left side (dense) to the right-rear counterweight corner landmark: W = 1.53-1.55.
  - Guard roof top (dense max) to tyre bottom (landmark; the fork tips are on the same level within 1 cm): H = 2.49-2.53.
- Car:
  - Rear diffuser (dense min) to front hood/nose (dense max): L = 4.40 (+ a few cm for the nose) -> 4.42.
  - Height: roof (dense max) to tyre bottom (landmark at -7.99), which is on the same ground as the forklift within 4 cm: H = 1.26-1.29.
  - The car carries grey box "slabs" at both rear wheels that stick out about 0.15-0.2 m laterally. Body width is about 1.90-2.0; the AABB including the slabs is about 2.25.
  - Answer 2.18 as a hedge.

## Confidence
- Forklift speeds: high.
- Car speeds and acceleration: high (about 2%).
- Forklift L: medium-high. W and H: medium (+-4%).
- Car L and H: medium. Car W: low-medium (slab inclusion is ambiguous).
