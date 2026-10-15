# internet_0066 notes
Scene: phone looking straight down at a gym floor (feet at bottom); a basketball rolls right-to-left across frames 50-71 (t=1.67-2.37 s) at ~constant apparent size (diameter ~263 px vertical, height robust to horizontal motion blur) and nearly constant y. Static camera apart from small jitter at start/end.
Prior (g=9.8) is unusable: no motion along gravity in the image plane (gravity is along optical axis; ball size constant -> rolling on floor).
Scale: basketball diameter assumed 24 cm (size 7). Cross-check: court line 5.08 cm = 54 px at floor -> 0.094 cm/px -> ball 24.8 cm at floor scale, ~22.5-24.5 cm after depth correction for ball centre above floor. Consistent.
Track: bg-subtracted, dark-colour mask (shadow excluded), centroid per frame; quadratic fit frames 55-68: vx ~ -87 px/frame, slight deceleration, vy ~1 px/frame.
Speeds: 0.24/263.5 m/px * ~88 px/frame * 30 = 2.37-2.42 m/s; displacements per 0.1 s ~0.24 m.
Confidence: medium-low (scale entirely from assumed ball size; if truth used a different scale, all answers shift together).
