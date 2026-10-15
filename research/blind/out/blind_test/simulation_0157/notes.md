# simulation_0157 (A2SS, turtle swimming left, 24 fps, 48 frames)
- Shell template tracking (TM_CCOEFF_NORMED, subpixel, frames 19-47): x(f) fits quadratic well; a = 0.9457 px/frame^2 = 544.7 px/s^2.
- Scale = 2.639 / 544.7 = 0.004845 m/px. Motion is purely horizontal (y constant), so a single planar scale is used.
- Speed (backward diff of the fitted track): f24 21.56 px/fr -> 2.51 m/s; f36 32.91 px/fr -> 3.83 m/s (raw diffs 21.05 / 32.9). Starts near rest (v=0 at about frame 0.7).
- Length: head-to-rear extent about 315 px (frames 36-47 bbox widths 305-312 px, head is faint) -> 1.52 m.
- Confidence: speeds high (~3%), length medium (~5-8%).
