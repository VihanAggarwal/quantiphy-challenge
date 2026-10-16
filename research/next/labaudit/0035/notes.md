# Lab audit: family 0035 (captured_0035a/as/ax, captured_0035b/bs/bx), 54 scored rows

Scripts are in `scripts/`, and frames, crops and overlays are in `frames/`. The scratch arrays live in the session scratchpad and are not needed to read these notes.

## Setup facts (from frames)
- a and b are **two different takes**, not two cameras of one event. In a, the far player has the soccer ball and the near girl kicks the basketball (bb). In b, the girl kicks the soccer ball and the far player kicks the bb. The stated depths differ between a and b, so each camera family has its own labels.
- All six videos have 49 frames at 24 fps. There are **dropped frames at 11->12 and 35->36**: both balls take a double pixel step there, in both cameras. So the source was 25 fps with one frame dropped per second. Video frame k maps to original frame k / k+1 / k+2 at 25 fps, and I used those true times for every rate.
- I segmented balls in the x renders (a: green background, b: white background) and in the s renders (median-background difference). Ellipse minor axis, circle fits to the mask boundary and visual crops agree to about 1-2 px.
- f = 711 px, principal point (640,360). The size-based range is r = f*D/(d_minor*cos(alpha)), where alpha is the off-axis angle. A sphere's minor axis grows by 1/cos(alpha), which matters at the frame edges in b.
- The 1.4 s depth lines in 0035b are both labelled "soccer". Size and the floor plane both say 2.602 = basketball and 2.373 = soccer. In 0035a at 1.6 s, 3.052 = soccer and 2.412 = bb.

## Camera b floor plane (two independent normals)
- Room corner: the left and right wall-floor baseboards are orthogonal in 3D (both straight to <1 px), and I added the vertical corner edge. This gives n = (-0.115,-0.822,-0.557), a pitch of 34 deg.
- The four stated depth points alone give n = (-0.144,-0.817,-0.558), 1.7 deg from the corner normal. Camera height above the floor from each stated point: 1.774-1.798 m, a spread of only 2.4 cm.

## Row verdicts
| rows | question | current | my measurement | verdict |
|---|---|---|---|---|
| 2616/2625/2634, 2645/2654/2663 | soccer diameter | 17.78 (17.75) | 17.7-18.1 (unblurred, ratio to bb with off-axis correction; a at 1.6 s, b at 1.4 s); 18.1-18.6 (plain d*r/f); blurred frames 19-20 (inflated) | OK |
| 2612/2621/2630 | soccer v 0.6 s (a) | 168 | 203-222 (plane, size) | ~0.8x, not gross: keep |
| 2613/2622/2631 | bb v 0.6 s (a) | 137 | 143-172 | OK |
| 2614/2623/2632 | soccer disp 0.5-0.6 (a) | 16.6 | 16-19 (video frames 12-14) | OK |
| 2615, 2624/2633 | bb disp 0.5-0.6 (a) | 13.8 / 14.23 | 11.6-14.5 | OK (the 3% split between renders is not worth touching) |
| 2617/2626/2635 | soccer v 1.5 s (a) | 54 | 51-54 (size, smoothed), 63-70 (plane) | OK |
| 2618/2627/2636 | bb v 1.5 s (a) | 46 | 40-43 | OK |
| 2619/2628/2637 | soccer v 1.6 s (a) | 44 | 51-54 (size), 65-73 (plane) | borderline (1.2-1.65x) but routes disagree, so no clear gross error: keep |
| 2620/2629/2638 | bb v 1.6 s (a) | 36 | 40-42 | OK |
| 2639/2648/2657 | soccer v 0.9 s (b) | 98 | 118-140 | ~0.75x, not gross: keep |
| 2640/2649/2658 | bb v 0.9 s (b) | 119 | 150-165 | ~0.75x, not gross: keep |
| 2641/2650/2659 | soccer v 1.4 s (b) | 55 | 47-65 | OK |
| 2642/2651/2660 | bb v 1.4 s (b) | 133 | 113-118 | OK (within 15%) |
| 2646/2655/2664 | soccer v 1.3 s (b) | 50 | 53-68 | OK |
| 2647/2656/2665 | bb v 1.3 s (b) | 122 | 114-117 | OK |
| 2643/2652/2661 | soccer disp 0.4-0.9 (b) | 86 | 81 (plane, and size with off-axis correction agree: rest range 2.14 vs 2.24 m) | OK |
| **2644/2653/2662** | **bb disp 0.4-0.9 (b)** | **71** | **~100 (92-109)** | **FIX -> 100** |

## The fix: basketball displacement 0.4->0.9 s in 0035b (all three renders share the label)
- At 0.4 s the bb is still **at rest** next to the far player's feet, near the room corner, at pixel (828.5,280). It does not move until video frame 11, about 0.46 s. At 0.9 s it is at (671,392) with a stated range of 2.7777 m. See `frames/b_bb_disp_overlay.png`.
- Route 1, floor plane: intersect the rest pixel ray with the plane at height R = 11.6 cm. With the stated-only plane the rest range is 3.44 m and the displacement 105.1 cm. With corner orthogonality plus the stated heights it is 105.3 cm, and with the corner plus the vertical edge 109.4 cm. The same plane reproduces the stated 0.9 s bb range (2.788 vs 2.778) and the soccer ranges.
- Route 2, size: the rest diameter is 52.7-55.4 px depending on the mask (crops show about 54 px, unblurred), against 59-62 px at 0.9 s. I applied the off-axis correction (cos alpha = 0.961 at rest) and calibrated each mask type on the two stated bb depths in the same camera. Rest range is 3.35-3.50 m, giving a displacement of 98.6 (hull), 103.8 (orange minor) or 109.4 (s-render minor) cm. A circle fit calibrated on camera a's slow basketball gives the low end, about 92 cm.
- The two routes agree: plane 105 vs size median 104. Current 71 is 30% or more too low.
- Why 71 is wrong: it misses most of the depth component. The ball approaches the camera by 0.5-0.7 m (3.3-3.5 m down to 2.78 m) while moving about 0.78 m laterally. 71 is close to the lateral-only image displacement scaled at the near depth: 193 px * 2.78 m / 711 = 76 cm. Earlier CV estimates of 80-83 cm also used an uncorrected, too-near rest depth.
- I propose **100 cm**. It hedges across 92-109, so it stays within about 9% at either end.

## Not changed (deliberately)
- Speed rows: none is more than 1.5x off with routes that agree, so the leaderboard-tuned values stay.
- Soccer diameter: confirmed to within about 2%.
