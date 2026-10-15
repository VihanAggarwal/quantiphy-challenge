# simulation_0276 (S2SC, top-down raccoon walking +x, 2560x1440, 24 fps, 72 frames; frames 0 and 1 are duplicates)
Scale: raccoon tail-tip to snout length measured on gridded 3x crops at frames 0/24/36/48: 302/289/~293/298 px -> ~296 px = 1.51 m -> 0.00510 m/px.
Width (Q974): body y-extent ~61-63 px on frames 0/24/48 -> 62 px -> 0.316 m (medium confidence; depends on length px).
Speed (Q975): frame-to-frame template matching of the body: mean 20.55 px/frame over whole clip (walk-cycle ripple 19.5-21.7); near t=1 s ~20.8-21.4 -> 2.53 m/s (medium-high).
Displacement 0.5->1.0 s (Q976): x[24]-x[12] = 248.2 px -> 1.266 m (medium-high).
Background-subtraction masks were contaminated by shadow; manual crops + template matching used instead.
Scripts: seg*.py, tm.py, crop.py
