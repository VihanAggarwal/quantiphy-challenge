# simulation_0281 (S2SC, top-down whale, 3840x2160, 24 fps, 72 frames)
Method: planar 2D scale from prior length 19.17 m. Whale length at frame 0 = nose x 1123 -> fluke tip x 3466 = 2343 px
(length oscillates 2127-2377 px as fluke pitches; frame-0 value used) -> 0.008182 m/px.
Head tracked by template matching on blurred HSV saturation (track2.py, nose_track.txt): ~8.5-8.6 px/frame leftward, near-constant, y drift <4 px.
- 989 speed @1.0s: linear fit frames 16-32 -> ~8.6 px/frame *24*s ~1.68 m/s. Confidence medium-high.
- 990 width: pectoral-fin y-span varies 954 px (f0, 7.8 m) to 1149 px (f24, 9.4 m), mean 8.7 m; chose 8.2 m hedge. Confidence low-medium.
- 991 displacement 0.5->1.0 s: frames 12->24 head moved 104.4 px -> 0.85 m. Confidence medium-high.
