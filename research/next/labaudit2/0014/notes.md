# Lab audit round 2: family 0014 (captured_0014, 0014s, 0014x). One event, one label set.

Inputs: `../inputs/0014.json`. That is 33 scored rows (11 questions x 3 renders), all D3.
- No S3 rows in this family.
- No labels used.
- No priors for these props exist in the test split. The only prior is "t=0.6, ball acceleration = 4.6 m/s^2".

Scripts are in `scripts/`; crops and masks are in `img/`. Frames are read straight from the mp4s; nothing is dumped.

Camera: f = 711, principal point (640, 360).

## Geometry

### Board (`board.py`, `geo.py`)
- Corners from line fits on a median of frames 30-48: TL (500.2, 312.4), TR (592.3, 301.4), BR (609.6, 409.1), BL (508.8, 423.2).
- Vanishing-point plane at f = 711:
  - The edges are orthogonal to within d1.d2 = 0.015.
  - The near anchor (bottom-mid at the stated 1.701) lies 1.3 cm off the plane through the far anchor (top-mid at the stated 1.854).
  - The slope direction from the stated anchors is within 2.5 deg of the vanishing-point direction.

### Table (`table.py`, `tplane.py`, `tcheck.py`)
- Edge-line fits (rms < 0.41 px) give FL (424.7, 501.3), FR (729.4, 454.4), BR (658.3, 308.7), BL (447.7, 331.8). BL is extrapolated behind the cup.
- PnP with 60.3 x 76 and f = 711 gives n = (0.048, 0.883, 0.467), c = 0.845, max reprojection 1.4 px. Swapping the two side lengths gives 13.6 px.
- **The stated ranges are about 6% longer than this metric plane.** pen, book and slope_near all need c = 0.894-0.896. cookie needs 0.867, but it stands upright.
- "Label scale" below means f = 711 with the stated ranges (c = 0.895). "Metric" means c = 0.845.
- Cross-check on the normal: the cup rim ellipse has a minor/major ratio of 0.405, which is a 66 deg view angle. The table normal predicts 65 deg at the cup.

## Clock
- Ball centroids come from background difference against a median of frames 28-48. The x and s renders agree to within 0.5 px. The o render track is unusable (the person moves behind the table).
- Image steps in y (px), frames 9->16: 3.9, 4.7, **19.8-20.5**, 11.3, 13.6, 16.0, 19.1.
- The 11->12 step is a double capture step, so capture n = k + (k>=12). This is the same pattern as 0028 (drops after video 11 and 35).
- Hence **t = 0.6 s = capture 15 = video 14**, and video 15 = t = 0.64.
- **Second route, the stated prior.** The forward second difference of the 3D track is:
  - at video 14: 4.49-4.55 m/s^2 on the plane route and 4.51-4.57 on the anchor-line route (f = 711). The stated value is 4.6.
  - at video 13: 3.75.
  - at video 15: would include the run-off at frame 17 (px second difference 7-9), so it is not ~4.6.
  - The alignment is therefore confirmed.
- Background-pixel energy is too weak to see the drop (only a small bump at 11->12).

## Motion rows

### v at 0.6 s (2240 / 2251 / 2262; current 118.39 / 125.60 / 125.14)
- **Route 1, board plane** (`motion.py`):
  - Ball centre on the plane offset by r; the clicked point is the front surface, (|C| - r) along the ray.
  - Label-style forward difference video 14->15 x 25 = **110.4-112.1 cm/s** for far, near or mid anchor and r = 3.0-3.5 cm.
  - Centre steps (cm), video 12->16: 3.38, 3.88, 4.49, 5.22.
  - Model surface range at video 14 is 1.70-1.72 against the stated 1.7288.
- **Route 2, stated depths only** (`route2.py`):
  - P14 = back-projection at 1.7288; motion along the stated top->bottom anchor line, fitted to the centroids (residual <= 1.2 px).
  - v = **109.0** at f = 711 (105-114 for f = 740-680); a = 4.5.
- **Monte Carlo** (`mc.py`):
  - Noise: click sigma 1-2 px; ToF sigma 0.5-2 cm on the unknown video 15-16 ranges; the stated-vs-model offset of 1.1-2.7 cm is carried as a bias.
  - Unconditional median 113-118.
  - Conditional on the label acceleration being ~4.6: 117-122 (vector second difference) or 111-117 (speed difference).
- Physical: central difference 104.6; forward 110.7. Rolling on a 31 deg board gives 5/7 g sin(theta) = 3.6 m/s^2; the measured acceleration is 3.1-4.6, rising along the board.
- **Verdict: leave.**
  - Current values are 3-13% above the label posterior of 111-122, so the 25% bar is not met.
  - Round 1's 118.39 for o is the best placed. Unifying s/x to it would be at most a few-percent gain, not a qualifying fix.

### Displacement 0-0.6 s (2243 / 2254 / 2265; current 16.21 / 16.60 / 16.22)
- Label-style: clicked centre at video 0 at 1.818 and video 14 at 1.7288.
  - Centre at f0 from the bg-difference centroid (544.4, 296.7) gives 16.6-16.8.
  - Centre from the visual click (543.7, 295.0) gives 17.1-17.2.
- Lateral 58 px is ~14.4 cm; radial -8.9 cm; together sqrt = 16.9.
- **Verdict: leave** (current is within 2-6%).

## Static rows (label scale unless noted)

| qids | question | current o / s / x | measured (routes) | verdict |
|---|---|---|---|---|
| 2233/2244/2255 | cookie diameter | 8.37 / 8.53 / 8.61 | Upright cookie, 33-36 px at 1.7355: 8.0-8.7 | ok |
| 2234/2245/2256 | ball diameter | 6.50 / 6.59 / 6.29 | Half-max bg-diff width 24-26.5 px is a lower bound (beige ball on a white board): 5.9-6.9. Round 1's 26.5-27.4 px gives 6.5-6.7. | ok |
| 2235/2246/2257 | cup height | 14.11 x3 | 3D axis from rim centre (470, 343) to base centre (479.8, 398) on the table-normal vanishing line: 15.0-15.3. Single-depth click variants: 12.9 (rim front to base front) to 16.5 (rim back to base front). | ok (-6 to -8% vs 3D) |
| 2236/2247/2258 | pen length | 14.94 x3 | Plane (PnP or VP normal), tip included: 14.7-15.3. Single depth: 15.0. Body only: 13.4-14.0. | ok |
| 2237/2248/2259 | book length | 17.26 x3 | Profile edges on the cover plane: cover 18.5 (VP normal) to 19.5 (PnP normal); with the dark outline 19.2-20.3. Metric 17.5-18.4. Same notebook in 0023: 18.9-20.2. | leave: -7..-15%, central -11%; the routes split by 5% |
| 2238/2249/2260 | book width | 10.31 / 10.93 / 11.05 | Half-max including the dark cover edge, 41-44 px: plane 10.1, single depth 9.9. Light-blue face only, 37-38 px: 9.2. Board-bottom ruler ratio: 9.7. | leave: s/x are +8-9% vs 10.1 and +19% vs 9.2; the edge definition decides |
| 2239/2250/2261 | book height | 1.46 x3 | Page block 5-6 px at a 65 deg view: 1.4-1.6 | ok |
| 2241/2252/2263 | slope length | 30.80 x3 | Stated anchors top-mid to bottom-mid: 31.2 (30.3-32.3 for f 740-680). Plane mid-to-mid: 31.9-32.2. | ok |
| 2242/2253/2264 | slope width | 24.09 / 24.0 / 25.34 | Top 92.8 px at 1.854: 24.2. Bottom 101.8 px at 1.701: 24.35. Plane: 23.7-24.0. | ok (x is +4-7%) |

## Result
**No fixes.** All 33 rows stay as they are.

Closest calls, none of which meets the bar:
- **Motion:** v(0.6) on s/x is +13% against the label-style value (needs >= 25%).
- **Static:** book width on s/x is +8-9% against the outer-edge 10.1 (needs >= 12% with two routes agreeing). The inner-face value of 9.2 would qualify, but the edge definition is the uncertainty, not the route.
- **Static:** book length is about -11% against the label scale and only -1..-6% against the metric scale.
