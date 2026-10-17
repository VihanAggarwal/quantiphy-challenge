# Lab audit round 2: family 0023 (captured_0023 / 0023s / 0023x; one event, shared labels)

Input: `../inputs/0023.json` (27 scored D3 rows = 9 questions x 3 renders; no S3 rows in this family).
Test inputs only (frames, prior, depth_info); no labels. Round 1 notes: `../../labaudit/0023/notes.md`
(round 1 changed book width 11.28 -> 9.0).

Work for this round is in `r2/`; frames are read from round 1's PNG dump. The `frames/`, `other/` and `scripts/` folders
here hold an earlier partial pass (board/table edge fits, averaged crops). They are not used below.
- `track.py`: blue-cover mask per frame -> `cover_track.json`.
- `board.py`: board corners (x render) -> `board.json`.
- `geo.py`: camera and planes. f 711, pp (640,360), depth = range. The board plane uses either the stated top/bottom
  ranges 1.201/0.9555 or a 24 cm width ruler. The table plane has horizon y 349.5 and h 0.169-0.171.
- `slope_track.py`, `smooth12.py`, `sizerange.py`: slope phase.
- `table_track.py`: table phase, from the cover back edge, the cover front dark line and the bottom contact line.
- `labelstyle.py`: label-style velocities.
- `disp.py`: displacement.
- `drops.py`: background frame-difference energy.
- `overlay.png`, `sheet_*.png`, `z_*.png`: the images I checked by eye.

## Capture clock
I used the lab mapping capture c = k (k<=11), k+1 (12..35), k+2 (>=36). Evidence:
- Background energy bumps at v11->12.
- The slope track has smooth step increments from v21 to v30, so there is no drop inside the slide.
- In the table phase, v35->v36 covers two capture frames.

Resulting frames:

| t | capture frame | video frame |
|---|---|---|
| 1.0 s | c25 | v24 |
| 1.2 s | c30 | v29 (forward step c30->31 = v29->v30) |
| 1.4 s | c35 | v34 (forward step c35->36 = v34->v35, a normal step) |
| 1.6 s | c40 | v38 (rest) |

The stated ranges fit this mapping:
- t=1.2: stated 1.02. Geometric cover centroid range at v29 is 1.016 (stated plane) or 1.000 (ruler plane).
- t=1.4: stated 0.857. Geometric top-face centre range at v34 is about 0.86-0.87.
- t=1.6: stated 0.851. Geometric top-face centre at rest is 0.81-0.82, so the stated value is 3-4 cm long. A click on the
  upper part of the grazing cover strip would explain this: across that 15 px strip the range spans 9 cm.

## Motion
The book slides down the board (a = 1.9-2.0 m/s^2 along the slope). Its front edge reaches the board bottom at
v30-31. It lands at v32-33, slides on the table at 2.1 cm per capture frame through v35, and is at rest from v37.

**v(1.2)**
- Raw 3D step v29->v30 of the cover centroid on the top-face plane (board plane + 1.46 cm):
  - stated plane: 82.3 (x render) / 82.8 (o render);
  - ruler plane: 85.6 (x) / 86.4 (o).
- The same step anchored to the stated 1.02 is identical. With bounding-box centres instead of centroids: 75-87.
- Smooth quadratic fits on the capture clock:
  - v(1.20) = 81-88;
  - forward difference of the fit over c30->31 = 84-92.
- The size-based range route (cover length) is too noisy per frame (54-94) and is used only as a sanity check.

**v(1.4)**
- Contact-line, front-edge and back-edge steps v34->v35:
  - o render: 53/55/52;
  - x render: 52/50/72;
  - s render: 42/46/68. The x and s renders have segmentation outlines at v34, so o is the cleanest.
- Label-style with the click at the visible centre, anchored to the stated 0.857 and given the plane's range change:
  50-58.
- Linear interpolation of the stated ranges (0.857 -> 0.851) to c36 gives 12. That is degenerate: the book stops at
  c39, so its range is not linear in time. Not used.

**Displacement 1.0-1.6**
- Label-style: slope centroid at v24 with range 1.02 + plane delta (1.120-1.129), to the rest visible-centre click
  (566.5, 494.5) at the stated 0.851. Result: 31.3-32.1.
- Physical, top-face centre to top-face centre: 32.2-34.0.

| row (qids o/s/x) | current | label-style | physical | verdict |
|---|---|---|---|---|
| v(1.2) 2407/2416/2425 | 99.8 / 93.4 / 96.4 | 82-86 (centroid), 75-87 (bbox) | 81-88 | Current is +9..+22%, under the 25% bar. No fix. |
| v(1.4) 2408/2417/2426 | 43.7 / 56.3 / 47.7 | 50-58 | 52-54 (o), 42-46 (s) | Within about 18%. No fix. |
| displacement 1.0-1.6 2415/2424/2433 | 33.5 x3 | 31.3-32.1 | 32.2-34.0 | OK (+4..+7%) |

The renders share one label, so the spread between renders on v(1.2) and v(1.4) is answer noise only. If a policy ever
harmonizes them, the noise-free centres are about 85 for v(1.2) and about 53 for v(1.4). This is not proposed as a fix,
because it does not meet the bars.

## Static rows (re-check)
| row | current | label-style (stated ranges) | physical / other | verdict |
|---|---|---|---|---|
| book length | 20.5 | 20.2. Rest ends x 479-654 at 0.851. | 18.9 (rest geometry), 19.0-19.7 (slope view) | OK |
| book width | 9.0 (round 1 fix) | back to front cover edge at rest: 9.4 (h 0.170) | round 1: 8.5 rest, 8.3-9.4 slope | OK |
| book height | 1.46 | front face 12.6 px: 1.37 (geometric range) to 1.51 (at 0.851) | | OK |
| slope length | 30.80 / 30.73 / 30.73 | 30.83 (stated top/bottom ranges) | 32.4 (ruler) | OK |
| slope width | 24.0 | 23.8 top / 24.2 bottom | | OK |
| table width | 59.6 | about 57 (front corners at 0.704/0.725) | 60.3 | OK (+4.5% / -1%) |

## Result
No fixes. Every motion row is within 25% of two agreeing routes (label-style and smooth physical), and every static row
is within 12% of the label-style value.
