# Audit sim2_24: notes

Inputs: `research/next/audit3/inputs/sim2_24.json`. 45 rows, all scored. The provenance of every row is "agent measurement or pipeline".
I read only the per-clip agent notes. The notes files for `simulation_0012_segmented` and `internet_0026_segmented` do not exist; those rows are older pipeline values.
I did not open `internet_0026.mp4`, the unsegmented twin that shows the sofa prior. It has no test rows in this item, so it may be a validation clip.

## Family tables

| family | clip | prior | quantity | current | quick check (own route) | verdict |
|---|---|---|---|---|---|---|
| 0012 | 0012 / 0012_seg | bird 6 m/s | house eave to eave (q5, q1648) | 15.4 / 15.4 | 983-992 px eave tips; at bird depth (x0.956) and 0.01596 m/px this is 15.1-15.2 m | ok |
| 0012 | 0012 / 0012_seg | | bird body length (q6, q1649) | 1.19 / 1.19 | 130 px (seg bbox) and 134 px (crop) give **2.08-2.14 m** | **FIX: 2.11** |
| 0012 | 0012 / 0012_seg | | wingspan (q7, q1650) | 2.234 / 2.284 | 256 px (seg max y-extent) and 259 px (crop) give **4.09-4.13 m** | **FIX: 4.11** |
| 0076/0077 | 0076 | black 1 m/s | white speed at 1 s (q67) | 1.30 | body ratio 1.305 and head ratio 1.302 (window 1.29) | ok |
| | 0076 | | distance at 1 s / 2 s (q68, q69) | 0.757 / 0.94 | body 0.758 / 0.93; head 0.758 / 0.925 | ok |
| | 0077 | | white speed at 1 s (q70) | 1.30 | window ratios 1.28-1.29 | ok |
| | 0077 | | distance at 1 s / 2 s (q71, q72) | 2.34 / 4.58 | body centroid 2.38-2.42 / 4.59-4.60; head 2.45 / 4.67 | ok (<5%) |
| 0130 | 0130 | car 11.155 m/s | scale | 0.088555 m/px | car template 5.248 px/frame gives 0.088564 m/px | ok |
| | | | car length / width (q301, q302) | 6.385 / 2.116 | 72 px (fork tips to counterweight) / 23-24 px | ok |
| | | | plane length / span (q303, q304) | 37.59 / 34.28 | ~416-424 / ~386 px | ok |
| | | | helicopter length / span (q305, q306) | 37.57 / 29.66 | probe tip y~175 to fin y~600; rotor tips x~1285-1620 | ok |
| | | | plane speed at 1 s (q307) | 11.155 | nose template 5.2464 px/frame gives 11.151 m/s | ok |
| 0208 | 0208 | typewriter a = 9.8 | scale | 1.404e-3 m/px | bbox top/bottom second differences ~12 px/frame^2 give 1.41e-3 m/px | ok |
| | | | table length (q554) | 2.56 | far corners x 272..1795 (1523 px); table-edge vanishing point at y = 539 (level camera); contact row 1027, so depth ratio 1.196 and length 2.56 | ok |
| | | | typewriter length / height (q555, q556) | 0.411 / 0.18 | in-air width 292 px gives 0.41; carriage-to-base ~123 px gives 0.17 | ok |
| | | | letter length (q557) | 0.29 | 193 px x 1.054 depth gives 0.286 | ok |
| | | | speeds at 0.125 / 0.25 / 0.333 s (q558-560) | 1.12 / 2.35 / 3.16 | free fall with release at about frame 0; g*t would be 1.23 / 2.45 / 3.27 (<10%) | ok |
| 0308 | 0278 (top view) | whale 1.67 m/s | length / width (q980, q981) | 18.9 / 9.1 | head template 5.80 px/frame gives 0.0120 m/px; x-extent max 1571-1596 px gives 18.9-19.2; y-extent 646-786 px gives 7.8-9.4 | ok |
| | 0279 (side view) | | length / height (q983, q984) | 20.2 / 5.1 | head template 7.995 px/frame gives 0.00871 m/px; x-extent max 2319 px gives 20.2; dorsal-to-fin-tip 536-597 px gives 4.7-5.2 | ok |
| | both | | displacement 0.5-1 s (q982, q985) | 0.835 | constant speed (fits linear, resid <0.6 px) | ok |
| 0293 | 0292 / 0293 | column 0.96 m/s | diameter (q1020, q1023) | 0.49 / 0.492 | 88-89 px x 0.0056 = 0.49-0.50 | ok |
| | | | height (q1021, q1024) | 0.99 / 1.0 | 176 px (hub bottom ~484 to column bottom ~660) gives 0.99 | ok |
| | | | displacement (q1022, q1025) | 0.48 | 85.1-85.6 px over frames 12-24 gives 0.48 | ok |
| internet_0026 | _segmented | sofa 90 cm (sofa removed in this clip) | baby sitting height (q2984), baby-man distance (q2985), truck length / height (q2986, q2987), truck speed at 0.5 s / average (q2988, q2989) | 64 / 2.35 / 68 / 56 / 74 / 71 | ratios only (no sofa visible): one scale of ~0.333 cm/px fits all six (baby 192 px; centroids 701 px apart; truck 203-205 x 166 px; v(0.5 s) 7.1-7.5 px/frame = 71-75 cm/s; mean 6.6-6.7 px/frame = 66-67 cm/s) | no fix (see note) |

Whale family: the length is 18.9 m in 0278 and 20.2 m in 0279, which is 7% apart for the same whale. Both values are within 3.5% of 19.55, which is under the 15% threshold, so neither changes. In 0279 (side, perspective view) the head template tracks the near flank, so 20.2 m may be slightly low. Neither view clearly wins.

internet_0026_segmented: at the uniform ~0.333 cm/px scale the crouching man's head (123 px) would be about 41 cm, and he would be 146 cm tall while crouching. That suggests the sofa (background) scale is being applied to foreground people and the truck. I can't check this without the sofa view, and the labels for internet clips may themselves use one 2D scale, so I propose no change.

## Deep check: simulation_0012 / 0012_segmented bird rows

Speed and time:
- Both clips have 61 container frames, with dropped frames at the 18->19 and 42->43 steps (the step doubles to 37-38 px against ~19 px on each side). That makes 62 Blender frame intervals.
- Route A, the segmented clip with bbox left-edge track: 684 -> 1655 px, which is 971 px / 62 = **15.66 px/frame**.
- Route B, the original clip with a body template track: 971.1 px / 62 = **15.663 px/frame**.
- The velocity profile is a parabola: 6.5 px/frame at the ends and a peak of 20.8 px/frame at Blender frame 30, with roots at -6 and 66 (Bezier ease).
- Scale for the 6 m/s prior:
  - Clip mean: 0.01596 m/px. This is the agent's choice, and the house answer of 15.4 m uses it.
  - Keyframe average (2/3 of the peak): 0.0180 m/px.
  - Peak: 0.0120 m/px.

Pixel extents:
- Body (beak to tail-fan tip): 124-140 px, median 130, from the segmented bbox x-extent in every frame. The crop of frame 17 of the original gives 134 px.
- Wingspan: the maximum y-extent over the flap cycle is 254-256 px in the segmented clip, at frames 0, 17-18, 33 and 49-50. The crop of frame 17 gives 259 px.

Results:

| row | current | Route A | Route B | proposed |
|---|---|---|---|---|
| q6 / q1649 (body length) | 1.19 | 130 x 0.01596 = 2.075 | 134 x 0.01596 = 2.14 | **2.11** |
| q7 / q1650 (wingspan) | 2.234 / 2.284 | 256 x 0.01596 = 4.09 | 259 x 0.01596 = 4.13 | **4.11** |

Why the current answers are wrong:
- At this clip's scale, 1.19 m is only about 75 px. That is roughly the dark torso without the light-grey tail fan; the full beak-to-tail-tip extent is 130-134 px.
- 2.23-2.28 m is about 140 px. That is the y-extent at a mid-flap frame with the wings raised (frames 8-9, 24-25 and 41-42 show 124-146 px), not the spread wingspan of 256-259 px.
- For 1.19 m to be the full 130 px body, the 6 m/s prior would need a bird speed of 27 px/frame. That is faster than the bird's peak of 20.8 px/frame, so no reading of the prior supports it.
- The current rows also contradict the same clip's house answer (15.4 m). That answer uses the same 0.016 m/px scale, which makes the bird 2.1 m. The ratio of house to body length is 7.3 in pixels but 12.9 in the current answers.

Risk: if "6 m/s" meant the peak speed, the truth would be about 1.58 / 3.1 m. The fix would then be 33% high, against 25% low for the current values. Under the clip-mean reading (2.11) or the keyframe-average reading (2.38) the fix is far better. I kept the agent's clip-mean reading so the bird rows stay consistent with the unchanged house rows.

## Fixes

| qid | clip | current | new |
|---|---|---|---|
| 6 | simulation_0012 | 1.19 | 2.11 |
| 7 | simulation_0012 | 2.2339 | 4.11 |
| 1649 | simulation_0012_segmented | 1.19 | 2.11 |
| 1650 | simulation_0012_segmented | 2.2835 | 4.11 |
