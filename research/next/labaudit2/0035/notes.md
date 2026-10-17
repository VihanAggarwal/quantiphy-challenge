# Lab audit round 2: family 0035 (captured_0035a/as/ax and captured_0035b/bs/bx), 54 scored rows

I used test inputs only (frames, `prior`, `depth_info`) and no labels. Scripts are in `scripts/`. Crops and overlays are in `frames/`. Tracks are in `tr_a.json`, `tr_b.json` and `xmask_*.json`.

## Setup (re-measured; agrees with round 1)
- a and b are **two takes**, so they have different labels. a, as and ax share labels, and b, bs and bx share labels.
- **Collisions.**
  - In a, the balls collide between video frames 19 and 20 (capture 20/21, about 0.82 s).
  - In b, they collide at about video frame 25 (capture 26, about 1.04 s).
- **Dropped frames.** There is a double pixel step at video 11->12 and 35->36 for both balls in both takes. So capture frames 12 and 37 are missing, and the mapping is: video k<=11 -> capture k; 12..35 -> k+1; >=36 -> k+2. An asked time t corresponds to capture frame t*25. For half frames (0.5, 0.9, 1.3, 1.5 s) I averaged the floor and ceil frames.
- **Tracks** (`track.py`). The foreground is where the original render equals both the x and s renders (the SAM cut-out). The basketball is the orange blob and the soccer ball is a round non-orange blob, linked from anchor frames.
  - The 3-way mask is about 1.5 px eroded relative to the x-render-only mask (`xmask.py`).
  - In camera a (green screen) the x-only mask is the clean SAM boundary. In bx the white soccer ball is lost on white, so I used the 3-way mask there.
- **Floor plane from the stated points** (`stated_plane.py`). Each label is a surface range; the ball centre is at label + R along the ray, and the soccer ball centre is offset by R_bb - R_s.
  - **a:** n = (0.022,-0.790,-0.613), camera height 1.96 m, pitch 37.8 deg. All 4 points lie within 1 cm. Leave-one-out: the soccer ball at 0.6 s is predicted at 2.737 vs 2.758.
  - **b**, with 2.602 = basketball and 2.373 = soccer at 1.4 s: n = (-0.167,-0.826,-0.539), camera height 1.80 m, pitch 32.6 deg.
    - This plane agrees with an independent fit of the size-based ball centres (pitch 34.8 deg, camera height 1.81 m, soccer diameter 17.9 cm, no labels used).
    - The swapped assignment gives pitch 45 deg and camera height 2.19 m, which contradicts the sizes. The basketball's size ratio between 0.9 s and 1.4 s also predicts a 1.4 s surface range of 2.66, which matches 2.602 and not 2.373.
- **Checks of the plane against sizes** (`cmp_routes.py`, `a_soccer_table.py`):
  - In a, the basketball's size-based range and plane range agree within +-3% from video 9 to 48.
  - The soccer ball late in take a (x-only mask) agrees within about 2% per frame.
- **Focal length.** f is not settled: 711 from earlier table-top right angles, 744-776 from the basketball size with these masks, 763 from the 80 deg spec. **Every number below is given for f = 711 and f = 763**, and any fix must hold for both.

## Label-style emulation (`labelstyle.py`)
- The clicked centre per capture frame comes from a local quadratic fit of the track, so click jitter is removed.
- The range comes from one of two routes, each scaled to the stated depth at the nearest stated time:
  - **S**: apparent size, from a local fit of 1/(d*cos^1.5);
  - **P**: the floor plane.
- The 3D point is range x ray. The value is the forward difference over one capture frame (0.04 s).
- In the table, "lat/rad" splits the result into the image-plane part and the camera-radial part. The variants are in `a_soccer_late.py` and `b_bbdisp.py`.

| qids (a/as/ax or b/bs/bx) | question | current | S (f711 / f763) | P (f711 / f763) | verdict |
|---|---|---|---|---|---|
| 2612/2621/2630 | soccer v 0.6 s (a) | 168 | 204 / 193 | 216 / 204 | 13-22% low: keep |
| 2613/2622/2631 | basketball v 0.6 s (a) | 137 | 136 / 130 | 139 / 132 | OK |
| 2614/2623/2632 | soccer disp 0.5-0.6 (a) | 16.6 | 21.0 / 19.8 | 22.9 / 21.6 | 16.6 equals capture frame 13->15. With 12->15 it would be about 24, so the time convention is ambiguous: keep |
| 2615/2624/2633 | basketball disp 0.5-0.6 (a) | 13.8 / 14.2 | 15.2 / 14.4 | 15.3 / 14.5 | OK |
| 2617/2626/2635 | soccer v 1.5 s (a) | 54 | 50-86 (window-dependent) | 64.5 / 61.8 | 13-16% low vs P: keep |
| 2618/2627/2636 | basketball v 1.5 s (a) | 46 | 42 / 39 | 43 / 40 | OK |
| **2619/2628/2637** | **soccer v 1.6 s (a)** | **44** | **x-mask 65-67 / 62-64 (3-way mask 69-79)** | **66.0 / 63.0** | **FIX -> 65** |
| 2620/2629/2638 | basketball v 1.6 s (a) | 36 | 41 / 39 | 41 / 38 | 5-15% low: keep |
| 2639/2648/2657 | soccer v 0.9 s (b) | 98 | 130-138 (biased, see below) | 114 / 108 | 9-14% low vs P: keep |
| 2640/2649/2658 | basketball v 0.9 s (b) | 119 | 147 / 139 | 152 / 143 | 14-22% low: keep |
| 2641/2650/2659 | soccer v 1.4 s (b) | 55 | 53 / 51 | 51 / 49 | OK |
| 2642/2651/2660 | basketball v 1.4 s (b) | 133 | 114 / 108 | 113 / 107 | 17-24% high: keep (below 25%) |
| 2643/2652/2661 | soccer disp 0.4-0.9 (b) | 86 | 79.5 / 76 | 81.5 / 78 | OK |
| 2644/2653/2662 | basketball disp 0.4-0.9 (b) | 91.65 (round-1 fix) | 97-102 (label scale), 85-90 (camera-a K) | 98.6-106 | 91.65 is inside the band: leave |
| 2646/2655/2664 | soccer v 1.3 s (b) | 50 | 54 / 52 | 56 / 54 | OK |
| 2647/2656/2665 | basketball v 1.3 s (b) | 122 | 114 / 108 | 116 / 109 | OK |
| 2616/2625/2634, 2645/2654/2663 | soccer diameter | 17.78 (17.75) | ratio to the basketball: a at 1.6 s 17.5-17.6 (x-mask), b at 1.4 s 18.0-18.2; joint plane+size fit 17.9-18.0 | | OK (within 3%) |

## The fix: soccer ball speed at 1.6 s in take a (qids 2619, 2628, 2637; 44 -> 65)
- **Image motion.** After the collision the soccer ball rolls back toward the far player. From video 31 to 46 the image speed is a steady 4.29 px/frame, so the lateral component at the stated 3.052 m is **46.1 cm/s (f 711) or 42.9 (f 763)**.
- **It is also receding from the camera.** Two routes agree on the radial rate over capture frames 32-48 (`a_soccer_table.py`):
  - **Plane route:** **+49.4 cm/s**. The ball's image climbs the floor toward the far wall, and the plane range at capture 40 is 3.060 (label 3.052).
  - **Size route (x-mask):** **+44.1 cm/s**. The diameter shrinks from 48.1 px at video 28 to 42.9 px at video 46. Frame by frame, the size and plane ranges agree within about 2%, from 2.84 to 3.22 m.
- **Combined speed:** sqrt(lat^2 + rad^2) = 64-68 (f 711) or 61-65 (f 763). The label-style forward difference over capture 40->41 gives P 66.0 / 63.0 and S (x-mask) 65-67 / 62-64. The routes agree within about 5%.
  - The 3-way mask gives 69-79 because its erosion grows as the ball shrinks. That makes it a weaker measurement, but it points the same way.
- **Why 44 is wrong.** 44 equals the image-plane (lateral) speed alone, 43-46 cm/s. It omits the ball's recession of about 45-50 cm/s, which the labels include through the ToF depth at each click.
  - At my value, 44 is 28-35% low. Even the lowest variant (61.5) puts it 28% low.
  - The physical speed is about constant over 1.4-2.0 s: image speed is steady while the range grows slowly. So the current 54 at 1.5 s and 44 at 1.6 s cannot both be right.
- **Proposed value: 65 cm/s for all three renders**, which share one label. ToF noise in the label's radial difference (a few cm per reading) can only push the expected label higher.

Physical (smoothed centre) speeds from `labelstyle.py`, f 711, P/S routes:
- a: soccer 0.6 s 223/211, 1.5 s 65/72, 1.6 s 66/77; basketball 0.6 s 147/145, 1.5 s 45/44, 1.6 s 44/45.
- b: soccer 0.9 s 119 (P), 1.3 s 63/59, 1.4 s 53/57; basketball 0.9 s 163/154, 1.3 s 121/120, 1.4 s 120/121.

These are the same as the label-style values to within the centre-vs-surface and forward-difference effects (≤ 8%).

## Rows examined and not changed
- **Soccer at 0.9 s in b.** The S route runs high because its fit window takes in two kinds of distorted frame:
  - the sliding/airborne frames just after the kick (video 14-18), where the image speed halves from 24 to 12 px/frame and the size is blur-inflated;
  - the occluded frames at the collision (video 24-25).
  
  Restricted to the rolling frames, the size slope is noisy (30-70 cm/s radial), so I use P, with 104 lateral and +52 radial. That puts 98 within 9-14%.
- **Soccer at 0.6 s in a.** The x-mask size of the fast, blurred ball at 0.6 s is about 12% larger than the plane and the label imply. The label agrees with the plane, so blur is the likely cause. The speed is 193-216 against the current 168, below the 25% threshold.
- **Basketball at 1.4 s in b.** It is 17-24% high (f 763 is the upper end). That is below the threshold, and the 1.4 s depth assignment (2.602 = basketball) is supported.
