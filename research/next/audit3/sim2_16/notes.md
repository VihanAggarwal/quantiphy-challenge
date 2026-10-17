# Audit sim2_16: families 0095/0096/0097, 0124 (+segmented), 0191 (+segmented)

44 rows were checked, all of them scored. **No fixes are proposed.** No row's quick check differs from the current answer by 15% or more.
Family 0191 has a systematic size bias of about 10-12%, which is below the fix threshold. It is documented in section 3.

Scripts are in `scripts/`:
- `fam1.py` and `fit1.py`: car/plane blob tracks and quadratic fits.
- `seg124.py` and `front124.py`: 0124 car tracks and the front-anchored centre at the start of the clip.
- `box191.py` and `acc191.py`: box tracks and the accelerations of the front-face texture and the box edges.
- `grab.py`: crops.

PNGs here are the crops that were viewed.

## 1. Family 0095 / 0096 / 0097 (plane and car side view, prior: car acceleration 10 m/s^2)

The scale comes from a quadratic fit of the car blob (bounding-box centroid and edges, frames 2..end):

| clip | a (px/s^2), mine | a (px/s^2), agent | m/px |
|---|---|---|---|
| 0095 | 290.6-292.2 | 291 | 0.0344 |
| 0096 | 200.8-201.6 | 200.6-202 | 0.0497 |
| 0097 | 212.6-212.9 | 213.4 | 0.0470 |

The fits have rms of about 0.1 px, and the parabola vertex is at about -0.04 s in all three clips.

The values are consistent across the family. In all three clips the plane and the car match an A320 (37.57 m) and a Cybertruck (5.68 m) at one scale, so they share a depth.

| qid | clip | quantity | current | quick check | diff |
|---|---|---|---|---|---|
| 164 | 0095 | plane v(0.5 s) | 60.22 | 73.0 px/f, so 60.1-60.2 | <1% |
| 165 | 0095 | car length | 5.67 | 164.5 px (centre of image, AA removed), so 5.65 | <1% |
| 166 | 0095 | car height | 1.849 | 54 px, so 1.85 | <1% |
| 167 | 0095 | plane length | 37.8 | 1095-1100 px, so 37.6-37.8 | <1% |
| 168 | 0095 | plane height | 11.16 | 326.5 px, so 11.2 | <1% |
| 169 | 0096 | plane v(0.3 s) | 60.2 | 50.5 px/f, so 60.2-60.3 | <1% |
| 170 | 0096 | car length | 5.67 | 114 px, so 5.67 | 0% |
| 171 | 0096 | car height | 1.84 | 37.5 px, so 1.86 | 1% |
| 172 | 0096 | plane length | 37.75 | 756-760 px, so 37.6-37.8 | <1% |
| 173 | 0096 | plane height | 11.28 | 226.5 px, so 11.26 | <1% |
| 174 | 0097 | plane v(0.3 s) | 60.05 | 53.4 px/f, so 60.2 | <1% |
| 175 | 0097 | car length | 5.647 | 120.5 px, so 5.66 | <1% |
| 176 | 0097 | car height | 1.851 | 40 px, so 1.88 | 1.5% |
| 177 | 0097 | plane length | 37.58 | 795-800 px, so 37.4-37.6 | <1% |
| 178 | 0097 | plane height | 11.13 | 238 px, so 11.18 | <1% |

No issues.

## 2. Family 0124 / 0124_segmented (top-down cars, prior: black car speed 26.085 m/s)

The segmented clip gave clean masks for an independent track.
- Red path speed: 22.27 px/frame, constant.
- Black path speed: 27.12 px/frame. The agent used 26.9.
- k = 26.085/(27.12*24) = 0.04008 m/px. The agent used 0.0404, a difference of 0.8%.

| qid | quantity | current | quick check | diff |
|---|---|---|---|---|
| 271 | red speed at 1.0 s | 21.547 | ratio 22.27/27.12 x 26.085 = 21.42 | 0.6% |
| 1838 | red average speed (segmented) | 21.48 | 21.42 | 0.3% |
| 272 / 1839 | red length | 4.909 | minAreaRect 125.5 minus AA = 124 px, so 4.97 | 1.3% |
| 273 / 1840 | red width | 1.99 | about 50 px including mirrors, so 2.00 | <1% |
| 274 / 1841 | black length | 4.586 | 113.5 px, so 4.55 | <1% |
| 275 / 1842 | black width | 1.97 | 47.5 px, so 1.90 | 3.5% |
| 276 / 1843 | distance at 1 s (centre to centre) | 4.283 / 4.23 | frame 24: 105.0 px, so 4.21; frame 25: 106.5 px, so 4.27 | <2% |
| 277 / 1844 | smallest distance | 3.6 / 3.52 | frame 1 (= frame 0) with front-anchored centres: 87.5 px, so 3.51-3.53 | 0-2.5% |

Notes:
- Extrapolating the trajectories backwards with a polynomial gave 69-79 px at frame 1, which is unreliable. The front-anchored method has a 0.5-1.8 px bias, checked on frames 5-11, and confirms the agent's masked-NCC value of 89 px to within 2%.
- In the segmented twin, "horizontal distance" must mean ground-plane distance. The image-x difference at 1 s is only about 2 px and changes sign, so a "smallest" image-x distance would be about 0.

No issues.

## 3. Family 0191 / 0191_segmented (box falls onto the truck roof, prior: box acceleration 9.8 m/s^2)

### Quick-check route

I fitted the box's far-bottom silhouette edge with sub-pixel coverage, over frames 0-57 of the segmented clip. This gives a = 1768-1778 px/s^2, so s = 180.9 px/m. The agent got 1760 px/s^2 and 179.6 px/m. At this scale every current answer is reproduced to within about 1%.

### Perspective finding (in-depth)

The camera is a pinhole close to box level, so the box's bottom face is visible as a trapezoid.
- The near-bottom-left corner is at x = 530. The far-bottom-left corner is at about x = 572, a constant 42 px shift in every frame.
- The vertical extent of the bottom face shrinks linearly as the box falls: 36, 34, 26 and 14 px at frames 0, 20, 40 and 58. That fits horizon y_h of about 532 and 1 - Z1/Z2 of about 0.095, so Z2/Z1 = 1.105 (front face to far face).
- The same constant also explains the 42 px x-shift with c_x of about 970.

I checked this independently with accelerations:
- Template tracking of the front-face texture gives a = 1965-1978 px/s^2 (rms 0.07 px, release at t = 0.000 +/- 0.003 s).
- The far-bottom edge gives 1773 px/s^2.
- Their ratio is 1.112, which matches the geometric ratio of 1.105.

Consequences:
- The agent's scale (179.6 px/m) belongs to the box's far-bottom edge.
- The front-face scale is s1 = 201 px/m. The box-centre scale is about 190.5 px/m.
- The box width and height are front-face pixel extents, so they should use s1:
  - Width: 408 px / 201 = 2.03 m. Current 2.27 is 11.8% higher.
  - Height: 189.5 px without the open flap gives 0.94 m. 206 px with the flap gives 1.02 m. Current 1.09 is 6-16% higher.
- The truck near side must be at or in front of the box centre, otherwise the box would not rest on the roof. Its scale is therefore between 190.5 and about 210 px/m (210 assumes a centred box, a 2.5 m truck body and Blender's default f = 2667 px).
  - Truck length is 1718 px, so 8.2-9.0 m. Current 9.57 is 6-17% higher.
  - Truck height is 714 px, so 3.40-3.75 m. Current 3.98.
  - Tire is 160-165 px, so 0.77-0.87 m. Current 0.92.
- The landing occlusion (the box bottom about 2 px above the truck top edge) did not pin down the truck depth further.

| qid | quantity | current | quick (far-edge scale 180.9) | front-face scale 201 | note |
|---|---|---|---|---|---|
| 466 / 1913 | box width | 2.27 | 2.26 | 2.03 | -11.8%, below threshold |
| 467 / 1914 | box height | 1.09 | 1.05-1.14 | 0.94-1.02 | -6% to -16%, depends on the flap |
| 468 / 1915 | truck length | 9.57 | 9.50 | 8.54 (range 8.2-9.0) | -6% to -17% |
| 469 / 1916 | truck height | 3.98 | 3.95 | 3.55 (range 3.4-3.75) | same |
| 470 / 1917 | tire diameter | 0.92 | 0.88-0.91 | 0.80-0.82 | same |
| 471 / 1918 | box v(0.2 s) | 1.92 | 9.8 x (0.2 - 1/240) = 1.92 (1.94 if release is at -0.002 s) | n/a, scale-free | ok |
| 472 / 1919 | box v(0.4 s) | 3.88 | 3.88-3.90 | n/a | ok |

**Verdict for 0191:** the size rows are probably about 10-12% too large because the far-edge scale was used. The difference is below the 15% fix threshold, and the truck's depth is not pinned down to 8%, so no fix is proposed. If a family-wide rescale is ever wanted, the best single estimate is to multiply all ten 0191 size rows by 0.89 (s = 201 px/m). The speed rows are fine.

## Fixes

None.
