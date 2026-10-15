# simulation_0267 (A2SC, 24 fps, 2560x1440, 72 frames)
Static camera; spacecraft enters at rest on the right (nose x=1578 at frame 0), accelerates leftward, exits by frame 68.
Mask = |frame - last frame (empty background)| > 20, components unioned (track.py / fit.py, edges in edges.npy).
Motion: quadratic fits of nose/centre/tail x over frames 3-52: a = 656-660 px/s^2, start time t0 ~ 0 s (rms 0.5 px for nose).
Vertical extent and pixel height constant (~314 px) -> no depth change; scale constant.
Scale s = 4 m/s^2 / 657 px/s^2 = 0.00609 m/px.
- Length: projected length varies 1031 px (frame 10, oblique view, both fins visible separately) -> 981 px (frames 47-48, fins aligned = side-on); no motion blur (sharp fins). Use ~981 px -> 5.97 m. Confidence medium (perspective/oblique ±3%).
- Height: 306-318 px incl. fins (median ~314); slight underside visible, use ~312 px -> 1.90 m. Confidence medium.
- Speeds: constant accel from rest at t=0; backward difference v(n) = a*(n-0.5)/24: v(0.5s)=1.92 m/s, v(1.0s)=3.92 m/s (pixel check: nose diff 11->12 = 13 px/frame -> 1.90 m/s; 23->24 = 26 px/frame -> 3.80). Confidence high.
