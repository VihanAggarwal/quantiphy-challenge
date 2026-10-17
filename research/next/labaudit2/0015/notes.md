# Lab audit round 2: family 0015 (captured_0015 / 0015s / 0015x; one event, one label set)

Input: `../inputs/0015.json` has 15 scored D2 rows (5 questions x 3 renders). Only the frames and the test `prior`/`depth_info` were used.
There is no depth_info and the only prior is g = 9.8. No labels were used. Round 1 is in `../../labaudit/0015/notes.md` and made no fixes.

Scripts are in `scripts/`:
- `common.py`: video loader, capture clock, f = 711, principal point (640, 360).
- `tops.py`: toy top track. Output in `tops_x.txt`.
- `gfit.py`: isolated toy blob in flight. Output in `gtrack_x.json`.
- `ballistic.py` (with `lsq.py`): 3D ballistic fits. Output in `ballistic_out.txt`.
- `toyseg.py`: toy segmentation during the catch.
- `motion.py`: label emulation plus Monte Carlo. Output in `motion_out.txt`.
- `static.py`, `vlines.py`, plus the crop and zoom helpers.

Crops are in `img/`. Frames are read in memory and never dumped.

**Result: no fixes.** No motion row meets the bar (two routes within 12% and the current value at least 25% away). No static row is 12% or more from a two-route value.

## Clock (checked again, from this clip only)
The toy-top track on the x render (`tops_x.txt`) shows two double steps:
- **Before video 12:** the step 11->12 is 49 px, against 30 for 12->13 while the hand is still accelerating the toy.
- **Before video 60:** the step 59->60 is 54 px. In free fall the steps are 10, 15 and 20 for 56->59 (5.0 px/fr^2), so two capture steps would be about 25 + 29 = 54.

So capture = video + 1 for video 12-35, + 2 for 36-59 and + 3 for 60 onward (the drop before 36 follows the 24-frame period).
- **t = 0.6 s** is capture 15 = video 14. The forward difference is video 14->15.
- **t = 2.6 s** is capture 65 = video 62. The forward difference is video 62->63.

## Toy range (depth) from gravity (`ballistic.py`)
I fitted a 3D ballistic trajectory on the capture clock with g = 9.8 along the camera's down direction, pitch -3/0/+3 deg. The vertical vanishing point from the TV edges gives about +1 deg, but it is weak.

| feature (frames) | toss 1, video 17-22 | toss 2, video 53-58 |
|---|---|---|
| top edge, depth (v_z = 0) | 2.10 | 2.10 |
| top edge, long run (15-22 / 50-59) | 2.21 | 2.16 |
| bbox centre | 2.16 | 2.20 |
| centroid | 2.39 | 2.22 |
| bottom edge | 2.23 | 2.31 |

- Pixel acceleration is 5.0-5.3 px/fr^2. I take toy depth Z = 2.20 (2.10-2.30); the range is about 7% larger because the toy is off-axis.
- Cross-check: the person is 509 px tall in every frame (`static.py`).
  - With the same woman's 162-167 cm from 0018 (round 1), her body is at Z 2.26-2.33.
  - The toy is held in front of her, so 2.1-2.25 fits.

## Motion rows (cm/s; forward difference of clicked centres on the 25 fps clock; `motion.py`)

| qids (o/s/x) | question | current | label-style | physical | verdict |
|---|---|---|---|---|---|
| 2267 / 2272 / 2277 | v toy at 0.6 s | 150 / 170 / 190 | Visible-centre clicks (450,232.5)->(447,214.5): 135-148 for Z 2.1-2.3. Top edge or top+46 (bottom hidden by the hand in video 14): 170-186. MC median with 2 px clicks and 0-3 cm ToF: 143-165 (visible) and 180-200 (top). | Scale-free free flight: g x (apex 19.9 - 15.5)/25 = 172 forward difference; about 190 instantaneous at capture 15 | **Keep.** All three currents lie inside the 135-200 label envelope and within 12% of the 160-175 middle. |
| 2270 / 2275 / 2280 | v toy at 2.6 s | 130 / 172.4 / 146.6 | Video 62->63 step is 16.5-20.5 px vertical and 1-4 px left. Seg centroid/bbox (o): 140; seg (x): 134; manual (x): 135; manual (o): 158; top/bottom mid (o): 160 (all at Z 2.2; ±4.5% for Z 2.1-2.3). MC medians: 137-172 (ToF 0-2 cm); +7-10 if the catch pulls the toy back 2 cm/frame. | The catch is abrupt. Step 61->62 is 30-34 px, about 240-290 cm/s backward; step 62->63 is about 18 px. The central difference at capture 65 is about 160-210. | **Keep.** s (172.4) is 9-30% above the deterministic forward values (central about 141, so +22%). It is inside the MC band and close to the central/physical value. o (130) and x (146.6) are within 10%. |

**Why v(2.6) s = 172.4 is not changed.**
- The label-style routes do not pin a value below 138, which is the level needed for a 25% gap: they spread over 127-168.
- The 4 px difference between the o and x click readings of the blurred toy bottom alone moves the value by 20%.
- At this moment the toy is being caught, so the speed halves within one capture frame. Any one-frame shift in the labeller's frame, or a central difference, gives 160-290.
- A ToF sigma of 2-3 cm, or a backward pull of the toy during the catch, raises the expected label to 155-170.
- So I cannot say concretely why 172.4 would be wrong. Harmonising all three renders to about 145 would only be a small +EV nudge, below this round's bar.

**Why v(0.6) is not changed.** The release is at video 14-15:
- The top steps 24 / 23 / 17 / 11 show the hand still pushing during 13->15.
- The bottom of the toy is hidden by the hand in video 14, so the clicked centre is uncertain by 5 px. The step is 17-23 px.

The current 150 / 170 / 190 spread covers this range. None of them is 25% from any route.

## Static rows (re-checked)

| qids (o/s/x) | question | current | measurement | verdict |
|---|---|---|---|---|
| 2266 / 2271 / 2276 | person height | 164 / 160 / 165 | 509 px (top 132-134, shoes 641-642, frames 0-70). Routes: body Z 2.25-2.40 (toy depth 2.2 plus 0.05-0.2 m) gives 161-172; identity transfer 0018 gives 162-167 (round 1); floor route 162-176 (round 1, pitch-sensitive). | Keep (all within 5% of 164-166) |
| 2268 / 2273 / 2278 | toy height | 28 / 32.09 / 28.72 | Upright in-flight extent 91-93 px (toss 1) and 97-98 px (toss 2). Times Z/711 with gravity Z 2.10-2.21, that gives 28.3-30.2. The same prop in 0062 (stated range) gives 29-31 at mid-thickness and 31-38 head-to-feet (0062 current 32.07). | Keep. 32.09 is +7-11% over the gravity route and inside the 0062 route; 28/28.72 are inside the gravity route. |
| 2269 / 2274 / 2279 | shoulder breadth | 34.5 / 36.75 / 32.02 | Shoulder corners and sleeve edges span 95-101 px. At body Z 2.29 that is 30.6-32.5 projected. The body is turned about 30 deg to camera right, so the 3D clicked breadth is 33-38. | Keep (all within 8% of 34.5; no two routes put any value 12% or more away) |

## Result
15 rows checked, no fixes. No row here is an S3 row. Both velocity rows depend on the exact click and frame at a release or catch.
The current values sit inside the label-emulation envelopes. The static rows agree with gravity-scaled and transferred sizes to within 11%.
