# Lab audit, family 0023 (captured_0023 / 0023s / 0023x): one event, one label set

Inputs: `../inputs/0023.json` (27 scored rows = 9 questions x 3 renders). I used test inputs only (frames, `prior`, `depth_info`) and no labels.
Video: 1280x720, 24 fps, 49 frames. The o, s and x renders have identical geometry: the board and book edges agree to within 0.5 px.
Camera: f = 711 px, principal point (640, 360). Depth is the range along the click ray.

## Scene and timeline
A white board (the "slope", same prop as in 0001/0014) leans on the lab table, facing the camera. The camera is low:
about 17 cm above the table top and nearly level.
- The light-blue notebook sits at the top of the board, held by the person behind, until frame 20.
- It starts sliding at frame 21 (0.875 s). By frame 24 (t = 1.0) it has slid 3.6 cm.
- Its lower edge reaches the table at frames 30-31. It lands flat on the table at frames 32-34 and decelerates.
- It is at rest by frame 37 (1.54 s), in front of the board base, with its long side horizontal in the image.

**The 24-fps time base fits the stated depths:**
- Book range on the slope plane at frame 28.8 (t = 1.2): 1.005-1.03 m. Stated: 1.02.
- Book centre at frame 33.6 (t = 1.4), just landed on the table: range 0.86-0.87. Stated: 0.857.
- At rest: geometric 0.81. Stated: 0.851 (+5%).
- The prior (2.8 m/s^2 at 1.4 s) matches the measured table-phase deceleration of 2.4-3.4 m/s^2.

Scripts:
- `extract.py`: frames to `frames/`.
- `montage.py`, `crop.py`: images.
- `table.py`, `tablevp.py`: table edges, corners, PnP, and the side-edge vanishing point.
- `board.py`: board edges.
- `geo.py`: back-projection.
- `slope3d.py`: board plane and 3D book track on the slope.
- `bookmask.py`: cover mask.
- `bookwidth_slope.py`, `bookwidth2.py`, `slopewidth3.py`: book width and length on the slope.
- `rest.py`: book at rest on the table plane.
- `disp.py`: displacement.
- `v14.py`: table-phase track.
- `book24.py`, `table24.py` and `others/`: a look at the same notebook in captured_0024. This was inconclusive (see below).

## Geometry
**Board (x20 / o44 edge fits):**
- Top edge y = 356.3, spanning x 517.7-660.5 (143 px).
- Bottom edge y = 482.6 at x 520 and 480.4 at x 650, spanning x 491.6-677.4 (185.5 px).

**Stated-depth route (label-like).** Top-mid at 1.201 and bottom-mid at 0.9555 give:
- slope length 30.8 cm (30.7-31.0 for f = 700-722);
- width 24.0 cm at the top and 24.2 cm at the bottom;
- incline 32.8 deg.

**24-cm ruler route.** z = 1.189 at the top and 0.920 at the bottom give a length of 32.3 cm and an incline of 30.4 deg. The vanishing point of the side edges also gives 30.4 deg.

**Table.**
- The side-edge vanishing point is (597, 349.5), from the x mask, the s render and two frames. So the table horizon is at y = 349.5.
- Camera height h from two rulers:
  - table front edge (643.4 px = 60.3 cm): h = 0.169;
  - board bottom width (24 cm): h = 0.171.
  - The two agree, so the 60.3 side faces the camera.
- The front corners at the stated 0.704 / 0.725 give a corner-to-corner distance of 57.5 cm, or 54-57 cm for clicks inset from the corners.
- Geometric front-corner ranges are 0.75-0.76, so the stated ranges are 3-7% short.

## Rows
| qids (o/s/x) | question | current | my routes | verdict |
|---|---|---|---|---|
| 2407/2416/2425 | v at 1.2 s | 99.8 / 93.4 / 96.4 | Slope-plane 3D track: forward 28.8->29.8 = 77-81 cm/s (stated and ruler planes) | OK. The 1.2-1.3x ratio is the usual small-object noise factor, not >1.5x. Not touched. |
| 2408/2417/2426 | v at 1.4 s | 43.7 / 56.3 / 47.7 | Table-phase contact-line track: f33->34 53, f34->35 50 cm/s; stopped by f37 | OK. Not touched. |
| 2409/2418/2427 | book length | 20.5 x3 | Rest view: 177 px at front-edge z 0.757 = 18.9. Rest at stated 0.851: 20.6. Slope view (cover mask, both planes): 19.0-19.7 | OK (0-8%) |
| **2410/2419/2428** | **book width** | **11.28 x3** | **Slope view 8.3-9.4 (centre 8.7). Rest view 8.5 (7.9-9.1). W/L = 0.44-0.48 in both views** | **Too high by about 20-25%. Fix to 9.0** |
| 2411/2420/2429 | book height | 1.46 x3 | Rest front face 12.5-13 px at z 0.757 = 1.36-1.55. On the table plane, cover front-edge z (0.762) equals contact-line z (0.760) only for H about 1.46. Slope view page strip 7-8 px = 1.3-1.5 | OK |
| 2412/2421/2430 | slope length | 30.80 / 30.73 / 30.73 | Stated 30.8; ruler 32.3; 0001 audit 31.8-32.0 | OK |
| 2413/2422/2431 | slope width | 24.0 x3 | Stated depths 23.8-24.2 | OK |
| 2414/2423/2432 | table width | 59.6 x3 | Physical 60.3 (front side). Label-like (stated corner ranges) 54-57.5 | OK (within 4-9%) |
| 2415/2424/2433 | displacement 1.0-1.6 s | 33.5 x3 | f24 top-face centre on the slope plane to rest centre. Geometric rest: 33.5-34.2. Rest at stated 0.851: 29.8-30.5. With t=1.0 at frame 23: +1.6 | OK |

## Book width (the one fix)
**Route A: slope view, frames 10-28, o/s/x renders.**
- The cover top face is mapped onto the board plane, offset by the book thickness (1.46 cm).
- Its up-slope extent is 29-32 px at frame 24.
- Ruler plane:
  - brightness edges (`slopewidth_v.py`, o22-o27, 9 columns each): 8.7-9.4, median 9.2;
  - one column by hand (362.2 -> 391.1 at x 560): 8.6;
  - saturation half-max: 7.5-8.6;
  - cover-mask medians over frames: 8.3-9.5.
- Stated-depth plane: 6% lower (8.2-8.9 from brightness edges).
- In the same model the book length is 19.0-19.7.

**Route B: rest view, frames 40-48, o/s/x renders.**
- The cover's back edge (board white -> cover, y 481.6-483.1) and front edge (y 496.2-498.0) are mapped on the plane at height h - H, with horizon 349.5 and h 0.169-0.171.
- Result: W = 8.5 (median over 14 columns, 7.9-9.1).
- Self-check: the cover front edge (height H) and the table contact line (height 0) land at the same z (0.762 vs 0.760). That holds only if the plane model and H are consistent.
- Length in the same model: 18.9. W/L = 0.45.

**Cross-check against another clip.** The 0014 audit measured the same notebook at 9.0-10.1 wide and 18.0-19.7 long (W/L of about 0.5).

**Assessment.**
- Physical width is about 8.5-9.0. The label scale factor (stated ToF vs my geometry in this clip) is 1.00 +/- 0.05.
- Using the scale-free ratio with the current length answer: 0.44-0.46 x 20.5 = 9.0-9.4.
- I propose **9.0** for all three renders.
- The current 11.28 is 25% above this. It was not measured in this clip: per `research/verify_labsize/out/changes_verified.csv` (rule NBpool, "notebook width pooled 0013/0014 (6 answers)"), it is a pooled transfer of earlier pipeline answers from other clips. Those answers (10.3-11.05 in 0014) were themselves above the 0014 audit's measurement.

**Route C (inconclusive).** In captured_0024 the same book lies on the table in an oblique view. I tried to rectify it with the 0024 table's vanishing points, but those points are only 85.7 deg apart at f = 711. The cover corners could not be resolved reliably either, so this route gave only W/L of about 0.47 (W about 9.7 with an uncertain h). I do not use it as evidence.

## Not changed but worth knowing
- Book ToF: the stated rest range 0.851 is 5% above the table-plane geometry (0.81). At t = 1.2 and t = 1.4 the stated ranges match my geometry within 2%.
- Motion rows: the physical speeds are about 79 (1.2 s) and about 52 (1.4 s). Both current sets are within the expected noise band and are not touched.
