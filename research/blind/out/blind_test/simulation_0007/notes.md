# simulation_0007 — boat passing a wooden pier (top-down 2D view, 1080x1080, 24 fps, 74 frames)

## Scene / scale
- Camera looks straight down (boat's pixel size is the same at t=0 and t=3: 197.1 vs 196.8 px), so one m/px scale works for the whole water plane.
  The house, pier and boat all sit about 21-24 deg off the image axes, so I assumed the world grid follows the pier/house.
- Boat (prior: length 3.62 m): I segmented the white gunwale rim (V>110, S<90) and took its convex hull. Tip to tip it is 197.5 px,
  and it is 70.5 px wide. Small dark keel or stern bits and oar ends stick out at the stern by up to ~7 px. I used L=202 px,
  between the bare hull (197.5) and the world bounding box with protrusions (~205-208).
  -> scale 3.62/202 = 0.01792 m/px (the error band is about ±3%).

## Measurements
- Pier width: I rotated the frame so the pier's long axis (66.24 deg) is vertical and found the edges at the steepest gradient
  in 50+ cross-sections. The median width is 82.8 px, so 1.48 m.
- Pier length: the water end is at s=+165.5 px. The visible deck stops under a pole-shadow band at s ~ -155. The two mooring poles
  at the shore end have their bases at about s=-158 to -166. The deck alone is ~321 px and deck plus poles is ~331 px; I used 324 px,
  so 5.8 m.
- Boat speed: I tracked the boat with masked template matching (subpixel). The track is a straight line with no acceleration:
  3.2456 px/frame = 77.9 px/s, and local fits around frame 24 give 77.9-78.9 px/s. 77.9 x 0.01792 = 1.40 m/s.
- Distance at t=3 s (frame 72): the closest point between the pier's water-end edge and the boat hull outline is 106.7 px (1.91 m).
  The gap between bounding boxes aligned to the world/pier grid is ~102.5 px (1.84 m). I used ~105 px, so 1.88 m.

## Confidence
- Q1 width 1.48 m: medium-high. Pixel measurement is ±1%; the scale is ±3%. Risk: if ground truth were the box aligned to image axes it would be ~4 m, which I think is unlikely.
- Q2 length 5.8 m: medium. Where the pier ends on shore (deck only vs poles) gives ±2%, plus the scale uncertainty.
- Q3 distance 1.88 m: medium. The definition is unclear (closest surface vs bounding-box gap; centre-to-end would be 2.6 m).
- Q4 speed 1.40 m/s: high (constant velocity, scale ±3%).
