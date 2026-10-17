# 0037 glass-jar height: independent re-measure (second measurer)

qids 2683 (captured_0037), 2689 (0037s), 2695 (0037x). All three are the same capture with only the background
replaced (I checked pixel profiles: the jar edges agree to within 0.3 px between the a and x medians), so the labels are shared.
Static object, so the label-style and physical values are the same thing. I treat the size label as a physical size.

Scripts and crops are in m2/: table_fit.py, pose.py, cyl.py, ranges.py, card.py, ball.py.

## Route 1: camera pose from the table, then fit a vertical cylinder to the jar silhouette
- I took the median of the 49 frames of the x render (black background). The table-top edges are fitted as lines
  (residual std 0.3-0.7 px). Corners: FL (209.9,535.3), FR (1141.4,586.8), BR (917.6,467.9), BL (453.3,446.4).
- I solved PnP for a 76.0 x 60.3 cm rectangle (front edge = 76 cm). The rectangle fits best at f ~725-735
  (max reprojection error 0.9 px). It fits at f=711 with 2.8 px. The 76/60.3 aspect is recovered at f~725, which agrees with f~711.
- Jar silhouette, in pixels: x 443.5-498.8, top 407.8 (the far edge of the lid top), front-bottom 485.5 (+-1).
- Fitting a vertical cylinder on the table plane (4 unknowns, 4 measurements) gives:
  - f=711: D=6.63 cm, H=9.07 cm
  - f=725: H=9.01
  - f=735: H=8.97
  - f=740: H=8.95
  Moving the bottom by +-1 px changes H by +-0.06 cm.

## Checks on the metric scale
- Credit card (85.6 mm) back-projected onto the table plane: the long edges measure 85.2/84.5 mm (inner contour)
  and 86.0/85.5 mm (outer contour) at f=711. They measure 85.1-85.9 mm at f=740. So the table scale holds.
- Table-pose ranges compared with the ToF depth_info for opaque objects at f=711: card 1.036, cup 1.011, tape 1.033.
  At f=740 the same ratios are 0.998, 0.977 and 1.008, so the ToF ranges agree best at f~735.
  The ping-pong ball's vertical half-max diameter at frame 24 is 27.9 px at 1.055 m, which gives f~735.
- Jar: the geometric range to its front surface is 0.907-0.93 m, but its ToF reading is 1.008 m. ToF is reading through the glass,
  so I do not use the jar's own depth_info as its range.

## Route 2: ToF scale taken from the opaque tape next to the jar
- Using the table geometry, the jar front is at 0.903 x the tape-front range. Multiplying by the tape ToF (1.038) puts the jar at 0.937 m.
  Rescaling route 1 to that range gives H = 9.02 (f=740) and 9.37 (f=711).
  The f=711 value comes from the 3% ToF/geometry mismatch at that f, and the card and table data do not support that mismatch.

## Value
H = 9.0 cm (range 8.95-9.1) for qids 2683, 2689 and 2695. The jar's diameter is about 6.6 cm.
If a label were built from ToF clicks on the glass (reading through the glass at 1.008 m), the lid-front edge to bottom
would give 10.0 cm and the silhouette top to bottom would give 10.5 cm. I consider that unlikely for a size label.
