# simulation_0080 — top-down view, walker (moving +x) and cyclist on a cyan bike (moving -x)

Video: 1920x1080, 29 frames @24 fps. Frames 0 and 1 identical (static first frame); time convention t = frame/24.
Camera static (band-pass phase correlation of the floor between consecutive frames: shifts < 0.1 px).

## Scale
- Bike extent (all-colour difference from median background, half-max sub-pixel edges) near image centre: 380.8 px
  -> k_bike = 380.8/1.7 = 224.0 px/m at bike-end height (~0.35 m, wheel tips).
- Camera is perspective (parallax visible): relative to the bike centre, the handlebar moves with slope 1.0317 and the
  rider's head (template tracked) with slope 1.0667 as the bike crosses the frame. Solving (Z - 0.35)/(H - Z) gives
  camera height H ~ 21 m (handlebar ~0.98 m, rider head ~1.64 m), f ~ 4600 px (HFOV ~23 deg). Results are insensitive to
  H in 19.5-22.5 (< 1%).
- Walker head (top-view hair blob, z ~1.68 m): k_head = f/(H-1.68) ~ 239.4 px/m.

## Measurements
- Bike centre (mid of ends) moves -47.45 px/frame, perfectly linear (residual < 0.5 px) from frame 1 to 16
  -> 5.08 m/s (constant).
- Walker head track (dark blob, morphological opening r=14, centroid): mean 13.39 px/frame over frames 1-28;
  backward diff at frame 12 = 13.47; 5-frame smoothed 13.12. Gait oscillation of head speed 11.3-15.5 px/frame.
  -> 1.34 m/s (mean ~ instantaneous at frame 12).
- Distances: walker pelvis = head XY minus 3 cm along travel; bike origin = bbox centre (mid of ends, axis y=640).
  Horizontal distance: 3.18 m at frame 12, 6.36 m at frame 24 (bike extrapolated: only rear tip visible at frame 24).
  With an unknown vertical offset between pelvis (~0.95 m) and bike origin (0-0.5 m), 3D distance 3.18-3.33 / 6.36-6.43;
  answered the middle: 3.24 / 6.39.

## Confidence
- Q81 bike speed 5.08: high (direct, same-height length and motion).
- Q80 walker speed 1.34: medium-high (pelvis instantaneous speed may deviate +-5% from head-based estimate).
- Q82 distance 3.24: medium (bike origin location along the bike and vertical offset unknown; +-1 frame timing = +-8%).
- Q83 distance 6.39: medium-high.
