# Lab audit: family 0036 (captured_0036, 0036s, 0036x), one event, so one label per question

Inputs: `../inputs/0036.json`, 15 scored rows (5 questions x 3 renders). The clip has 49 frames at 24 fps, 1280x720.
I used test inputs only (frames, `prior`, `depth_info`) and no labels. Scripts are in `scripts/`, and frames and crops
are in `frames/`.

## Scene
- A ping-pong ball (4 cm, stated prior) rests at the back-left corner of the lab table (frames 0-12). A hand pushes
  it, and it rolls diagonally toward the camera and to the right. It leaves the front-right corner at about video
  frame 35-36, then falls out of view (frame 39).
- The camera is almost at table height: the table-top normal is about 1.7 deg off the image y axis.
- s and x are background-replaced renders of the same event, with identical geometry.
- **Dropped frame at video 35->36.** The ball's x step goes 28.4, 29.6, 32.2, then **70.6**, then 39. This is the
  same 25 fps capture with one frame dropped per second seen in 0035. Mapping: video k <= 11 -> original k,
  12..35 -> k+1, >= 36 -> k+2, at 25 fps. So t = 0.9 s is video ~21.5 and t = 1.4 s is video 34. The 24 fps
  reading (21.6 / 33.6) gives almost the same frames.

## Measurements (f = 711, pp = (640, 360))
- **Track** (`track.py`): median-background difference plus a white mask in the original render. Centroids at
  0.9 s are about (561, 450) and at 1.4 s (838, 506).
- **Table plane** (`table_geom.py`, `table_ortho.py`): lines fitted to the x-render table mask (side edges, back
  edge) and to the top/front-band boundary (front edge).
  - Normal n = (-0.03..-0.04, 0.999, 0.030).
  - Side/front ratio = **1.222**. This does not depend on the camera height, and it holds with or without
    orthogonality enforced.
  - So the front edge (across the image) is the **short side** and the receding side is the long one. The lab table
    is 60.3 x 76.0, ratio 1.26.
- **Ball-centre plane height** from the two stated points:
  - surface ranges: 0.160 (0.9 s) and 0.154 (1.4 s);
  - with +2 cm to reach the centre: 0.163 / 0.158.
  - So the camera is h = 0.174-0.185 m above the table top.
- **Ball size** (`size2.py`): vertical extent from the sharp top edge to the contact shadow, which avoids the
  horizontal motion blur.
  - 21.5 px at rest (range 1.32), 29.5-30.5 px at 0.9 s (0.93-0.96), 41.5 px at 1.4 s (0.685).
  - These agree with the plane ranges to within about 5%, and with the stated 1.01 / 0.716 to within about 5%.

## Row verdicts
| qids (o/s/x) | question | current | route 1 | route 2 | verdict |
|---|---|---|---|---|---|
| 2669/2674/2679 | table width (m) | 0.596 | plane, h 0.174-0.185: short side 0.56-0.60 | lab table prior 60.3 (side ratio 1.22 vs 1.26 confirms the orientation) | OK |
| 2670/2675/2680 | table length (m) | 0.745 | plane: long side 0.69-0.74 | lab table prior 76.0 | OK |
| 2668/2673/2678 | ball displacement 0.9-1.4 s (cm) | 43.5 | stated ranges at the tracked pixels: 43.8 (surface) / 44.3 (centre); other frame choices 42.7-46.3 | plane-intersected track 40.8-42.4, size track 41.0-42.7 | OK |
| 2666 / 2671 / 2676 | v at 0.9 s (cm/s) | 76.7 / 77.5 / 77.5 | plane track, smoothed fits: 81-86 | size track: 79-87 | OK (within 5-10%) |
| 2667/2672/2677 | v at 1.4 s (cm/s) | 95.0 | plane track: 78-84 (near-constant roll) | size track: 82-103 (shows some speed-up) | OK; ratio at most 1.2, nowhere near the 1.5x gross bar |

Notes on the rows:
- Width/length ambiguity: the side across the image is the short one, so "width = across, length = depth" and
  "length = longer side" both give 0.60 / 0.76. Swapping them is not a risk here.
- From frames 18-35 the roll is steady at about 80-85 cm/s. The average from the stated endpoints is
  43.8 cm / 0.5 s = 88 cm/s. The 1.4 s instant (video 34, original 35 -> 36) is still on the table, before the ball
  leaves the corner.
- Frames 13-17 (just after the push) show higher, decaying plane speeds (180 -> 100). That is partly the grazing ray
  geometry near the back edge, and it does not affect the asked times.

## Result
**No fixes.** All 15 rows were checked. Every current value is within about 10% of two agreeing routes, except
v(1.4 s) = 95, which is within about 20% and is a leaderboard-tuned motion value that the rules say to leave.
