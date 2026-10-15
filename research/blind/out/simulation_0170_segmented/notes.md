# simulation_0170_segmented: astronaut, 3D (S3SX), 24 fps, 80 frames, 1920x1080

## Method
- Background is white. The astronaut is segmented by thresholding (255 - min channel > 40).
- Scale per frame: SIFT matches inside the mask, with a RANSAC similarity transform between consecutive frames.
  The cumulative product gives the image scale S(k) ∝ 1/Z. Direct matches to frames 24 and 48 agree to about 1%.
  Over the clip S grows by 2.16x, from frame 0 to frame 79.
- Pelvis: chosen at the hip/crotch in frame 79 (972, 297), then carried back to frame 0 through the per-frame
  similarity transforms. Overlays at frames 0, 24, 48 and 72 confirm it stays on the hips.
- Motion model: the 3D track (Z = Z24/S, X = uZ/f, Y = vZ/f) fits a straight line with Blender's
  smoothstep easing (3τ²-2τ³) almost exactly. Best fit: τ = (k+0.4)/79.5, rms 2-3 cm.
- Depth ratio checked a second way: the projective line fit u = (α+βE)/(1+γE) to the pelvis pixel track gives
  γ = -0.546 (end/start depth ratio 2.20). The SIFT scale gives γ = -0.537 (2.16). Used γ = -0.542.
- Anchor: range 23.137 m at t = 1 s, converted to optical-axis depth with the pixel angle (cos ≈ 0.974).
  Start depth Z_A = 25.67 m.
- Focal length: the body length (helmet top to feet) is about 260-263 px at frame 24.
  With H = 2.2 m and Z = 22.5 m this gives f ≈ 2690 px, a lower bound because tilt shortens the image length.
  Used f = 2800. f only affects the lateral part, so f from 2500 to 3200 changes the speeds by about ±1.5%.
- Displacement vector B = (-6.29, -3.40, -13.91) m, |B| = 15.64 m.
  Speed = |B|·ΔE·24 (backward difference).
  Acceleration = change of speed per second, taken as the mean of the forward and backward differences
  (the two differ by 3-12%). It is SIGNED: negative while the astronaut decelerates (t = 2 s and 3 s).
  If the ground truth uses magnitudes, the absolute values are 1.754 and 6.919.

## Answers (confidence)
- 1989 v(0.5) = 3.606 m/s (medium; the timing offset a ∈ [-1, 0] gives 3.54-3.73)
- 1990 a(0.5) = 5.994 m/s² (medium)
- 1991 v(1) = 5.958 m/s (medium-high)
- 1992 a(1) = 3.411 m/s² (medium)
- 1993 v(2) = 6.786 m/s (medium-high)
- 1994 a(2) = -1.754 m/s² (low-medium; small value and the sign convention is uncertain)
- 1995 v(3) = 2.450 m/s (medium)
- 1996 a(3) = -6.919 m/s² (medium; sign convention uncertain)
