# Audit internet_12 (internet_0014, 0017, 0020, 0037, 0038, 0039)

Each clip is its own family (no twins/segments), so the cross-clip table check (step 1) is
trivial: no shared objects across clips. Every scored row (30) got a quick independent check on
frames; rows with a >=15% quick-check gap were re-measured with a second route.

**Result: no fixes proposed.** No row met "two independent routes agree within 8% AND the current
answer is >=15% off". The only gaps >=15% come from ambiguities that a second route does not settle
(2D vs 3D scale for the tray and sink in 0020; which body point is tracked in 0037 3036).

## Scales re-verified
- 0014: center circle diameter ~233 px in frame 0, so r = 117 px = 9.15 m (12.79 px/m). Camera static.
- 0017: flat card in frame 18 (hand lifted). Right short edge corner to corner is ~203 px straight; adding the
  rounded corners gives ~213-218 px, which matches the agent's 216.4 px = 5.4 cm. Keyboard check: ~28.5 x 13.3 cm
  (A1314 spec 27.9 x 13.0), so the flat card is the physically consistent scale.
- 0020: picked bottle cap top y~1187-1190, base y~1805-1817 in frame 0, so ~620 px = 11.7 cm.
  ECC drift is 24 px over the clip, compensated in the motion masks.
- 0037: swimmer head-to-toe read in frames 0/30/60/90/125/150 is 596/691/700/582/700/618 px (median ~655).
  The agent used 670 px. The 2% difference is within noise.
- 0038: mouse 68 x 134 px in frame 14. Laptop 426 x ~293 px. Spacebar 107 px (frame 0).
- 0039: swimmer 975/1032/1050/1056 px in frames 0/25/58/71 (the agent used 1030). Red-float rope separation at the
  swimmer's rows is 1364-1387 px over frames 0-71. The separation near the bottom of the frame grows ~4% (slight tilt
  change), which is negligible at the swimmer's rows.

## Rows checked
| qid | clip | quantity | current | quick-check route | quick value | gap | verdict |
|---|---|---|---|---|---|---|---|
| 2070 | 0014 | initial player distance m | 4.4 | zoom f0: A(1463,530) B(1407,520) 56.9 px | 4.45 | 1% | ok |
| 2071 | 0014 | closest player to goal m | 10.39 | A to goal line x~1595: 132 px | 10.3 | 1% | ok |
| 2072 | 0014 | ball speed @7 s | 2.6 | NN-gated bright-blob ball track, linear fits 195-225 / 200-220 / 205-215 | 2.53-2.57 | 2% | ok |
| 2073 | 0014 | player-with-ball avg v 8-9 s | 2.85 | zoom f240 (1430,630) to f270 (1403,653): 35.5 px | 2.77 | 3% | ok |
| 2074 | 0014 | distance at 9 s | 7.56 | A(1403,653) B(1458,575) 95.4 px | 7.46 | 1% | ok |
| 2084 | 0017 | tin diameter cm | 9.8 | silhouette 400-418 px (rim smaller, agent 9.3-9.7) | 10.0-10.4 | 4-6% | ok |
| 2085 | 0017 | keyboard length cm | 28.9 | corner picks 1122-1134 px (rounded corners, slight under-read) | 28.0-28.3 | 2-3% | ok |
| 2086 | 0017 | keyboard width cm | 13.5 | corner picks 507-519 px | 12.7-13.0 | 4-6% | ok |
| 2087 | 0017 | pen length cm | 14.4 | end to end ~570 px | 14.2 | 1% | ok |
| 2088 | 0017 | middle fingertip speed @0.4 s | 49 | fingertip picks f7..f10: 102, 88, 63 px/frame; at 8.8 ~88-95 px/frame | 48-52 | <5% | ok |
| 2099 | 0020 | sink height cm | 18.5 | sink base is out of frame. Bracket: 2D 18.7-19.7, 3D 15-16 (agent). No independent second route | - | - | keep (low conf) |
| 2100 | 0020 | tray width cm | 32 | front edge x 1250-3000 (f18) ~1750-1766 px. 2D: 33.0-33.3. Ground-plane row factor (2040-375)/(1805-375)=1.164 gives 3D 28.4-28.6 | 28.5 / 33.2 | the two routes differ by 17% | keep (hedge) |
| 2101 | 0020 | pump bottle height cm | 17.0 | ~900-910 px | 17.0-17.2 | 1% | ok |
| 2102 | 0020 | bottle avg velocity cm/s | 44 | ECC-aligned diff vs f18. Bottle low point f0 (2667,1817) to f16 (2600,350): 1469 px / 0.64 s | 43.3 | 2% | ok |
| 2103 | 0020 | bottle velocity @0.5 s | 70 | aligned diff mask f12 to f13: low point 152 px, left base corner 155 px | 72-73 | 4% | ok (the raw-frame eyeball of 188 px was a motion-blur artefact) |
| 3036 | 0037 | speed 0-2.07 s | 0.42 | hips/skin centroid 351 px; face-patch (head) track 436 px; feet 390; bbox 382 | 0.41 / 0.51 / 0.46 / 0.45 | head +21% | keep: breaststroke phase, routes disagree |
| 3037 | 0037 | speed 2.07-5.20 s | 0.44 | hips 565 px; head 539; feet 522; bbox 658 | 0.44 / 0.42 / 0.41 / 0.51 | <=5% (bbox +16%) | ok |
| 3038 | 0037 | speed 0-5.20 s | 0.43 | hips 916 px; head 975 | 0.43 / 0.456 | 0-6% | ok |
| 3039 | 0037 | accel 0-5.20 s | 0.008 | head route decelerates (-0.03); hip route +0.008 | sign ambiguous | - | keep (unverifiable) |
| 3040 | 0037 | pool width m | 4.57 | water from y~178 (top coping) to y~2065-2080 (bottom water line with glints), ~1890 px | 4.59 | <1% | ok |
| 3041 | 0038 | mouse length cm | 11.2 | 134 / 68 px x 5.71 | 11.25 | <1% | ok |
| 3042 | 0038 | MacBook length cm | 35.5 | 426 px | 35.4 | <1% | ok |
| 3043 | 0038 | MacBook width cm | 24.4 | ~290-296 px | 24.1-24.6 | 1% | ok |
| 3044 | 0038 | spacebar cm | 9.0 | f0 x 585.7-692.7 = 107 px | 8.9 | 1% | ok |
| 3045 | 0038 | right hand speed 0-0.54 s | 0.45 | hand centroid ~(990,510) to ~(713,436), ~290 px / 14 frames @26 | 0.45 | <2% | ok |
| 3046 | 0039 | speed 0-1 s | 0.741 | cap y 2081 to 1612: 469 px | 0.765 | 3% | ok |
| 3047 | 0039 | speed 1-2.33 s | 0.773 | cap 1612 to ~970 at frame 58.25: 642 px / 1.33 s | 0.788 | 2% | ok |
| 3048 | 0039 | speed 0-2.33 s | 0.759 | 1111 px / 2.33 s | 0.778 | 2.5% | ok |
| 3049 | 0039 | accel 0-2.33 s | 0.02 | signal is below the tracking noise | - | - | keep (unverifiable) |
| 3050 | 0039 | lane rope distance m | 2.25 | red-float medians: 1364-1387 px at the swimmer's rows | 2.23-2.25 | <1% | ok |

## Notes on ambiguous rows (no change)
- **3036:** the woman swims breaststroke. Her head lunges relative to her hips, so the 0-2.07 s displacement depends
  on the body point tracked: head 436 px vs hips 351 px, a 20% spread. The current 0.42 follows the hips (skin centroid).
  The midpoint of all routes is ~0.46. That would be a hedge, not a two-route fix, so it is left as is.
- **2100 / 2099:** whether ground truth uses the 2D pixel ratio at the bottle's scale or a depth-corrected size is unknown.
  For 2100 the current 32 sits 4% from 2D and 12% from 3D, which is a reasonable hedge.
- **fps:** the dataset fps (30/22/25/24/26/25) was used throughout, matching the agents. The container fps differs for
  0020 (19.6), 0037 (22.5), 0038 (18.5) and 0039 (18.5). This is a shared convention risk, not a row error.

## Fixes
None.
