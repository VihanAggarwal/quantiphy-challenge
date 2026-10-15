# simulation_0077 - notes

Scene: Blender, fixed top-down camera, uniform grey floor, 72 frames @ 24 fps (frames 0 and 1 identical; motion starts at 1->2).
Two walkers start near the image centre: black shirt walks +x (image y ~405), white shirt walks -x (image y ~607).
Image paths are horizontal and pixel speed does not change with x, so the camera is effectively nadir-looking. Heads sit
radially outside their soft shadow blobs, symmetric about the image centre, which also points to a top-down view.
Perspective is noticeable (k = head/ground scale ~1.16-1.25, camera ~8-10 m up), so all measurements use ONE feature at
one height: the head (hair blob, HSV mask), on both people.

Method
- Hair mask (hue<=20, S>=25, 45<=V<=125) -> per-frame head centroid for each person (overlay checked visually).
- Gait period ~17 frames per step for both. Head pixel paths are linear with +-3 px gait wobble, so the root moves at
  constant velocity (consistent with the exact 1 m/s prior; planted feet slide slightly, i.e. the root is driven at a set speed).
- Linear fits: black 12.093 px/frame, white 15.697 px/frame. Ratio 1.293-1.298 over matched windows.
  Scale at head level = 12.093*24 = 290.2 px/m (black = 1 m/s). Ground-scale differences cancel because both heads are at
  about the same height (similar k from shadow offsets, similar torso widths).
- White speed = ratio * 1 m/s = 1.295 m/s (likely a designed 1.3 m/s).
- Distances: mean-path head positions at frames 24 and 48, with mean y (black 404.6, white 607.2; dy = 202.6 px = 0.70 m).
  Each head is about 10-18 px (4-6 cm) ahead of its pelvis/root in its walking direction: at frame 0 the head is ~10 px
  ahead of the torso centre, and if both roots start at the same x it would be 18 px. So 2*14 px is removed from dx.
  t=1.0 s (frame 24): dx 647.5 px -> 2.34 m (2.43 if head = root)
  t=2.0 s (frame 48): dx 1314.5 px -> 4.58 m (4.68 if head = root)

Confidence
- qid 70 (white speed 1.295 m/s): high (~2%).
- qid 71 (2.34 m): medium-high (~4%; head-vs-pelvis offset and a +-1 frame time mapping each cost about 4%).
- qid 72 (4.58 m): high (~2-3%).
Discarded: shirt-centroid tracks (side-visibility bias gives ratio 1.36) and shadow-blob fits (unstable, constant inward bias).
