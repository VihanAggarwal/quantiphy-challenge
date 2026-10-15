# simulation_0156 (2D, shark + leatherback turtle, 1920x1080, 48 frames @24 fps)
Static camera; median background is clean. Both animals swim leftward, horizontally (no vertical drift).
Scale: shark speed by frame-to-frame template matching (body template, subpixel): 57-59.7 px/frame, mean 58.7 px/frame
= 1409 px/s -> 7 m/s => 0.004969 m/px.
- 357 shark length: nose tip x~621 to tail tip x~1545 at frame 20 (zoomed crops), ~914-924 px over frames 14-26 -> 920 px -> 4.57 m. Conf: medium-high.
- 358 shark displacement: constant speed over 47 frame intervals = 7*47/24 = 13.71 m (2759 px). Conf: medium (14.0 if 2 s convention).
- 359 turtle speed at 1 s: shell template shift 21.5-22.4 px/frame (frames 20-28 mean ~21.9) -> 525.6 px/s -> 2.61 m/s. Conf: medium-high (assumes same depth plane as shark).
- 360 turtle length: bbox width varies with flipper pose 297-352 px (median ~312, extended ~346) -> ~320 px -> 1.6 m. Conf: medium.
