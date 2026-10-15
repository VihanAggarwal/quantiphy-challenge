# simulation_0154: shark crossing the frame (2D, static camera, 48 frames at 24 fps, 1920x1080)

Prior: shark speed = 7 m/s. Q353: shark length. Q354: shark displacement over the clip.

## Method
- The camera is static: the sand-dune silhouette does not move (median shift 0 px). The shark swims from right to left at a constant image row. It enters at frame 0 (snout at about x=1784) and has left the frame by frame 47.
- I made a median background of all frames and took |frame - bg| as a silhouette map. Bubbles and caustics were removed by keeping only large connected components.
- Pixel speed came from linear fits of crisp silhouette edges, which are not affected by the moving light shafts that biased textured template matching:
  - dorsal-fin leading and trailing edges on 10 rows, frames 6-38: 58.7-58.9 px/frame (median 58.78), residual about 1.5 px
  - pectoral-fin edge, frames 14-42: 58.63 px/frame
  - lower caudal-lobe leading edge, frames 14-45: 58.59 px/frame
  - so v_px is about 58.7 px/frame (1409 px/s), giving 7/1409 = 0.00497 m/px
- Shark size stays constant (dorsal-to-snout offset 396-409 px, height constant), so the motion is fronto-parallel.
- Length in pixels: snout tip to the upper caudal-lobe tip. The snout tip is 396 px ahead of the dorsal leading edge (crisp frames 7-8). The tail tip is 500-527 px behind it; the tail sways. Snout-to-tail extent in frames 15-26 is 915-928 px, mean 921. I used about 923 px, the straight-body maximum.
- The whole-silhouette frame-to-frame shift shows a mild hump (about 50 px/frame at frames 1-3, about 59.7 at frames 18-22, about 56 at frames 40-44). Most of the hump comes from tail sway and lighting on the head; the dorsal fin shows constant speed. Summing the shifts gives about 2695 px of total motion over 47 intervals (mean 57.3 px/frame).

## Answers
- Q353 length: 923 px x 0.00497 = 4.59 m. If the prior were the mean speed over the clip instead, it would be 4.69 m; using the peak speed, 4.51 m. **Answer 4.6 m.** Confidence: medium-high.
- Q354 displacement over the clip (frame 0 to frame 47, 47 intervals): 7 x 47/24 = 13.71 m at constant speed. The measured pixel path gives 13.4-13.7 depending on the scale convention. **Answer 13.7 m.** Confidence: medium-high (14.0 if the full 2 s were used).
