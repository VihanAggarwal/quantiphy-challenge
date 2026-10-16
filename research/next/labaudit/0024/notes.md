# Lab audit, family 0024 (captured_0024 / 0024s / 0024x): one event, one label set

Inputs: `../inputs/0024.json` (30 scored rows = 10 questions x 3 renders). Test inputs only; no labels used.
Video: 1280x720, 24 fps, 49 frames. Scene: lab table seen almost edge-on (camera ~15 cm above the table top),
white board (the slope) leaning on a stack of books, teal book resting at the top of the slope until n~18-19
(t~0.77 s), slides down, crosses the slope foot at n~31-32 and rests on the table from n~36 at (572,474).
Same board and same teal book as family 0023 (frontal camera). Camera f = 711, pp (640,360), depth = range.

Scripts (all in `scripts/`): `extract.py` (frames, montages), `crop.py`/`cropg.py` (grid crops),
`table_edges*.py` + `table_fit.py` (table edge points, 6-dof pose fit with a 60.3 x 76 top, own LM in `lsq.py`;
scipy is not installed), `geo.py` (table plane), `slope3d.py`/`slopeplane.py` (board as a rectangle: bottom edge on the
table plane, top corners on their rays with the side edges perpendicular to the bottom edge), `book_*.py`
(book on slope / on table), `route0023.py` (independent camera: 0023 slope line from its stated depths),
`track.py`/`path.py` (book track, speeds, path), `slope_stated.py`/`table_stated.py` (label emulation with stated depths).

## Geometry checks
- Table pose (x00 edge points, f 711): rms 0.57 px; left-front edge = 60.3 side, front-right = 76 side (the other
  orientation: 76 px max error). Model corner ranges L 1.068 (stated table_left 1.035), F 0.522. Camera 14.8 cm
  above the table top.
- Board from that plane: bottom edge 23.1, top edge 23.1, sides 29.8 / 30.7 (mid-to-mid 30.2), incline 32 deg.
  Same board elsewhere: 0023 stated-depth line 30.7, 0014 30.87, width 24 (0023/0014). Model scale ~0.96-1.0.
- Stated book depths vs model (teal centroid on the slope): t=1.0 1.0685 vs 1.030-1.050, t=1.2 0.977 vs 0.980.

## Row verdicts (current o / s / x -> my measurement)
| question | current | measured | verdict |
|---|---|---|---|
| velocity at 1.0 s | 76.2 / 76.9 / 76.2 | track on slope plane: fwd n24->25 57, centred 54 cm/s (accel ~1.8 m/s^2 vs stated 2.8) | ok (1.33x, label-noise inflation; under 1.5x guard) |
| velocity at 1.2 s | 85.7 / 86.4 / 85.6 | n28->29 71, n29->30 61 (book hits the foot, transition to table) | ok (<1.5x) |
| length of book | 20.5 / 20.09 / 20.5 | slope plane, top-face long edges at rest (n0-18): 20.3-20.5; 0023 frontal 20.3-21.0 | ok |
| **width of book** | **11.28 x3** | **8.75 (0024 slope plane), 9.1 (0023 stated-depth slope line), 8.2-9.1 (0024 table plane at rest)** | **wrong: -> 9.0** |
| height of book | 1.46 x3 | pages band 8-9 px on the slope (= 1.46 under the model), 10-12 px at rest on the table (1.1-1.35) | ok |
| length of slope | 30.80 / 30.61 / 31.93 | 30.2 (29.8-30.7) here, 30.7 / 30.87 same board in 0023 / 0014 | ok (see risk note) |
| width of slope | 24.0 x3 | 23.1 top and bottom edges (x1.0-1.04 scale -> 23.1-24.0) | ok |
| length of table | 74.5 x3 | 76.0 (pose fit with 76 x 60.3, rms 0.57 px) | ok |
| width of table | 59.6 x3 | 60.3 | ok |
| distance travelled by book | 43.0 x3 | slope leg 28.3 + table leg 9.9 = 38.2 polyline, 35.1 straight (labstatic emulation 41-47) | ok (motion row, 1.13x) |

## Book width (the only fix): 11.28 -> 9.0 for qids 2437, 2447, 2457
- Route 1 (0024, slope plane, book at rest at the top n2-17 median, no occlusion in the original render): top
  silhouette row 351.3-352.3 (x 755-840) = up edge of the top face (h = 1.46 cm), pages bottom row 391-394 (x 750-810)
  = down-slope bottom edge (h = 0). Along-incline coordinates 30.18 and 21.43 -> 8.75 cm (8.2-9.2 for thickness
  1.2-1.8). The up edge lands at 30.2 = the board's top edge (book flush with the top), a consistency check.
  Top-face corner quadrilateral (751,354) (846,356) (818,385) (720,381): long 20.3-20.5, short 7.4-8.2.
- Route 2 (0023 camera, independent pose: only its stated slope depths 1.201 / 0.9555 at top-mid / bottom-mid,
  slope line 30.7): book at rest at the top, top silhouette 349.3-350.3, pages bottom 387.5-388.5 -> 9.1 cm
  (8.5-9.5 for thickness 1.2-1.8; 8.7-9.2 for depth errors that keep the slope at 30.2-31).
- Route 3 (0024 table plane, book at rest n40-48, grazing view, weakest): top-face short edges 7.7-8.9, bottom
  short edge 8.2-9.1 (its long edge comes out 17-19.7, i.e. this route under-reads depth extents).
- Routes 1 and 2 agree within 4%; with the 1.00-1.04 model scale -> 8.75-9.1. Proposed 9.0 (-20% vs 11.28).
- Why 11.28 is wrong: it was never measured on this event. `research/path85_lab/build_t6.py` ("NBpool") copied the
  median of the agent's notebook-width answers from 0013/0014 into 0023/0024. Those answers (10.3-11.05) are
  themselves above the 0014 audit's own geometry (9.0-10.1), and on this event's frames the book's along-slope
  extent is ~9 cm from two cameras. A 11.3 cm book at the top would put the pages bottom at v~403 here, 10 px below
  the observed 393.
- 0023 (same book, same label process) carries the same 11.28; its family audit should be consistent with this.

## Risks / not changed
- Slope length: the stated slope depths here (far 1.243, near 0.990) do not fit the board geometry (no board point
  is beyond 1.18 m on the model). Back-projecting plausible click pairs with those depths gives 33-39.5 (top-mid /
  bottom-mid 38.4). If the label was built from these depths it is ~37, not ~31. Only one route supports that
  (physical routes all give 30.2-30.9), so no change; flagged.
- 0023 table-plane grazing view gives 5.6-7.8 cm for the book width (pose maxerr 11 px, horizon/camera-height
  ambiguity ~12%); unreliable, not used, but it also says the width is below 11.28.
- Motion rows untouched (none >1.5x off). Labels for this event's motion look ~1.1-1.15x physical (stated-depth
  displacement 1.0->1.2 s 16.6 vs model 14.5 cm).
