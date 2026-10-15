# simulation_0289 (V2SS, koi fish swimming right->left, 24 fps, 72 frames, 2560x1440)
Method: median-background subtraction (full res, thr 12/25, shadow rows >1100 excluded), per-frame bbox + centroid.
- Centroid pixel speed constant: ~22.25 px/frame (frames 12->68, 4-frame steps 86.6-91.5 px). Nose 22.7, tail 21.8 px/frame.
- Scale from prior 0.67 m/s: 0.67/24/22.25 = 1.255e-3 m/px.
- Fish x-extent (nose to tail-tip) 595-642 px over video (tail flap / slight yaw), median ~612 px -> 0.766 m. Height ~290 px -> 0.36 m (plausible koi ratio).
- Displacement 0.5->1.0 s (frames 12->24): centroid 2056.5 -> 1788.7 = 267.8 px -> 0.336 m; constant-speed check 0.67*0.5 = 0.335.
Answers: 1012 = 0.766 m (medium confidence, +-5%), 1013 = 0.335 m (high confidence).
