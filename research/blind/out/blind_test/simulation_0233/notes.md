# simulation_0233 (V2MC, top-down camera, 24 fps, 50 frames)
Scene: camera looking straight down; black cat walks +x on a table (table top plane), chair on floor at right.
## Scale from prior
- Cat front edge (dark head, rows 460-560) tracked per frame: linear fit 13.40 px/frame (frames 0-44, very steady) = 321.6 px/s.
- m_head = 0.714/321.6 = 0.002220 m/px (plane of the cat's head, ~0.2 m above table).
## Cat length (758)
- Tail tip to nose (background-subtraction blob, frames 22-48): 325-347 px, mean ~335 px -> 335*0.00223 = 0.75 m. Confidence: medium-high.
## Perspective / floor scale
- Table legs (feet visible beyond table edge, equal-inset assumption): Z_table/Z_floor = 0.868, 0.859 -> 0.863.
- Chair rear-left leg: floor end x=1537 vs seat edge 1585 -> Z_seat/Z_floor = 0.928.
- Backrest (assumed centred over seat): Z_backbottom/Z_seat 0.964, Z_backtop/Z_seat 0.933.
- Cat head height ~0.038 Z_floor (plausible-height assumption, small term).
- m_floor = m_head/(0.863-0.038) = 0.00269 m/px.
## Chair (759 width = side-to-side X, 760 length = front-back Y)
- X extent in floor-px units: 570..760 (backrest overhang) or 577..750 (legs/seat) -> 183-190 -> 0.49-0.51 m -> 0.50.
- Y extent: backrest rear top (y~497 at back-top plane) -37 to front foot/seat front +160..168 -> 197-205 -> 0.53-0.55 m -> 0.545.
- Confidence: medium (depends on table-height ratio from legs, +-4%; width/length naming ambiguity ~8%).
