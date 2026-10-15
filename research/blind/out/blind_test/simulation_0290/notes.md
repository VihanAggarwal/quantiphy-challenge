# simulation_0290 - top-down koi over a caustic floor, static camera, 2560x1440, 24 fps, 72 frames (f0=f1 and f70=f71 are duplicates)
- The camera is static: background template shifts are 0 px. The floor caustics change every frame, so median background subtraction fails.
- The black fish-shaped blob with a gray nose is the koi's SHADOW on the floor. It is offset toward the image centre by perspective: ahead of the koi at the start, under it near x~1280 (f48), behind it at the end. It moves ~17-19 px/frame against the koi's ~23, so the floor is about 1.3x farther from the camera than the koi.
- Koi speed: template matching on the mid-body texture between consecutive frames gives 22.90 px/frame (std small, 3 templates 22.6-23.1) = 549.6 px/s.
  Scale = 0.67/549.6 = 1.219e-3 m/px (in the koi's plane).
- Length: koi head to tail-tip, measured by hand on zoomed crops: f12 662, f24 647, f48 635, f60 640, f71 657, f36 573 (strongly bent). I used the straight-body maximum, ~662 px, giving 0.807 m. Answer 0.80 (medium confidence).
- Width: pectoral-fin span perpendicular to the body, 232-250 px (~240), giving 0.29 m. Body-only width is ~150 px (0.18 m). Low confidence: it is unclear whether the box includes the fins.
- Displacement 0.5->1.0 s (f12->f24): texture track moves 275 px, giving 0.335 m, equal to 0.67*0.5. High confidence.
