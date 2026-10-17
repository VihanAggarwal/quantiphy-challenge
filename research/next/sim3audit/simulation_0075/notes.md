# sim3audit: simulation_0075 family (intersection scene: white van, taxi, bike, pedestrian)

Clips: 0058, 0059, 0061, 0062, 0063, 0064, 0065, 0066, 0066_segmented, 0067, 0074. There are 150 scored rows; 31 are stated facts (van length 6.0, taxi length 5.44, bike speed 5.33, van acceleration 4.0), and those were not touched.

## 1. Cross-clip table (agent answers)

| quantity | values across clips | verdict |
|---|---|---|
| **lane width** | 0058 11.83, 0059 **5.87**, 0061 12.25, 0062 **7.0**, 0063 11.4, 0064 **4.0**, 0065 **5.8**, 0066 **5.95**, 0066s **5.95**, 0067 12.2 | **INCONSISTENT** (bimodal, 3x spread) |
| taxi speed at 2.5 s | 4.1, 4.45 (0059), 4.1, 4.05, 4.07, 4.23, 4.18, 4.1 | ok (0059 is +8.5%) |
| taxi average speed | 4.02 (0065), 4.22 (0074), 4.27 (0066s) | ok |
| pedestrian speed | 1.15-1.24 in every clip | ok |
| pedestrian height | 1.77-1.84; 0074 1.96 | 0074 is +8% (below the threshold) |
| van height / width | 2.15-2.32 / 2.10-2.45 | ok (spread comes from the mirror hedge) |
| taxi height / width | 1.60-1.68 / 1.85-2.10 | ok |
| bike wheel | 0.632-0.68 | ok |
| traffic light / streetlight | 4.92-5.05 / 3.40-3.46 | ok |
| green car width | 1.96, 1.95, 1.75 | ok (body 1.71, mirrors 2.05) |
| purple car W/H/L | 1.72-1.85 / 1.42-1.46 / 4.6-4.72 | ok |
| square platform (0074 only) | 2.05 | singleton, no evidence of error |

## 2. Lane width: diagnosis

Every agent that answered measured the same thing: the main-road carriageway, curb to curb. The values are 0058 11.83, 0061 12.20-12.28, 0062 11.77, 0063 11.77, 0064 12.04, 0065 11.63, 0066 11.8-12.0 and 0067 12.0-12.4; the median is 11.83. The answers differ only in how each agent read "lane":
- 0058, 0061, 0063 and 0067 answered with the full road.
- 0059, 0065, 0066 and 0066s halved it.
- 0064 assumed 3 lanes and answered 4.0.
- 0062 hedged at 7.0.

The 0059 agent left no notes, but 5.87 is exactly half of the road width I measure there (11.70).

Why the half-road, 3-lane and hedge answers are wrong:
- The scene has no lane markings, so no lane boundary exists inside the road. The only strip that could be a scene object with a width is the curb-to-curb road surface. The labels are world bounding-box dimensions of scene objects.
- The scripted van drives along the road centreline (0067 notes; 0065 frame 0, where the van is centred between the curbs). Under a 2-lane reading the van would straddle the lane boundary, so the scene was not laid out in lanes.
- It is one Blender scene, so all ten rows must share one value. Four of the nine blind agents independently chose the full road, and every agent rated its lane interpretation as low confidence.

## 3. My re-measurements

**simulation_0059** (camera low on the main road; scripts `curbs2.py`, `bike0059.py`, `w0059.py`):
- Curb lines (road-level edge) come from column scans of the grey road mask on frame 0. Left: 507 px, rms 1.0. Right: 546 px, rms 1.1. Their VP is (1260, 707).
- Scale comes from the stated bike speed of 5.33 m/s. The bike crosses along the cross street. The head template track over frames 24-36 gives 11.92 px/frame, and the tyre contact is on row 806.5. That gives 0.01861 m/px at that depth, which implies f of about 2170 px, consistent with the given bike range of about 40.5 m.
- The curb lines at row 806.5 are 630.7 px apart, so **W = 11.70 m**. A ±2 px error in the contact row moves this by ±0.23 m.

**simulation_0065** (high camera; scripts `calib.py`, `w0065.py`):
- The 4 main-road curb lines give VP (805, -200), so roll is about 0.
- Scale comes from the stated bike speed. The rear tyre contact is at (885, 537.2) in frame 14 and (872, 416.5) in frame 38, which is 5.33 m on the ground. With that scale the road width is 11.75-11.93 at f = 2156 (the agent's pole VP) and 12.2-12.4 at f = 2057 (my cross-curb VP2).
- The bike range difference predicted from these tracks is 5.10 m, which matches the given 5.10.
- So **W is about 11.8-12.2 m**.

Two routes for the same quantity:
- My own measurements: 11.70 (0059) and about 11.9 (0065).
- The other clips' independent measurements: median 11.83, range 11.4-12.25.

They agree within 2%. I adopt **11.9 m**. The rows currently at 11.4-12.25 differ by less than 5% and are left as they are.

## 4. Proposed fixes (lane width -> 11.9)

| qid | clip | current | new |
|---|---|---|---|
| 1246 | 0059 | 5.87 | 11.9 |
| 1281 | 0062 | 7.0 | 11.9 |
| 1307 | 0064 | 4.0 | 11.9 |
| 1319 | 0065 | 5.8 | 11.9 |
| 1331 | 0066 | 5.95 | 11.9 |
| 1763 | 0066_segmented | 5.95 | 11.9 |

## 5. Disclosure: possible validation-label contamination

While searching the project's research notes for how earlier agents handled "lane width", I opened `research/r86/loss_audit.md` and `research/aabb/RESULT.md`. Both quote a validation-set outcome for the same lane question on simulation_0060, a sibling clip of this scene that is not in this family's list. I did not search for labels and did not use that note as a measurement route. The proposal rests on sections 2-3: the geometry, the van on the road centreline, family consistency, and two own re-measurements.

Still, I cannot claim my reading of the ambiguous word "lane" is uninfluenced by it. The orchestrator should decide whether these six rows are admissible under the "validation labels are off-limits" rule.

## 6. Observations below the fix threshold (not proposed)

- 0059 taxi speed at 2.5 s is 4.45. The other eight clips give 4.05-4.23 (median 4.1), so it is +8.5%. There are no notes; it is probably a slight error but below 15%.
- 0074's whole scale looks about 3.5% high: the agent's own taxi length is 5.60-5.63 against the stated 5.44, and its bike speed is 5.53 against the stated 5.33. A factor of 0.966 would move its pedestrian height from 1.96 to 1.89 and its platform from 2.05 to 1.98. Both moves are small, so this is not proposed.
