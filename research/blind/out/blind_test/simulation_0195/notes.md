# simulation_0195: Jupiter + orbiting Callisto (3D sim, 1920x1080, 30 fps, 100 frames)

## Method
- Static camera. Callisto tracked per frame by threshold + contour circle fit (thr 8/12/20; centre jitter ~0.1 px).
  Jupiter disk: sub-pixel edge coverage gives a diameter of 283.0 px, centre (941.3, 489.9); radial half-max median radius 141.4 px.
- 3D model: pinhole with principal point at (960,540) and unknown f. Jupiter centre at Euclidean range 16.549 m along its pixel ray.
  Callisto moves on a 3D circle around it at constant speed 0.627 m/s (omega = v/R). Fitted to 100 pixel positions plus ranges
  13.004 m (t=0) and 13.856 m (t=3 s, frame 90) with Levenberg-Marquardt and random restarts.
- Convention check: Euclidean range fits with 0.08-0.10 px RMS and 1 mm range residuals. Optical-axis Z does not fit
  (0.35 px RMS, 6 cm range residuals), so Euclidean range is used.
- Cross-checks:
  (a) With the orbit centre free: f = 2667, R = 4.257, and the centre lands 0.017 m from the Jupiter position.
  (b) With the speed free (centred on Jupiter): the fit recovers 0.626 m/s, against the prior of 0.627, and f = 2671.
  (c) Fits from different track variants agree: f = 2667-2671 px, R = 4.254-4.260 m. HFOV is about 39.6 deg.

## Answers
- 1554 orbital diameter = 2R = 8.514 m. Confidence: high (about 0.3%).
- 1556 Jupiter diameter = 2 * 16.549 * sin(atan(141.5/2667.3)) = 1.753 m. Confidence: high (about 0.5%).
- 1555 Callisto diameter: horizontal edge-coverage width (27.6 px at t=0 down to 26.3 px at t=3), converted with the model range
  and an off-axis ellipse correction, gives 0.1328 m averaged over all frames. A circle fit to the lit limb gives 0.1321 m, and
  low-threshold contours give up to 0.138 m. Answer 0.133 m. Confidence: medium-high (about 3%; the 28 px disk is blurred by compression).
