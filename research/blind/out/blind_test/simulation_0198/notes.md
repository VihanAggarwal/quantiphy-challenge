# simulation_0198 (2D, droplet falling from pipette next to SKYNOVA bottle)
- 14 video frames @60 fps, 2560x2560. Video has a duplicated frame (v7=v6) and a skipped sim frame; mapping video->sim index: 0-6 ->0-6, 8->7, 9->9, 10->10 (verified by quadratic fit, residuals <1 px).
- Droplet track by median-background differencing. Quadratic fit of top/bottom edge: a = 31.8 px/frame^2 (31.7-31.9), release at ~frame 0.
- Scale: 9.7 / (31.8*3600) = 8.47e-5 m/px. Droplet size constant during fall (same depth plane).
- Droplet 91 x 58 px (h x w). Bottle body 425 px (edges 1703-2129). Neck incl. threads 270-294 px -> used 280 (core w/o threads ~226; moderate confidence).
- SKYNOVA text is rotated (reads vertically): image-horizontal extent 38 px, vertical 326 px. Interpreted horizontal/vertical as world axes (low confidence: could be swapped if question meant reading length).
- Speeds: backward difference from fit at sim frames 3, 6, 12 (12 extrapolated, droplet out of frame): ~9.7*(n-0.5)/60.
Confidence: speeds high; droplet/body high-medium; neck medium; text low-medium (interpretation).
