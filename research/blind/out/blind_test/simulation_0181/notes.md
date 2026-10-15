# simulation_0181: box falls onto an inclined conveyor and slides down it (24 fps, 40 frames)

## Method
- The camera is static. I made a median-background mask (colour difference > 30) and tracked the box by template matching (sub-pixel):
  - fall phase: a patch on the frame-0 face, frames 0-7;
  - slide phase: a patch on the frame-20 face, frames 12-35.
- Fall (frames 0-7): the box starts from rest with a clean parabola. Pixel acceleration is 2561 px/s^2 (fit residuals under 0.1 px).
- Slide (frames 12-32): the box moves along a 28.5 deg image path with constant acceleration of 615 px/s^2 (fits over different windows give 593-631, rms 0.4-0.7 px).
- Scale cross-check:
  - from the prior: 615 / 2.338 = 263 px/m;
  - from gravity: 2561 / 9.81 = 261 px/m.
  - The two agree within 1%, so I used 262 px/m. This also shows that the fall and the slide are at the same depth (planar motion).
- Speeds come from a quadratic fit of path length against time, using backward differences:
  - at 1.0 s: 761 px/s, which is 2.90 m/s;
  - at 1.5 s: the fit extrapolates to 1067 px/s (4.07 m/s). However, the box reaches the end of the conveyor at that point, becomes occluded and tips over. Direct corner and patch tracks for frames 32-37 give about 850-990 px/s, so I compromised at 3.9 m/s.
- Acceleration over 0-0.3 s is free fall (contact with the ramp starts at about frame 7.5):
  - g in pixel units is 9.77 m/s^2;
  - finite-difference variants give (v at frame 7 - 0) / 0.3 = 8.86, or 9.11.
  - I answered 9.4.
- Sizes are measured on frame 0, when the box is axis-aligned:
  - the front face is about 280 px wide (x 379 to about 657; the side face shows from 657 to 704) and 192.5 px tall (y 228 to 420);
  - a slanted top flap rises about 21 px above the face;
  - the perspective of the side and bottom faces suggests the back is about 1.18-1.2 times as far as the front;
  - the tracked patches lie on the front face, so the 262 px/m scale applies to it directly.
  - Width = 1.07 m.
  - Height = 0.735 m without the flap and about 0.82 m with it. I answered 0.775.

## Confidence
- 436: medium (it depends on the difference convention).
- 437: high.
- 438: medium-low (end-of-ramp tipping).
- 439: medium (the side-face boundary is uncertain).
- 440: medium (whether the flap counts in the height).
