# simulation_0279 (whale, 2D sim, 2560x1440, 24 fps, 72 frames)
Method: static camera, side view; whale translates left at constant image speed.
- Snout x tracked per frame (horizontal gradient, rows 450-600): 612 -> 77 px over frames 1-68, 7.985 px/frame = 191.6 px/s (very linear).
- Scale: 1.67 m/s / 191.6 px/s = 0.008715 m/px.
- Sharp-edge bbox per frame (Sobel>60, shadow edges are soft): max x-extent 2319 px (frames 48-56, body straight) -> length 20.2 m.
- Vertical extent in straight pose (dorsal back to pectoral fin tip) 570-610 px -> height ~5.1 m (pose dependent: 4.8-5.3 m; 7+ m if tail raised at end).
- Displacement 0.5-1.0 s: constant speed -> 1.67*0.5 = 0.835 m.
Confidence: displacement high; length medium (pose/frame used for GT unknown); height low-medium (fins/tail pose).
