# Lab audit, family 0062 (captured_0062 / 0062s / 0062x): 24 rows, all D3 sizes

**Result: 6 fixes in 2 label groups (whiteboard width, shopping-bag width). The other 18 rows are left as they are.**

## The scene
- The camera is fixed and high, looking down at about 39 deg onto the carpet. A white whiteboard (about 0.88 x 0.62 m,
  with two grey clips on its far corners) lies flat on the floor at the bottom right. It is static for n0-16, then is
  pushed and slides away up-left while rotating about 25 deg (n17-48).
- The other objects are static:
  - a blue "MARINE ..." tote bag, lying flat with its handles spread,
  - a small white box lying on its side, about 7 x 7 cm in section,
  - a brown plush ("mario toy") lying on its back,
  - the blue confetti-print recycling bin at the back left, the same bin as in 0052/0053.
- All three renders are the same 49 frames; s and x are SAM2 composites. The x masks match the 50% intensity edge to
  within 0.5 px on the static board.
- The image content is 2x upsampled (pixel values come in pairs).
- Timing: there is a double step in the board track at n35->36 (31 px against about 15 px), so this is the usual 25 fps
  capture with dropped frames. t = 1.4 s is n34 (24 fps would give n33.6; the difference is negligible here).

## Geometry
- **Floor normal** (`scripts/wbquad.py`, `scripts/wbplane.py`). I fitted a quad to the x-mask of the moving board in
  n20-48 (29 poses, several rotations) and searched for the floor normal that makes every pose the same rectangle.
  - At f = 711: pitch 38.9 deg, roll 8.5 deg.
  - Residual |cos| of the corner angles is 0.007. The side lengths vary by only 0.6-0.8% (CV) across poses.
  - Board: W/h = 0.3385, L/h = 0.4703 (h = camera height). Shrinking the mask by 1 px gives 0.332 / 0.466. f = 700-722
    changes these by less than 1%.
- **Independent pose check** (`scripts/wbstatic.py`): the sharp static pose (n2-13, near the camera, manual corners)
  gives W/h = 0.322-0.330, L/h = 0.463-0.470, with corner cos 0.000-0.007.
- **Wall-seam check** (`scripts/seamnormal.py`): the vertical VP from the right-wall seams lies 4 deg from the board
  normal. That normal fits the board much worse (CV 3.6%), probably because of lens distortion at the image edge. With
  it, the board's own ToF gives W 69.5 and L 88.6.
- **Camera height h** (`scripts/scale.py`, `scripts/binh.py`, `scripts/predrange.py`):

  | source | h |
  |---|---|
  | board ToF, 2.815 at n34 | 1.879 (1.86-1.90 over n33-35) |
  | bag ToF, 3.307 | 1.79 |
  | mario ToF, 2.016 (+ about 5 cm centre height) | 1.78 |
  | bin, 37.5 cm physical from 0052 | 1.79-1.84 |
  | box ToF, 2.082 | 1.64 (outlier: the box reads about 10% short, like the 0052 shoe) |
  | bin ToF, 2.303 | wrong; the floor geometry puts the bin at 3.9-4.0 m, past the useful ToF range |
  | velocity prior 1.9339 at 1.4 s | 2.04-2.19 raw. Plane speed at 1.4 s is 0.885-0.947 h/s. The ratio label/true is 1.11-1.19 at h = 1.84, which is the usual label-noise inflation |

  Consensus h is 1.78-1.88.
- **Tennis ball by the tripod (6.7 cm)**: FWHM 13.5-14 px against 12 px predicted. It is blurred and 2x upsampled, so it
  is inconclusive and not used.

## Row by row
| qid (o/s/x) | question | current | measured | verdict |
|---|---|---|---|---|
| 2923/2931/2939 | whiteboard length | 83.0 / 97.7 / 96.6 | 0.463-0.470 h, so 83-88 (board ToF 87.6-88.4; bag/bin scale 83-86.5; seam normal 88.6) | o OK. s/x are 11-16% high: below the 15% bar, no fix (see note) |
| 2924/2932/2940 | whiteboard width | 45.9 / 48.3 / 48.3 | 0.322-0.339 h. Board ToF scale gives 61.4-63.7, bag ToF 58.6-60.7, bin scale 58.6-62.3, static pose about 59-62, seam normal 69.5 | **FIX: 61 for all three** |
| 2925/2933/2941 | bag length | 57.1 | body across the opening 0.246-0.26 h, so 44-49; body bottom-to-opening 0.19-0.20 h, so 34-38; including the handles 0.344 h, so 62-65 | ambiguous (handles?), no fix |
| 2926/2934/2942 | bag width | 12.1 / 30.2 / 21.3 | the smaller visible body side is 34-38 (board normal and bag ToF 34.0-35.9; board ToF 35.7-37.7; seam normal 37.1-39.2). The other side is 44-49 | **FIX: 36 for all three** |
| 2927/2935/2943 | white box length | 18.7 / 18.4 / 18.5 | 3D top-face corners on a plane raised by the box height: 0.106 h, so 19.0-20.0 | OK |
| 2928/2936/2944 | white box width | 7.98 | top-face width 0.038-0.040 h, so 6.9-7.5; box height 6.9-7.8 | OK (6-15%) |
| 2929/2937/2945 | mario toy height | 32.07 | head-to-feet 31-38 depending on endpoints; minAreaRect at mid-thickness 0.163 h, so 29-31 | OK |
| 2930/2938/2946 | trashbin height | 37.67 (pooled from 0052) | front rim (y 135-136) to bottom (209.5), in this clip's floor geometry: 0.204-0.212 h, so 36.5-39.8 | OK under the physical convention (see risk) |

### Why the two fixed groups are wrong now
- **Whiteboard width.** The current values come from `geometry:3d_focal_from_prior` (scale from the velocity prior),
  pooled through physb2. The short side of the board lies mostly along the line of sight. At n34 it is about 108 px in
  the image, and pixels x 2.815/711 gives 43 cm.
  - That foreshortened image extent is what the current 46-48 reproduces.
  - Rectified on the floor plane, the side is 0.33 h, about 61 cm. A label built from per-click ToF back-projection, or
    a tape measure, both see the true side.
  - The length is barely foreshortened, which is why L agrees and W does not.
- **Bag width.** The three renders give 12.1 / 30.2 / 21.3 for one shared label, a factor 2.5 apart. They are agent
  direct guesses (17 / 44 / 30) times the prior scale ratio of about 0.7, not measurements.
  - The bag lies flat. Its visible body is about 46 (across the opening) x 36 (bottom to opening) cm, and about 63 cm
    with the handles.
  - Any visible-extent reading of "width" is at least 34-38, so 36 is a lower bound.
  - Moving to 36 improves every render whether the true value is 36 or 46. It only hurts if the label were a physically
    measured gusset (about 12 cm), which is not visible in the clip.

### Notes and risks (no fix)
- **Whiteboard length.** o 83.0 matches. s/x 97.7/96.6 are 13-14% above the central 85.5. One label is shared, so
  setting s/x to about 86 would be a small, low-risk gain, but it is below the 15% bar.
- **Trashbin.** The stated ToF range 2.303 is about 42% short of the geometric 3.9-4.0 m. If the label had been
  back-projected with that ToF depth, it would read about 22 cm instead of about 37.5. The label convention is unknown,
  and 37.67 matches the physical bin here and in 0052, so it is left as it is.
- **Bag length.** 57.1 sits between the body (44-49) and the body plus handles (62-65). It cannot be judged.

## Files
- `scripts/common.py` (loader, f = 711, principal point at the image centre), `extract.py` (contact sheets),
  `masks.py` (x-mask components and the board track, `xcomps.json`)
- `wbquad.py` (board quads, `wbquads.json`), `wbplane.py` (floor normal from the rectangle constraint),
  `wbmargin.py`, `wbstatic.py`
- `scale.py` (h from the stated ranges and the velocity), `predrange.py` (stated vs predicted ranges), `binh.py`
  (bin height), `seamnormal.py`, `vlines.py`, `lines2.py`
- `objrect.py`, `bagquad.py`, `bagmanual.py`, `baghandle.py`, `bagseam.py` (bag), `box3d.py` (box)
- Crops in `frames/`: `wb_quads.jpg`, `wb_static_grid.jpg`, `bag_grid.jpg`, `bag_quad.jpg`, `box_grid.jpg`,
  `mario_34.jpg`, `bin_34.jpg`, `tennis_grid.jpg`
