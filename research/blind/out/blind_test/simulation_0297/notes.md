# simulation_0297 notes
Q1033: displacement of jellyfish 0.5-1.0 s, prior speed 1.75 m/s (no depth info).
Method: background-median subtraction at 1280x720, tracked jellyfish blob (track.py).
Over frames 0-26 the blob's leading/left edge moves linearly (~10.7-11 px/frame, 369@f10 -> 536@f25),
blob height/area roughly constant (no depth change) -> straight lateral, constant-velocity motion in 0.5-1.0 s.
No ease-in at start (moves from frame 2), consistent with constant-speed animation.
Mid-video (f30-55) the blob grows and slows on screen (moving toward camera / turning), irrelevant to the asked interval.
Answer = 1.75 m/s * 0.5 s = 0.875 m. Confidence: moderate-high.
