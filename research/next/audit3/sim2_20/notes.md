# Audit sim2_20 (0092/0093 car+plane, 0116(+seg) football+doors, 0190(+seg) / 0192(+seg) truck+box)

Inputs: the audit json, the agent notes it lists (0092, 0093, 0116, 0190, 0192; the *_segmented notes files do not exist), and the frames.
Scripts in this folder: grab.py (crops), carplane.py, ball.py, track190.py, track192.py. Small track txt files are kept; the PNGs are crops I viewed.

## Family structure found
- 0092/0093: the same Cybertruck (prior 5.67 m) and A320. Car px 128.0 / 90.6, plane/car px ratio 6.68 / 6.67 in both, constant speeds. Consistent.
- 0116 / 0116_seg: the same clip. The seg mask shows the two "doors" (middle and bottom), each including the transom. They are identical, 160.5 px x 340-361 px.
- **0190 and 0192 are the same scene** (the json lists them as separate families). Same truck (body 567.5 px wide in both), same box
  (281.7 vs 280.8-281.0 px wide, so the same depth), with the camera translated vertically. Between 0192 (rest, f150) and 0190 f0:
  the wall shifts 49 px, the floor patches shift 94-128 px (nearer floor shifts more, so this is a translation, not a pitch or lens shift),
  the truck rear-face texture shifts 195.0 px, and the box-face texture shifts 160.7 px. Verticals are exactly vertical in both clips (pitch 0),
  and the horizon is y~540 (floor parallax gives 532+-13; the bottom-face perspective of the falling box in 0192 gives ~540-550).

## Quick check of every scored row (independent route on the frames)
| qid | clip | quantity | current | quick check | route | verdict |
|---|---|---|---|---|---|---|
| 150 | 0092 | car height | 1.85 | 1.84 | half-max car 41.5/128.0 px x 5.67 | ok |
| 151 | 0092 | plane length | 38.2 | 37.9 | 855/128.0 px | ok |
| 152 | 0092 | plane height | 11.3 | 11.26 | 254.3 px | ok |
| 153 | 0092 | plane speed 1.0s | 61.0 | 60.6 | nose 57.0 px/f | ok |
| 154 | 0092 | car speed 1.0s | 30.0 | 30.3 | 28.48 px/f | ok |
| 155 | 0093 | car height | 1.818 | 1.81 | 29.0/90.6 px | ok |
| 156 | 0093 | plane length | 38.0 | 37.8 | 604.8-607 px | ok |
| 157 | 0093 | plane height | 11.27 | 11.28 | 180.3 px | ok |
| 158 | 0093 | plane speed 0.5s | 60.73 | 60.65 | 40.4 px/f | ok |
| 159 | 0093 | car speed 1.0s | 30.0 | 30.2 | 20.12 px/f | ok |
| 236/1824 | 0116(+seg) | football length | 0.337 | 0.32 | seg ball h ~59 px (f19-25) x 9.8/a, a=1800-1836 px/s2 | ok (-5%) |
| 237/1825 | 0116(+seg) | football width | 0.184 | 0.19-0.20 | 37.4 px raw; the off-axis correction depends on f | ok (<=10%) |
| 238 | 0116 | middle door height | 2.031 | 1.87-2.05 | seg door 341-361 px (bottom hidden by a rail at 1716-1736) x 0.00542 x depth 1.01-1.05 | ok |
| 239 | 0116 | middle door width | 0.902 | 0.88-0.91 | 160.5 px | ok |
| 240/1828 | 0116(+seg) | football speed 0.5s | 4.696 | 4.68-4.70 | release at t=0; 9.8*11.5/24 | ok |
| 1826 | 0116_seg | each door height | 1.853 | 1.87-2.05 | same door as 238 | ok (inconsistent with 238 by 9.6%; both in range) |
| 1827 | 0116_seg | each door width | 0.869 | 0.88-0.91 | same | ok |
| 461/1908 | 0190(+seg) | truck height t=0 | 3.32 | 3.05-3.34 | floor parallax Hc192/dc=4.0 with body height equal in both clips; s_t 242-258 px/m | ok |
| **462/1909** | 0190(+seg) | truck width | **2.68** | **2.21-2.35** | see below | **FIX -> 2.28** |
| 463/1910 | 0190(+seg) | box height | 0.90 | 0.95-0.98 | front face 198-202 px (0192 fall and rest) / 211.8 + flap ~0.03 | 7% low, below the 15% bar, no fix (family value 0.975) |
| 464/1911 | 0190(+seg) | box speed 1s | 0.094 / 0.0866 | 0.085-0.090 | box face texture and top-edge tracks, 211.8 px/m | ok |
| 465/1912 | 0190(+seg) | box speed 2s | 0.118 | 0.117 | same | ok |
| 473/1920 | 0192(+seg) | box height | 0.975 | 0.95-0.98 | as 463 | ok |
| 474/1921 | 0192(+seg) | truck width | 2.45 | 2.21-2.35 | as 462 | 4-11% high, no fix (see note) |
| 475/1922 | 0192(+seg) | box width | 1.33 / 1.34 | 1.33 | sibling prior; gravity scale gives 1.31-1.37 | ok |
| 476/1923 | 0192(+seg) | box speed 0.2s | 1.86 | 1.86-1.91 | g*(T-1/240-t0), t0 0.001-0.006 s from the fit | ok |
| 477/1924 | 0192(+seg) | box speed 0.4s | 3.83 | 3.82-3.88 | same | ok |

## In-depth: truck width (0190 rows 462/1909)
The 0190 agent assumed the box front face is flush with the truck rear and used the box scale (211.7 px/m) for the truck: 567/211.7 = 2.68.
That assumption is excluded by the sibling clip:
- In 0192 the box's front face is fully visible: 198-202 px tall during the free fall and at rest, at the same px width (281 px, so the same depth).
- In 0190 only 172.7 px of it are visible above the roof rim (box top 166.0, rim 338.7). With a pitch-0 camera (horizon y~540),
  ~27-30 px of the face are hidden behind the rim. That is possible only if the box front is farther from the camera than the truck rear.
  If the box were flush, its bottom would be at the rim line and the whole face would show.
- Route 1 (inter-clip parallax, no horizon needed): the truck rear and the box ride together; the camera translates by the same amount for both.
  truck shift 195.0 / box shift 160.7 = Z_box/Z_truck = 1.213 (the top-edge shift of 156.5 gives 1.246).
  s_t = 1.213 x 211.8 = 256.9 px/m, so width = 567.5/256.9 = **2.21 m** (2.15 with the edge shift). This assumes the box rests
  on the same supports in both clips. 0192 shows the box sitting 4.8 cm above the rim, with a visible 7 px white gap.
- Route 2 (single clip 0190, occlusion/horizon geometry): s_t*(Hr-Hc) = 540-338.7, and s_b*(Hr+clearance-Hc) = 540-363.8, where 363.8 is
  the box front-bottom edge (0192 rest 524.5, shifted by the box shift). With clearance 0 (the box directly on the rim plane) the ratio is 1.142,
  giving **2.35 m**; with the 0192 clearance of 4.8 cm it gives 2.20 m. A horizon anywhere in 532-548 changes this by <1%.
- The routes agree within 6% (2.21 vs 2.35). The current 2.68 is 14-21% above them (+17.5% vs the midpoint 2.28).
  Proposed 2.28 is within 3-4% of either end.
- 0192 rows 474/1921 (2.45; that agent "assumed" 231 px/m) are 4-11% above the range. This is below the 15% bar, so there is no fix here.
  For family consistency the reviewer may consider moving them to 2.28 as well.
- Caveat: the box's motion in 0190 does not ride the body rigidly. Ratios of truck to box px velocity are 1.26, 1.03, 1.10, 1.21 and 1.55 in successive windows,
  so that route was not used. "Truck width" is taken as the body width; mirrors or other parts wider than the body, which would be hidden from this view, are not accounted for.

## Other notes
- Box height: the family is inconsistent (0.90 in 0190, 0.975 in 0192). 0192 sees the whole box, while in 0190 the bottom ~28 px are hidden.
  The 0190 value is about 7% low, which is below the fix bar. Suggest 0.975 for consistency (optional).
- Doors in 0116: 238 (2.031) and 1826 (1.853) measure the same door object and differ by 9.6%. The door bottom is hidden by a rail, so the true
  extent is 341-361 px; both values are inside the plausible range. No fix.

## Fixes proposed
| qid | current | new | why |
|---|---|---|---|
| 462 | 2.68 | 2.28 | The flush box/truck depth assumption is wrong. The truck rear is ~14-21% nearer than the box front (two routes give 2.21-2.35). |
| 1909 | 2.68 | 2.28 | Same clip footage (segmented twin of 0190). |
