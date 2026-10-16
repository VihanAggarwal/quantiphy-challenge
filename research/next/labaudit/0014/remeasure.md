# 0014 independent remeasure: qid 2240 only

Second measurer working from scratch. I did not read any other file in this folder.
Scripts, frames and crops are in `remeasure2240/`.

## qid 2240: velocity of the rolling ball at 0.6 s (captured_0014), current answer 83.77 cm/s

**Best value: about 112 cm/s.** This is a label-style forward difference at 0.6 s on a 25 fps source time base.
The plausible range is 104 to 115. Confidence: medium.

### Setup seen in the frames
- The ball is a beige ball, about 29 px across. It is held at the top edge of a white board (the slope), which leans on the table.
- The ball rolls down the board in frames 12 to 16. It leaves the board at frame 17 and bounces on the table at frames 20 to 22.
- The foreground is the same in all three renders. Ball tracks from the x, s and original renders agree within 0.5 px.

### Time base
- The file is 24 fps with 49 frames. The ball moves 21 px between frames 11 and 12, but only 11.6 px between 12 and 13. Frame 11 is still sharp.
- A single 1/24 s interval cannot produce that jump. One source frame is missing, which fits a 25 fps to 24 fps conversion where our frame k shows source frame round(25k/24).
- So our frames 12, 13, 14, 15 and 16 are source frames 13 to 17, at 0.52, 0.56, 0.60, 0.64 and 0.68 s. **t = 0.6 s is our frame 14.**
- Independent check using the stated ranges: the stated ball range changes from 1.818 m at t=0 to 1.7288 m at t=0.6, a change of -8.92 cm. My 3D model gives the same change at our frame 14.05. This holds for any ball-radius offset, because the surface/centre offset cancels in the difference.

### Route 1: 3D board-plane model (`model3d.py`, `final.py`)
- Board corners come from line fits to the board mask. Top-mid is (546.3, 307.0) and bottom-mid is (559.1, 416.0).
- I back-projected these with the slope_far range (1.854 m) and slope_near range (1.701 m), using f = 711 and the principal point at (640, 360).
- Checks: slope length 31.2 cm; width 23.6 cm (top) and 24.0 cm (bottom); bottom edge perpendicular to the slope direction.
- Ball centres lie on the plane offset from the board by r = 3.25 cm. Centroids come from background difference against the median of frames 34 to 48:

  | frame | y (px) |
  |---|---|
  | 12 | 329.2 |
  | 13 | 340.8 |
  | 14 | 354.0 |
  | 15 | 370.0 |
  | 16 | 389.2 |

- 3D steps between frames: 3.36, 3.75, 4.43 and 5.18 cm. A quadratic fit has residuals of 0.06 cm or less.
- Forward difference 14→15 × 25 = **110.8 cm/s**. At 24 fps it would be 106.3.
- Instantaneous v(0.6) from the fit is 104 cm/s. Changing r from 3.0 to 3.5 cm moves the result by less than 0.3%.

### Route 2: stated ranges only
- The ball range is interpolated linearly in image y between (frame 0, 1.818 m) and (frame 14, 1.7288 m), then back-projected.
- Forward difference 14→15 × 25 = **114.8 cm/s**. At 24 fps it would be 110.2.

### Physics check
- I got the table normal from the vanishing point of the table's side edges and the board's bottom-edge direction (h·d = -0.03, so the two are close to orthogonal). This puts the board at **32.6°**.
- A solid ball rolling down that incline gives a = (5/7) g sin θ = **3.77 m/s²**. The track measures **3.87 m/s²** on the 25 fps time base, or 3.6 at 24 fps.
- So the kinematics hang together. The stated "4.6 m/s²" is a noisy second difference and fits roughly.

### Other cross-checks
- The pixel step 14→15 is 16.0, 15.8, 16.1 and 15.1 px across four centroid methods (background difference on x, s and the original render; darkness-weighted centroid).
- Label-style displacement from 0 to 0.6 s (stated ranges, ball at frame 14) is 16.5 cm. This agrees with the current displacement answers of 16.2 to 16.6.
- Scale caveat: on the plane through slope_near, with f = 711, the table comes out about 63 × 76 cm against the expected 60.3 × 76. The stated ranges may be up to about 4% large. The labels use those same ranges, so I made no correction.

### Verdict on the current answer
- Before any noise correction, the label is about 111 to 115 cm/s if the labels use forward differences at 25 fps. Other alignments would be 106 to 110 (24 fps, frame 14) or 104 (instantaneous).
- The current 2240 = 83.8 is 0.75 of my estimate. That is low, but not more than 1.5x off from my raw number.
- The s and x renders (2251 = 125.6, 2262 = 125.1) share the same label, so 2240 should not differ from them by a factor of 1.5. Their 125 is about 1.12 to 1.18 times my raw value, which fits the stated small-ball correction.
- A value of 83.8 would need the forward difference 13→14 at 24 fps (90) or slower. Both the dropped-frame timing and the stated-range check put t = 0.6 at our frame 14, not 13.
- **Recommendation:** set 2240 the same as 2251 and 2262 (about 125 with the current correction; about 112 raw).
