# simulation_0275 (S2SS, 2D side view, raccoon galloping left->right, 72 frames @24fps, 2560x1440)
Method: median-background subtraction (blur 5, |diff|>5, rows<865 to drop ground shadow at 865-870), components near body merged (snout is pale).
- Length tail-tip->snout: 318-333 px across frames, ~330 typical (frame 0: 331). Scale = 1.51/330 = 0.004576 m/px.
- Height (top/ears -> ground ~866): frame 0 = 145 px (0.663 m), gallop-cycle mean ~130 px (0.595 m). Answer 0.64 (leans to frame-0 AABB). Confidence: medium.
- Speed: centroid/edge tracks give 22.4-22.6 px/frame average (frames 2-71); 23->24 centroid diff 22.6 px. 22.55*24*0.004576 = 2.48 m/s. Confidence: medium-high.
- Displacement frames 12->24: centroid 272.5, tail 275, snout 270, constant-speed 270.6 px -> ~271.5 px = 1.24 m. Confidence: high.
