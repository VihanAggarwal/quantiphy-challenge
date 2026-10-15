# simulation_0200 (A2MS, 2560x2560, 14 frames @60fps)
Droplet falls from dropper tip straight down (x~1175 px), static camera.
Track: background diff vs last frame (droplet gone); bbox top y per frame 0-11:
518,539,580,654,756,888,1049,1239,1459,1706,1983,2287. Second diffs ~29 px/frame^2.
Quadratic fit frames 2-10 (top): a = 29.06 px/frame^2 = 104,600 px/s^2 -> scale 9.27e-5 m/px
(centroid fit gives 9.38e-5, ~1% diff). Fall starts ~frame 0 (vertex at -0.04 frame).
Sizes (px -> m): droplet 83 tall x 53.5 wide (stable over frames, thresholds 15-40);
neck threads ~235 px, collar bead ~253 px -> used 240; body 711..1070 = 359 px;
SKYNOVA lettering y 679..949 = 271 px.
Speeds: backward diff from fit; frame 12 (t=0.2) droplet out of view -> extrapolated (1.865 fit).
Measured frame 3: 74 px/frame -> 0.41; frame 6: 161 px/frame -> 0.895.
Confidence: speeds high; droplet/body/lettering medium (assumes same depth scale as droplet); neck medium-low (which part counts).
