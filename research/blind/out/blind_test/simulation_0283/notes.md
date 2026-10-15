# simulation_0283 (S2SC, 24 fps, 2560x1440, 72 frames)
Dragon flies right-to-left in front of snowy cliff, static camera, flapping cycle ~24 frames; exits left by ~frame 62.
Scale: head-snout to tail-tip horizontal extent measured in frames 0,3,24,27 = 496-510 px (use 505 px) = 0.75 m -> 0.001485 m/px.
Motion: background diff vs last frame (empty). Mask centroid over one full flap cycle (frames 4->28, 6->30, 8->32) = 36.8 px/frame;
head-tip track frames 17-24 ~35-36 px/frame; vertical motion near t=1s small. Apparent size grows ~2-3%/s (slight approach; negligible).
- 995 speed at 1.0 s: ~36 px/frame * 24 = ~870 px/s -> 1.29 m/s. Confidence medium (scale definition of "length" is main risk).
- 996 displacement 0.5->1.0 s (frames 12->24): ~435 px horizontal + ~60 px vertical bob -> ~440 px -> 0.65 m. Confidence medium.
