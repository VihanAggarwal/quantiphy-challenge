# sim2_08 independent remeasure: qids 885 (0257 table width) and 892 (0258 table width)

I did not read the other measurer's files in sim2_08/. Inputs I used: the input json, the agent notes for 0257 and 0258, and the videos for 0257-0260 (same scene family).

## Setup facts
- All 4 clips use the same fixed camera: the table front face spans the same pixels in every clip, and so do the AC and the window.
- Container fps is 24 for 0257/0258 and 30 for 0259/0260, but every falling object has the same per-frame
  acceleration (~6.9 px/frame^2). Each object lands at about frame 15, which is 0.5 s at 30 fps and matches "before 0.5s".
  So I used fps = 30 as the json states. At 24 fps every size would be 1.56x larger and would disagree with the sibling clips.
- The view is telephoto. The right side edge of the tabletop converges from x=1538.9 at the front-top edge (y=895.4)
  to x=1524.4 at the back edge (y=864.8). With cx=960 this gives Z_front/Z_back = 0.975 (all 4 clips: 0.9736-0.9763).
  Vertical lines converge only slightly (window edge, AC edge), which gives f ~ 23-29k px and pitch ~2 deg. The vertical/horizontal
  scale mismatch is therefore about -0.1%, which is negligible. Implied table depth is ~1 m.

## Pixel measurements
- Front face of the tabletop (wood strip, rows 899-908), half-level edge crossings: left 517.85, right 1538.5, so L_front = 1020.65 px (the same in all clips).
- Contact rows of the falling objects at rest, on the top-surface strip (back edge 864.8, front edge 895.4):
  plant 870, pen 868, red cup 872, mug 871. All objects sit near the back of the table.
  Object-centre depth fraction from the back, adding about 0.035 for the radius: plant 0.21, pen 0.11, cup 0.28, mug 0.24.
  Z_obj/Z_front = 1 + 0.0256*(1-frac).
- Falling-object pixel acceleration, from a quadratic fit to a template-matched track (route A) and from difference-blob centroid and edges (route B, noisier):
  - 0257 plant: A 6.890-6.922 (best 6.905), B 6.97-6.98
  - 0258 pen:   A 6.82-6.89 (best 6.86),   B 6.83-6.86
  - 0259 cup:   A 6.97-6.985 (best 6.978), B 6.94-7.01
  - 0260 mug:   A 6.89-7.03 (best 6.96),   B 6.95-7.03
  Scale = 9.8/(a*900) m/px.

## Table width = L_front * Z_front/Z_obj * scale * 0.999
- 0257 (plant prior): 1020.65/1.0202 = 1000.4 px * 1.5770e-3 = **1.576 m**
- 0258 (pen prior):   1020.65/1.0228 = 997.9 px * 1.5873e-3 = **1.582 m**
- Cross-checks on the siblings (same table, own priors): 0259 cup 1.562, 0260 mug 1.564. Mean of the 4 clips: 1.571.
- Without the perspective correction (front-edge pixels at the object scale): 1.609 / 1.620. That is the upper bound, and the
  current 1.62 for 892 is this uncorrected value. Using the back-edge length alone (995 px) gives 1.569 / 1.579.

## Answers
- 885: 1.576 m (high confidence; within ~2%)
- 892: 1.58 m (high confidence; within ~2%). The current 1.62 is about 2.5% high because it skips the depth correction.

Flag: the sibling answers for the same table in 0259/0260 (1.367 / 1.34, qids 900/910) are 13-15% below what my method gives
for those clips (1.562 / 1.564). The camera and table pixels are identical across clips and all four falling objects have nearly the
same pixel acceleration, so those two answers look inconsistent with the family.
