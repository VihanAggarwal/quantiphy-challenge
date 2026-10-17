# Audit internet_09: clips internet_0009, 0018, 0026, 0029, 0041, 0042

Result: **no fixes proposed.** I quick-checked all 30 scored rows with my own pixel measurements or tracks.
Every current answer is within about 10% of my quick check, so no row reached the 15% threshold for an in-depth re-measure.
Scripts are in `scripts/` (frame.py, blobs.py, bright.py, cdiff.py, plus inline snippets). The PNG crops here are the ones I viewed.

## Families and cross-clip consistency
- Family "internet_0018" = {0009, 0018}. They share only the prior (singles width 8.23 m). They are **different footage**:
  0009 is a hard court filmed vertically (2160x3840 at 60 fps, low sun, long shadows), and 0018 is a clay court filmed horizontally (3840x2160 at 30 fps).
  No object is shared. Both scales were re-derived independently and agree with the agents' values:
  - 0009: singles sidelines about 1345 px apart, doubles/singles ratio 1.33, baseline to service line also consistent, giving 6.12 mm/px.
  - 0018: singles width about 920 px, doubles/singles ratio 1.34, giving 8.89 mm/px.
  Rally ball 18.5 m/s against serve 32.5 m/s is plausible.
- The other clips are singletons.

## Camera, fps and time-base checks
- 0009: background-difference blobs are stable, so the camera is static. File fps is 59.83 against the stated 60, which is negligible.
  The ball's shadow (dark blob, about 35 px/frame) is a separate track from the ball itself (light streak, about 52 px/frame). The agent tracked the ball, which is correct.
- 0018: the camera is static. File fps is 29.97.
- 0026: the camera pans. The background shift relative to frame 0 grows smoothly to about 68 px at frame 28 (phase correlation on the wall/stools, which accelerates late).
  **Time base:** the file runs at 19.68 fps (r_frame_rate 492/25), but the stated fps is 24. Truck steps alternate large and small, which looks like 29.97 -> 19.68 resampling.
  If the label used the file's real-time base, the speeds would be about 18% lower. I kept the stated 24 fps, as the agent did. This is a convention risk, not a fixable error.
- 0029: dropped frames confirmed (60 -> 50 fps; double steps at 6->7, 11->12, 16->17, 21->22). Frames 10, 15 and 20 map to real 0.2, 0.3 and 0.4 s.
- 0041: the camera is static.
- 0042: drone near nadir, static. File fps is 28.70 against the stated 30 (4%). The agent used 30.

## Quick-check table (all scored rows)
| qid | clip | quantity | current | quick check (route) | diff | verdict |
|---|---|---|---|---|---|---|
| 2047 | 0009 | player distance at t0 (m) | 6.0 | body centres (650,1500)-(1465,965): 975 px -> 5.97 | 0.5% | ok |
| 2048 | 0009 | ball avg velocity across net (m/s) | 18.5 | own bright-streak track f44->f70: 52.6 px/f -> 19.3 (whole flight 50.2 px/f -> 18.4) | 4% | ok |
| 2049 | 0009 | right player displacement (m) | 2.92 | crops f0/f110: body 459 px -> 2.81, head 3.07 | 4% | ok |
| 2089 | 0018 | player distance at t0 (m) | 25.5 | body points (788,640)-(3640,1180): 2903 px -> 25.8 | 1% | ok |
| 2090 | 0018 | benches to court (m) | 3.1 | bench front y~88 to doubles line y~432: 344-352 px -> 3.06-3.13 | 1% | ok |
| 2091 | 0018 | ball v at 1.5 s (m/s) | 32.5 | ball seen at f38 (3469,1129), f41 (3036,1073), f44 (2644,1024), f47 (2289,987): ~125 px/f near f45 -> 33.3 | 2.5% | ok |
| 2130 | 0026 | baby sitting height (cm) | 64 | 285 px x (90 cm / 400 px arm-top-to-floor at the sofa's near end) = 64.1 | 0% | ok |
| 2131 | 0026 | baby-man distance (m) | 2.35 | about 1100 px centre-to-centre x 0.225 = 2.48 (flat), lower with perspective | 5% | ok |
| 2132 | 0026 | truck length (cm) | 68 | 309 px (f28, unoccluded) x 0.225 = 69.5 | 2% | ok |
| 2133 | 0026 | truck height (cm) | 56 | 255 px x 0.225 = 57.4 | 2.5% | ok |
| 2134 | 0026 | truck speed at 0.5 s (cm/s) | 74 | yellow-chassis edge f10->f14: 13.75 px/f x 24 -> 330 px/s -> 74 (raw); camera-compensated flat 86, perspective-physical ~69 | 0% raw | ok (hedge) |
| 2135 | 0026 | truck avg speed (cm/s) | 71 | 370 px / 28 f x 24 -> 317 px/s -> 71 (raw); compensated flat 84; physical ~67 | 0% raw | ok (hedge) |
| 2997 | 0029 | ball diameter (cm) | 7.7 | own track. 60-fps-source parabola a = 8861 px/s^2 (rms 0.7 px); early 9308, late 8677 (ball recedes 77 -> 74 px). D = 7.9 (depth-corrected) to 8.35 (flat) | 3-8% | ok |
| 2998 | 0029 | v at 0.2 s (m/s) | 1.34 | central diff at f10 (60-fps steps): 1401 px/s x 1.0-1.05 mm/px = 1.40-1.48 | 5-10% | ok |
| 2999 | 0029 | v at 0.4 s (m/s) | 3.28 | central diff at f20: 3153 px/s x 1.045 mm/px (ball-size scale) = 3.29 | 0% | ok |
| 3000 | 0029 | ball-desk distance at 0.4 s (m) | 0.37 | bottom 645 to contact ~1005: 360 px x 1.015-1.045 = 0.365-0.376 | 1% | ok |
| 3001 | 0029 | ball-desk distance at 0.3 s (m) | 0.645 | bottom 371 to ~1005: 634 px -> 0.64-0.66 | 1% | ok |
| 3002 | 0029 | displacement 0.3->0.4 s (m) | 0.282 | cy 330.7 -> 604.4: 273.7 px x 1.03 = 0.282 | 0% | ok |
| 3054 | 0041 | middle duck displacement (cm) | 82.3 | crops f0/f25/f51: length 131/143/139 px; bill 2281->2105, tail 2412->2244: 172 px -> 82.3 | 0% | ok |
| 3055 | 0041 | middle duck avg speed (cm/s) | 38.7 | 82.3 / (51/24) = 38.7 | 0% | ok |
| 3056 | 0041 | ground pillar distance (cm) | 190.8 | front columns at x 1089, 1497, 1897, 2295, 2700, 3103: centre spacing 403 px -> 193; clear gap ~305 px -> 146 | 1% (centre) | ok; convention ambiguous |
| 3057 | 0041 | ground arch height (cm) | 256 | plinth base y~1413 to intrados apex y~866: 547 px -> 261 | 2% | ok |
| 3058 | 0041 | upper pillar distance (cm) | 108 | column centre spacing 224-226 px -> 107.6 (clear gap ~186 px -> 89) | 0% (centre) | ok; convention ambiguous |
| 3059 | 0041 | upper arch height (cm) | 157 | balustrade top y~571 to apex y~255: 316 px -> 151 | 4% | ok |
| 3060 | 0042 | white car width (m) | 1.86 | body 173-175 px x 4.572/445 = 1.78-1.80 (mirrors 2.05) | 3-4% | ok |
| 3061 | 0042 | black car width (m) | 1.76 | body ~165-170 px -> 1.70-1.75 | 1-3% | ok |
| 3062 | 0042 | black car length (m) | 4.68 | 445 (f0) to 480 (f20) px -> 4.57-4.93 | ~3% | ok |
| 3063 | 0042 | road width (m) | 14.5 | row 1900: road 508 -> 1880 = 1372 px -> 14.1 | 3% | ok |
| 3064 | 0042 | bridge width (m) | 16.5 | row 1900: outer bright edges 416 -> 1970 = 1554 px -> 16.0 | 3% | ok |
| 3065 | 0042 | white car avg speed (m/s) | 10.1 | bright-roof blob front f3->f43: 31.75 px/f (agent 31.4) x 30 x 0.01027 = 9.7-9.8 | 3-4% | ok |

## Notes on agent methods (skim)
- 0041 notes give 153 / 96 cm for 3056 / 3058 (a compromise between centre spacing and clear gap). The current answers are 190.8 / 108, which is the centre spacing; an earlier pipeline step changed them.
  My pixel spacings match the centre-spacing values. Whether the label means centre-to-centre or clear gap cannot be decided from the video, so I give no fix.
  All building answers use the duck's planar scale. The building lies behind the pond, so physical sizes would be larger, but the 2D convention is the likely annotation.
- 0026: the answers are hedges between the flat 2D ratio and a perspective model. The speeds use raw image motion without camera compensation.
  Compensated-flat (~84-86) and physical (~67-69) bracket the current 71-74, and each differs from it by less than 15%. No fix.
- 0029: careful dropped-frame analysis. My independent 60-fps-source fit reproduces the agent's numbers within 0-10%.
- 0009, 0018, 0042: methods sound. Low-confidence rows (3062, 2131) are still within 5% of my quick checks.

## Fixes
None. No row met the criteria: two independent routes agreeing within 8%, the current answer differing from them by 15% or more, and a concrete error.
