# simulation_0296 - blue butterfly, top-down static camera, flies left at constant altitude
Scale: open-wing (same flap phase, period 21 frames) bbox edges move 15.43 px/frame (frames 1->18->39->60 consistent)
= 370.3 px/s -> 0.32/370.3 = 8.64e-4 m/px. Apparent open-wing size constant all video (no depth change).
- 1030 wingspan (perpendicular to motion, open wings): colour mask 255 px, bg-diff 261-267 px -> ~260 px -> 0.224 m (conf medium-high)
- 1031 wing length (along body axis): colour mask 188 px, bg-diff 193-200 px -> ~192 px -> 0.166 m (conf medium; ambiguous definition)
- 1032 displacement 0.5-1.0 s: constant velocity 12 frames * 15.43 px = 185 px -> 0.160 m (= 0.32*0.5); centroid/bbox give 0.164-0.173 (flap-biased) (conf high)
