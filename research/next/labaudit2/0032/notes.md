# Lab audit round 2: family 0032 (captured_0032 / 0032s / 0032x; one event, labels shared)

Input: `../inputs/0032.json`, 18 scored S3 rows. Round 1 notes: `../../labaudit/0032/notes.md` (round 1 fixed qid 2537,
white ball v(1.6), 40 -> 64). I used test inputs only (frames, `prior`, `depth_info`) and no labels.
Scripts are in `scripts/` (frames are read from the mp4s into memory; only crops go to `img/`). f = 711 px and
principal point (640, 360), with f = 770 as a sensitivity check. The `remeasure/` folder in this directory was written by
another process. I did not use it.

**Result: one fix.** The white ball's v(1.5 s) (qids 2541 / 2547 / 2553) goes from **49.6 to 68.0** cm/s in all three renders.
Every other row stays as it is.

## Geometry (`edges.py`, `geo.py`)
- **Table-top corners** (x-render median of video frames 0-19, sub-pixel edge fits with 0.2-0.5 px residuals):
  BL (574.8, 424.3), BR (850.1, 427.8), FL (462.9, 482.6), FR (963.8, 495.2). These are within 0.5 px of round 1.
- **Horizon** (the only plane quantity that sets the *relative* range change):
  - vanishing point of the side edges: y = 349.7;
  - front/back edge length ratio 1.819 against the plane's (y_front - y_h)/(y_back - y_h): y_h = 349.1.
  The two agree.
- **Absolute scale** (camera height h above the top):
  - stated ranges at video 36 (c38): 0.1757 from the ping-pong ball and 0.1770 from the tennis ball (centroid clicks);
  - table 60.3 wide: 0.168; table 76.0 deep: 0.180.
  For the label-style values I anchor to the stated range, so h only rescales the result.
- **Plane checks against sizes:**
  - The tennis ball's half-max width (b* - a* channel) against the plane-predicted exact sphere silhouette, over c23-c43
    (range 1.70 -> 1.11 m): trend -3.0 % (x) and +1.7 % (o) per 12 frames, so no systematic drift.
  - White ball: +4.2 % (x) and +1.7 % (o) per 12 frames (`zseries.py`). That is the size-vs-plane gap behind the two
    routes below.

## Clock
- Tennis-ball image step at video 35 -> 36: 31.7 px, against 14.6 and 16.7 px for the neighbouring steps. One capture
  frame is missing there, so capture c = k + (k >= 12) + (k >= 36).
- t = 1.6 s is c40 (video 38).
- t = 1.5 s is c37.5:
  - c38 (video 36) under the rounding / `labnoise.treal` convention used in 0040;
  - c37 (the dropped frame) otherwise.
- This family cannot decide between them. The two balls' stated ranges fit a common plane slightly better at c38
  (h mismatch 0.7 %) than at c37 (1.7 %). That is within ToF noise.

## White ball (ping-pong ball) motion (`track.py`, `topbot.py`, `planetrack.py`, `white3d.py`, `fitroll.py`)
- The ball is held at the back edge and is hit around video 30-32 (the tennis ball passes in front of it).
- It then slides toward the camera and to the right at about 100-115 cm/s (c34-c36), then rolls at a steady speed from
  c38 on.
- Lateral image step (x render, edge mid-points), video 36 -> 48: 4.9, 6.1, 6.1, 5.3, 5.6, 6.5, 5.7, 5.8, 6.8, 5.7, 6.1, 5.7 px.
  Before that: 10.6 and 9.6 px, and 6.75 px per capture frame across the drop.
- Apparent width over c38 -> c50: 21.8 -> 29.9 px (x) and 22.2 -> 29.7 px (o). The ball comes about 26 % closer.
- The motion is mostly radial. Over c38-c50 it is 61.5 cm/s radial and 23 cm/s lateral, so sin(psi) is about 0.35. The
  focus of expansion (the track line meeting the horizon) is at x of about 481, consistent with this.

### Rows 2541 / 2547 / 2553: white ball v(1.5), current 49.6 -> **fix to 68.0**
The label-style value is |P(c39) - P(c38)| x 25, with P(c38) = 1.353 x ray(click at video 36) and
P(c39) = d(c39) x ray(click at video 37). d(c39) is the stated range plus the model range change. Values by route, in cm/s:

| route | x | o |
|---|---|---|
| A: plane depth change, straight-line fit over c38-c50, raw clicks (f 711 / 770) | 65.2-66.3 | 65.6-66.7 |
| A: plane, raw per-step depth (noisy) | 49.1 (centroid) / 66.4 (edge) | 70.5 / 59.0 |
| A: plane, quadratic fit, forward difference c38 -> c39 (physical) | 68.8 / 70.1 | 65.4 / 67.3 |
| A: plane, linear fit c38-c50 (physical mean speed) | 65.2 / 66.2 | 64.8 / 65.8 |
| B: size, exact-silhouette widths (proportional or additive calibration, anchored at the stated range), linear fit c38-c50 | 74.6 / 76.1 | 68.7 / 71.4 |
| B: size, label-style with dR = -2.8 cm/frame | 73.3-74.3 | 73.7-74.6 |
| t = 1.5 read as c37 (dropped frame; click interpolated), c37 -> c38 | 84-93 | 90 |

Route A gives about 66 (label-style) to 68 (physical forward difference). Route B gives about 72. The two are within
9 %, which passes the 12 % agreement bar.
- Against 68, the current 49.6 is 27 % low.
- It is 24-25 % low against route A's most conservative value (66) and 31-34 % low against route B.
- Under the c37 reading of t = 1.5 it is 41-47 % low.

**Why 49.6 is wrong.** 49.6 = 31 (base) x 1.6 (labnoise cap factor) (`research/labnoise/out/test_rows_cap1.6.csv`).
- That row's track has sin_psi = 0.99999, a purely lateral motion at constant range. Round 1 found that the stored
  track put the ball at the tennis ball's range, 1.183 m.
- 31 cm/s is about the lateral part alone.
- The 1.6 factor models depth noise on a lateral motion. It does not restore the missing radial component, about
  61 cm/s.
- This is the same root cause as round 1's fix of qid 2537.

Expected item score under the labnoise click/ToF model (`emu.py`, sigma_px = 2):

| sigma_z | answer 68.0 against 49.6, c38 plane / c38 size / c37 |
|---|---|
| 0.5 cm | +0.08 / +0.15 / +0.19 |
| 1 cm | +0.01 / +0.05 / +0.11 |
| 2 cm | -0.006 / +0.01 / +0.04 |

The new value applies to all three renders, which share the label.

### Row 2537: white ball v(1.6), current 64 (round-1 fix): OK
- c40 -> c41 (video 38 -> 39), with the range at c40 from the plane anchored at c38:
  - label-style with fitted depth change: 66.0-67.5;
  - raw per-step: 57.7-63.4.
- Physical: 64.7-66.2 (plane); size route 69-76.
- 64 is within 5 % of route A. Leave it.

## Tennis ball v(1.5) (2540 / 2546 / 2552; current 88.128 / 83.016 / 88.128): OK
- Label-style c38 -> c39 (stated 1.183, plane depth change): 83.6 (x) and 93.1 (o).
- If t = 1.5 is c37: c37 -> c38 gives 84.9 and 73.9.
- Smooth plane fits (video 31-41, 33-40, 34-39), linear or quadratic at c38: 86.4-90.7.
- The current values are within 6 %.

## Static rows
| qids | question | current | route A | route B | verdict |
|---|---|---|---|---|---|
| 2542 / 2548 / 2554 | ball-ball distance at 1.5 s | 29.53 / 29.68 / 29.54 | label-style (stated ranges x click rays) at c38: 29.65-29.78 (f 711), 28.2-28.3 (f 770); at c37: 26.5-26.6 | centre to centre at c38: 29.3-29.5 | OK (at most 11 % even under c37) |
| 2538 / 2544 / 2550 | table width | 59.6 | known lab table 60.3 | plane anchored on the stated ranges: front and back edges 63.1-63.7 | OK (1-6 %) |
| 2539 / 2545 / 2551 | table length | 74.5 | known 76.0 | plane anchored on the stated ranges: 74.1-74.7 (f 711) | OK |
| 2543 / 2549 | white-ball diameter | 4.0 | ping-pong ball, stated 40 mm in 0021 / 0036 priors | half-max width against the exact silhouette at the stated range (video 36): 4.13-4.21 (f 711), 3.8-3.9 (f 770 equivalent) | OK |

The s render's white-ball threshold catches its pale background. The s render shares the label with o and x, so I did
not track it separately.
