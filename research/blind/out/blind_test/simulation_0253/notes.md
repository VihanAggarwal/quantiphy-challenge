# simulation_0253 (S2SS, box sliding down slope, 24 fps, 45 frames)
Method: box mask = saturation>70 & diff from frame0 (box absent at t=0). Along-slope coordinate (unit vector (1080,1000)) of
mask centroid / leading / trailing edge per frame. Frames 27/28 and 10/11 are duplicates (frame 27 shows true frame 28) -> frame 27 dropped.
Scale: front-face edge parallel to slope ~85 px (82-88 measured on zoomed gridded crops f20, f30) -> 0.611/85 = 0.00719 m/px;
perpendicular extent shrinks 74.5->72.5 px over the clip so scale increased ~1-2.6% for later frames.
Cubic fits (frames>=16, residual <~1.6 px) give px/frame backward speeds 18 (f12, extrapolated, box entering frame), 37.0 (f24),
52.7 (f36), 59.2 (f42); pixel acceleration declines 1.7 -> 1.45 -> 1.15 -> 1.03 px/frame^2 (quadratic fit avg 1.3).
Answers: speeds 3.1/6.38/9.2/10.48 m/s; accel 6.9/6.0/5.0/4.6 m/s^2 (slightly hedged toward constant accel).
Confidence: speeds at 1,1.5,1.75 s medium-high (scale +-5%); speed at 0.5 s medium (box partially off-frame);
accelerations medium-low (trend vs constant-accel ambiguity, constant fit would be ~5.5).
