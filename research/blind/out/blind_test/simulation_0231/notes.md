# simulation_0231 (classroom, cat on teacher's desk, paper airplane) - prior: cat speed 0.714 m/s

## Camera
- Static camera, facing wall frontally. Principal point (960,541): horizon from linear fit of ceiling-tile spacing vs row (zero at y=541); cx=960 from ceiling-line convergence.
- f ~1880 px (HFOV ~54 deg) from square-tile assumption: X spacing/row slope gives s/H'=0.311; depth spacing of horizontal tile lines (y=9,52,89, wall at 171.5, 3 tiles further) gives s/(fH')=1.66e-4.

## Scale
- Cat: bg subtraction (composite bg from frames 0 and 49); centroid/front-edge pixel speed 9.0 px/frame = 216 px/s -> s_cat = 0.003306 m/px (Zc ~6.21 m with f=1880).
- Depth ratios via ground/table planes (y - 541 = f*height/Z): wall-floor line y=952 (411), table top front edge y=763 (223), front leg floor ~1027 (486) -> table height/cam height = 0.54; cat paws y~740 (199) -> Zw/Zc = 1.052, Zf/Zc = 0.89.
- Wall scale 0.003477 m/px; table-front scale 0.00294; chair-back (legs at y=992) 0.00317.
- Sanity: camera height 1.43 m, table height 0.77 m, desk depth 0.8 m, ceiling 2.71 m, tile 0.40 m.

## Answers
- 736 chalkboard height 438.5 px -> 1.52 m (medium)
- 746 chalkboard length 1368 px -> 4.73 m (medium)
- 747 clock diameter 111 px -> 0.383 m (medium)
- 739 ceiling height: floor line 952 to ceiling line 171.5 = 780.5 px on wall -> 2.71 m (medium)
- 738 teacher's table length: front top edge x 72-775 = 703 px at front depth -> 2.07 m (medium)
- 737 orange chair width: back panel 1600-1752 = 152 px at back-leg depth -> 0.48 m (medium-low)
- 744/745 cat length/height incl. tail: ~187 x 143 px at cat scale -> 0.615 / 0.47 m (medium)
- 740/742 airplane speed at 1.0/1.25 s: 5.55 / 4.85 m/s; 741/743 deceleration magnitude ~2.6 / 2.8 m/s^2.
  The airplane depth is unknown (no shadow or occlusion cue), so it is ASSUMED to fly in the cat's plane (2D video convention). If it flies closer to the camera, all four values are too high. (low confidence)
