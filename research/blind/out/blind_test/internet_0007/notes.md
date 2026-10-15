# internet_0007 — top-down drone view of a 2-lane rural road (1080x1920, 30 fps, 298 frames)

Objects: dark (blue-black) car in left lane driving up (frames 0-130, briefly under a tree ~88-105);
white hatchback/sedan in right lane driving down (frames ~96-295).

Camera: nearly static nadir drone. ECC affine vs frame 0: drift <= ~11 px, zoom <= 1.1% -> compensated (<1% effect).

Scale (prior lane width = 3.66 m): road is grey asphalt ~78 px wide (chroma boundary to brown verge strips;
range 71-84 px depending on edge criterion; visual zoom gives ~520..600), centre dashes at x~561.
Lane = 39.5 px  ->  0.0927 m/px. (If annotators included the brown verges lane could be ~42-46 px -> answers ~10-15% lower.)
Cross-check: dash period 134 px (UK 6m/3m hazard line -> real scale ~0.067 m/px) => prior scale is ~1.4x real; GT uses prior.

Lengths (multi-frame, colour-edge extents + 5x crops at 6 frames):
- white car body 60.5 px (sharp edges, little motion blur) -> 5.61 m
- dark car 71 px (69-72 across frames) -> 6.58 m
Speeds (background-subtraction track, camera-compensated linear fit over whole visible window):
- dark car 355.5 px/s (constant within +-3%) -> 32.94 m/s
- white car 291 px/s (decelerates ~303 -> 270 px/s) -> 26.96 m/s
Confidence: moderate; dominated by lane-pixel definition (+-5-15%).
