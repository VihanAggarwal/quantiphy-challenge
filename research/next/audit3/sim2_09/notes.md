# Audit sim2_09 — family simulation_0221 / simulation_0222

Same Blender living room, same nadir camera (identical framing; 0221 = sunlit render, 0222 = soft light).
Prior in both clips: vacuum diameter 0.438 m. All 32 rows scored; none are 'stated fact' / 'earlier audit fix'.

## Scale and family consistency
- Vacuum disc at rest (0222 frame 79): bbox 121x120 px, area-equivalent diameter 120.1 px. So s = 0.438/120.2 = 3.644 mm/px at the
  vacuum top. Floor scale is about 3.667 mm/px. Both agents used 120.3-120.5 px, which matches.
- The vacuum disc keeps a 117-123 x 119-120 px mask bbox along the whole path, so the scale is uniform in the motion plane (nadir camera).
- Both clips show the SAME scripted motion. I tracked each clip independently (0221 with its own gradient-annulus template).
  The positions agree to <= 0.4 px in every frame, so the motion labels must be identical across the twins.
- Sizes: the two agents (blind to each other) agree within 1-5 % on every object. Their pixel extents also match mine
  (listed below). Nowhere is a clip off by 1.3-2x, nor is an object or unit confused.

## Vacuum track (vacuum_track.csv)
Four tracks: 0222 positive-diff mask centroid (bg = frame79 with frame0 pasted at the end spot), 0222 TM_CCOEFF template,
0222 masked gradient-annulus template, and 0221 masked gradient-annulus template. Motion runs over frames 1..69 at 24 fps.
The speed profile is 0 -> 1.79 m/s (frame 25) -> 1.33 (frame 39, kink) -> 2.01 (frame 51) -> 0 (frame 69).

Label convention (task statement and qp/geometry.py docstring): s_i = |p_i - p_{i-1}|*fps, a_i = (s_i - s_{i-1})*fps,
i = round(t*fps), t=0 at frame 0. The raw a_i is noisy (about +-0.3 m/s^2 per frame), so it was evaluated on local fits:
- route P: local cubic/quartic polynomial fit of x(t), y(t) (hw 5-9) for each track separately, then the difference operator
- route V: local quadratic/cubic fit of the raw s_i series (hw 3-6) for each track separately, then (s(i)-s(i-1))*fps

| t | speed s_i (all tracks) | a_emu route P | a_emu route V | instantaneous d|v|/dt at t |
|---|---|---|---|---|
| 0.5 s (i=12) | 1.071-1.077 | 2.17-2.30 (22A noisier, up to 2.56) | 2.16-2.25 | 2.11-2.23 |
| 1 s (i=24) | 1.773-1.781 | 0.407-0.443 | 0.399-0.458 | 0.22-0.25 |
| 2 s (i=48) | 1.939-1.945 | 1.12-1.20 | 1.09-1.23 | 0.81-0.90 |

## Rows checked (quick check = my independent pixel measurement with s_floor = 3.667 mm/px and the same modest height correction)
| qid | clip | quantity | current | quick check | verdict |
|---|---|---|---|---|---|
| 649 / 665 | 21 / 22 | bench length | 1.02 / 1.00 | 290 px -> 1.06 raw, 1.01-1.03 corrected | ok |
| 650 / 666 | 21 / 22 | bench width | 0.41 / 0.401 | 115-118 px -> 0.40-0.42 | ok |
| 651 / 667 | 21 / 22 | TV stand length | 1.71 / 1.71 | 710 -> ~1197 (right end under lamp, symmetric shelf/legs) 487 px -> 1.71-1.73 | ok |
| 652 / 668 | 21 / 22 | TV stand width | 0.40 / 0.422 | top 112-120 px -> 0.39-0.42 | ok |
| 653 / 669 | 21 / 22 | lampshade diameter | 0.51 / 0.494 | 146-148 px -> 0.54 raw, 0.49-0.51 at rim height | ok |
| 654 / 670 | 21 / 22 | vase diameter | 0.255 / 0.246 | 72 px -> 0.264 raw, 0.245-0.255 | ok |
| 655 / 671 | 21 / 22 | floor-mirror width | 0.60 / 0.616 | bottom (floor) edge 1345 -> 1508, 162-165 px -> 0.59-0.61 (mirror leans, top edge magnified 1.20x) | ok |
| 656 / 672 | 21 / 22 | carpet diameter | 1.75 / 1.745 | y 592 -> 1070, 478 px -> 1.75 | ok |
| 657 / 673 | 21 / 22 | sofa length | 3.08 / 3.05 | x 568 -> 1452, 884 px -> 3.24 raw, 3.05-3.13 (arm height 0.4-0.6 m) | ok |
| 658 / 674 | 21 / 22 | sofa width | 1.70 / 1.62 | y 578 -> 1058, 480 px -> 1.76 raw, 1.64-1.70 (front-edge height 0.4-0.6 m) | ok (agents differ 5 %; within range) |
| 659 / 675 | 21 / 22 | speed 0.5 s | 1.07 / 1.07 | 1.075 | ok |
| 660 / 676 | 21 / 22 | acc 0.5 s | 2.15 / 2.15 | 2.2 (emu), 2.15 (inst) | ok |
| 661 / 677 | 21 / 22 | speed 1 s | 1.75 / 1.774 | 1.777 | ok |
| 662 / 678 | 21 / 22 | acc 1 s | **0.20** / 0.40 | 0.42 (emu), 0.23 (inst) | **fix 662 -> 0.42**; 678 ok |
| 663 / 679 | 21 / 22 | speed 2 s | 1.90 / 1.938 | 1.942 | ok |
| 664 / 680 | 21 / 22 | acc 2 s | **0.95** / 1.05 | 1.16 (emu), 0.85 (inst) | **fix 664 -> 1.16**; 680 -9 % (below the 15 % bar, left) |

## Fixes
- qid 662 (0221 acc @1 s): 0.20 -> 0.42. Route P gives 0.407-0.443 and route V gives 0.399-0.458, per track, on both clips.
  The 0221 agent took a linear fit of speed over +-3-4 frames centred on frame 24. That window straddles the speed peak
  at frame 25-26, so it flattens the slope to about 0.2-0.33. The label is (s_24 - s_23)*fps, measured where the speed is still rising.
  Twin 0222 has an identical trajectory, and its agent independently got 0.40.
- qid 664 (0221 acc @2 s): 0.95 -> 1.16. Route P gives 1.12-1.20 and route V gives 1.09-1.23. The same windowed-linear-fit-at-t method
  returns about d|v|/dt at t (0.85-0.98), but the label is the backward difference (s_48 - s_47)*fps, measured while the speed
  climbs to its peak at frame 51.
- Caveat: both fixes depend on the backward-difference-of-speed label convention stated for these clips. Under a pure instantaneous
  convention, the values would be about 0.23 and 0.85 instead.
- 680 (1.05) sits 9 % below 1.16. The rules leave it alone, but for twin consistency it could be set to 1.16 too.
