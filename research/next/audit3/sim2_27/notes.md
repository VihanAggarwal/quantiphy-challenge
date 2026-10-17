# Audit sim2_27 (Track A, 2D sims + 2 internet segmented clips)

Input: research/next/audit3/inputs/sim2_27.json (44 rows, all scored). Scripts are in scripts/ (frame.py crop dumper,
track.py subpixel template tracker, bgobj.py / birds*.py / seg0121.py / apple.py / eleph.py / pizza.py mask trackers,
crow2.py second route for the crow). The crops I looked at are kept here as PNGs. The folder holds no frame stacks.

## Family structure
Most families have only one clip. The twins are 0121 + 0121_segmented and 0177 + 0177_segmented. Their current answers
are identical, and my tracks on the segmented twin agree with the original clip's agent notes. No clip in this item
is scaled differently from a sibling. Note: internet_0017.mp4, which is not in this item, shows a different scene (a
plant) from internet_0017_segmented (keyboard/hands), so it cannot be used as that clip's twin.

## Current answers that differ from the per-clip agent's own answers.json (changed downstream; provenance still "agent/pipeline")
- 0007 q4 boat speed: agent 1.40, current 1.5
- 0091 q149 crow length: agent 0.528, current 0.94   <-- large change, see fix
- 0094 q160 car length: agent 5.57, current 5.67
- 0091 q146: 17.973 vs 17.98 (rounding only)

## Quick check of every scored row (my own route on the frames)
| qid | clip | quantity | current | quick check (route) | diff |
|---|---|---|---|---|---|
| 1 | 0007 | pier width | 1.48 | ~83 px x 3.62/200-207 px = 1.45-1.50 (boat tip-stern 200 px, oar-end 207 px) | <3% |
| 2 | 0007 | pier length | 5.8 | ~324-328 px -> 5.7-5.9 | <3% |
| 3 | 0007 | min dist pier end-boat t=3s | 1.88 | ~105-110 px -> 1.85-1.99 | <6% |
| 4 | 0007 | boat speed 1.0 s | 1.5 | template track 233.6 px/72 fr = 3.245 px/fr = 77.9 px/s; x 3.62/(200..207) = 1.36-1.41 | 6-10% (below fix threshold; the agent had 1.40) |
| 15 | 0047 | booth width | 1.20 | roof 111-113 px; walker-head scale 1.236/109.8 px/s = 0.01126 m/px -> 1.25 planar, 1.20 with roof-height correction | <=4% |
| 16 | 0047 | planter length | 3.28 | hedge 270 px x 0.0113-0.0120 = 3.04-3.24 | <=7% |
| 17 | 0047 | bike length | 1.76 | ~150 px x 0.0115 = 1.73 | 2% |
| 18 | 0047 | bike speed 1.0 s | 4.88 | rack track 12.82 px/fr vs walker 3.326 px/fr -> 4.76 (same-height) to 5.08 (ground scale) | <=4% |
| 146 | 0091 | eagle speed | 17.98 | centroid 128.1 px/fr / crow 78.43 px/fr x 11 = 17.97 | 0% |
| 147 | 0091 | bird distance 0.3 s | 9.648 | frame 7: eagle centroid extrapolated -32, crow 1630 -> 1662 px x 0.005844 = 9.72 | 1% |
| 148 | 0091 | eagle length | 0.874 | 147.6-150 px x 0.005844 = 0.86-0.88 | 1% |
| 149 | 0091 | crow length | **0.94** | 87-90 px x 0.005844 = **0.51-0.53** | **+78%** -> in-depth check, FIX |
| 160 | 0094 | car length | 5.67 | bg-diff extent 129-136 px x 0.04397 (centroid 28.43 px/fr) = 5.67-5.98; agent half-contrast 126.5 px -> 5.57 | <=5% |
| 161 | 0094 | car height | 1.8 | 43 px -> 1.89 (before perspective trim) | 5% |
| 162 | 0094 | plane length | 37.57 | 838-853 px -> 36.9-37.5 | 2% |
| 163 | 0094 | plane height | 11.12 | 255 px -> 11.2 | 1% |
| 257 | 0120 | sofa length | 2.831 | y-extent 624-626 px; planar 3.11, perspective (top at 0.64 m, H~6.1) 2.83 | 10% (planar) |
| 258 | 0120 | TV length | 1.605 | planar 406/200.87 = 2.02 (+26%) is not a valid route: wall-mounted TV ~1-2 m above floor, front face visibly foreshortened. Radial-geometry route: L = (y-extent / radial distance at same edge) x D_tv = 1.03-1.05 x 1.535 m = 1.59-1.61 | ~1% (valid route) |
| 259 | 0120 | robot diameter | 0.348 | robot track 8.374 px/fr (frames 4-32) = 200.98 px/m; ~69-70 px -> 0.345-0.348 | 1% |
| 260 | 0120 | chessboard side | 0.392 | 83.3 px: planar 0.415, table-height-corrected 0.392 | <=6% |
| 261 | 0120 | tray length | 0.295 | 63 px: planar 0.314, corrected 0.295 | <=6% |
| 262 | 0121 | left ball v 0.5 s | 5.98 | segmented-twin bbox edges around f15 ~16.0-16.3 px/fr x 60/161 = 5.96-6.07 | <2% |
| 263 | 0121 | left ball v 1.0 s | 0.339 | segmented-twin centroid after collision 0.8-1.2 px/fr; smooth fit 0.965 px/fr -> 0.36 | 6% |
| 315 | 0133 | apple diameter | 0.0978 | saturation-mask extents 60-64 px x (9.8/6361) = 0.092-0.099 | <=5% |
| 316 | 0133 | table height | 0.9877 | apple centre drop table->floor 639-643 px -> 0.985-0.991 | <1% |
| 317 | 0133 | vx leaving table | 0.6617 | parabola fit frames 37-47: g_px = 6361 px/s^2, vx = 429.4 px/s -> 0.6615 | 0% |
| 318 | 0133 | horizontal flight displacement | 0.2966 | vertex f34.44 -> floor: t = sqrt(2*639/6361) = 0.448 s, 192 px -> 0.296 | 0% |
| 319 | 0133 | speed 1.2 s | 0.74 | p36-p35 = (-14.1, 7.9) px -> 484.8 px/s -> 0.747 | 1% |
| 423 | 0177 | elephant height | 3.2 | seg mask: centroid 3.36 px/fr -> 0.01766 m/px; median height 185 px -> 3.27 (agent's torso track 3.44 px/fr -> 3.19) | <=2% |
| 424 | 0177 | displacement | 3.5 | 200.7 px over f0-59 x 0.0173-0.0177 = 3.47-3.55; 1.424 x 59/24 = 3.50 | <1.5% |
| 1829 | 0121_seg | left ball v 0.5 s | 5.98 | same as 262 | <2% |
| 1830 | 0121_seg | left ball v 1 s | 0.339 | same as 263 | 6% |
| 1831 | 0121_seg | right last ball v 2 s | 2.54 | centroid p60-p59 = 6.78 px/fr -> 2.50-2.53; cubic-smoothed 6.95 -> 2.59 | <=2% |
| 1890 | 0177_seg | elephant height | 3.2 | same as 423 | <=2% |
| 1891 | 0177_seg | displacement | 3.5 | same as 424 | <1.5% |
| 2953 | int_0003_seg | pizza diameter cm | 46 | bills: short side 67-69 px, long side 137-145 px. "Width" = short side, matching card width = 5.4 cm in int_0017 and real Monopoly notes: 0.110 cm/px. Pizza 436 (v) - 462 (h) px -> 48-51 | 5-10% |
| 2954 | int_0003_seg | wine glass diameter cm | 12 | bowl/rim ~105-120 px, oblique view -> 11.5-13 | <10% |
| 2955 | int_0003_seg | cutter velocity 0.2 s cm/s | 42 | handle template track, duplicated frames; frames 3-9: 14.6 px/fr; frames 0-8: 11.75 px/fr; x 30 fps x 0.110 -> 39-48. The file decodes at 24 fps, but the json says 30; at 24 fps it would be 31-39 | ~0-10% at the json fps |
| 2956 | int_0003_seg | pepperoni diameter cm | 5.9 | ~54-55 px -> 5.9-6.0 | <2% |
| 2966 | int_0017_seg | container diameter cm | 9.8 | No credit card is visible in the segmented clip (checked frames 0-33), so the scale comes from the keyboard (Apple wireless, 27.9 cm long, 358 px -> 0.078-0.081 cm/px). Container 130 px -> 10.1-10.5 | <=7% |
| 2967 | int_0017_seg | keyboard length cm | 28.9 | 358 px x 0.078-0.081 | ~3% |
| 2968 | int_0017_seg | keyboard width cm | 13.5 | 159 px -> 12.4-12.9 | 5-8% |
| 2969 | int_0017_seg | pen length cm | 14.4 | 181 px -> 14.1-14.7 | <3% |
| 2970 | int_0017_seg | middle fingertip speed 0.4 s cm/s | 49 | middle fingertip f11 -> f12 ~20-23 px/fr x 30 x 0.08 = 48-56 | <15% |

## In-depth re-measure: q149 (simulation_0091, length of the small bird = crow)
- Route 1 is the background-difference bounding box (sky median of empty frames 12-29) at thresholds 20, 40 and 80.
  The crow's x extent is 89/87/80 px in the static frames 0-1 and 88-90 px in frames 8-10. Its size is the same at
  start and end, so it does not move in depth. The centroid moves from 1161.0 (f1) to 1866.9 (f10), which is
  78.43 px/frame. That gives a scale of 11/24/78.43 = 0.005844 m/px, and so a length of **0.51-0.53 m**.
- Route 2 is a subpixel column-darkness profile with 25%/50% contrast crossings. Beak to tail is 90.3 px / 86.6 px
  (frames 0, 8, 9, 10). The scale here comes from the beak-tip leading edge, 78.40 px/frame (the tail edge gives
  78.41), which is 0.005846 m/px. That gives a length of **0.528 m / 0.506 m**.
- The two routes agree within 4% (0.506-0.528). The current 0.94 is 78% above them.
- Why 0.94 is wrong: it needs a crow about 161 px long. No extent of the crow comes close to that. Its largest x extent
  in any frame is 90 px, and its largest y extent, with the wing raised, is 77 px. 0.94 m would also make the "small
  bird" longer than the eagle, which is 0.874 m (148 px in the same plane). The crow's scale comes from its own
  stated speed, so depth cannot explain the gap. The clip agent's own answer was 0.528, and the value was changed
  downstream by an unknown step. My guess is that it is a wingspan-like figure (about 1.8x the body length), but a
  side view cannot measure wingspan, and the eagle row (0.874 = body length) was not treated the same way.
- **Fix: 149 -> 0.528** (same as the clip agent's original answer and route 2 at 25% contrast).
- Caveat: if the downstream change to 0.94 was made on evidence I am blind to by design, the orchestrator should weigh
  that. From the frames alone, 0.94 is not supported.

## Not fixed (below threshold or no second route)
- 0007 q4 (1.5): my value is 1.36-1.41, which is 6-10% lower. That is below the 15% threshold, so I propose no change.
  The agent's own 1.40 was the frame-based value.
- 0120 q258 TV: the planar quick check is 26% off, but it is not a valid route for a wall-mounted TV high above the
  floor. The radial-geometry route, which barely depends on camera height, reproduces 1.59-1.61. Kept.
- internet_0003 q2955: the answer depends on the fps convention (the json says 30, the file decodes at 24). The
  current value matches the json fps. Kept.
- internet_0017: the credit-card prior cannot be measured in the segmented clip. All rows match a keyboard-based
  scale within 8%. Kept.
