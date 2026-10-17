# Audit simulation_0153 family (parking garage, clips 0149, 0150, 0151, 0151_segmented, 0152; 0153 used as reference)

Scene: underground garage. The yellow car is a 1.2x-scaled RX-7 FD: the 0.764 m tire = 1.2 x 255/40R17. The blue car is a small cart (tire 0.369 m).
There are three distinct cameras:
- A, aisle view: 0150, 0151, 0151_segmented. 0150 and 0151 share the yellow car depth_info, 11.38 m at t=0.5 s.
- B, corridor view: 0152, and 0153 (the 2D clip with the same blue-cart motion and no yellow car; it has no rows here).
- C, oblique view: 0149.

The answers have no stated-fact rows; all are agent measurements.

## Cross-clip table (current answers)
| quantity | 0149 (C) | 0150 (A) | 0151/_seg (A) | 0152 (B) | 0153 (B, 2D, ref) | spread |
|---|---|---|---|---|---|---|
| yellow car width | 2.09 | 2.05 | - | - | - | 2% (1.2x RX-7 body width 2.11) |
| marking height | 0.745 | 0.755 | - | - | - | 1.3% |
| pillar width | 1.02 | 0.99 | - | - | - | 3% (camera B: 205 px at 13.04 m = 1.00) |
| yellow v(0.5) | 6.40 | 6.44 | - | - | - | 0.6% |
| yellow a(0.5) | 9.9 | 10.3 | - | - | - | 4% |
| yellow v(1) | 9.64 | 9.84 | 9.71 | 9.87 | - | 2.4% |
| yellow a(1) | 3.3 | 3.6 | 3.56 | 3.62 | - | 9% (0149 lowest) |
| blue width | - | - | 0.87 | 0.82 | - | 6% |
| blue v(1) | - | - | 3.93 | 3.95 | 3.937 | 0.5% |
| blue a(1) | - | - | 1.44 | 1.45 | 1.478 | 2.6% |
| B1 lettering W x H | - | 1.62 x 1.51 | - | - | - | singleton |
| pillar spacing | - | 6.3 | - | - | - | singleton |

The motion is the same scripted Blender smoothstep in every clip: zero speed at frames 0 and 59. The yellow car travels about 16.6-16.85 m and the blue car about 6.74 m. The cameras give independent scales, and they agree to within 2.4% on speed.

## Singleton re-measurement (crosscheck.py)
- **B1 lettering.** In 0150, the pixel bbox is 181 x 167 px at Z = 23.44 m.
  - With f = 2606 (wall base plus tire): 1.63 x 1.50. With f = 2667 (Blender default): 1.59 x 1.47.
  - **Independent route, camera B (0153 frame 0).** The far-wall B1 is 69 x 65 px, with the same aspect ratio.
    - Camera height comes from the blue tire: h = R(vb - v0)/(vb - vhub) = 1.407 m. The wall base row is v = 599.3 and v0 = 539.2.
    - The resulting size, which does not depend on f, is **1.615 x 1.52 m**.
    - This agrees with the current 1.62 x 1.51 within 1%. OK.
- **Pillar spacing.** Front faces only, so the result is centre-to-centre.
  - 0150 (f*h = 3724): 6.55-6.61 m.
  - Camera B (0153, f*h = 3752 from the blue tire): 6.63 and 6.61 m.
  - Two cameras therefore agree on **6.6 m c-c**. The clear gap is about 5.5 m (pillar depth about 1.1 m).
  - The current answer of 6.3 hedges the two readings (-4.6% vs c-c, +15% vs gap). The definition is ambiguous, so no fix.

## Suspects considered
- **0149 a(1s) = 3.3.** This is an average of the backward, central and forward conventions.
  - The 0149 backward value alone is 3.43, and it also carries t0 = -0.3 fr. With t0 = 0, as the siblings fit, it becomes about 3.6.
  - The family backward value is about 3.6-3.7. The answer is about 9% low, which is below the 15% threshold, so no fix. A soft candidate for 3.55 if desired.
- **0149 a(0.5s) = 9.9** vs the family backward value of about 10.4-10.5. That is 5%, so no fix.
- **Blue width 0.87 vs 0.82.** These come from two cameras with tire and roof depth ratios. The track is 0.82-0.85 m, so it is consistent and no fix.

## Result
No fixes. All 31 rows are consistent across clips or confirmed by an independent route.
