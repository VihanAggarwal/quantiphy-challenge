# Lab audit round 2: family 0031 (captured_0031 / 0031s / 0031x; one event, shared labels)

Input: `../inputs/0031.json` (17 scored rows). Test inputs only (frames, prior, depth_info); no labels.
Round 1: `../../labaudit/0031/notes.md` (fixed 2530, white v(1.6) 30.0 -> 46.6).
Scripts are in `scripts/` and frames are read straight from the mp4s (nothing dumped):
- `track.py`: HSV masks.
- `chords.py`: sub-pixel half-level chords, with a circle-chord fit and a widest-row fit, giving the diameter and centre.
- `table.py`: table edges and corners.
- `pose.py`: PnP with the 76.0 x 60.3 top.
- `routes.py`: 3D size and plane routes.
- `speed.py` and `profile.py`: speeds.
- `mc.py`: label-style emulation and MRA.
- `dist.py`: ball-to-ball distance.

The crops I checked by eye are in `img/`.

## Clock
- The tennis ball's image y step from video frame 35 to 36 is 3.9-4.0 px, against 1.7-2.7 px for its neighbours. The white ball's x step over the same pair is 2.4 px, against 1.1-1.9 px. That pair is a double capture step.
- The earlier drop (after frame 11) cannot be seen because the balls rest until frame 15. The pattern is periodic, so I used capture n = k + (k>=12) + (k>=36), the same as 0023 and 0028.
- **t = 1.6 s is capture frame 40, which is video frame 38.** The forward step 40->41 is video 38->39, a normal step.

## Geometry (two independent range routes)
- **Size route:** sub-pixel chord diameter (o and x renders averaged), tennis 6.7 cm.
- **Plane route:** PnP on the table-top corners BL(574.4,424.0), BR(849.0,427.5), FL(462.8,482.6), FR(963.0,494.9), with front edge = 60.3 and depth = 76.0.
  - At f=711 the reprojection error is 2.45 px and the camera sits 16.2 cm above the top. At f=760 it is 0.33 px and 16.9 cm.
  - The swapped orientation fits at 14-17 px.
  - Rays through the ball centres meet the plane r above the top.
- **Tennis ball, centre range:** plane/size = 1.00 +- 0.015 at every frame k28-41. At t=1.6: R_c = 94-96 (f=711) or 102.5 (f=760).
- **White ball:** plane/size = 0.96, so D_white = 3.9 cm if the plane route is taken. At t=1.6: R_c = 114 (plane, f=711) or 121 (plane, f=760).
- **The depth_info names are swapped:**
  - At f=760 the swapped stated values match my surface ranges to within 0.5 cm. Tennis: stated 0.994 against 1.025 - 0.0335 = 0.992. White: stated 1.190 against 1.208 - 0.02 = 1.188.
  - The literal values are wrong by +20 cm (tennis) and -15 cm (white).
  - So the readings are clean, there is almost no ToF noise at frame 40, and the effective scale is f ~ 760, or equivalently ToF = 1.065 x my f=711 ranges.
- **Motion:** the balls were pushed at frame ~15 and then decelerate.
  - Tennis: ~85 cm/s at n20, 65 at n34, 59-62 at n40. Its centre reaches the front edge at k42 and it falls at k43.
  - White: ~44 cm/s at n40.

## Motion rows

### v(1.6) on the 25 fps clock
| route | tennis (cm/s) | white (cm/s) |
|---|---|---|
| size route, physical | 53-61 (f=711), 56-65 (f=760) | 39-50 |
| plane route, physical | 56-64 (f=711), 58-64 (f=760) | 42-45 |
| local hand check | 55-59 | |
| velocity direction | ~(-14.5, 0.5, -57); mostly toward the camera | |

### Label-style (`mc.py`)
Method:
- Clicks at the centres at video frames 38 and 39.
- D(40) is the stated reading for the object whose depth series the label uses.
- D(41) = D(40) + ToF-scaled dR, with click jitter 2 px.

Results:
- **H1** (only the text is swapped; the labels are on the right objects):
  - tennis deterministic 57.9-61.6, MRA-best 58.5-62.5 at sigma_z = 0;
  - white 44-47, MRA-best 46.5-49.5.
- **H2/H0** (the tennis label carries the white ball's depth series or identity): tennis ~44-48, white ~57-62.
- Nothing in the inputs separates H1 from H2. H1 is the literal reading of the question.

### Rows
| qids (o/s/x) | question | current | label-style | verdict |
|---|---|---|---|---|
| **2523/2529/2534** | **v tennis 1.6 s** | **77.52 / 71.84 / 71.84** | H1 58-62; H2 44-48; both routes physical 55-64 | **Fix all three to 60.0** |
| 2524/2530/2535 | v white 1.6 s | 47.76 / 46.60 / 45.60 | H1 44-49 (MRA-best 46.5-49.5); H2 57-62 | Keep. Correct under H1, and no evidence for H2. |
| 2525/2531/2536 | ball-ball distance 1.6 s | 22.78 / 23.58 / 22.92 | 22.4-23.4 (f 650-760; symmetric under the swap); click MC 22.5-23.1 | Keep |

### The fix: qid 2523, 2529, 2534 (tennis v at 1.6 s) -> 60.0
- **Why the current value is wrong:**
  - All three rows rest on p8 = 80, the low-confidence (0.15) eyeballed `direct_answer` from runs/test_v1_high_854. They were then multiplied by labnoise factors of 0.969 (o) and 0.898 (s, x).
  - Two independent routes measure the tennis ball's speed at capture frame 40 at 55-64, central ~59-60. The size route and the table-plane route agree in range to 1%.
  - So the 80 base is ~30% high. The labnoise factor near 1 does not rescue it, because with the measured speed the emulator's factor is ~1.0.
- **Bars:**
  - (a) The two routes agree within 12%.
  - (b) 77.52 is +29% over 60. The renders share one label, so the fix applies to all three; 71.84 is +20%.
- **Expected MRA** (`mc.py`, sigma_z on the next-frame reading):

| hypothesis | sigma_z | 60 | 71.84 | 77.52 |
|---|---|---|---|---|
| H1 | 0 | 0.92-0.93 | 0.73-0.81 | 0.64-0.72 |
| H1 | 1 cm | 0.61-0.64 | 0.56-0.60 | 0.52-0.57 |
| H1 | 2 cm on both readings (labnoise model) | 0.44-0.45 | 0.43-0.44 | 0.42-0.44 |
| H2/H0 | 0 | 0.66-0.75 | 0.40-0.51 | 0.29-0.39 |

  60 is at least as good as both current values under every hypothesis and noise level.

## Static rows (re-check)
| qids | question | current | measured | verdict |
|---|---|---|---|---|
| 2520/2526/2532 | white ball diameter | 4.0 | Plane route 3.9 (k38); rest-pair ratio corrected for the plane 3.8-4.0; ping-pong ball 4 cm stated in 0021/0036 | Keep |
| 2521/2527/2533 | table width | 59.6 | Front edge 500 px. With the tennis-size scale at the front edge: 61 +- 2. Known top 60.3. | Keep |
| 2522/2528 | table length | 74.5 | Known top 76.0. The depth aspect is ill-conditioned at this grazing view, but PnP prefers 60.3 x 76 over 76 x 60.3 by 6x in error. | Keep |

## Result
One fix, applied to all three renders of the shared label: qid 2523 (77.52), 2529 (71.84) and 2534 (71.84) all become 60.0.
All other rows are unchanged.
