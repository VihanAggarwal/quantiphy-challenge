# sim3audit simulation_0209 (family: 0202, 0205, 0206, 0209; desk, typewriter, gun and letter)

## Family structure (verified on frames)
- All four A3 clips share one fixed camera. The depth_info for gun and desk corners is identical, and the desk-corner pixels are identical
  (N 698.9,877.2 / R 1979.8,640.3 / L 472.5,685.5 / F 1599.2,525.3).
  - There are two takes: the glass drop (0202 complex background, 0205 simple background), where the typewriter sits still on the desk,
    and the typewriter drop (0206 complex, 0209 simple).
- The A2 clips 0203/0204 (glass take) and 0207/0208 (typewriter take) are the same scene seen by a level, frontal camera
  (table side-edge VP at (1061, 540) = image centre). They are not in this item, but they show the whole letter under the gun.
- Camera model for A3 (a3cam.py): from the desk VPs, f = 2637 px, pitch 13.4 deg, roll 0.
  - The plane is 1.257-1.272 m below the camera, from the near and far-right corner ranges (Euclidean).
  - On-plane desk top is 2.41-2.44 x 1.03 m with a 90 deg corner. The range chord N-R is 2.44-2.46.
  - The 0206 agent's camera (f 2724, pitch 15, plane 1.36) is the outlier of the family.

## Tabulation (current answers)
| quantity | 0202 | 0205 | 0206 | 0209 | A2 agents (0203/0204/0207/0208) |
|---|---|---|---|---|---|
| table length | 2.44 | 2.47 | 2.36 | 2.44 | 2.34/2.29/2.42/2.56 |
| table width | 1.035 | 1.08 | 0.94 | 1.06 | - |
| typewriter length | 0.43 | 0.39 | 0.39 | 0.38 | 0.395/0.412/0.388/0.411 |
| typewriter width | **0.41** | 0.32 | 0.32 | 0.38 | - |
| typewriter height | 0.19 | 0.188 | 0.19 | 0.18 | 0.20/0.224/0.176/0.18 |
| paper width | 0.21 | - | 0.20 | - | 0.205/-/0.27/- |
| letter under gun, length | - | - | 0.24 | **0.14** | 0.276/0.259/0.27/0.29 |
| speeds (0.125/0.25/0.333 s) | 1.042/2.268/3.084 (glass) | 1.04/2.27/3.08 (glass) | 1.10/2.32/3.14 (typewriter) | 1.07/2.29/3.10 (typewriter) | consistent |

## Fix 1: qid 1587 (0209, letter under the gun, length): 0.14 -> 0.27
- **Why 0.14 is wrong.** In the A3 view the gun covers most of the letter.
  - The 0209 agent measured the visible side along the desk depth (0.144 m). It took the side along the desk length (0.10 m) as complete,
    and so called 0.144 the long side.
  - I reproduced its geometry: L-N side = 0.142 m along the desk depth, and 0.108 m visible along the desk length.
  - But the 0.108 m ends where the gun's frame starts to cover the paper; it is not a corner.
  - Contrast-enhanced crops show no paper past the grip. The grip and frame are 3-4 cm tall and, at 13 deg elevation, they hide the table behind them.
    Projected outlines for lengths 0.20-0.29 (a3_project.py, frames/a3_letter_hyp.png) all put the far corners under the gun.
- **Route 1, A2 frontal view** (a2_ratio2.py; 0208 and 0204 frame 0, simple background).
  - The letter is fully visible and extends past both the barrel tip and the grip end.
  - Letter x-extent / table silhouette width at the same image row = **0.1118 +- 0.0002** over 17 rows, identical in both clips.
    Silhouette rms 0.2-0.6 px, VP (1061, 540).
  - Times the family table length 2.44-2.47 (A3, anchored on the corner ranges in depth_info) gives **0.273-0.276 m**.
- **Route 2, independent of the table length.** A2 glass free fall in 0204, centroid of full-silhouette frames: a = 12.885 px/frame^2, rms 0.17 px.
  - This gives camera height h = g*(y_c-540)/(a*576) = 0.623-0.634 m (glass contact row 1012-1020).
  - Letter = 192.1 px * h / (1000-540) = **0.260-0.265 m**.
- The two routes agree within about 4.5%. The other A2 agents' medians are about 0.27.
- The visible left edge of the letter sits at the same place along the desk in both views (u about 1.46 m).
- The long side runs along the desk length, i.e. the same axis as the table "length". Proposed **0.27**.
- Note: 0206 qid 1583 (0.24) is 11% below this value, under the 15% bar, so it is left unchanged. Moving it to 0.27 would be a small, safe improvement.

## Fix 2: qid 1560 (0202, typewriter width): 0.41 -> 0.33
- **Why 0.41 is wrong.** The 0202 agent said the typewriter base was rotated 18 deg to the desk.
  - It then hedged length and width toward a world AABB of a rotated box (0.455 x 0.43 -> answered 0.43 x 0.41).
  - Its corner pixel FL (1003,757) is not the base corner. The real front-left corner is at (936-939, 759-761).
- **Re-measured** (tw_edges2.py), base-plate bottom outline in 0205 with a band-limited gradient fit (rms 0.17 / 0.53 px):
  front edge yaw -0.3 +- 0.4 deg and left edge 89.6 deg relative to the desk axes. 0202 itself gives about 3.7 / 89 deg (noisier background).
- So the typewriter in the glass take is desk-aligned, and its AABB equals its local box under either convention.
- Footprint (tw_footprint.py): 0.37-0.38 m along the desk length x **0.32-0.34 m** in depth, 90 deg corner.
- Family route: 0205 agent 0.320 (same footage), 0206 agent 0.32, 0209 agent's rest-pose depth 0.32-0.35. Proposed **0.33**.
- Caveat: this assumes width = front-to-back (Y), like the table. The whole family uses length = side-to-side for the typewriter.
  If the model's axes were swapped, the truth would be about 0.38-0.40.
- 0202 typewriter length 0.43 (same cause, local is about 0.38-0.40) is about 12% high, under the bar, so it is left unchanged.

## Checked, no change
- **Typewriter in the typewriter take (0206/0209).**
  - At frame 0 it is yawed about -39 deg to the desk axes (front edge almost parallel to the A3 image plane), whereas in the A2 typewriter take it faces the desk.
  - Under local dimensions, width is about 0.33 and length 0.37-0.40. Under a world AABB at frame 0, both would be about 0.49.
  - The convention cannot be settled without labels, so 0206 (0.39/0.32) and 0209 (0.38/0.38) are kept.
  - 0209 width 0.38 is about 15% above local, a borderline case.
- **Table width 0206 (0.94).** The model gives 1.03 for the top surface, plus a 2 cm lip per side, so 1.05-1.07. 0.94 is 11-13% low, under the bar,
  and comes from the 0206 agent's f/pitch/plane outlier.
- Table lengths, typewriter heights and paper widths are consistent.
- Speeds: the glass falls from rest (g(t - dt/2) = 1.021/2.246/3.062; answers +2%), and the typewriter release offset is about 0.1-0.25 frame.
  All within 3% across clips.
- **Gun-ruler route for the letter** (gun_route.py) gave 0.22-0.25. It is unreliable: a barrel-tip height error of 1 cm moves the projected u by about 2 cm
  at 13 deg elevation, and it implies a gun orientation that contradicts the A2 view. Not used.
