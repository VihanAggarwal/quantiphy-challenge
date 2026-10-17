# 0024 independent re-measure: book width (qids 2437, 2447, 2457)

I did this on my own. I did not read research/next/labaudit*/0024 notes or the r2/ folder.
Scripts and crops are in `remeasure_work/` (16 MB).
The three renders (captured_0024 / 0024s / 0024x) have the same pixel geometry, so all three qids get one value.

## Answer
**Book width ≈ 9.4 cm** (spread over routes 8.4–10.1; this is the physical value).
All three qids (2437, 2447, 2457) get the same value. Current answer 9.0 is within ~4%.

## Setup
- Pinhole camera, f = 711, cx,cy = 640,360.
- The book is a light-blue hardcover notebook. It sits static on the slope in video frames 0–18, slides from frame ~19, and rests on the table from frame ~37.
- Static medians: medA = frames 0–17 (book on the slope), medB = frames 39–48 (book on the table, board fully visible).
- Slope board corners come from sub-pixel edge-line fits on the white mask (0024x): LL (606.6,467.5), LR (708.0,492.5), HR (862.7,361.5), HL (751.1,360.1).
- Planar-rectangle solve at f = 711 gives a corner angle of **89.6°**. This supports f ≈ 711. With f = 650 the angle is 85.5°, and with f = 800 it is 95.2°.
- Board normal ≈ (-0.388,-0.877,-0.283), which is a 28.7° incline.
- Scale: low-edge midpoint range = 0.99 (depth_info slope_near). This gives a board low-edge height of 16.2 cm below the camera, which matches an independent table-rectangle fit (h ≈ 0.157–0.167).
- Cross-check of the scale: the tracked book centroid range on the slope plane is 1.085 / 1.072 at video frames 24 / 25. depth_info at t = 1.0 is 1.0685, so they agree within about 1%.

## Routes
1. **R1, 0024 book on the slope (medA).**
   - Method: fit the four top-face edge lines and back-project them onto the plane parallel to the board, offset by T = 1.5 cm.
   - Visibility check: the left and back side faces are hidden, so the left and back silhouettes are the top-face edges.
   - Results: L = 19.7 cm, W = 10.1 cm when the front edge is taken at the centre of the dark cover line. W = 9.8 when it is taken at the highlight 1 px above (x render); the s render gives 9.5–9.8.
   - The top-face corner angles are 86.5–92.6°.
   - Book thickness from the same geometry is about 1.5 cm.
2. **R2, 0023 (same book, head-on camera), book on the slope.**
   - Method: board rectangle plane (f = 711), scale h = 0.16. This reproduces depth_info slope_near: 0.953 vs 0.9555. The side edges are constrained through the board's up-slope vanishing point.
   - Results: L ≈ 19.5–20.0, W = 9.6 (dark line) or 9.2–9.3 (highlight). W/L ≈ 0.47–0.49.
   - Caveat: the same board gives an aspect of 1.37 here and 1.44 in 0024. That is ±2.5% on the foreshortened direction, so the true W for R1/R2 is roughly 9.3–9.8.
3. **R3, 0023 book resting on the table (medB).**
   - Method: grazing view; table plane from the horizon (table-side vanishing point at y_h = 349.5) with h = 0.16.
   - Results: W = 8.4 cm, T = 1.25. With y_h = 353–356 the result is 8.9–9.2. This route is very sensitive to the horizon (top face is only 15 px tall).
4. **R4, 0024 book resting on the table.** I rejected this one: the book lies rotated and may be tilted against the board's low lip, and the edges cannot be identified reliably. A naive estimate gave 8.2–8.8.

## Combination
- The slope routes are well conditioned and give 9.3–9.8.
- The table-resting route gives 8.4–9.2.
- Best estimate is 9.4 cm, uncertainty about ±0.5 cm.
- Label-style note: the label is two clicked edge points with ToF depth. The separation runs mostly along the line of sight, so ±1–2 cm of depth noise maps to roughly ±1 cm in the label. Clicks placed inside the edges would bias it low by a few mm. I made no correction.
- Confidence: medium.
