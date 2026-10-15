# simulation_0098_segmented (2D planar side view, white background, 1920x1080, 73 frames @24 fps)
Objects: red fishing boat (AH805) and a shark below it, both translating leftwards at constant speed.
Frames 0 and 1 show the same position (held first frame); motion is linear from frame 1 to frame 72.

Method: non-white mask (765 - RGB sum > 60, opening), split boat (y<760) / shark (y>=760); per-frame bbox + centroid
(work/track.py, work/fit.py, threshold sensitivity in work/thr.py).
- Shark x: slope -10.745 px/frame (xmin/xmax/centroid agree to 0.01), residual std 0.5-0.7 px.
- Boat x: slope -17.86 (bow) / -17.95 (stern) / -17.92 (centroid, fully visible frames 27+) px/frame.
- Scale from prior (shark 3 m/s): 3 / (10.745*24) = 0.011633 m/px.

Answers:
- 1896 boat avg speed: 17.90 px/frame * 24 * 0.011633 = 5.00 m/s (ratio boat/shark 1.666 ~ 5/3). If the held first frame
  (zero displacement) is counted, the average would be ~4.93; difference 1.4%. Confidence high.
- 1897 boat length: bbox width 857 px (854-861 over frames 27-72, insensitive to threshold) -> 9.97 m. Confidence high.
- 1898 shark length: bbox width ~278 px (276-281; tail swish) -> 3.23 m. Confidence high-medium.
- 1899 shark height: dorsal-fin top to pectoral-fin tip 103.6 px -> 1.21 m. Confidence medium (3D AABB could differ slightly).
