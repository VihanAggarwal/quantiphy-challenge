# internet_0074 pickleball, top-down drone
- Video is 122 frames at 23.976 fps (5.09 s). It is 30fps footage with every 5th frame dropped, so times use container time (t*23.976). Camera is nearly static.
- Scale: court width 6.1 m = ~908 px (outer edges 333-1247, line centres 340-1242), about 0.00672 m/px. Length 2002 px gives 13.36 m. Kitchen lines check out (628 px = 4.27 m).
- Ball tracked by HSV colour threshold (track.py). v(1.0s) is ~1260 px/s, about 8.5 m/s. v(3.0s) is ~1215 px/s, about 8.2 m/s.
- Ball to net at 1.0s: ball y 1801, net tape y 1314, 487 px = 3.27 m.
- Net: posts at x ~263 and ~1292, 1029 px = 6.9 m (rule length 6.71 m; the net top is raised toward the camera).
- Players (body/hip centre, read from zoomed crops): 0s gives 2110 px = 14.2 m. 4.5s gives ~1400 px = 9.4 m. Ball to top player at 2.0s is ~2.85 m.
- Confidence: high for court length, net length and the speeds. Medium for the player distances (depends on which body point is clicked).
