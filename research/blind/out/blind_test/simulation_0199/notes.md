# simulation_0199 (2D, 60 fps, 14 frames, 2560x2560)
Droplet falls from pipette tip (frames 0-10, exits bottom at frame 11). Mask = colour diff vs frame 13 (droplet absent).
Bbox mid-y: 743,759.5,809,889.5,1001.5,1145.5,1321,1528,1768,2038.5,2340.5 -> 2nd diffs ~31.7 px/frame^2 (very steady).
Quadratic fit (frames 1-10) of x,y; speed via backward diff -> accel 114093 px/s^2 -> scale 9.7/114093 = 8.50e-5 m/px.
Droplet bbox ~90 x 57 px (steady across frames). Bottle body edges 1702-2132 (430 px); neck incl. threads 1772-2067 (~295), under threads ~252 -> used 290.
SKYNOVA text is vertical: image x-extent 1784-1823 (39 px), y-extent 814-1142 (328 px); answered literal horizontal/vertical.
Speeds: frame 3 (0.05s) 0.411, frame 6 (0.1s) 0.896, frame 12 (0.2s, droplet off-screen, extrapolated from fit) 1.866 m/s.
Confidence: speeds high; droplet/body high-medium; neck medium; text width/height medium-low (orientation ambiguity, same-depth assumption).
