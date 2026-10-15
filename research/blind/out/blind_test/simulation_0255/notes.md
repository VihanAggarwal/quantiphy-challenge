# simulation_0255 (S2SS, tennis ball rolling left->right, 24 fps, 41 frames)
- Static camera, 2D planar view; ball stays at y=563.6 px with constant apparent size -> constant depth, single scale.
- Ball tracked by HSV green threshold (centroid per frame, track.py).
- Diameter: subpixel FWHM of saturation profile, vertical (no motion blur) = 23.5-23.8 px -> 23.7 px. Scale = 0.17/23.7 = 0.007173 m/px.
- x(frame) fits a quadratic well (rms 0.24 px): pixel speed 44 -> 34 px/frame, constant deceleration.
- Speed = backward difference of fitted track * fps * scale: 0.5s 7.075, 1s 6.524, 1.5s 5.972 m/s (local 5-frame means agree within 0.3%).
- Acceleration: global quadratic -1.103 m/s^2; local windows 1.14/1.10/1.04. Report 1.103 magnitude for all three.
- Confidence: high for speeds (scale error ~2%), medium-high for accel.
