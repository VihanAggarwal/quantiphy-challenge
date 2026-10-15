# simulation_0262 (A2SS, red cup free fall, 24 fps, 1080x1920)
- Cup enters top ~frame 3, falls, lands ~frame 18-19 (bottom px 1845), rests.
- Tracked red-mask top/bottom per frame (track2.py). Parabola fit frames 6-18: a = 11.2 px/frame^2 (bottom 11.36, top 11.02, mid 11.2), residuals <2 px; vertex (release) ~frame 0.
- Cup width constant (~64-65 px red median) during fall -> uniform scale. Scale = 9.8/(11.2*576) = 1.519e-3 m/px.
- Speeds: backward diff with release at t=0 -> v = 9.8*(n-0.5)/24; checked directly vs midpoint diffs (frame 12: 128.5 px/frame -> 4.685 m/s).
- Height: rest frame, lid top ellipse centre ~1696, bottom ellipse centre ~1839 -> 143 px (camera elevation ~11 deg; cos factor cancels with fall projection) -> 0.217 m. Confidence medium (lid edge faint, +-5%).
- Speeds confidence high.
