# simulation_0201 - falling droplet from dropper (3D sim, 60 fps, 14 frames, 2560x2560)

## Method
- Droplet segmented in frames 0-9 by differencing against the last frame (droplet gone), blur, threshold 12, close, fill holes. Overlays checked visually (work/seg.py). It leaves the frame after frame 9 (t=0.15 s).
- 3D pinhole fit (work/fit.py): principal point at the image centre, f free, fall direction g (camera coords) free, s(t)=v0 t + 0.5*9.7 t^2,
  P(0) = 0.156 m along the ray of the frame-0 centroid (range convention), constraint |P(0.1)| = 0.186 m. Pixel residuals are under about 1 px (frames 0-7).
  Result: f=3771 px (FOV 37.5 deg), g=(0.001,0.784,0.621), v0=0.009 m/s, so the drop is released from rest at about t=0.
- Cross-checks:
  - The drop's bbox width times the fitted range stays constant within 2% (frames 0-6). Width ratio 123/103 matches 0.186/0.156.
  - The vertical vanishing point from the pedestal corner edge plus the drop track is (1285,5974). The fit predicts (1286,6045).
  - Computing per-frame s_k by ray-line intersection gives backward speeds of 0.411 (t=0.05) and 0.901 (t=0.1), and frame-to-frame acceleration of about 9.2-9.8.
  - Using optical-axis Z instead of range, dropping frames 8-9, or adding a width constraint changes answers by under 0.5%.
- Speed uses the backward difference: v(t) = v0 + a (t - 1/120).

## Answers
- 1446 (t=0.05): 0.413 m/s. High confidence if the convention is backward difference; the instantaneous value would be 0.494.
- 1447 (t=0.1): 0.898 m/s. High confidence (instantaneous: 0.979).
- 1445 (t=0.2): 1.868 m/s. Medium-high confidence: extrapolated because the drop is out of frame, assuming continued free fall (no impact).
