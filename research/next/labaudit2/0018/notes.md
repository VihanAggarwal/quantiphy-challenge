# Lab audit round 2: family 0018 (captured_0018, 0018s, 0018x; one event, one label set)

Input: `../inputs/0018.json`, 57 scored D3 rows (19 questions x 3 renders). There are no S3 rows.
- Only test inputs were used: frames, the prior (g = 9.8) and depth_info (soccer ball 2.80 m, near person 2.002 m, far person 3.130 m; no time stamps).
- No labels were used. I did not look at any probe or leaderboard result for these rows.
- Round 1 (`research/next/labaudit/0018/notes.md`) audited the static rows. Its only fix was the 0018s box width (2316, 11 -> 7.85).
  It left all 30 time-stamped rows alone because their times (3.0 s and 3.4 s) lie past the clip end (2.04 s).
- `remeasure2335/` in this folder belongs to another agent's box-width re-measure. It is not mine and I did not touch it.

**Result: 21 fixes in 7 label groups (velocity x4, object distances x3). All of them depend on one clock reading (below).**
If that reading is rejected, this family has no fixes, and the static rows are confirmed as they are.

Scripts are in `scripts/`. Outputs are `labelstyle_out.txt`, `track_x_raw.json`, `track_obj.json` and `track_refined.json`. Crops are in `img/`.
- `common.py`: in-memory loader, f = 711, principal point (640, 360).
- `times_vs_duration.py`: question times against clip length for every lab clip.
- `track_x.py`, `track_obj.py`, `refine.py`, `refine2.py`: x-matte components, plus o-render centroids against a clean background built from the x matte.
- `fallfit.py`, `bounce.py`: drop-pattern test and gravity-implied depths of the falls and rebounds.
- `tennis_size.py`: size route for the tennis ball.
- `altclock.py`: object layouts at v39 and v48, end-of-clip speeds and the feet floor check.
- `labelstyle.py`: label-style distances and velocities, a Monte Carlo over click jitter (2 px), ToF noise (2 cm) and the depth-route ranges, ±1 capture-frame sensitivity, and the physical values.

## 1. The clock problem and the reading used
- 0018/s/x is the only lab family whose question times (3.0 s, 3.4 s) exceed the clip.
  - Every other lab clip has max T at or below its length. 0015 is cut to 3.04 s because it asks about 2.6 s.
  - The mp4 metadata has start_time 0, no edit list and no timecode, so it says nothing about the offset.
- Drop pattern: the steps double between v35 and v36 for the box (27, 30, **69.5** px), the soccer ball (22, 25, **62**) and the pineapple (54, **116**).
  - The fits on c = v + (v>=12) + (v>=36) have rms 0.5-0.7 px. The alternatives give 6-11 px.
  - This is the usual 25 -> 24 pattern.
- Events (capture clock):

  | object | starts moving | lands |
  |---|---|---|
  | tennis ball | c27 (v26) | about c37.2 |
  | pineapple | c27-28 | about c37.5 (v36 on the floor) |
  | box | c29-31 (it slides out of the hand) | c41 (v39) |
  | soccer ball | c29-30 | about c41.3 |

  **All four objects are in the air only during c32-c36 (v31-v35).**
- **Reading used: the label clock = clip clock + 2.0 s.** Then 3.0 s = c25 = v24, when all four are still held, and 3.4 s = c35 = v34, when all four are falling.
  - This is the only reading under which the question set is coherent: velocities of all four objects at one time, and pairwise distances between all four at a nearby earlier time.
  - It turns the times into 1.0 s and 1.4 s, the most common lab question pair (0036, 0037, 0038, ...).
  - It matches the family's design pattern: velocities are asked during flight (0016, 0020), and static configurations before the release.
  - The soccer-ball depth carries no time stamp, unlike 0016/0020 where the stated depths are at the velocity time. That fits a depth read while the ball was held still.
- Alternatives I considered:
  - (a) Label clock = clip clock (t0 = 0). Then 3.0-3.4 s is 1-1.4 s after the clip, when the box and pineapple are at rest. Asking the velocity of a resting object is not a plausible design, and the label would be about 0.
  - (b) The clip ends at the label's 3.4 s (t0 = 1.36). Then 3.0 s = landing and 3.4 s = the last frame. There is no reason for such a cut.
  - (c) The labels come from another take of the same scene. The values would then be the same as under the reading used.
- My estimate is P(t0 = 2.0, or another take) of about 0.65-0.75. Break-even for the velocity fixes is about P > 0.3, and for box-soccer about 0.4.
- Under (a), the current box and pineapple speeds also score about 0 (their labels would be about 0), so their downside is small.
  Under (b) (3.0 s = v39), the layout gives box-soccer 24, box-tennis 103 and tennis-soccer 97 (`altclock.py`), so all three distance fixes hold there too.
- **What the current answers are:** they are VLM direct answers (or copies of them) for the clip's last frame.
  - v48 geometry (`altclock.py`, floor depth for objects lying on the floor) gives box-soccer 81, box-pineapple 148, box-tennis 128, tennis-soccer 87, pineapple-soccer 125 and pineapple-tennis 69.
    The current values are 87 / 159 / 133 / 74 / 132 / 69.
  - The speeds also match. At v46-48 the box slides at 75-106 cm/s, the soccer ball is at 12-74 (near its rebound apex), the tennis ball at 54-88 and the pineapple at 40-54. The current values are 60 / 23-28 / 55 / 35.
  - So the current values are not a measurement at the asked time under any reading in which the question makes sense.
  - Within ±1 capture frame of the offset, 3.0 s still falls inside the held window: the right person's hand starts moving at c27.

## 2. Geometry (independent of the labels)
- Floor: h = 0.875 m with zero pitch, from the soccer ball's floor contact (the fall/rebound parabolas meet at c41.3, bottom y 579) and its stated range.
  - Check: the far person's feet (matte bottom y 577) give Z 2.87, against a torso Z of 2.93 from the 3.13 range (2%).
  - The near person's feet are cut by the frame bottom (y 719), so they give no check.
- **Soccer ball:** the stated range 2.80 at the held click gives a surface Z of 2.749. The gravity fit of the fall (v33-38) gives a centre Z of 2.85, which agrees.
- **Box** (front face Z):
  - The 0062 white-box size (L 19-20, W 6.9-7.5, round 1 of 0062) on 51.9 x 20 px gives 2.45-2.74.
  - The landing front-bottom edge (y 602 at v39) on the floor model gives 2.57.
  - The box is in front of the ball-holding forearm, so Z is at most 2.8.
  - Used: 2.50-2.74, central 2.61.
  - The box's own gravity fit gives 3.35, which conflicts with everything above. The box slid out of the hand and its matte is blurred, so it is not used.
- **Tennis ball** (centre Z):
  - Floor contact: the fall and rebound parabolas intersect at c37.2 with the bottom at y of about 638, giving **2.24**.
  - Fall gravity: 2.07. Rebound gravity: 2.51 (x stays constant). Matte width of 20-21 px with the 6.7 cm prior: 2.27-2.38. The half-max profile is too low-contrast to use.
  - Used: surface Z 2.04-2.38, central 2.21.
- **Pineapple:** the landing bottom (y of about 698, v36) gives 1.84. The near person's torso is at 1.80, and she holds the toy in front of her body. Used: surface Z 1.76-1.86, central 1.80.
- Held clicks (v24, by eye on 4-6x crops): box (480.5, 264), soccer ball (542.6, 263.4), tennis ball (763.5, 249), pineapple body (870, 250).
- Falling clicks: x-matte centroids. I checked them by eye on 3x crops for the tennis ball and pineapple at v34/v35; the o-render weighted centroids are biased there by the dark baseboard.
  - v34 -> v35 steps: box 30.3, soccer 25.3, tennis 52.6, pineapple 53.7 px.
  - o-render steps: box 30.1, soccer 25.7. By eye: tennis about 57, pineapple about 52.5.

## 3. Rows (label-style = 25 x |P(c+1) - P(c)| with per-click surface depth; MC = median [10-90%])

### Velocities at 3.4 s (forward difference c35 -> c36 = v34 -> v35)

| qids (o/s/x) | object | current | label-style central / MC | ±1 frame (c34 / c36) | physical \|v(c35)\| | fix |
|---|---|---|---|---|---|---|
| 2302/2321/2340 | box | 60 | 278 / 289 [253-328] | 249 / 301 | 263 | **280** |
| 2303/2322/2341 | soccer ball | 23.4/27.6/25.2 | 244 / 255 [219-294] | 215 / 285 | 236 | **248** |
| 2304/2323/2342 | tennis ball | 55 | 409 / 414 [374-458] | 392 / 425 | 406 | **410** |
| 2305/2324/2343 | pineapple | 35 | 340 / 347 [318-385] | 354 / 327 | 355 | **345** |

- Route 1 (matte clicks with the per-object depth route) and route 2 (the smooth parabola slope, or the o-render/eye clicks) agree within 3-8% for every object.
- Each current value is 4.5-10x low.

### Distances at 3.0 s (v24, held)

| qids (o/s/x) | pair | current | central / MC | routes | fix |
|---|---|---|---|---|---|
| 2306/2325/2344 | box-soccer | 87 | 25.2 / 25.2 [22.9-30.1] | box Z from the 0062 size: 23.6; from the landing: 27.0 | **25.5** |
| 2308/2327/2346 | box-tennis | 133 | 104.9 / 105.6 [99.8-113.2] | tennis Z floor 104.9, fall gravity 110.0, rebound 102.5; box Z size 108.5, landing 102.6 | **105.5** |
| 2309/2328/2347 | tennis-soccer | 74 | 93.3 / 93.2 [87.8-100.8] | floor 93.3, size about 88, fall gravity 102, rebound 85 | **92** |
| 2307/2326/2345 | box-pineapple | 159 | 142.3 / 142.8 [135.5-150.5] | 139-147 | keep (+8-14%, below the bar) |
| 2310/2329/2348 | pineapple-soccer | 132 | 135.2 / 134.8 | | keep |
| 2311/2330/2349 | pineapple-tennis | 69 | 46.0 / 45.3 [34.7-57.6] | floor 46, fall gravity 33, rebound 70.5 | keep (dominated by the tennis-pineapple depth gap; routes spread 2x) |

- Tennis-soccer is the weakest of the three distance fixes: the routes spread ±9% around 93, but every route is 15-38% above 74.
  - It also carries little risk: the end-of-clip layout gives about 86, so 92 is closer than 74 under that reading too.

### Static rows (re-check; no change)
- Heights of the persons, distance between the two people, box length and width, ball diameters and shoe length: round 1's numbers stand. None is 12% or more off.
- Yellow (pineapple) toy height, 15.89 / 17.16 / 16.41:
  - Held, sharp v10: 60 px (leaf tip y 218.7 to body bottom 278.3). At surface Z 1.80-1.85 that is **15.2-15.6 cm**.
  - The 0020 audit of the same toy found 15-17.5.
  - The s value 17.16 is at most 11% high, so there is no fix. If the family is harmonised to one value, 15.9 is the best.

## 4. Risk statement
- Every fix assumes the label clock is the clip clock + 2.0 s, or that the labels come from another take of the same drop.
- If the labels were instead taken 1-1.4 s after this clip ends, the box-soccer distance fix (25.5 against perhaps 50-150) and the soccer-ball and tennis-ball speed fixes would lose. The box and pineapple speeds would lose little, since their labels would be about 0.
- Expected value is positive for every fixed group at any P(reading) above 0.4. My estimate is about 0.7.
