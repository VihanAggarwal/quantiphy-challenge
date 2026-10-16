# 0054 independent re-measurement (second measurer)

Scope: qids 2851, 2874, 2886, 2898 (green ball speed at 1.5 s), 2875, 2887, 2899 (white ball speed at 1.5 s),
2870 (white ball diameter, 0054b). I did not read any other file in this folder; all of my work is in
`remeasure/` (scripts, extracted frames, crops). No labels were used. Only test inputs (depth_info, priors) were used.

## Recommended values

| qid | clip | question | current | mine | confidence |
|---|---|---|---|---|---|
| 2851 | 0054as | green ball speed at 1.5 s (m/s) | 2.02 | **3.6** | medium-low |
| 2874 | 0054b  | green ball speed at 1.5 s (m/s) | 1.37 | **3.6** | medium-low |
| 2886 | 0054bs | green ball speed at 1.5 s (m/s) | 1.19 | **3.6** | medium-low |
| 2898 | 0054bx | green ball speed at 1.5 s (m/s) | 1.17 | **3.6** | medium-low |
| 2875 | 0054b  | white ball speed at 1.5 s (m/s) | 1.75 | **4.9** | medium |
| 2887 | 0054bs | white ball speed at 1.5 s (m/s) | 1.64 | **4.9** | medium |
| 2899 | 0054bx | white ball speed at 1.5 s (m/s) | 1.64 | **4.9** | medium |
| 2870 | 0054b  | white ball diameter (cm) | 5.39 | **6.8** | medium |

All of the current speed answers are low by a factor of 1.8 to 4. Both of my independent routes show this. The values in
this table are physical forward differences. I did not apply a label-noise factor to them.

## Key facts established

1. **Timing.** Each mp4 has 49 frames at 24 fps, but the original capture ran at 25 fps. The steps between frames
   11->12 and 35->36 are twice the normal length: the basketball moves 37 px and 15 px there, against about 18 px and
   8 px for its neighbouring steps. Ball steps in both cameras show the same doubling. This matches the ffmpeg 25->24
   resampling pattern, which drops original frames 12 and 37. So video frame k is original frame k for k<=11,
   k+1 for 12<=k<=35, and k+2 for k>=36. Video frame 36, at t=1.5 s, is original frame 38. Video frame 37 is
   original frame 39. Both t=1.5*24=36 and round(1.5*25)=38 point to the same instant.
2. **The cameras are synchronized.** Cameras a and b see the green ball bounce at video frame 37 and the white ball
   bounce at frame 38.
3. **Camera a is level.** The wall-panel seams at x=35, 198, 318, 404, 517 and 605 px are exactly vertical
   (Hough fit, 90.0 deg). So gravity points along +y in camera a's coordinates.
4. **The green ball bounces between original frames 38 and 39.** The camera-a ray at video 37 sits 30 px above the
   pre-bounce parabola, and the triangulated position sits 6-7 cm above it. The white ball is still in free fall at
   original frame 39 (its frame 37 lies within 1 cm of the parabola) and bounces after that.
5. **Why the current b-family speeds are low.** From 1.5 s to 1.54 s the balls fall almost along camera b's line of
   sight: the displacement is 37-44 deg off b's viewing ray. At 1.5 s the balls are also about 2.0-2.1 m from b, but
   the b depth_info gives 1.235/1.331 m at t=1.0. Projecting b's image motion at the t=1.0 depth reproduces the
   current 1.2-1.75 m/s values.
6. **A side finding to pass on.** In 0054b, depth_info gives the orange ball at 1.0 s as 1.8100 m, the same value as
   camera a. Camera b's basketball size and the triangulation both put it at about 2.6-2.75 m (surface). The value
   looks copied from camera a.

## Route 1: two-camera triangulation (cameras a and b)

- I took ball centres from the SAM-segmented renders: ax (green screen) for camera a and bx (black background) for
  camera b. I picked components by colour and checked by eye. There are 26 small-ball correspondences
  (white and green balls, frames 24 and 27-38) and 15 basketball correspondences (frames 12-26; in camera a I fitted
  a circle to the upper arc to avoid the floor shadow).
- I ran a relative-pose bundle adjustment with numpy Levenberg-Marquardt (`ba.py`), using f_a=711 and f_b scanned
  from 620 to 900. The reprojection rms is 0.6-0.8 px, which constrains f_b only weakly, so I used f_b=711.
- The fitted parabola's gravity direction lands 2-4 deg from camera a's +y. This is an independent sanity check of
  the geometry.
- The overall scale is the main uncertainty. Each constraint gives a scale value; at f_b=711:

  | scale constraint | value |
  |---|---|
  | gravity (fitting 9.81 m/s² over original frames) | 3.93 |
  | depth_info for the small balls in camera a | 4.26 |
  | depth_info for the small balls in camera b | 4.05-4.12 |
  | depth_info for the basketball in camera a | 3.90 / 4.05 |
  | basketball forward-difference speed against the stated prior (2.21 m/s) | ≥4.2 |

  I used s=4.1±0.15.
- Results at s=4.1:

  | ball | interval | ×25 | ×24 |
  |---|---|---|---|
  | green | video 36->37 (original 38->39) | 3.51 m/s | 3.37 m/s |
  | white | video 36->37 (original 38->39) | 5.18 m/s | 4.97 m/s |

  The instantaneous speeds at exactly 1.50 s, from the pre-bounce parabola, are 4.83 m/s for green and 4.55 m/s for
  white.

## Route 2: camera a alone, with gravity as the metric scale (no camera b, no labels)

- I fitted a ballistic model P(t)=P0+V0 t+g t²/2 with g=(0, 9.81, 0) in camera a, using the true timing at 25 fps.
  The data are the 2D tracks for the white ball (frames 25-37) and the green ball (frames 25-36). The rms is
  1.06 px for white and 0.66 px for green (`route2_a.py`).
- The ranges this fit predicts at t=1.0 s are 3.071 m (white) and 2.975 m (green). depth_info gives 3.107 and 3.073
  (surface plus radius), so they agree within 1-3%. This validates the depth labels, the timing and gravity together.
- The speeds from this route:
  - **White:** 4.92 m/s for original 38->39 ×25 (4.72 m/s ×24), and 4.57 m/s instantaneous at 1.50 s.
  - **Green:** 3.30 m/s ×25 for original 38->39 (3.17 m/s ×24). I placed the post-bounce point on the camera-a ray at
    video 37, at the parabola's horizontal position. The pre-bounce speed at 1.50 s is 4.78 m/s.

## Choosing the speed values

- **Convention.** For t=1.5 s, the likely labelled pair is original frame 38->39 (video 36->37), under either the mp4
  or the 25 fps convention. That gives about 3.3-3.5 m/s for green and 4.9-5.2 m/s for white.
- **Green.** If the labels used original 37->38 or an instantaneous value, green would be about 4.8 m/s, because the
  ball has not yet bounced at that point. I chose 3.6 to hedge between the two.
- **White.** 4.9 is central across both conventions (range 4.55-5.2).

## Route for 2870, white ball diameter (and the tennis-ball cross-check)

- **Ratio to the green tennis ball (6.7 cm stated prior), independent of scale.**
  - SAM-mask widths perpendicular to the motion, times the triangulated range ratio, over 18 frame-camera pairs
    (frames 25-35 in cameras a and b): W/G = 0.99±0.06. The camera-a median is 1.01 and the camera-b median is 0.99.
  - Half-contrast vertical extents near the apex in camera a (frames 25-28, where motion is horizontal): W/G = 1.01 to
    1.08, mean 1.04.
- **Absolute size with route-2 ranges.**
  - The white ball comes out at 6.8-7.0 cm (mean 6.93).
  - The green ball comes out at 6.3-6.7 cm (mean 6.48), which is consistent with a 6.7 cm tennis ball. Half-contrast
    extents read about 3% small.
- **Best estimate: 6.8 cm.** The white ("pink") ball is tennis-ball sized. The current 5.39 is about 20% low. The
  other renders' current answers range from 6.4 to 7.7 cm.

## Files

The files are in `remeasure/`:

| file | purpose |
|---|---|
| `extract.py` | extracts the frames |
| `comps.py` | lists the components per frame |
| `pts.py` | curated 2D tracks |
| `ba.py` | bundle adjustment |
| `vel.py`, `fbscan.py`, `final_vel.py` | Route 1 |
| `route2_a.py` | Route 2 |
| `sizes.py`, `wsize.py`, `vext.py`, `wabs.py` | diameter |
| `floor.py` | floor check |

The crops are `a_seq.png`, `b_seq.png`, `gz_*.png`, `a_apex.png` and `bx_merge.png`.
