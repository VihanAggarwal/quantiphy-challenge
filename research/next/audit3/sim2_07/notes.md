# Audit sim2_07: family simulation_0253 / 0254 / 0255 / 0255_segmented / 0256

## Scene family

| clip | view | object / prior | motion |
|---|---|---|---|
| 0253 | side view of a ~44.2 deg ramp (same camera and background as 0254) | box, width along slope 0.611 m (front-face bottom edge about 85 px) | slides down the ramp. Box enters at frame 4. |
| 0254 | same ramp and camera as 0253 | tennis ball, D 0.17 m (24.4 to 25 px) | rolls down the ramp. Visible from frame 19, reaches the floor at frame ~48. |
| 0255 / 0255_seg | side view of the floor | tennis ball, D 0.17 m (23.4 to 23.7 px) | rolls left to right, decelerating at ~1.1 m/s^2 |
| 0256 | top-down view of the floor | tennis ball, D 0.17 m (32.3 to 34.7 px) | same rolling motion as 0255 (speeds within 3%) |

**Key finding: 0253 (box) and 0254 (ball) show the same scripted motion.** Each clip was measured with its own prior and gives
the same speeds:

| t | box (0253) | ball (0254) |
|---|---|---|
| 1.0 s | 6.38 m/s | 6.36 m/s |
| 1.5 s | 9.13 m/s | 8.94 m/s |
| 1.75 s | 10.23 m/s | 10.03 m/s |

- Both objects start from rest at t ~ 0. The box leading-edge track (seen from frame 5) gives zero speed at frame 0 to 0.5. The ball's cubic fit, extrapolated, gives zero speed at frame 0.9.
- In both clips the acceleration falls roughly linearly over time: about 7 m/s^2 at 0.5 s, 6 at 1.0 s, 4.8 at 1.5 s and 4.1 at 1.75 s, measured in pixels at one scale.
- For the ball, a cubic fit of path length against frame has 0.20 px rms. The quadratic (constant acceleration) fit has 1.61 px rms, with systematic residuals.

The 0254 agent assumed constant acceleration (4.89 m/s^2 at every time) and extrapolated the speed at 0.5 s back with that
model, giving 4.0 m/s, which implies v(0) = 1.6 m/s. This is the error.

There is a small perspective scale gradient along the ramp:
- the box front-face height shrinks ~2-3% from top-left to bottom-right (mask extent 82.5 -> 81 px; zoomed rotated crops 75 -> 72 px);
- the ball's apparent D shrinks ~2.7% (sat-edge circle fit).

That is d ln(scale)/d(px) ~ -2.3e-5. Corrected acceleration is a = (p'' + 2.3e-5 * p'^2) / s_local. This adds +0.5% at 0.5 s,
+2.4% at 1.0 s, +6% at 1.5 s and +8% at 1.75 s. Applying it reduces the apparent fall in acceleration at the late times.

Video glitch in 0253: frame 9 shows true frame 10 and frame 10 = frame 11 (a duplicate). Likewise frame 27 shows true frame 28
(a duplicate of 28). I remapped or dropped these frames. 0254 has no glitches (its per-frame steps are smooth).

## Rows checked (all 34 scored)

The quick check uses my own tracks: a bg-diff/saturation mask centroid and a circle fit on the saturation edges. I used
backward differences of cubic fits, with each clip's own scale. The in-depth routes are local quadratic windows and the
sibling clip.

| qid | clip | quantity | current | quick check | 2nd route | verdict |
|---|---|---|---|---|---|---|
| 855 | 0253 | v 0.5 s | 3.10 | 3.03 (box leading edge, frames 5-18; 3.12 after back-face depth corr.) | ball 0254 cubic extrap 3.2 | ok |
| 856 | 0253 | v 1.0 s | 6.38 | 6.38 | ball 6.36 | ok |
| 857 | 0253 | v 1.5 s | 9.20 | 9.13 | ball 8.94 | ok |
| 858 | 0253 | v 1.75 s | 10.48 | 10.23 (10.43 at local scale) | ball 10.03 | ok |
| 859 | 0253 | a 0.5 s | 6.90 | 6.3-6.5 (leading edge) | ball cubic extrap 6.85 | ok (<10%) |
| 860 | 0253 | a 1.0 s | 6.00 | 6.32 (6.47 corr.) | ball 5.76 | ok |
| 861 | 0253 | a 1.5 s | 5.00 | 4.83 (5.2 corr.) | ball 4.67 | ok |
| 862 | 0253 | a 1.75 s | 4.60 | 4.09 (4.5 corr.) | ball 4.12 (4.45 corr.) | ok (hedged correctly) |
| 863 | 0254 | v 0.5 s | 4.00 | 3.23 (cubic extrap; 3.13-3.34 over windows) | box 0253, observed at t=0.5: 3.03-3.12 | **FIX -> 3.15** |
| 864 | 0254 | v 1.0 s | 6.44 | 6.36 | box 6.38 | ok |
| 865 | 0254 | v 1.5 s | 8.89 | 8.94 | box 9.13 | ok |
| 866 | 0254 | v 1.75 s | 10.11 | 10.03 (10.14 local scale) | box 10.23 | ok |
| 867 | 0254 | a 0.5 s | 4.89 | 6.85 (cubic extrap; 6.5-7.05 over windows) | box leading edge 6.3-6.5 | **FIX -> 6.7** |
| 868 | 0254 | a 1.0 s | 4.89 | 5.76 cubic, 5.5-5.6 local windows (5.6-5.9 corr.) | box cubic 6.32 / box agent 6.0 (6.15-6.47 corr.) | **FIX -> 5.9** (marginal, see below) |
| 869 | 0254 | a 1.5 s | 4.89 | 4.67 (4.9 corr.) | box 4.83 | ok |
| 870 | 0254 | a 1.75 s | 4.89 | 4.12 cubic, 3.97-4.04 local (4.43-4.54 corr.) | box 4.09 (4.49 corr.) | not fixed: corrected estimate 4.45 is only ~9% below the current answer |
| 871 | 0255 | v 0.5 s | 7.075 | 7.18 (D=23.35 chord) / 7.08 (D=23.7) | local window 7.17 | ok |
| 872 | 0255 | v 1.0 s | 6.524 | 6.62 / 6.53 | 6.62 | ok |
| 873 | 0255 | v 1.5 s | 5.972 | 6.07 / 5.98 | 6.07 | ok |
| 874-876 | 0255 | a 0.5/1/1.5 s | 1.103 | 1.12/1.11/1.10 (cubic) | 0256: 1.13-1.20 | ok |
| 877 | 0256 | v 0.5 s | 7.29 | 7.30 (D=33.2) / 7.50 (D=32.3) | 0255 7.08-7.18 | ok |
| 878 | 0256 | v 1.0 s | 6.72 | 6.72 / 6.91 | 0255 6.53-6.62 | ok |
| 879 | 0256 | v 1.5 s | 6.15 | 6.18 / 6.35 | 0255 5.98-6.07 | ok |
| 880-882 | 0256 | a | 1.13 | 1.20/1.13/1.06 (cubic) | 0255 1.10 | ok |
| 2000-2005 | 0255_seg | same as 0255 | copies of 0255 | same footage; ball centroid track identical | - | ok |

Notes on scales:
- 0255: the subpixel gray chord (linear coverage) gives D = 23.4 px (median of 41 frames); the agent used 23.7. Colour-based edges
  (saturation/chroma) give 22.2-22.6. They read low because of 4:2:0 chroma blur and the darker limb, so the gray chord is preferred.
- 0255_segmented: the segmentation mask is dilated by ~1 px per side (equivalent diameter 26.8 px). Do NOT measure D on the
  segmented clip. Copying the 0255 answers was correct.
- 0256 (top view, shadow above the ball): the saturation circle fit gives 32.3, the horizontal sat chord 33.4 and the gray chord
  34.7 px. The agent used 33.2 (middle of this range). 0255 and 0256 agree within 3%.
- 0254: the gray chord gives 24.4 px and the agent's half-max gives 25. With D=25 the ball speeds match the box (independent
  prior) within 2%, so D=25 is consistent.

## Fixes proposed (0254 only)

1. **qid 863** (v at 0.5 s): 4.00 -> **3.15**. The ball is not visible at 0.5 s (it enters at frame 18/19).
   - The agent extrapolated a constant-acceleration fit.
   - The data reject that fit: the quadratic has 1.6 px rms with systematic residuals, the cubic 0.2 px.
   - The cubic extrapolation gives 3.13-3.34 across fit windows, and the ball starts from rest at t ~ 0.04 s.
   - The sibling box (0253, same scripted motion, observed directly at t=0.5 s) gives 3.03-3.12; the 0253 agent also had 3.1.
2. **qid 867** (a at 0.5 s): 4.89 -> **6.7**.
   - Ball cubic extrapolation: 6.5-7.05.
   - Box observed leading edge over frames 5-18: 6.3-6.5 (0253 agent: 6.9).
   - Same constant-acceleration error.
3. **qid 868** (a at 1.0 s): 4.89 -> **5.9**.
   - Ball's own track: cubic 5.76, local window 5.5-5.6, 5.6-5.9 after the gradient and local-scale corrections.
   - Box sibling: 6.0-6.47.
   - The current answer is 15-20% below both routes. This one is marginal on the 15% threshold, but the fix improves the error
     across the whole plausible range (5.5-6.4).

Not proposed: **qid 870** (a at 1.75 s). The raw pixel-acceleration routes give 4.0-4.1 (current 19% high), but the perspective
gradient correction (+8%) raises them to ~4.45. That leaves the current answer only ~9% off, below the threshold. If someone
wants consistency with the shared-motion value, 4.45 is a soft candidate for both 0253 (4.6) and 0254 (4.89).

## Files
- scripts/: track_ball.py, track_box.py, ball_diam.py (gray chord), ball_radial.py (sat-edge circle fit), ball_chroma.py,
  box_height.py, speeds.py, compare_0253_0254.py
- tracks/: my per-frame tracks (small json/txt)
- PNG crops viewed: ov_*.png, crop0255_f20.png, crop0256_f20.png, box_*.png, ball0254_crops.png
