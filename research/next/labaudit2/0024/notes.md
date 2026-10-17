# Lab audit round 2: family 0024 (captured_0024 / 0024s / 0024x; one event, shared labels)

Input: `../inputs/0024.json`, 30 scored rows (10 questions x 3 renders). Only test inputs were used (frames, `prior`,
`depth_info`); no labels. Round 1 is in `../../labaudit/0024/notes.md`; its only fix was book width 11.28 -> 9.0.

My scripts are in `r2/scripts/`, with the small track in `r2/track.json` and the viewed crops in `r2/png/`. Frames are
read in memory and never dumped. `remeasure.md` and `remeasure_work/` in this folder belong to a separate,
concurrent book-width re-measure. That work reached 9.4 cm (range 8.4-10.1), which is consistent with the current 9.0.

**Result: no fixes.** None of the motion rows meets the round-2 bar: two routes that agree within 12% and put the
current value at least 25% away. The static rows still agree with round 1.

## Geometry (`geom.py`, rebuilt from round-1 edge points; f = 711, principal point (640, 360))
- Table pose with a 76.0 x 60.3 top: rms 0.57 px, camera 14.75 cm above the table top. The board rectangle has its
  bottom edge on the table and comes out at 23.1 x 29.8-30.7 cm, inclined 32 deg. The overlay of table, board and
  track on frame x24 matches (`png/overlay_x24.png`).
- Scale check:
  - Book top-face corners on the slope plane measure 20.3 / 20.4 cm.
  - The teal extent along the board edge stays at 19.2-21.0 cm across video frames 10-29 (`sizerange.py`), so the
    plane ranges follow the book's apparent size during the slide.
  - The same board measures 30.7 / 30.87 in 0023 / 0014. My scale may therefore be 1-3% low.
  - The concurrent re-measure anchored the scale to slope_near = 0.99 and is about 6% larger. That makes the board
    about 32 x 24.6, too large against its siblings.
  - All speeds below have about 3% scale uncertainty.

## Capture clock
- Teal-cover tracks (`track.py`): the o, s and x renders agree to within 1-2 px. The book is at rest until video frame
  18, slides from 19, reaches the foot at 29 (tip-model leading edge x = -0.2 cm), tips onto the table over 30-31, is
  flat at 32 and rests from 36.
- No double step inside the slide (`drops.py`). Quadratic fits of the along-slope coordinate over video 20/21/22-29 fit
  best with no drop in all three renders and both click definitions (rms 0.10-0.23 cm, against 0.25-0.43 for any drop
  position).
- The drops before video 12 (book at rest) and 36 (book stopping) cannot be seen in this clip. I used the cross-family
  pattern: capture = video + 1 for video 12-35. So t = 1.0 is capture 25 (video 24) and t = 1.2 is capture 30 (video
  29). The alternative mapping (no drop before 12) is in the robustness check below.

## Motion rows (cm/s or cm; label = forward difference on the capture clock)
**3D tracks.** Slope-plane top surface (h = 1.46) until video 29, then a tip model (`tipmodel.py`) for the transition.
In the tip model:
- The leading bottom edge is on the table at distance x beyond the foot.
- The trailing bottom edge is on the incline, and the book width is 9 cm.
- (x, across position) are solved per frame so that the top-face centre projects onto the tracked centre.
- The solve gives x = 2.9 / 6.4 / 9.8 at video 30 / 31 / 32: flat at 32, as seen in `png/foot_x.png`.

**Stated anchors.** Model ranges at the anchor frames are 1.010-1.022 at capture 25 (stated 1.0685) and 0.961-0.972
at capture 30 (stated 0.977). Between the anchors the stated range falls 9.15 cm; the model gives 4.7-5.0 cm. So the
labeller's ToF readings carry errors of a few cm, and two label emulations bracket the label:
- **offset:** stated range at the anchor, plus the model's range change to the next frame (a persistent ToF bias).
- **lin:** stated ranges interpolated or extrapolated linearly in capture time.

| row (qids o/s/x) | current | label-style (main clock) | label-style (alt clock) | physical | verdict |
|---|---|---|---|---|---|
| v(1.0) (2434/2444/2454) | 76.2 / 76.9 / 76.2 | offset 62-68; lin 72-74; pure model 59-66 | 68-77 | 57-60 (smooth 3D quadratic, forward diff 25->26); 53-56 instantaneous; a = 2.0-2.2 m/s^2 | No fix. The current value is 3-23% above the label-style routes, which disagree with each other by about 15%. It is 27-34% above physical, but the lin route supports it. |
| v(1.2) (2435/2445/2455) | 85.7 / 86.4 / 85.6 | tip model: offset 50-69 (per-frame noisy), lin 67-76 | 77-87 | 72 (65-80): leading edge moves about 3.3 cm per frame through the transition; mean centre speed over capture 30-33 is 73-76 | No fix (current is 10-20% above the central 72-75). |
| distance travelled (2443/2453/2463) | 43.0 | not determinable: per-frame ToF noise inflates a path sum; the stated-anchor segment is 1.14x the model | - | path 37.0-38.2 (slope leg about 21 + transition 8-9 + table 7-8); straight 35.2-35.8; leading-edge path 20.9 + 16.9 = 37.8 | No fix (1.13-1.16x physical, inside the label band). |

**Why v(1.0) and v(1.2) are not changed.**
- The stated acceleration of 2.8 m/s^2 at t = 1.0 is close to physical (2.0-2.2). With independent per-click ToF
  errors of a few cm, a frame-level second difference would be tens of m/s^2. So the label track near capture 25 is
  either locally smooth, which supports the offset/lin emulations (62-75), or the acceleration was not taken from
  the frame track.
- The same 2.8 is stated for family 0023 at t = 1.4, which suggests a shared nominal value.
- Either way, nothing pins the labels to within 12% at a value 25% away from the current answers. Under the alternative
  clock, the label-style values (68-77 and 77-87) almost equal the current answers.

## Static rows (re-checked; no change)

| row | current o / s / x | check | verdict |
|---|---|---|---|
| book length | 20.5 / 20.09 / 20.5 | top-face corners on the slope plane 20.3 / 20.4; teal extent along the board edge 19.2-21.0; 0023 frontal 20.3-21.0 (round 1) | OK |
| book width | 9.0 (round-1 fix) | round 1: 8.75 / 9.1 from two cameras; concurrent re-measure 9.4 (8.4-10.1) | OK, left |
| book height | 1.46 | round 1: pages band 8-9 px on the slope | OK |
| slope length | 30.80 / 30.61 / 31.93 | physical 29.8-30.7 here, 30.7 / 30.87 for the same board in 0023 / 0014 | OK, but see risk 1 |
| slope width | 24.0 | 23.1 on the model (scale 1.00-1.04 gives 23.1-24.0) | OK |
| table length / width | 74.5 / 59.6 | 76.0 / 60.3 table top (pose rms 0.57 px) | OK (2% / 1%) |

## Risks (flagged, not changed)
1. **Slope length, label style.** The stated slope depths (far 1.243, near 0.990) do not fit the board. No board point
   is beyond 1.18 m on the model, and even with a 6% larger scale the top-mid point is about 1.155.
   - Back-projecting click pairs along the top and bottom edges with those depths gives 34.5-42.4 (`slope_stated.py`).
   - If the label was built from them, it is about 36-38, and the current 30.8 would be about 17% low.
   - Only this one route says so (and it spreads widely); every physical route gives 30-31.
   - The x render's 31.93 differs from o / s (30.8 / 30.6) although the label is shared: a 4% inconsistency, not a fix.
2. **Table, label style.** The stated table depths (left 1.035, right 0.573) fit the L corner (model 1.068) and the
   front corner F (model 0.522), i.e. the 60.3 side. The label-style L-F distance with those depths is 53.3. If that
   is the label for one of the table rows, the error is up to about 12%. This is not decidable, so no change.
