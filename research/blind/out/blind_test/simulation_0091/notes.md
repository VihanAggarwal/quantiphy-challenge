# simulation_0091 — eagle (big bird, flying left) and crow (small bird, flying right), blue-sky background, 30 frames @24 fps, 1920x1080
Method: 2D planar scale from prior (crow speed 11 m/s). Static camera, uniform sky -> background colour difference mask (seg.py / inline scripts), bbox per frame at thresholds 25-90.
- Frames 0 and 1 identical (motion starts at frame 1). Both birds then move at constant pixel speed, no visible size change (same depth plane).
- Crow: beak edge 1199->1905 (f1->f10), tail edge 1110->1815 -> 78.39 px/frame = 1881 px/s -> scale 0.005847 m/px.
- Eagle: beak edge 669->157 (f1->f5), tail edge 818->49 (f1->f7) -> 128.08 px/frame.
- Q146 eagle speed = 128.08/78.39*11 = 17.97 m/s (constant). Confidence: high (given same-depth assumption).
- Q147 distance at t=0.3 s (frame 7): eagle mostly off-frame, bbox centre extrapolated -25 px (consistent with visible tail edge at 49); crow bbox centre 1625 px; dx=1650 px, dy~5 px -> 9.65 m. Confidence: medium (frame convention; 1 frame = 1.2 m change; origin location).
- Q148 eagle length: static frame 0 x-extent beak->tail 669..818 (149-150 px) -> 0.874 m. Confidence: medium-high.
- Q149 crow length: x-extent 1110..1199 (frame 0), 90-91 px in frames 8-10 -> 90.3 px -> 0.528 m. Confidence: medium-high.
Plausibility: bald eagle ~0.87 m at 18 m/s, crow ~0.53 m at 11 m/s.
