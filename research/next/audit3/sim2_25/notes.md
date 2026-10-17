# Audit sim2_25 — notes

Scope: 42 scored rows across 12 clips (0107, 0108, 0114, 0114_segmented, 0118, 0129, 0129_segmented, 0173, 0175, 0179,
0280, 0281). I read every clip's agent notes. I did not open any label, val or other research/submission file.
Scripts are in this folder (grab.py, strip.py, track_grad.py, whale_track.py, virus.py, virus2.py, virus_scale.py, plane.py,
car.py, car2.py, fork.py, air.py, trolley.py, trolley2.py). The small crops I looked at are in img/.

## Family consistency (step 1)

- **Viruses 0107 / 0108.** The right virus's pixel track is identical in both clips: (1306.9, 614.0) at f1 and
  (1623.1, 599.0) at f24, r = 139.8 px. So the camera is the same and the R motion is the same, and the R speed is 1.7393 m/s in both
  clips (stated prior in 0107). The left virus starts at the same depth in both clips (core radius 124.0 vs 124.1 px, minor axis
  122.93 vs 123.14 px). In 0107 L moves left at constant depth. In 0108 L moves up and toward the camera.
- **Plane 0114 / 0114_segmented.** Both clips give the same track (a = 344.3 px/s² in both). The answers are identical and consistent.
- **Forklift 0129 / 0129_segmented.** The answers are identical. The segmented clip gives the forklift bbox directly (it agrees with the agent).
- **Airplane 0173 / 0175.** Same scene and same flight (only the sky differs). Agent scales 0.10427 / 0.10435 m/px.
  The answers agree with each other (47.2/47.9, 44/43, 1.25/1.2).
- **Whale 0280 (side) / 0281 (top).** Head speeds are 12.02 px/frame × 0.005594 m/px and 8.54 px/frame × 0.008182 m/px, giving
  1.61 and 1.68 m/s. These are consistent within 4%, so the scripted motion and the scale are the same. The 0.5–1.0 s
  displacement is 0.806 m (0280) and 0.836 m (0281). The current answers 0.78 / 0.855 are both within 4% of these.

## Quick check of every scored row (step 3)

| qid | clip | quantity | current | quick check (route) | diff | verdict |
|---|---|---|---|---|---|---|
| 218 | 0107 | v left virus @1s | 1.7393 | **2.00** (L 14.16 px/f; s_L from 0108's L prior = 0.005897 m/px) | −13% (vs new) | **FIX** (see below) |
| 219 | 0107 | dist @1s | 6.72 | 7.21 (equal size, L 1.125× deeper) / 6.61 (coplanar) | −7% / +2% | keep |
| 220 | 0107 | dist @2s | 10.35 | 10.88 / 10.14 | −5% / +2% | keep |
| 221 | 0108 | v left virus @1s | 1.7393 | = prior (linear motion) | 0 | keep |
| 222 | 0108 | dist @1s | 5.50 | 5.34 (equal size) | +3% | keep |
| 223 | 0108 | dist @2s | 7.74 | ~7.48 (equal size, agent) | +3.5% | keep |
| 233/1816 | 0114(+seg) | plane width | 8.71 | bbox 166 px × 18/344.3 = 8.68 | 0.3% | keep |
| 234/1817 | 0114(+seg) | plane length | 5.49 | bbox 104–108 px → 5.44–5.65 | <3% | keep |
| 235/1818 | 0114(+seg) | speed @1.5s | 26.56 | 344.3·(1.5−1/48)·0.05228 = 26.6 | 0.2% | keep |
| 246 | 0118 | car displacement | 0.25 | 312.8 px × 7.973e-4 = 0.249 | 0.4% | keep |
| 247 | 0118 | car length | 0.1007 | body ~126–128 px (zoom) → 0.100–0.102 | <2% | keep |
| 248 | 0118 | disc diameter | 0.2064 | ~258 px → 0.206 | <1% | keep |
| 249 | 0118 | book length | 0.176 | sides 0.171 / image AABB 0.180 | ±3% | keep (convention hedge) |
| 250 | 0118 | table length | 0.72 | sides 0.69 / AABB 0.74 | ±4% | keep (convention hedge) |
| 251 | 0118 | table width | 0.59 | sides 0.53 / AABB 0.61 | +11% / −3% | keep (convention cannot be resolved) |
| 298/1846 | 0129(+seg) | ball diameter | 0.375 | g_px 513.6 (f1–30, rms 0.18 px), 19.5–20 px → 0.372–0.381 | <1% | keep |
| 299/1847 | 0129(+seg) | forklift length | 4.68 | seg bbox 247–257 px × 0.01908 = 4.71–4.90 (naive 2D) | −1…−4.5% | keep |
| 300/1848 | 0129(+seg) | forklift height | 3.48 | seg bbox 193–195 px → 3.70 (naive 2D; camera above roof) | −6% | keep |
| 417 | 0173 | airplane length | 47.2 | agent 61.37 px/f; 0175 track 61.6 px/f; 440–459 px → 45.7–47.7 | ≤3% | keep |
| 418 | 0173 | cliff height | 44.0 | rock only 400 px → 41.7; with trees 503 px → 52 | +5% / −15% | keep (convention cannot be resolved) |
| 419 | 0173 | rear wheel diameter | 1.25 | ~11–12 px → 1.15–1.25 | ≤8% | keep |
| 420 | 0175 | airplane length | 47.9 | as 417 | ≤5% | keep |
| 421 | 0175 | cliff height | 43.0 | as 418 | | keep |
| 422 | 0175 | rear wheel diameter | 1.20 | ~11–12 px (zoom) | ≤5% | keep |
| 430 | 0179 | trolley length | 1.12 | 224 px at f0 (bg = f57) × 0.00499–0.00509 → 1.10–1.13 | <2% | keep |
| 431 | 0179 | trolley height | 1.21 | 248 px → 1.24–1.26 (naive, camera above) | −3% | keep |
| 432 | 0179 | gate height | 4.0 | ~903 px × ground-plane depth ratio 0.904 → ~4.1 | −3% | keep |
| 433 | 0179 | tile side | 0.5 | agent: camera model consistent with the prior | — | keep |
| 434 | 0179 | speed @1s | 1.5 | right edge a = 302.3 px/s², vertex t = 0.002 → a·t = 1.507 (bd 1.476) | <2% | keep |
| 435 | 0179 | speed @2s | 3.01 | 3.014 (bd 2.98) | <1% | keep |
| 986 | 0280 | whale speed @1s | 1.66 | head gradient-template 12.02 px/f × 24 × 19.17/3427 = 1.614 | +3% | keep |
| 987 | 0280 | whale height | 5.2 | 850–940 px (tail and flipper pose vary) → 4.75–5.26 | ≤9% | keep |
| 988 | 0280 | displacement 0.5–1 s | 0.78 | 143.9 px → 0.805 | −3% | keep |
| 989 | 0281 | whale speed @1s | 1.679 | 8.54 px/f × 24 × 0.008182 = 1.677 | 0.1% | keep |
| 990 | 0281 | whale width | 8.2 | fin span 920–1130 px (fins flap) → 7.5–9.3 | in range | keep |
| 991 | 0281 | displacement 0.5–1 s | 0.855 | 102.2 px → 0.836 | +2% | keep |

## In-depth: qid 218 (simulation_0107, velocity of the left virus at 1.0 s)

The current value 1.7393 is the right virus's stated speed copied to the left virus. The original agent answered 1.84,
a hedge. The left virus moves at a different pixel speed and sits at a different depth.

- Pixel speeds in 0107: L = 14.16 px/frame (ellipse-fit core centres f2→f24; constant, no easing). R = 13.77 px/frame.
  Template-scale tracking shows that both stay at constant depth. Net scale change after removing off-axis stretch
  (f = 2667 px) is 1.000 (L) and 0.997 (R) by f18.
- **Route 1 (0107's own prior + equal-size assumption):** s_R = 1.7393/(24·13.77) = 0.005263 m/px. The R/L core-size ratio
  is 1.125 (off-axis-corrected circle fit 1.124, mean axes 1.125, agent 1.1256). So s_L = 0.005921 m/px and
  v_L = 14.16·24·0.005921 = **2.012 m/s**.
- **Route 2 (the sibling's prior on the same left virus; no equal-size assumption):** In 0108 the left virus starts at the
  same depth as in 0107 (same radius), and its stated 3D speed is 1.7393 m/s. Template-scale growth in 0108, after
  off-axis correction, is +2.5% by f18. That makes the 3D displacement f1→f18 = 209.0 px-units at the initial depth
  (198.5 in-plane, 65.3 in depth), or 12.29 px/frame. The range is 12.2–12.46 across windows (f18, f24, f36 growth estimates).
  So s_L = 1.7393/(24·12.29) = 0.005897 m/px and v_L(0107) = 14.16·24·0.005897 = **2.004 m/s** (range 1.98–2.02).
- The two routes agree within 0.4%. Route 2 also confirms that the two viruses are the same size, with L about 12% deeper.
  The other model (same depth, smaller left virus) would make 0108's left virus 1.55 m/s, which contradicts its stated 1.7393.
- Proposed value: **2.00**. The current 1.7393 is 13% below it, or 15% when measured against the current value.
  This is at the 15% threshold, so I flag it as borderline. The evidence is strong, though: two routes agree within 0.4%,
  and the cause is concrete (the right virus's speed was copied to the left virus, which is deeper and moves faster in pixels).

Side note, not proposed: under the same equal-size geometry, 219/220 would be about 7.21 / 10.88, versus the current 6.72 / 10.35
(−7% / −5%). That is below the 15% threshold, so they are left unchanged.

## Fixes

| qid | current | new | reason |
|---|---|---|---|
| 218 | 1.7393 | 2.00 | The right virus's stated speed was copied to the left virus. The left virus moves 14.16 px/frame at a scale 1.125× coarser (deeper), measured two ways: 2.012 and 2.004 m/s. |

No other row met the fix criteria. Ambiguous conventions (0118 table/book, the 0173/0175 cliff with or without trees, the
whale's pose-dependent height and width) are kept as the agents' hedges.
