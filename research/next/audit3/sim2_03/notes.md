# Audit sim2_03: family simulation_0103 (0041, 0098-0103, plus segmented twins)

**Result: no fixes proposed.** All 59 scored rows were checked (48 measured, 11 stated facts). Every current answer agrees with the family-consistent re-measurement, or the remaining doubt comes from an unknowable modelling choice (the boat origin). One row (1744, boat height) is about 12% low. That is below the 15% bar, so it is listed as a watch item.

## Family structure
- The side-view clips 0098-0103 all use one identical fixed camera with the same framing: the AH805 fishing boat on the water surface and a shark in the cut-away underwater band. Each segmented twin is frame-aligned with its original; template offset between twin and original is 0 px at frames 5, 24 and 40 for every clip.
- 0041 / 0041_seg is a steep oblique telephoto view of the same AH805 boat on a beach with a walking person. The stated facts there are: boat length 10.0 m, boat speed 4.0 m/s, person speed at 1.0 s 1.3 m/s.
- One world scale covers every side clip, and three independent priors give it:

| Source | Pixel value | Scale |
|---|---|---|
| Boat length, bow tip to stern extreme (stated 10 m), median over 6 seg clips | 858.2-858.7 px | 85.85 px/m |
| Shark acceleration (prior 1 m/s²), quadratic fit to the 0101/0102/0103 shark edges | 85.2-86.4 px/s² | about 86.0 px/m |
| Shark speed (prior 3 m/s in 0098) | 257.8 px/s | 85.9 px/m |

  These agree within 0.2%. Shark and boat are therefore in the same depth plane, as the agents assumed.
- Motion is the same across the family:
  - Boat: 428.6-429.4 px/s, which is 5.00 m/s, constant (quadratic term about 0).
  - Shark in 0098-0100: 257.8-258.2 px/s, which is 3.00 m/s, constant.
  - Shark in 0101-0103: v0 = 171-173 px/s, which is 2.00 m/s, and v(1 s) = 258 px/s, which is 3.0 m/s.
- Video frames 0 and 1 are identical in every clip, and t = frame/24 is the correct clock (v0/a = 2.00 s).

## Quick check of every scored row
Method for the side clips: masks from the segmented twin (white background), sub-pixel half-level edges, and linear or quadratic fits over frames ≥ 1. The scale is 85.85 px/m. Code is in `code/side_all.py`.

| qid | clip | quantity | current | quick check | verdict |
|---|---|---|---|---|---|
| 12 / 1746 | 0041 / _seg | boat width | 3.1 | 2.72 m at the last station visible ahead of the cabin, still widening; parallax ratio gives about 2.5-2.7 m at the letter line (below the gunwale) | OK (plausible 2.8-3.2; no ≥15% evidence) |
| 1744 | 0041_seg | boat height | 8.3 | 9.3-9.5 (see below) | **watch** (about 12% low; below the bar) |
| 1748 | 0041_seg | avg person speed | 1.263 | 1.36 by camera model; stated 1.3 at 1.0 s for the same footage; walking speed is steady | OK (within 3% of 1.3) |
| 183 / 1788 | 0099 | boat speed | 5.0 | 429.1 px/s → 5.00 | OK |
| 184 / 1789 | 0099 | shark speed | 3.0 | 258.0 → 3.00 | OK |
| 185 / 1790 | 0099 | shark length | 3.27 | 279.6-281.9 px → 3.26-3.28 | OK |
| 186 / 1791 | 0099 | shark height | 1.16 | 104.6 px raw → 1.22; about 1.15 after the near-pectoral-fin correction | OK |
| 187 / 1792 | 0100 | boat speed | 4.99 / 5.0 | 428.6 → 4.99 | OK |
| 188 / 1793 | 0100 | shark speed | 3.0 | 258.0 → 3.00 | OK |
| 189 / 1794 | 0100 | shark length | 3.24 | 279.5-280.9 → 3.26-3.27 | OK |
| 190 / 1795 | 0100 | shark height | 1.19 | 1.22 raw / 1.15 corrected | OK |
| 191 / 1796 | 0101 | shark v(0) | 2.0 | 172-173 px/s / 86 → 2.00 | OK |
| 192 / 1797 | 0101 | boat speed | 5.0 / 4.99 | 428.8-430.9 → 5.0 | OK |
| 194 / 1799 | 0101 | shark length | 3.27 | 278.9-280.7 → 3.25-3.27 | OK |
| 195 / 1800 | 0101 | shark height | 1.16 | 1.22 raw / 1.15 corrected | OK |
| 196 / 1801 | 0102 | shark v(0) | 2.0 | 171.3-171.7 / 86.3 → 1.99 | OK |
| 197 / 1802 | 0102 | boat speed | 4.95 / 5.0 | 429.0 → 5.00 | OK (1%) |
| 199 / 1804 | 0102 | shark length | 3.22 | 279.8-281.6 → 3.26-3.28 | OK (1.5%) |
| 200 / 1805 | 0102 | shark height | 1.21 | 1.22 raw / 1.15 corrected | OK |
| 201 / 1806 | 0102 | shark-boat distance at 0.5 s | 3.9 | dx = 1.53 m; depends on the boat origin: keel 3.45, hull middle 4.35, bbox centre with mast 7.96 | unresolvable (hedge kept) |
| 202 / 1807 | 0103 | shark v(0) | 2.0 | 172-173 → 2.00 | OK |
| 203 / 1808 | 0103 | boat speed | 4.99 / 5.0 | 428.6 → 4.99 | OK |
| 205 / 1810 | 0103 | shark length | 3.24 | 279.0-280.8 → 3.25-3.27 | OK |
| 206 / 1811 | 0103 | shark height | 1.22 | 104.8 px → 1.22 raw | OK |
| 207 / 1812 | 0103 | shark-boat distance at 0.5 s | 15.6 | dx = 14.96 m; 15.27 (keel origin) to 16.87 (bbox centre) | OK (within 8% of every hypothesis) |

The remaining scored rows are stated facts and were not touched: 11, 13, 14, 193, 198, 204, 1745, 1747, 1798, 1803 and 1809.

Shark height: the same shark gets 1.16-1.22 across the clips, against a family consensus of about 1.15-1.17. The raw dorsal-tip to pectoral-tip extent is 104.8 px (1.22 m). The near pectoral tip moves 1.1-1.9% faster than the centreline, so perspective pushes it about 4-7 px low. All current values are within 8% of each other, so nothing was changed. Harmonising to about 1.16 is optional.

## Watch item: 1744 (boat height in 0041_seg, current 8.3)
The height was built from two parts.

**Keel to roof, from the side clips:**
- The keel or skeg bottom is at y about 639. The reflection starts below it.
- The roof silhouette at the mast is at y about 237.
- At 85.85 px/m this gives 4.68 m. Correcting the near roof edge for perspective (cabin parallax 2.5%) gives 4.59 m.

**Mast above the roof, from 0041:**
- The mast is cut off by the top of the frame in all side clips, so this part comes from 0041.
- Pinhole model from the 0041 agent: f = 5900 px, pitch 52.6°, principal point at the image centre, no roll.
- Camera height was solved from the stated boat speed of 4.0 m/s, giving Hc = 138.5 m. This matches the agent's person-height calibration (about 139 m).
- The mast foot to the top of the mast ball spans 100.0-101.6 px over 9 frames. That gives 4.80-4.85 m above the roof, or about 4.73 m after correcting for the foot radius.

**Total:** 9.3-9.5 m (best estimate about 9.4). The current 8.3 is about 12% below this, which does not meet the ≥15% bar, so no fix is proposed. The second part rests on a single camera model. A rough cross-check against the black box on the mast, visible in both views, agrees to about 6-10%.

## Distance rows (201 / 1806)
The vertical offset depends on where the boat's origin sits (keel, hull middle, or bbox centre including a mast of about 9.4 m), and the footage cannot tell these apart. The hedge of 3.9 has about the same expected score as any other choice in the 3.9-4.4 range.

Code is in `code/`. No frames or arrays were saved, and the work folder is about 110 KB.
