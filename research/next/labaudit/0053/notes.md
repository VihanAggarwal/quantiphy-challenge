# Lab audit, family 0053 (captured_0053 / 0053s / 0053x): 24 rows, 8 questions x 3 renders

## Scene
- One event, three renders: o is the original, s has a colour background, x has a green-screen background with SAM masks.
- The camera is high and looks down at the carpet: pitch about 35-37 deg, roll about -9 deg.
- 0062 uses the same camera pose. A phase correlation of the background against 0062 gives a shift under 0.1 px.
- Static objects:
  - Book: flat paperback near the camera, (666,618), depth 2.082.
  - White cup: a white tumbler with a lid, (564,424), depth 2.516.
  - Basketball: (986,370), depth 2.925.
- Moving object: the blue recycle bin, lying on its side.
  - It slides up and to the left at about 1 m/s.
  - Its orientation stays constant: the same faces and markings are visible in every frame (bin_sheet.png).
- Timing: 48 frames at 24 fps, made from a 25 fps capture.
  - The bin track double-steps at n11->12 and n35->36, the same drop pattern as 0054.
  - So 0.4 s = n10 and 1.4 s = n34.

## Camera model (important, and it disagrees with the default camera knowledge)
I tested several floor and camera models with independent cues (scripts/jointfit.py, jointfit2.py, wb62b.py, wbfit.py, ftest.py):
- Visual verticals: four right-wall panel seams give a vertical VP at (453,1379). The cup axis tilt and the cabinet edge confirm a roll of about -9 to -10 deg.
- Floor horizon: the carpet-streak VP (2195,121) and the wall-floor junction VP (219,-241). They give a horizon tilted 10.4 deg.
- Rigid rectangle on the floor: the 0062 whiteboard (same camera) at frames 40 and 48.
  - It must rectify to 90 deg corners with the same size at both positions.
  - The whiteboard alone gives roll -8.5 deg.
  - It excludes the "roll 0" plane that the ranges seem to prefer (73-105 deg corners under that plane).
- Depth points: book, cup, ball (centre at R=11.6 cm), 0062 whiteboard and 0062 bag, all at known heights above the floor.
- Basketball apparent size: 67.7 x 59.4 px (o render, edges), diameter 23.2 cm.

Result:
- Taking depth_info as Euclidean range does not fit, at any f. Joint cost is at least 70.
  - The ball would float 18-31 cm above the floor.
  - The 0062 whiteboard would sink 8-12 cm below it.
- Taking depth_info as z-depth (along the optical axis) with f about 770-790 fits every cue.
  - Joint cost 5.5 for f 780, pitch 37, roll -9, camera height H 1.805.
  - Residual heights: book 1.8, cup 9.7, ball 11.9, whiteboard -1.7, bag 2.2 cm.
  - The predicted vertical VP (478,1382) matches the seams.
  - The ball size matches 23.2 cm.
- f=711 with z-depth fits the depths but misses the ball size by 9% and the VPs by about 5 deg (cost 18-33).

So this floor camera looks like f about 780 with z-depth. It may be a different setup from the table-top clips that gave 711. I computed every row under four models:
- M1: f 711, range, VP normal (the default knowledge).
- M2: f 780, z-depth, fitted normal (best).
- M3: f 711, z-depth.
- M4: f 760, z-depth.

I propose a fix only when it holds under M1 and M2 both (answers_out.txt, disp_routes_out.txt).

## Rows
| row | current o / s / x | M2 (best) | M1 (f711 range) | verdict |
|---|---|---|---|---|
| book width | 11.68 / 10.97 / 12.99 | 11.6 (10.5-12.4 by outline) | 12.2 (11.0-13.0) | fine. x is +12% at most. No fix. |
| book length | 19.98 / 18.51 / 19.81 | 20.2 (19.4-21.2) | 20.9 (19.9-21.7) | fine |
| cup rim diameter | 7.90 / 7.22 / 7.22 | **8.4** | 9.1 | **fix s, x to 8.4**. o (+6%) stays. |
| basketball diameter | 23.2 fact | 23.2 (ball size fits M2) | | fine |
| trashbin height | 37.7 / 43.3 / 43.3 | 34-41 | 38-45 | no robust fix (see below) |
| cup-basketball distance | 1.512 / 1.507 / 1.509 | 1.60 | 1.56 | fine (-3 to -6%) |
| cup-book distance | 0.727 / 0.724 / 0.727 | 0.721 | 0.798 | fine |
| bin displacement 0.4-1.4 s | 0.826 / 0.822 / 0.752 | **0.91-0.93** | 0.96 | **fix x to 0.92**. o and s are +11-13% only, so they stay. |

### Cup rim (2817, 2825: 7.22 -> 8.4)
- Width of the widest chord of the lid ellipse:
  - o render, gradient edges at rows 410-414: 26.4-26.9 px.
  - s render: 25.7 px.
  - x mask: 26-27.5 px.
  - I use 26.0 +- 0.7 px.
- Route 1 (M2): 26.0 x z_rim 2.528 / 780 = 8.43 cm.
- Route 2: ratio to the 23.2 cm basketball. This route does not depend on f.
  - Ball on-axis-equivalent size: 54.3 px at 3.316 m.
  - Result: 8.34 cm with z-depth, 9.25 with range.
- Under M1 route 1 gives 9.1.
- Why the current value is wrong: s and x come from agent clicks 22.5 px apart at row 409. That is the narrow upper part of the lid ellipse, not the 26 px major axis. A 0.907 scale was then applied. o used 24 px and gives 7.9; it is within 6% of 8.4, so it stays.
- 8.4 is the low end of the two models. If the labeller clicked about 1 px inside each edge, the label is about 8.0. The fix is still better than 7.22 in every scenario I tried.

### Bin displacement 0.4->1.4 s (2830: 0.752 -> 0.92)
- The bin recedes: its apparent size shrinks by 1/1.15 (sqrt area, bbox w and h at n9-11 vs n33-35), and it moves toward the horizon.
- The current values are the "same depth" artefact: both ends back-projected with the 0.4 s depth of 2.73.
  - Under M2 that gives exactly 0.752, which is x.
  - Under M1 and M3 it gives 0.81-0.825, which is o and s.
- Routes under M2:
  - Floor plane, click point kept at its 0.4 s height (z-depth at n34 = 3.17): 0.909.
  - Apparent-size ratio corrected for off-axis position: 0.879-0.912.
  - Scaled to the stated prior of 0.9962 m/s at 0.4 s (forward difference or local fit; robust across all four models, 0.897-0.954): 0.897-0.928.
  - Floor-level white tab under the bin: 0.965.
- Median under M2 is 0.91. M4 gives 0.93, M1 0.96.
- M2 reproduces the prior speed (0.976 vs 0.9962).
- Decision:
  - Fix x to 0.92: +22% (+21-27% across models).
  - o and s at 0.82 are about 11-13% low under M2 and 16% low under M1. They are below the 15% bar, so they are left alone. Setting them to 0.92 as well is +EV and optional.
- This is a displacement between two positions of a sliding bin. It is not a ball speed or path, and it carries no label-noise correction (its provenance is the static rule).

### Trashbin height (no fix)
- 0062 upright bin (same camera, n34), bottom-front edge on the floor to the top rim:
  - M2: 34.5-36.3 cm.
  - M1: 37.6-39.5 cm.
- 0053 lying bin, box fitted to the silhouette at n34 and n40:
  - M2: near-bottom edge 40-41 cm (motion blur runs along this edge, so about 39), depth edge 33-35, lying height 18-19.
  - M1: 44-46 / 42-43 / 20-21.
- I cannot tell which edge is the axis.
- Possible labels: 34-41 (M2) or 38-45 (M1).
- 43.3 is high only under M2, and 37.7 is fine under both. No robust fix.

## Other observations (not this family)
- 0062 depth names look shuffled:
  - "white_box 2.082" sits at the mario-toy position (floor model 2.08).
  - "trashbin 2.303" fits the white box (2.26-2.34).
  - The real 0062 trashbin is about 4.0-4.2 m away.
  - The 0062 bin-height label may be odd.
- Range vs z-depth and f about 780 may hold for the other floor clips from this camera (0052? 0062). Worth checking before the depth-based floor rows elsewhere are trusted.

## Files
- scripts/: extract.py (frames; rerun it to regenerate the frames/ PNGs, which were deleted to save disk), geo.py, models.py, masks.py, bintrack.py, binsize.py, binbox.py, bin62h.py, jointfit*.py, wb62b.py, wbfit.py, cup*.py, ball.py, booktop.py, answers.py, disp_routes.py
- Crops: crop_cup_*.png, crop_book_*.png, crop_bin*.png, bin_sheet.png, bin_o*_grid.png, binx_*.png, bin62_x.png, vlines2.png
