# simulation_0208 notes
Typewriter free-falls (frames 0-10, lands ~0.44 s) onto a long desk; camera level (horizon from table side-edge vanishing point at y~542 = image centre).
- Pixel acceleration from quadratic fits of bbox edges (frames 0-6): 12.0-12.1 px/frame^2 -> s = 9.8/(12.12*576) = 1.404e-3 m/px at the typewriter front-bottom depth. Release time fit: -0.25 frame.
- Speeds (backward difference, physical free fall): v(n) = 9.8*(n-0.5+0.25)/24 -> 0.125s 1.12, 0.25s 2.35, 0.333s 3.16 m/s. High confidence.
- Table: far edge corners x 273..1797 (1524 px) at row 947; typewriter contact row 1027; depth ratio (1027-540)/(947-540)=1.197 -> 2.56 m. Medium.
- Typewriter length: in-air frontal width 293 px -> 0.41 m. Medium.
- Typewriter height: plate top to base ~123-143 px in air -> ~0.18 m. Low-medium (pose/perspective ambiguity).
- Letter: front edge 194 px at row 1002, depth ratio 1.054 -> 0.29 m. Medium-low.
