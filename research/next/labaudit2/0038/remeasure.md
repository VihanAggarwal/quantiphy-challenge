# 0038 independent re-measure (second measurer) - qids 2703, 2710, 2717

Question (all three renders captured_0038 / 0038s / 0038x, shared labels):
"displacement of the white ball between 0.9s and 1.4s in cm". Given: ball range 0.7160 m at t=1.4s.
I did not read labaudit/0038 or the other labaudit2/0038 notes. All my scripts/images are in `rm2/`.

## Result

| qid | render | label-style best | physical | confidence |
|---|---|---|---|---|
| 2703 | captured_0038 | **20.1 cm** | 20.2 cm | medium-high |
| 2710 | captured_0038s | **20.1 cm** | 20.2 cm | medium-high |
| 2717 | captured_0038x | **20.1 cm** | 20.2 cm | medium-high |

The label is 20.9 cm if the labeller took capture frame 22 for t=0.9s, and 19.3 cm if they took frame 23
(0.9 s x 25 fps = 22.5). 20.1 is the midpoint, within about 4% of either.

## Method

1. **Ball track** (`track.py`, `tm.py`). I first used background subtraction on the x render, then NCC template matching
   with a frame-24 template, refined to sub-pixel. The o, s and x renders agree to about 0.2 px, and a frame-40
   template gives the same x positions. The true vertical centre is the template y plus 5.4 px, measured from the
   ball's top and bottom edges. The ball diameter is about 40 px.
2. **Capture clock.** The video track has a double step from video frame 35 to 36 (33.3 px against about 16.3 px per
   frame). Frame-difference energy in the person region of the o render also spikes from 11 to 12 and from 35 to 36.
   This fits round-half-up 25-to-24 fps resampling: c(k)=k for k<=11, k+1 for 12..35, and k+2 for k>=36.
   A single line in capture frames fits video frames 16-45 with 0.55 px rms, at 16.29 px per capture frame.
   So t=1.4s is capture 35 (video 34), and t=0.9s is capture 22 or 23 (video 21 or 22).
3. **Table plane** (`table.py`, `pnp2.py`). I fitted lines to the table-top edges and intersected them for the corners:
   FL(212.9,535.7), FR(1140.6,586.9), BR(917.3,466.9), BL(448.5,448.2). IPPE PnP used a 76.0 x 60.3 cm table with
   the 76 cm side at the front, f=711, and principal point (640,360). The camera sits about 16.6 cm above the
   table top. The plane matches the stated cup and bottle depths to within about 1.5 cm (`anchors.py`). The card
   depth disagrees by about 3.5 cm, probably because it sits at the table's front edge.
   The ball rolls parallel to the front edge, about 12 cm behind it, at a near-constant 1.6 cm per capture frame
   (about 41 cm/s). Its surface range is 69.8 cm at video 34 (stated: 71.6) and falls about 1.5-1.8 cm from video 21-22 to video 34.
4. **Displacement** (`disp.py`, f=711), with pixel displacement 210.7 / 202.7 / 194.6 px for capture 22 / 22.5 / 23 to 35:
   - A, label-style: P = r_surface * ray. r(1.4) = 71.6 (stated), and r(0.9) = 71.6 + the plane-predicted change.
     Gives 20.92 / **20.10** / 19.29.
   - A2, constant r = 71.6: 20.57 / 19.80 / 19.04.
   - B, plane-only surface points with no stated anchor: 20.40 / 19.60 / 18.81.
   - C, physical ball-centre displacement from the table plane (scale set by the table size, so it barely depends
     on f): 20.97 / **20.16** / 19.34. The table-x coordinate moves 21.0 cm over 13 capture frames.
   - D, physical centre anchored to the stated range: 21.50 / 20.66 / 19.83.
   - Ball-diameter check: 202.7 px / ~40 px per 4.0 cm ping-pong ball gives about 20 cm.

## Uncertainty
- **Frame choice for 0.9s (±4%):** the largest error source. Frame 22 (int or round-half-even of 22.5) gives 20.9;
  frame 23 gives 19.3.
- **Focal length:** the label value scales as 1/f. The rectangle PnP fits best at f≈750, while the cup/bottle depths
  and the earlier audit support 711. At f=730 the label-style midpoint is 19.6.
- **Click jitter and ToF noise:** a 2 cm error in the 0.9s depth changes the result by about 0.5 cm.

## Side observation (not my qids)
The ball's physical speed near 1.4s is about 41 cm/s. The label-style forward difference from capture 35 to 36
(video 34 to 35) is about 41-43 cm/s (17.1 px raw, 16.3 px smoothed, at 71.6 cm range). The current answer of 60.165 for "velocity at 1.4s" (qids 2700/2707/2714)
looks inconsistent with this track and is worth a check. Captured_0036 also states 0.7160 m at 1.4s, so the stated
depth may have been copied from that family.
