# internet_0032 — rowing boat on a lake, moving right-to-left (prior: boat length 3.5 m)

## Method
- Camera static: phase correlation on treeline and reeds shows less than 0.5 px drift over 220 frames.
- Boat segmented by dark threshold (gray < 35, the silhouette is about 0-10 against water at about 70), largest component in ROI x300-1100, y440-620.
  Bow tip = leftmost mask pixel in rows 490-515 and stern = rightmost in rows 514-527, both with subpixel threshold crossing.
  Overlay checked visually (frames/overlay.png). Frames 0-2 are duplicates (the video freezes at the start).
- Boat centre = (bow+stern)/2, smoothed over 5 frames. Keyframes are 0, 60, 135 and 210.
  - Centre displacement in px: 81.9 / 112.8 / 118.9 (bow: 87.8 / 118.2 / 124.5).
- The boat's apparent length grows linearly from 215 px (t=0) to 249 px (t=7), a 16% increase, while its vertical size and image y stay about constant.
  So the boat is turning toward broadside at about constant depth; it is not approaching the camera.
- Scale: in a 2D annotation the scale would be the boat's pixel length, but which frame it came from is uncertain (first frame 215 px, middle 233, end 249).
  I used a hedged constant L_ref = 221 px, so 3.5/221 = 0.01584 m/px.
- Speed = distance / interval. Acceleration = (v_next - v_prev) / (gap between interval midpoints): 2.25 s, 2.5 s, and 4.75 s for 0-7 s.

## Variants (d1, d2, d3 in m; a1, a2, a3 in m/s^2)
- Centre, first-frame scale: 1.326, 1.825, 1.924; a = 0.030, 0.016, 0.022
- Centre, mid scale: 1.233, 1.697, 1.789; a = 0.028, 0.015, 0.021
- Bow, first-frame scale: 1.420, 1.912, 2.015; a = 0.024, 0.017, 0.020
- Per-frame scale (3.5/L(t)) integrated: 1.297, 1.705, 1.711; a = 0.015, 0.001, 0.008
- Quadratic fit over the whole track (centre, L=221): a = 0.019 m/s^2

## Answers
- 3013 d(0-2) = 1.30 m (medium confidence, about ±8%)
- 3014 d(2-4.5) = 1.79 m (medium)
- 3015 d(4.5-7) = 1.88 m (medium)
- 3016 v = 0.649 m/s, 3017 v = 0.715 m/s, 3018 v = 0.753 m/s (medium)
- 3019 a = 0.026, 3020 a = 0.015, 3021 a = 0.020 m/s^2 (low confidence)
  - These are small differences of speeds and depend strongly on the scale convention and on stroke phase.
