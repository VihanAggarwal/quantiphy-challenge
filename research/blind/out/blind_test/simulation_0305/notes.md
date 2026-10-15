# simulation_0305 - plane flying away from a fixed camera (V3SS, 24 fps, 2560x1440 letterboxed)

## Inputs
- Prior: speed 22.16 m/s. Depth: range 102.67 m at t=1 s, 121.83 m at t=2 s.
- Questions: plane length (1476), plane width (1477), displacement 0.5-1.0 s (1478).

## Method
1. Built a median background, then segmented the plane (upper blob) and its shadow on the ground (lower blob) in every frame. Checked the masks against overlays.
2. Motion: the plane-centroid and shadow-centroid tracks are both straight lines (rms 1.1 px and 0.3 px). They meet at a common vanishing point VP_v = (-729, -467).
   1/|x - VP| is linear in t to 0.07 %, so velocity is constant. Frame 0 duplicates frame 1.
3. Focal length, all routes assuming the principal point is at the image centre:
   - Zero-roll horizon through VP_v. The vanishing point of the shadow's lift-fan-hole pairs (span direction) is orthogonal to VP_v: f = 3535 px.
   - The fin tops triangulate as exact mirror points (dv component 0): f ~ 3420-3525 px.
   - Speed plus the two ranges, using the VP direction and the centroid as origin: f ~ 3480-3510 px.
   - Blender's default 50 mm / 36 mm lens: f = 3556 px.
   - Adopted f = 3530 px (HFOV ~ 40 deg). The range-convention speed check also agrees.
4. Width, primary route: triangulated rigid silhouette features from their own image motion, using the known velocity 22.16 m/s along VP_v. This route needs neither the ranges nor the origin; reprojection rms is ~0.6 px.
   - Fin tops are 17.6 m apart.
   - The left fin's bottom-outer corner lies 9.63 m from the symmetry plane, which gives an outer span of 19.27 m (19.1-19.4 for f = 3480-3580). The mirrored right corner projects inside the silhouette, which is consistent.
   - The tail tip lies on the symmetry plane (offset 0.03 m), which supports the VP and f choice.
5. Shadow route: rectified the ground (zero-roll horizon plus f) and set the metric scale from the shadow's own speed. This cancels the point-light magnification k.
   - The shadow is a clean, symmetric top-view planform.
   - Span: 18.6-18.9 m at the half-max edge, 19.0-19.3 m at the 0.2 threshold. The fin bottoms sit below wing level, so their shadows are slightly compressed.
   - Length (pod nose-cone tips to tail tip): 13.5-13.7 m at half-max and 14.1-14.3 m at the 0.2 threshold. Both ends are pointed, so half-max underestimates the length.
   - Light/height effects add roughly ±0.3 m.
6. Displacement: the motion is rigid and at constant velocity, so 22.16 m/s x 0.5 s = 11.08 m.
7. Origin note: the ranges place the origin about 4 m nearer the camera than the visual centre. This affects only the range-based cross-checks, not the answers.

## Answers / confidence
- 1476 length: 14.2 m. Medium confidence, ~±4 %. Risk: the dataset may call the span "length". If so, the truth could be ~19 m.
- 1477 width: 19.0 m. Medium-high confidence (triangulated 19.27, shadow 18.9-19.3). Nudged slightly toward the length in case the labels are swapped.
- 1478 displacement: 11.08 m. High confidence (constant velocity verified).
