# simulation_0155 (V2SS, 2D, 24 fps, 48 frames, 1920x1080)
Shark swims right->left across a static camera (seabed edges register with 0 px shift over the whole clip).
Prior: speed of the shark = 7 m/s -> scale from pixel speed.

## Measurements (scripts in scr/)
- Segmentation: median background + red-channel diff (snout from frame 14 on renders as a faint grey patch;
  red-diff>4 is needed to catch the true nose tip; plain diff only finds the lower jaw).
- Pixel speed (px/frame): nose template frames 0-6 = 37.9, 50.0, 53.4, 54.3, 55.7, 56.3 (shape unchanged -> real
  in-plane speed change, no yaw); dorsal-fin template 6->36 rises 56.5 -> ~59.0 and plateaus at 58.7-59.3 (frames 15-36);
  nose/tail-tip line fits over frames 15-21: 59.3 / 59.1. Body thickness constant (no depth change).
- Pixel length nose tip -> caudal upper-lobe tip, frames 15-21: 922-930, mean 925 px (tail wag gives 905-930).
- Whole-clip pixel displacement (nose at f0 = 1776; tail tip at f47 = 7, minus length): ~2690-2715 px (mean 57.3 px/frame).

## Answers
- 355 length: 925 px / 59.0 px/frame * 7/24 = 4.57 m (plateau scale); with mean-clip speed scale 4.69 m. Answer 4.6 m.
  Confidence: medium-high.
- 356 displacement: constant 7 m/s over 47 intervals = 13.71 m; image-based with plateau scale 13.3-13.4 m. Answer 13.6 m.
  Confidence: medium-high.
