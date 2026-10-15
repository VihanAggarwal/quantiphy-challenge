# internet_0001: top-down drone view of a multi-lane freeway, black SUV/minivan moving left to right

Setup: 3840x2160, 31 frames, dataset fps 24. The camera is static (phase correlation shows less than 2 px drift over the clip). The view is near-nadir: dash lengths are uniform (~300 px) across the frame. A small parallax (low parts of the car shift about 20-30 px relative to the roof over 2000 px of travel) suggests the camera is about 80 m up, so magnification from car height is only ~2%. That is ignored, since the ground truth is pixel/prior based.

Scale (prior: lane width = 3.66 m):
- Dash centroids come from a median background with a local-contrast threshold. I fitted the 6 dashed lane lines.
- Lane spacings centre-to-centre at x~1900 are 307, 324, 317, 305.5 and 332 px. The car's own lane (lines 4-5) is 305.5 px; the mean is 317.
- I used 310 px per lane as a hedge, giving 0.01181 m/px.

Car (template matching, sub-pixel):
- Displacement is 121.4-126.9 px/frame. The average over frames 0-26 (while visible) is 123.2 px/frame, with y drift ~1.6 px/frame (negligible).
- Motion blur is ~32-40 px, from bright point streaks and edge ramps.
- Length: 445-455 px at the 50% edge crossings; the visible extent including blur is ~480-490 px. I used 465 px, giving 5.49 m.
- Width: 190-192 px (50% crossings on vertical profiles; there is no blur in y). I used 191 px, giving 2.26 m.
- Speed: 123.2 px/frame x 24 fps x 0.01181 m/px = 34.9 m/s.

Confidence:
- Speed is medium-high: the only real uncertainty is which lane width the scale is taken from, ±3%.
- Length is medium: it depends on how the blur is handled and on the lane choice, ±6%.
- Width is medium: depends on the lane choice and whether mirrors are included, ±4%.
