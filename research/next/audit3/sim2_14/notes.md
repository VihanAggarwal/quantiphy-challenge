# Audit sim2_14: notes

Families:
- simulation_0057 family: 0053 (2048², camera shifted), 0054 and 0057 (1080², same camera), and 0057_segmented. Prior: orange car a = -2.86 m/s².
- simulation_0172 family: 0169, 0169_segmented, 0171 and 0171_segmented. Prior: astronaut height 2.2 m.

Scored rows checked: 33 (19-32, 1759-1761, 401-408, 1858-1865). The 0171 and 0171_segmented rows are unscored. I only skimmed their notes.

Scoring note: qp/mra.py takes abs(pred), so the sign of a deceleration answer does not matter.

## Family table (current answers)

### Car family

| quantity | 0053 | 0054 | 0057 | 0057_seg | quick check (mine) |
|---|---|---|---|---|---|
| orange car pixel acc (bbox-mid, 1080-eq px/s²) | -316.1/1.896 = -166.7 | -165.4 | -165.0 | -164.2 | consistent; agents -163.7 to -166.6 |
| green speed @2 s (m/s) | 11.86 | 11.98 | - | - | 11.57 (0053: 42.64 px/f) / 11.66 (0054: 22.43 px/f) |
| orange length (m) | 5.03 | 5.16 | 5.20 | 5.20 | mask 286-287 px (1080) / 546 px (2048) -> 4.94-4.98 |
| green length (m) | 5.18 | 5.29 | - | - | 565.5 px / 296 px -> 5.12 |
| lamp distance (m) | 7.85 | 8.01 | 8.17 | 7.97 | 443-444 px (1080) x ground scale -> 7.8-7.96 |
| orange width (m) | - | 2.08 | 2.13 | 2.13 | body 108-111 px -> 1.92; mirror-to-mirror ~124-127 px -> 2.15-2.2 |
| green width (m) | - | 2.04 | - | - | body ~114 px -> 1.98 |
| person speed @2 s (m/s) | 0.47 | - | - | - | 1.71 px/f (2048) -> 0.46-0.47 |

- Scale: s = 2.86/|a_px| at the bumper-extreme height. That is 0.01733 m/px (1080) or 0.009048 m/px (2048). The ground scale is 1.6-3.3% larger, for camera height 17-35 m.
- 0053 is at exactly 2048/1080 = 1.896 of the 1080 scale. Lamp separation is 842.5 vs 444.4 px, and the green car moves 1279 vs 673 px/s. So the world scale is the same in all clips.
- All current values agree with each other within about 4%, and with my quick checks within 5%. The residual spread comes from the agents' different camera-height assumptions (lamp 7.85-8.17).
- No car row differs by ≥15%, so there are no fixes.
- The person speed was checked by phase-matched template displacement over one gait period (15 frames). It is 1.60-1.89 px/f centred at f64-68 and 1.92-1.98 px/f centred at f82, which extrapolates to about 1.71 px/f at f60. That gives 0.46-0.47 m/s.

### Astronaut family

- 0169 shows a small astronaut (89-90 px tall at f0) drifting upward past the moon limb.
- 0171 shows a large astronaut bounding across the lunar surface. It is a different animation, so no motion values transfer between them. Only the size prior is shared.

## 0169 / 0169_segmented: details

Tracks:
- t169.txt: original clip, threshold >60 blob, intensity-weighted centroid.
- t169s.txt: segmented twin, non-white blob.

The trajectory fits a single 2-key Blender Bezier ease (smoothstep), p = p0 + Δ·S((f-f0)/T) with f0 ≈ -0.45 and T ≈ 78.7 frames:
- dy = -274 px and dx = +16 px (the x drift is mostly tilt).
- rms 0.33 px (centroid).
- A free cubic or quintic fit gives the same derivatives.

Reproduce with astro_fit.py (uses lm.py and the t169*.txt files).

Conventions:
- v(k) = |p(k)-p(k-1)|·fps
- aB = (v(k)-v(k-1))·fps, the stated "change of speed per second", centred at k-1
- aM is centred at k-0.5
- aF is centred at k

| qid (twin) | t | current | route A smoothstep (orig / seg) | route B poly5 (orig / seg) | verdict |
|---|---|---|---|---|---|
| 401 (1858) | 0.5 v | 1.56 | 1.588 / 1.589 | 1.583 / 1.586 | ok (2%) |
| 402 (1859) | 0.5 a | 2.45 | aB 2.66 / 2.68 (aM 2.61, aF 2.56) | aB 2.79 / 2.75 | 8-12% low, below 15%, no fix (2.65 would be better) |
| 403 (1860) | 1 v | 2.58 | 2.608 / 2.619 | 2.629 / 2.629 | ok |
| 404 (1861) | 1 a | 1.30 | aB 1.516 / 1.530 (aM 1.47, aF 1.42) | aB 1.516 / 1.533 | FIX -> 1.50 (borderline, see below) |
| 405 (1862) | 2 v | 2.94 | 2.934 / 2.948 | 2.919 / 2.940 | ok |
| 406 (1863) | 2 a | 1.00 | aB 0.769 / 0.775 (aM 0.82, aF 0.87) | aB 0.796 / 0.792 | FIX -> 0.80 |
| 407 (1864) | 3 v | 0.99 | 0.975 / 0.972 | 1.005 / 0.989 | ok |
| 408 (1865) | 3 a | 2.95 | aB 3.05 / 3.08 | aB 2.93 / 3.00 | ok |

As a third, local check, I fitted cubics over ±6, ±9 and ±12 frames around k-0.5. They are noisy, but give medians of about 1.5 at 1 s and 0.81 at 2 s.

Why the current answers for 404 and 406 are wrong: the 0169 agent differentiated noisy centroids. It used ±5-frame quadratic fits, then a 5-frame moving average, then the slope. That biased the acceleration near the speed peak, which is at frame 39. On the clean smoothstep the acceleration changes by about 2.3 m/s³, so it is steep around 1-2 s, and a smoothing window shifts the estimate.

- **406/1863, a at 2 s.** 1.0 is 15-30% too high under every difference convention (0.77 / 0.82 / 0.87). The two routes agree within 3%. 0.80 hedges the aB and aM conventions.
- **404/1861, a at 1 s.** 1.30 is 17% below the aB value (1.52) relative to the current answer, or 14.5% relative to the new value. It is also 12% below aM (1.47). Under every convention 1.50 scores the same as 1.30 or better. This fix is borderline on the 15% rule, so drop it if the rule is applied strictly against the new value.

## Fixes

| qid | clip | current | new | reason |
|---|---|---|---|---|
| 406 | simulation_0169 | 1.0 | 0.80 | smoothing bias; clean 2-key ease gives aB 0.77-0.80 |
| 1863 | simulation_0169_segmented | 1.0 | 0.80 | same object and motion as 406 (twin track agrees) |
| 404 | simulation_0169 | 1.3 | 1.50 | smoothing bias; aB 1.52-1.53 (borderline 14.5-17%) |
| 1861 | simulation_0169_segmented | 1.3 | 1.50 | twin of 404 |
