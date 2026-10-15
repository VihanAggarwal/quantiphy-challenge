# simulation_0278 (V2SS, top-down view of a whale swimming left, 2560x1440, 72 frames @24 fps)
Method: background = 2D degree-6 polynomial fit to whale-free rows (vignette), mask = bg - frame > th (15/25/40/55/70),
connected components per frame; edges checked on zoomed crops (dark AO halo inflates nose by ~15 px at low thresholds).
- Nose x track is perfectly linear: -5.85 px/frame (th40, resid 1.1 px) = 140.4 px/s. Body centroid oscillates (tail flex), nose used.
- Scale: 1.67 m/s / 140.4 px/s = 0.011894 m/px. Head size constant over clip -> no depth motion.
- Length: x-extent varies 1440-1600 px with tail flex; straight pose (frame 58) nose 420.7 -> fluke tip 2014.7 = 1594 px -> 18.96 m;
  frame 0 = 1562 px -> 18.58 m. Answer 18.9 m (confidence medium).
- Width (pectoral fin span, y-extent): oscillates 640-782 px with fin flapping; max (fins horizontal, frame 27) 385->1166 = 781 px -> 9.29 m;
  frame 0 643 px -> 7.65 m. Answer 9.1 m (slight hedge toward smaller; confidence medium-low).
- Displacement 0.5->1.0 s: constant velocity, 12 frames * 5.85 px * 0.011894 = 0.835 m (= 1.67*0.5). Confidence high.
