# Lab audit round 2: family 0006 (captured_0006 / 0006s; one event, one label set)

Input: `../inputs/0006.json` has 10 scored D3 rows (5 questions x 2 renders, o and s). There is no x render and there are no S3 rows.
Only the frames and the test `prior`/`depth_info` were used: g = 9.8, and the ranges 1.402 m at t = 1.0 s and 1.065 m at t = 1.2 s.
No labels were used. Round 1 is in `../../labaudit/0006/notes.md` and made no fixes.

**Result: no fixes.** One row pair comes close to the bar and is described below: v(1.2 s) (2153/2158), currently 2.1.
Two independent routes agree on about 2.7, but the current value is 22-24% off, not the 25% required.

Scripts are in `scripts/`. Outputs are `motion_out.txt`, `track_o_s90.json` and `bgtrack.json`. Crops are in `img/`.
- `common.py`: loader, f = 711, principal point (640, 360).
- `track.py`: yellow-mask centroid, bbox and hull per frame.
- `bgtrack.py`: background-difference silhouette, including the grey face-blur patch.
- `ballistic.py`: 3D ballistic fits on the capture clock under several drop hypotheses.
- `motion.py`: label emulation and Monte Carlo.
- `variants.py`: centre and depth-model variants.
- `static.py`: toy extents.
- `dropcheck.py`: optical flow.

## Clock
- I use the usual 25 -> 24 pattern: capture c = v + 1 for video 12-35. So t = 1.0 s is c25 = v24, and t = 1.2 s is c30 = v29.
  c31 = v30, c32 = v31 (last airborne frame) and c33 = v32 (first frame on the table).
- Neither the drop before v12 nor the drop before v36 can be seen directly in this clip.
  - The toy is held still in frames 0-18. At 35/36 the toy is bouncing.
  - Optical flow on the person is too small, and the toy contaminates the flow.
- What the track does show is that **no drop falls inside the flight v25-v31**.
  - A ballistic fit (g along the camera's down, pitch 1.17 deg from the table VP) has rms 0.9 px with the standard map.
  - A drop before v28, v29, v30 or v31 gives 2.1-7 px.
- A drop between v24 and v25 is the only alternative that would move t = 1.2 s (to v28). It fits the stated ranges worse when v24 is included (2.8 vs 1.3 px rms).
  It also contradicts the 11/12 and 35/36 pattern found in every other lab clip.

## Track (o render; the s render agrees within 2-3 px)
- The toy has a blurred grey face patch. The yellow mask leaves it out, and when the toy turns (v29-v31) the yellow-only centroid moves about 10 px right.
  I therefore used the background-difference silhouette, plus the s render's outline, which shows the whole toy.
- Centres:
  - v24: (606, 142.5) (yellow ring hull; the face patch sits inside the ring)
  - v29: (580.5, 224)
  - v30: (571, 283)
  - v31: (560.5, 367), a vertical blur streak from y 301 to 430
  - v32: (550, 446), on the table
- Image steps in the fall: v29->v30 is 59.8 px, v30->v31 is 84 px.
- **Depth motion.** The stated ranges imply Z 1.341 -> 1.044 between c25 and c30, so Vz is about -1.49 m/s (toward the camera).
  Second route: the toy is 56 px wide at v24 and 77-90 px on the table (v32-v35, table-plane Z 0.85-0.89 from round 1).
  That gives Z falling about 0.45 m in 0.32 s, so Vz is about -1.4. The two routes agree.
- Ballistic fit with the stated ranges as soft constraints (fits on v25-31, v26-31, v26-30 and v24-31):
  - apex t = 0.990-0.995 s
  - V(1.2 s) = (-0.12, 2.04-2.10, -1.49 to -1.73) m/s
  - rms 1.15-1.35 px
  - model ranges R(c25) 1.40-1.42 and R(c30) 1.03-1.06, consistent with the stated ranges
- Gravity-only fits (free scale) are ill-conditioned: R(c30) comes out anywhere from 1.1 to 1.9. They were not used.

## Motion rows

| qids (o/s) | question | current | label-style | physical | verdict |
|---|---|---|---|---|---|
| 2154 / 2159 | displacement 1.0 -> 1.2 s | 36.28 / 36.38 | Stated ranges at the v24 and v29 clicks give **36.5 cm**. The yellow-only centre gives 36.3. MC with 3 px clicks: 36.1-36.8. (If depth_info were Z-depth: 40.6.) | about the same; the ranges are inputs | **Keep** (within 1%) |
| 2153 / 2158 | v at 1.2 s | 2.1 / 2.1 | 25 x \|P(c31) - P(c30)\|, with P(c30) at the stated 1.065 and R(c31) from:<br>(a) linear range extrapolation, 0.998 m: **2.70**<br>(c) Z linear from c30 to the table contact at c33 (Z 0.866-0.92): 2.53-2.74<br>(b) the ballistic fit's R(c31), 0.951-0.992: 2.78-3.2<br>Centre variants (yellow-only, bbox, s render): 2.68-2.75 at R31 0.998. Z-depth reading: 2.9.<br>MC (3 px clicks, ToF sigma 2-4 cm at c31): median **2.71**, 10-90% 2.2-3.6. Reaching 2.1 needs R(c31) of about 1.06-1.07 (a ToF error of +7 cm). | Fit: \|V(1.2)\| 2.53-2.71 instantaneous; forward difference c30->c31 2.69-2.86 | **Keep (near miss).** See below. |
| 2155 / 2160 | v at first desk impact | 2.7 / 2.7 | Forward difference c32 -> c33 (last airborne frame -> first frame on the table), with Z(c32) 0.91-0.94 and Z(c33) 0.866-0.90: **2.61-2.81**. If the labeller had used the contact frame c33 -> c34 (the bounce): 0.62. | Fit plus table plane (camera 0.17-0.22 m above the top, toy radius 4.5-5 cm): impact at t = 1.313-1.331 s, \|V\| 3.50-3.74 (vertical 3.15-3.30) | **Keep.** The current value matches the forward difference across the impact. The physical value is 25-28% higher, but the routes disagree, so condition (a) fails. |

### Why v(1.2 s) = 2.1 is not changed, and why it is close
- **The current value looks wrong for a concrete reason.** 2.1 equals the vertical-only free-fall speed g x (1.2 - t_apex), which is 2.01-2.11 for an apex at 0.985-0.995 s.
  It ignores the 1.4-1.7 m/s toward-camera component shown by the stated ranges (1.402 -> 1.065 m in 0.2 s) and by the toy's growth in size.
- Every label-style variant gives 2.5-3.2, and the physical value is 2.53-2.71. Two routes, (a) at 2.70 and the physical fit at 2.53-2.71, agree within 7%.
- **But gate (b) fails narrowly.** Against the central label-style value of 2.70-2.75, the current 2.1 is 22-24% off, not the required 25%.
  The ratio is 1.29, so the gate would pass only if the gap were measured as a ratio.
- Expected score from the MC, with linear credit beyond 5%: answer 2.1 gives 0.775; answers 2.6-2.7 give 0.88-0.92.
  So about +0.11-0.14 per row, for 2 rows that share one label.
- **If the orchestrator relaxes the gate:** set 2153 and 2158 to 2.7. Use 2.6 if the physical value is preferred.
  The risk case is a ToF reading at c31 that is 6-7 cm too far, which would make the label about 2.1.

## Static rows (re-checked)

| qids (o/s) | question | current | measurement | verdict |
|---|---|---|---|---|
| 2151 / 2156 | toy height | 9.63 / 10.54 | Yellow mask at v24 (R 1.402): 54 px gives 9.7 cm. v25 gives 10.0, v26 gives 10.4-10.8. The silhouette sits about 5 cm behind the visible front surface: +3.6%. Round 1 table route: 10.8-11.4 (toy on its side). | **Keep** (both within 10% of 9.7-11) |
| 2152 / 2157 | toy width | 10.19 / 10.82 | v24: 56 px gives 10.5 cm. v25: 10.7-10.9. The s outline is 9.4-11.1 (the left edge is faint in s). Round 1 face-on on the table: 9.0-10.4. | **Keep** |

- I checked the stated priors of the other lab clips for this prop. The 'yellow toy' in 0018/0020 is a different, larger pale-yellow pineapple (about 15 cm), so no size transfers.
- The two renders carry slightly different size answers, 9.6 vs 10.5 and 10.2 vs 10.8. Both are inside the measured band and the gap is below the 12% static gate. Harmonising to about 10.1 / 10.6 would be optional.

## Result
10 rows checked, **no fixes**. The one near miss is v(1.2 s) on 2153/2158: 2.1 now, about 2.7 label-style.
