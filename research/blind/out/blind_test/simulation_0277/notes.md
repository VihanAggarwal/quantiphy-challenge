# simulation_0277 (2D side view, raccoon running left->right, static camera)
- Mask: background median difference (seg2.py), clean frames 0-20 (later frames merge with shadows/trunk occlusion).
- Length incl. tail: median bbox width 321 px (frames 0-20) => scale 1.51/321 = 0.00470 m/px.
- Height: bbox height 121-145 px (gait-dependent), median ~128-130 px => 0.61 m (medium confidence, pose-dependent).
- Nose (xmax) track is linear: ~21.6 px/frame over frames 0-35 and 49-71 (constant speed).
- Speed @1.0s = 21.6*24*0.0047 = 2.44 m/s (good confidence).
- Displacement 0.5->1.0 s = 12 frames * 21.6 px * 0.0047 = 1.22 m (good confidence).
