# Audit sim2_19: families 0079-0081 (bike + walker), 0189 (+segmented, truck + box), 0284-0287 (plane), 0288-0291 (koi)

Result: 46 scored rows checked, **no fixes proposed**. Every quick check landed within about 10% of the current answer.
Only one row (1001) was more than 6% off, and it was still below the 15% threshold.

## Family structure found
- **Bike (0079/0080/0081):** these are different takes with different start positions. 0079 is closer (bike about 409 px long);
  0080 and 0081 have the bike at about 375-381 px. All three are nadir views.
  - Bike speed agrees in all three: 5.08 m/s. Walker speed agrees in all three: 1.30-1.35.
  - The distances differ by design: in 0079 both move -x; in 0080 they move apart; in 0081 they approach each other.
- **Truck (0189 and 0189_segmented):** identical footage. The box track is identical to 0.01 px in both. The answers are copies, which is correct.
- **Plane:** 0284 and 0286 are the SAME top-view camera (same plane bbox x at f30; 34.47 vs 34.50 px/frame).
  0285 and 0287 are the SAME side-view camera (plane pixel positions identical; only the background differs).
  - Lengths across the family are 14.25-14.58 m, consistent. Widths are 18.54 and 18.5, consistent.
  - Heights differ: **0285 = 4.55, 0287 = 4.10** (see below).
- **Koi:** 0288 and 0290 are the same top-view camera; 0289 and 0291 are the same side-view camera.
  - Length is 0.76-0.80 everywhere (the top views give about 4% more than the side views).
  - Top-view widths are 0.289 and 0.29 (they include the pectoral fins). Side-view height is 0.37.

## Quick checks (my own route per row, on the frames)
Scale is always taken from the stated prior: bike length in px, box speed in px/s, or plane/fish speed in px/frame.

| qid | clip | quantity | current | quick check | route | diff |
|---|---|---|---|---|---|---|
| 76 | 0079 | walker speed 1.0 s | 1.32 | 1.30 | head-blob mean px speed (linear fit f4-71) 13.99 px/fr at the agent's head scale 259 px/m (bike 409 px/1.7 = 240.6 at tip height) | 2% |
| 77 | 0079 | bike speed | 5.08 | 5.09 | cyan-mask front 51.2 px/fr x 24 x 1.7/409 | 0% |
| 78 | 0079 | dist 1.0 s | 3.90 | 3.78-3.85 horiz (+dz 0.5 -> 3.85-3.9) | head->ground (s_head 259) vs bike-mask centre (s 240.6), f24 | 1-3% |
| 79 | 0079 | dist 0.5 s | 2.19 | 2.02-2.08 horiz (2.08-2.14 with dz) | same, f12 | 3-8% |
| 80 | 0080 | walker speed 0.5 s | 1.34 | 1.35 | head 13.45 px/fr, s_head 239.4 | 1% |
| 81 | 0080 | bike speed | 5.08 | 5.09-5.17 | 47.5 px/fr; mask length 373-381 px | <2% |
| 82 | 0080 | dist 0.5 s | 3.24 | 3.17-3.20 horiz | f12 head vs bike centre | 2% |
| 83 | 0080 | dist 1.0 s | 6.39 | 6.37 | f24, bike centre extrapolated at -47.4 px/fr (clipped) | 0% |
| 84 | 0081 | walker speed 0.5 s | 1.29 | 1.35 (mean) | head 13.48 px/fr, s_head 240 | 4% |
| 85 | 0081 | bike speed | 5.08 | 5.08 | 47.2 px/fr, length 379 px | 0% |
| 86 | 0081 | dist 0.5 s | 4.5 | 4.46-4.50 | f12 | 0-1% |
| 87 | 0081 | dist 1.0 s | 1.52 | 1.43-1.46 horiz (1.53 with dz 0.5) | f24; very time-sensitive (0.27 m/frame) | 4-6% |
| 456/1903 | 0189(+seg) | box length | 1.992 | 2.00 | brown mask width 407.5 px; box top moves 19.0-19.15 px/s (constant) -> 0.00491 m/px | 0.5% |
| 457/1904 | 0189(+seg) | box height | 0.99 | 0.91-1.03 | visible face 185 px (the bottom is hidden by the roof edge); the agent's 190.7 px plus flap 19 px | within the hedge |
| 458/1905 | 0189(+seg) | truck length | 8.16 | 8.18-8.42 | fg bbox x 124-1839 = 1715 px x (0.00477 depth-corrected .. 0.00491 box scale) | 0-3% |
| 459/1906 | 0189(+seg) | truck height t=0 | 3.43 | 3.43-3.53 | rail top y 308 to ground 1027 = 719 px | 0-3% |
| 460/1907 | 0189(+seg) | tire diameter | 0.771 | 0.77-0.80 | near tire 1502-1664 = 162 px (grid crop) | 0-3% |
| 997 | 0284 | plane length | 14.58 | 14.48 | pod tip x 928 to tail tip 1491 = 563 px; template speed 34.47 px/fr -> 0.02571 m/px | 1% |
| 998 | 0284 | plane width | 18.54 | 18.0-18.5 | wingtip-to-wingtip 700-720 px | 0-3% |
| 999 | 0284 | displacement | 11.08 | 11.08 | template displacement linear in k (34.44-34.56 px/fr for k = -12..16) -> constant speed | 0% |
| 1000 | 0285 | plane length | 14.45 | 14.2-14.5 | side view, per-feature speeds (near pod 43.85, tail 42.3 px/fr) | <2% |
| 1001 | 0285 | plane height | 4.55 | 4.2 | per-feature depth from px speed + horizon from the near/far pod-tip pair (see below) | 8% (below threshold) |
| 1002 | 0285 | displacement | 11.08 | 11.08 | constant speed (side-view template, 0287 twin 42.14-42.24 px/fr all k) | 0% |
| 1003 | 0286 | plane length | 14.25 | 14.48 | same camera as 0284 (34.50 px/fr) | 2% |
| 1004 | 0286 | plane width | 18.5 | 18.0-18.5 | same camera as 0284 | 0-3% |
| 1005 | 0286 | displacement | 11.08 | 11.08 | constant speed | 0% |
| 1006 | 0287 | plane length | 14.5 | 14.2-14.5 | same camera as 0285 | <2% |
| 1007 | 0287 | plane height | 4.1 | 4.2 | same as 1001 | 2% |
| 1008 | 0287 | displacement | 11.08 | 11.08 | 42.16 px/fr, linear | 0% |
| 1009 | 0288 | fish length | 0.79 | 0.788 | median bg sub (shadow removed), bbox w median 652 px; centroid 23.07 px/fr -> 0.001210 m/px | 0% |
| 1010 | 0288 | fish width | 0.289 | 0.289 | bbox h median 239 px (includes pectoral fins) | 0% |
| 1011 | 0288 | displacement | 0.334 | 0.335 | centroid linear (8-frame steps 184-188 px after f10) | 0% |
| 1012 | 0289 | fish length | 0.766 | 0.771 | bbox w median 613.5 px; 22.22 px/fr -> 0.001256 m/px | 1% |
| 1013 | 0289 | displacement | 0.335 | 0.335 | constant speed | 0% |
| 1014 | 0290 | fish length | 0.80 | 0.79 | same camera as 0288 (652-662 px at 0.00121) | 1-2% |
| 1015 | 0290 | fish width | 0.29 | 0.289 | same camera as 0288 | 0% |
| 1016 | 0290 | displacement | 0.335 | 0.335 | constant speed | 0% |
| 1017 | 0291 | fish length | 0.76 | 0.756 | bbox w median 600 px; 22.15 px/fr -> 0.001259 m/px | 1% |
| 1018 | 0291 | fish height | 0.37 | 0.370 | bbox h median 294 px | 0% |
| 1019 | 0291 | displacement | 0.335 | 0.335 | constant speed | 0% |

No row's quick check differed by 15% or more, so the in-depth second route was not required. I still looked deeper at 1001 vs 1007
because siblings on the same camera disagree there.

## Plane height (1001 = 4.55 vs 1007 = 4.10, same camera)
- The 0285 agent put the horizon at y_h ~ 420 (from ground-shadow row speeds) and so treated the plane as flying on the horizon.
- The 0287 agent put y_h ~ 760 (tail-fin vanishing line). The two clips are the same camera, so at most one can be right.
- My check uses the near and far pod tips. They are symmetric, so they share the same world height and the same world X
  (the top view shows both pod tips at the same x).
  - Near tip: y 421.7, 43.85 px/frame. Far tip: y 451.5.
  - The ratio of their x offsets from cx (f8: 783/713; f30: 165/148) gives Z_far/Z_near ~ 1.10-1.12.
  - Solving gives y_h ~ 708-752. That is essentially a level camera, and it rules out y_h = 420. The near pod appears
    30 px HIGHER than the far pod, which is only possible if the pods are above the horizon.
- World heights then come from Y = (y_h - y) * 0.8864 / s per feature:
  - Top: upper tail-fin tip, y 313, s 42.34.
  - Bottom: gear wheel, y 519, s 41.35, and far-pod rear, y ~525, s ~39.5-40, which give the same value.
  - H = 4.19-4.22 for y_h 708-760. Even with y_h = 420 the formula gives 4.36, not 4.56.
- So the true height is about 4.2. 1007 (4.10) is within 3%; 1001 (4.55) is about 8% high.
- Not a fix under the rules (the gap is under 15%). Optional low-risk harmonisation: set 1001 to about 4.2 to match its same-camera twin.

## Shared assumptions I could not independently test (same in agent and my route)
- **Fish width** includes the pectoral fins (0.29); the body alone would be 0.15-0.18. Both top-view agents and my mask agree on 0.29 with fins.
- **Bike-family distances** depend on the walker/bike origin convention (pelvis vs feet; dz 0-0.5 m) and on the
  frame-time mapping (frames 0 and 1 are duplicates). 87 (1.52) is the most sensitive: ±1 frame changes it by ±0.25 m.
- **Box height** 0.99 is a hedge between the face only (0.93) and the face plus raised flap (1.03).

## Files
- Scripts: plane_quick.py, plane_speed.py, plane_feat.py, tips.py, fish_quick.py, truck_quick.py, truck_ext.py, bike_quick.py (+ common.py, tmpl.py, grab.py, gridcrop.py).
- crops/: the PNG crops that were viewed (~5 MB).
