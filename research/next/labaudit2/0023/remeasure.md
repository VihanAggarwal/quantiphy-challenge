# 0023 independent re-measure: book width (qids 2410, 2419, 2428)

All three renders (captured_0023, 0023s, 0023x) show the same event and the same pixels for the book, so they share one value.
No stated size prior for this book exists in the test 'prior' column. The light-blue notebooks in 0013/0014 are a different,
smaller notebook (about 13-14 cm long), so I did not transfer anything from them.

Camera: f=711, c=(640,360). Scale anchor: ToF slope-near range 0.9555 m at the board bottom edge (590,481.5).
Cross-check of the anchor: the table front edge comes out 60.9 cm (known 60.3). A PnP of the board with W=24.2 cm
gives L=32.4 cm, and the predicted ranges (0.951 / 1.217) match the ToF values (0.9555 / 1.201).

## Route A: book at rest on the slope (frames 0-20 averaged)
- Board plane comes from the vanishing point of its side edges: (602, -60), sd 3 px over 6 fits (3 renders x 2 phases, rows 380-436).
  The plane is about 30.5 deg to the optical axis.
- Subpixel cover edges per column (x 548-644): back edge 349.5-350.4 and front edge (cover-to-shadow) 378.4-379.3,
  so the cover is about 29.0-29.4 px tall.
- I back-projected onto the cover plane (board plane offset by thickness 1.46 cm).
  - w = 9.33 / 9.48 / 9.34 cm (x / raw / s render).
  - Spread from VP ±10 px, near or far anchor, and t 1.3-1.7: 9.0-9.7.
  - f = 650 / 780 gives +2.4% / -2.2%.
- The book's back edge lands within 0.2 cm of the board's top edge, which is a sanity check. In the loaded phase the top
  corners look 4.5 px lower, most likely hidden by hands; the plane below row 380 is identical in both phases.

## Route B: book at rest on the table (frames 38-48 averaged)
- Table horizon comes from the vanishing point of the table side edges: y_h = 349.4 ± 1 (4 fits).
- Cover back edge 477-483 and front edge 492-498, so the cover is 14.7-14.9 px. The front face is 15-16 px.
- Per-column 3D distance on the cover plane: 8.85 / 8.98 / 9.03 cm.
  - The book is yawed about 8.5 deg (from its end points), which changes the result by less than 0.3%.
  - Spread from horizon ±2 px, roll, and board-ToF vs table-width anchor: 8.6-9.1.
- The back edge sits against the white board, where contrast is low, so this route has the larger edge uncertainty
  (±1 px is about ±6%).

## Sanity checks
- Book length from the same geometry: 19.6-20.0 cm (slope) and 20.2 cm (table).
- The book is yawed about 8.5 deg on the table.

## Result
- Width = 9.2 cm (mean of route A 9.39 and route B 8.95).
- Routes disagree by 5%. Estimated uncertainty about ±4%.
- This is a size question, so the physical value is the label-style value.
- Scripts are in scripts/: edges_book.py, width_geom2.py, vp_refit.py, table_vp.py, length_check.py.
