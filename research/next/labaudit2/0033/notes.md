# Lab audit round 2: family 0033 (captured_0033 / 0033s / 0033x; one event, labels shared)

Input: `../inputs/0033.json`. There are 9 scored rows, all S3 and all for the ping-pong ball: v(0.5 s), v(1.4 s) and
v(1.5 s), once per render. None has a round-1 fix (round 1 made no changes; see `../../labaudit/0033/notes.md`).
I used test inputs only (frames, the prior "ping pong ball = 40 mm", and depth_info: 1.457 m at t = 0.9 and 0.738 m at
t = 1.4). I used no labels.

**Result: no fix.** No row meets the round-2 bar, which needs two routes within 12 % of each other and the current value
at least 25 % away from them. All 9 rows stay as they are.

| qids | question | current (o / s / x) | label-style routes (cm/s) | physical (cm/s) | verdict |
|---|---|---|---|---|---|
| 2555 / 2558 / 2561 | v at 0.5 s | 182.21 / 190.0 / 182.21 | c12->13: 152-176; c13->14: 192-223; stated-depth hold (1.457 m): 207-218 / 262-276 | 158 (c12->13), 197 (c13->14) | no fix |
| 2556 / 2559 / 2562 | v at 1.4 s | 123.93 / 125.415 / 123.93 | A (stated d35, plane ratio): 110-120; B (vanishing-point line through stated d35): 96-114 | 105-109 (smooth line, ToF scale) | no fix (current +4 to +15 % vs consensus ~108) |
| 2557 / 2560 / 2563 | v at 1.5 s | 154.36 / 156.06 / 154.36 | model depth: c37->38 132-137, c38->39 145-150; size depth: 235-258 / 100-116 (not credible) | 134-138 (c37->38), 162-165 (c38->39) | no fix |

## Scripts (`scripts/`; frames are read into memory, only crops go to `img/`)
| script | purpose |
|---|---|
| `track.py` | blob tracking of the ball (difference from the temporal median), all renders |
| `capsule.py` | capsule fit (segment plus radius, IoU 0.86-0.98) per frame: mid point = mid-exposure click, diameter |
| `geo.py` | camera pose from the table corners (round-1 `corners.json`), plane intersection, 25 fps clock map, small LM solver (no scipy in the venv) |
| `arc1.py` | t = 0.5 s: image parabola, range routes, label-style forward differences |
| `arc2.py` | arc-2 ballistic fit, used to compare against the stated range at t = 0.9 |
| `fall.py`, `v15.py` | rolling line and fall phase, v(1.5) routes |
| `edgefit.py` | roll-then-fall model with no hop (shows that the fall is faster than a plain roll-off) |
| `vp_route.py` | v(1.4) route B |
| `streak.py` | PCA streak geometry |

## Clock
- I mapped video frame k to capture frame c = k + (k>=12) + (k>=36) on the 25 fps clock. Capture frames c12 and c37 are
  the dropped ones.
- **Evidence for the drops:**
  - Arc-1 parabola on capsule mid points, c8-c14: rms 0.08 px with the drop after video 11. Without the drop it is 7.1 px; with the drop after video 10 it is 10.1 px; after video 12 it is 14.0 px.
  - The u steps are -16.8, -22.4 and -20.9 px, then **-49.5** across video 35->36 (that is, -24.7 per capture frame).
- **Question times:**
  - t = 0.5 s is c12.5, so c12->13 (floor) or c13->14 (round half up). c12 itself is not in the video; I interpolated its click from the parabola.
  - t = 1.4 s is c35 (video 34), so c35->36 (video 34->35).
  - t = 1.5 s is c37.5, so c37->38 (c37 dropped, click interpolated) or c38->39 (video 36->37).

## Geometry and scale
- **Table pose.** I used IPPE PnP on the four table corners (60.3 wide x 76 deep).
  - Reprojection error is 2.45 px at f = 711 and 1.26 px at f = 740. The swapped 76 x 60.3 gives 25 px, so that reading is excluded.
  - The camera is 18.0 cm (f 711) or 18.6 cm (f 740) above the top and about 70 cm in front of the near edge. The horizon is at v of about 341.
- **The stated depths do not match one plane scale:**
  - At c35 (rolling, near), the plane gives a ball-centre range of 81.3 (f 711) or 85.0 (f 740). Stated 73.8 + 2 = 75.8, so ToF/plane = 0.93 (f 711) or 0.89 (f 740).
  - At c22.5 (in flight, arc 2), constrained ballistic fits give 105-131 cm. Stated 145.7, so ToF/plane is about 1.1-1.4.
  - Round 1 found the same conflict. The in-flight ToF reading is probably partly background. This is the main reason the 0.5 s label is uncertain.
- **Ball size** (capsule diameter, x render):
  - Arc 1: 23.5-24.8 px. Arc 2: 29.7-31.2 px. Rolling: 31-36 px. c35: 33.7 px.
  - c38-c39: 57-59 px. This is inflated: the u coordinates at c38/c39 continue the rolling line exactly (line time 37.7 and 38.3), which puts the range at about 67 cm, not the 45 cm the size implies.
  - So the size route is unusable in the fall phase and noisy in the rolling phase (±3 px).

## v(0.5 s): 2555 / 2558 / 2561 (current 182.21 / 190.0 / 182.21)
- Arc 1 is a free fall. Over c8-c14 the image parabola has a = 10.63 px/frame² and the apex is at c8.47 (rms 0.08 px). The
  ball barely moves sideways (u slope -0.8 px/frame), and its size stays within 5 %, so there is little depth motion.
- The o-render crops show the shadow of bounce 1 on the table at v of about 446, which puts the bounce at a horizontal
  distance of about 122 cm.
- **Physical:** 158 for c12->13 and 197 for c13->14 (vertical, from g).
- **Label-style**, by range route (clicks interpolated at c12):

  | range route | range (cm) | c12->13 | c13->14 |
  |---|---|---|---|
  | gravity | 103-109 | 154-155 | 195-196 |
  | size, raw | 118-124 | 176 | 222-223 |
  | size, calibrated to the stated c35 range | 106-107 | 152-158 | 192-200 |
  | hold the first stated depth (1.457 m) | 145.7 | 207-218 | 262-276 |

- **Verdict.** 182-190 lies between the c12->13 and c13->14 families of values. Only the 1.457-hold c13->14 value is more
  than 25 % away, and it is a single hypothesis that no second route supports. No fix.
- **Possible upward bias.** If the labels used the in-flight ToF (about 1.1-1.4 times the plane, as at t = 0.9), the label
  would sit around 210-275. That cannot be shown, so it is not acted on. The 4 % render split (190 for s) is left as is,
  as in round 1.

## v(1.4 s): 2556 / 2559 / 2562 (current 123.93 / 125.415 / 123.93)
- **Route A** (stated d35 = 73.8; d36 from the plane-range ratio; raw clicks c35 and c36): 110-120 across both renders,
  both focal lengths, and centroid or weighted-centroid clicks. Scaling the plane to the ToF value gives 111-120.
- **Route B** (direction of travel from the image track line meeting the horizon; X35 = (73.8 + 2) x ray; X36 = the point
  on that 3D line closest to the c36 ray). Neither the table size nor the camera height is used. The result is 96-114
  (dX/dZ 0.23-0.32; the ray miss distance is under 0.2 cm). The mean over c33->35 is 105-126.
- **Physical:** a straight-line fit of the plane positions over c31-c36 gives 117 cm/s on the plane scale, or 105-109 once
  rescaled to the stated depth.
- **Verdict.** The routes agree at about 108 (A against B is within 12 %). 124-125 is 15 % above that, under the 25 % bar.
  No fix.
- The size-ratio route gives 250+, because the c36 capsule is inflated by the diagonal blur over the table edge. It is not
  credible and I did not use it.

## v(1.5 s): 2557 / 2560 / 2563 (current 154.36 / 156.06 / 154.36)
- **What the frames show.** At c36 the ball is at the near edge. At c38 and c39 it is a long falling streak (capsules 48
  and 90 px long; c39 runs off the bottom of the frame).
- **Route A** (`fall.py`, `v15.py`):
  - Horizontal motion continues the rolling line: 4.66 cm/frame on the plane scale, 105-109 cm/s on the ToF scale.
  - Heights come from the image v: -4.3 cm (table coordinates) at c38, -6.9 cm at the start of the c39 exposure. These fit a free fall from rest starting at c35.3.
  - That is earlier than the plane-based edge crossing (c37). `edgefit.py` shows that a plain roll-off cannot reach v = 576 by c38. Either the ball dropped off the edge with a small hop, or the edge position is a few cm off. The image-based heights are used as measured.
  - **Physical forward differences:** c37->38 134-138, c38->39 162-165 (instantaneous at c38: 147-151).
  - **Label-style** with model depths: c37->38 132-137, c38->39 145-150.
- **Route B** (size depths): c37->38 235-258, c38->39 100-116. This is driven by the inflated c38/c39 sizes. It disagrees
  with route A by far more than 12 %, so it cannot support anything.
- **Verdict.** 154-156 is 3-16 % from route A under both frame conventions. No fix.

## Not changed
None of the 9 rows qualifies. The candidate values sit inside the spread of the label-style routes, and the remaining
uncertainty comes from the unknown ToF readings at the unstated times: in flight at 0.5 s, and during the fall at 1.5 s.
Scratch use is 4.5 MB (crops only).
