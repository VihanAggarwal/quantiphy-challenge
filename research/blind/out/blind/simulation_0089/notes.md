# simulation_0089 notes (S2MX, 2D bottom-up sky view, 24 fps, 30 frames)

## Scene
- Camera looks straight up at two birds in a horizontal plane (sky background). Big bird (bald-eagle model) flies left,
  small bird (dark crow-like model) flies right. Both fly in straight horizontal lines at the same image row (y~552-556).
- Video frames 0 and 1 are identical (animation clamped before first keyframe). Big bird leaves frame by f6, small by f10;
  frames 10-29 are empty sky (used as background).

## Measurements (scripts/extent.py, speed.py, wingroot.py; bg subtraction vs median of frames 12-29)
- Small bird x-extent (beak to tail): 108.6-110 px (subpixel/thresholds), constant over frames.
- Big bird x-extent: 174-175 px; ratio big/small length = 1.600-1.603.
- Speeds (linear fits of edge tracks, residuals <0.4 px): big 150.3 px/frame, small 91.93 px/frame, constant (linear motion).
- Wingspan (y-extent) varies with flapping: big 230-232 px (f0/f1) -> 384 px (f5); small 169 (f0/f1), 199, 206, 199, 175, 136, 161, 169.

## Scale
- Interpretation A (chosen): length = world X extent = beak-to-tail (flight along image x = world X). s = 0.94/109.3 = 0.0086 m/px.
  Check: speeds become 31.0 and 18.98 m/s, i.e. both integer (31, 19) at L=109.3 px, matching the measured 108.6-110 px
  -- strong numerical support for A. (Alt. B: length = wingspan -> scale 1.54x smaller; rejected, ~20% risk.)

## Answers
- 139 big length = 1.60*0.94 = 1.505 m (conf: medium-high).
- 140 big width = Y extent; first-frame pose 231 px -> 1.99 m; hedged +5% toward fuller-span poses -> 2.08 m (conf: low; pose convention unknown, full spread would be ~3.3 m).
- 141 small width: first-frame 169 px -> 1.45 m; hedged -> 1.52 m (conf: low-medium; full spread ~1.77 m).
- 142/143 avg speed: v = 19 / 31 m/s; first frame duplicated (zero backward diff) so GT mean likely 28/29 v; chose 0.965 v -> 18.35, 29.9 (covers v and 28/30 v within ~3.5%).
- 144 separation at 0.5 s (video frame 12, extrapolated at constant velocity): bbox-centre 27.0 m, wing-root origins 27.5 m; frame-13 alternative 29.3 m; chose 27.8 m (conf: medium).
