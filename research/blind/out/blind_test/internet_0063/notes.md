# internet_0063 - bottle drop (camera rotated 90 deg: gravity = +x in image, floor at right)
- Static camera. Bottle tracked by median-background subtraction (track.py), centroids frames 42-52.
- Parabola fit x(frame) frames 44-52: a = 11.4-11.6 px/frame^2 -> scale ~1056 px/m (g=9.8, 30 fps). Range 1030-1110.
- Height: held bottle cap-to-base 256 px -> 24.2 cm (med conf). Diameter 69 px -> 6.5 cm (med).
- v(1.5s)=66.7 px/fr -> 1.89 m/s; v(1.7s)=136 px/fr -> 3.87 m/s (dv consistent with g*0.2s). Med conf.
- Displacement 1.5->1.7: centroid 459.6->1064.2 px = 605 px -> 0.573 m (med-high).
- Floor contact x~1475 px (bounce at frame 54); bottle base at 1.5 s x~560 -> 0.866 m. Time-to-impact check consistent (~frame 53). Med.
