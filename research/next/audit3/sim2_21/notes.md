# Audit sim2_21: simulation_0153(+seg), 0178(+seg), 0198, 0199

All 38 rows are scored. All provenance is "agent measurement or pipeline". No stated-fact rows.
Agent notes exist only for the non-segmented clips. The segmented twins carry identical answers.
Scripts used: /tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/{car.py,car_tm.py,el.py,el_tm.py,drop.py}.
Crops I looked at: img/.

## Family consistency (step 1)
- 0153 / 0153_segmented: same footage, so the answers are identical by construction. Static camera; the cart moves in +x at constant depth.
- 0178 / 0178_segmented: same footage, and the shared rows have identical answers. 1892 (average speed of the small elephant, 2.02)
  agrees with 425 (speed at 1 s, 2.006) because the root motion is linear.
- 0198 / 0199: same scene and same camera with different lighting. The droplet bbox positions per sim frame match within 1 px, so the
  scripted motion is the same. 0198 has a duplicated video frame (v7=v6) and a skipped sim frame (sim 8); its agent handled this.
  Sizes across the two clips agree within 0.8-4% (neck 0.02372 vs 0.0247 is the largest gap), and speeds within 0.7%.
  No clip is off in scale.

## Notes review (step 2)
- 0153: careful work: cubic (Blender Bezier smoothstep, v=0 at frames 0 and 59) and depth-corrected length. The only open issue is the
  acceleration convention (x''(n-1) for the backward-of-backward difference), which the agent flagged medium. 1.5 s is decelerating and is
  answered as a positive magnitude. Not changed, because no measurement error was found.
- 0178: consistent, same depth (feet y~692 for both).
- 0198/0199: the "skynova" text reads vertically. "Horizontal length" = image-x extent (~38 px), the literal reading, which both agents chose
  independently. The swap is an interpretation risk, not a measurement error, so it was not changed. For the neck, the agents used the
  outer extent including threads (280-295 px; core ~220-250 px). This is also an interpretation choice.

## Quick checks (step 3)
| qid | clip | quantity | current | quick-check value (route) | diff |
|---|---|---|---|---|---|
| 348/1853 | 0153 | length incl. flap | 1.914 | mask extent 542-550 px (fr 30-41) x 0.369/107.5 px = 1.86-1.89 (no depth corr.); tire D 108 px from hub (918,895) to edge 972 and bottom 949 | 1-3% |
| 349/1854 | 0153 | v(1 s) | 3.937 | front-wheel template track (seg), cubic rms 0.34 px, v=0 at fr 0.01/58.93: vbd(24)=47.56 px/f -> 3.92 | 0.5% |
| 351/1856 | 0153 | v(1.5 s) | 3.938 | vbd(36)=47.52 px/f -> 3.92 | 0.5% |
| 350/1855 | 0153 | a(1 s) | 1.478 | x''(23)=0.74 px/f^2 -> 1.46 | 1% |
| 352/1857 | 0153 | a(1.5 s) | 1.248 | x''(35)=-0.632 -> 1.25 (magnitude) | 0.2% |
| 425 | 0178 | small v(1 s) | 2.006 | torso template, small/big rate 6.167/6.986 -> 2.04; local diffs fr 21-27 -> 2.09 | 2-4% |
| 1892 | 0178s | small avg speed | 2.02 | 6.167/6.986 x 2.313 = 2.04; bbox centroid 6.125/7.056 -> 2.01 | 0.5-1% |
| 426/1893 | 0178 | big height | 3.123 | seg bbox ~226 px (top 461-473, feet 691-695) x 0.01367 = 3.09 | 1% |
| 427/1894 | 0178 | small height | 2.11 | ~151 px (top 536-545, feet 691-694) -> 2.06 | 2.4% |
| 428/1895 | 0178 | big displacement | 5.685 | 2.313 x 59/24 = 5.686 | 0% |
| 429/1896 | 0178 | small displacement | 4.952 | 362.7/411.3 x 5.686 = 5.01 (torso); 361.4/416.3 x 5.686 = 4.94 (centroid) | 0.3-1.2% |
| 514 / 505 | 0199 / 0198 | droplet height | 0.00765 / 0.00771 | bbox 89-90 px, a_px = 31.8 px/f^2 -> 8.47e-5 m/px -> 0.0076 | 0.5-1% |
| 515 / 506 | | droplet width | 0.00485 / 0.00491 | 52-57 px (median ~55) -> 0.0047 | 3-4% |
| 516 / 507 | | neck diameter | 0.0247 / 0.02372 | thread outer 1775-2068 = 293 px -> 0.0248 (core ~220-250 px -> 0.019-0.021) | 0.4% / 4.4% vs threads |
| 517 / 508 | | body diameter | 0.0366 / 0.03601 | 1705-2135 = 430 px -> 0.0364 | 0.5-1% |
| 518 / 509 | | text horizontal | 0.00332 / 0.00322 | x extent 37-39 px -> 0.0031-0.0033 | 0-6% |
| 519 / 510 | | text vertical | 0.0279 / 0.02762 | y extent 327 px -> 0.0277 | 0.3-0.7% |
| 521 / 512 | | v(0.05 s) | 0.411 / 0.408 | backward diff sim 2->3 = 80-81 px -> 0.41 | <1% |
| 522 / 513 | | v(0.1 s) | 0.896 / 0.893 | sim 5->6 = 176 px -> 0.894 | <0.5% |
| 520 / 511 | | v(0.2 s) | 1.866 / 1.863 | extrapolated step 12 = 368 px -> 1.87 | <1% |

No row differs by >= 15% from its quick check, so no in-depth re-measurement was triggered.

## Fixes
None. Every current answer is within ~6% of an independent quick check, and the families are mutually consistent.

## Open risks (not fixable without labels)
- 509/510 and 518/519: if "horizontal length of the text" means reading length, the two values would swap.
- 507/516 neck: thread-outer (~0.0248) vs core (~0.020) interpretation.
- 350/352 and 1855/1857: the acceleration time convention (x''(23) vs x''(24), Blender 1-index), and the sign at 1.5 s (deceleration answered as a positive magnitude).
