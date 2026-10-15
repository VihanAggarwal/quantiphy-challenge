# internet_0003 (pizza + Monopoly money, top-down, 2732x1440, 37 frames @24 fps)

## Scale
- Prior: monopoly money width = 7.5 cm. Interpreted as the SHORT side of a bill (the usual "width" of a banknote,
  and 7.5 cm is a typical real-banknote short side; 7.5 cm for the long side would be implausibly small).
  Measured bill aspect is about 1.92, so if the prior meant the long side, every answer below should be divided by about 1.9.
- Bill short side in pixels (frame 24): upside-down 500 bill left edge 151 px (vertical in image), "1" bill top/bottom edge 175-177 px
  (horizontal). They differ because the camera is tilted.
- Camera geometry: the camera is tilted about 19-21 deg from straight down. Evidence: the pizza ellipse is 1010 x 947 px, the glass foot is
  216 x 196 px, and the glass rim/foot offset points to a nadir below the image. Fitting the bill rectangles (same size, same aspect) gives
  f about 2600-3750 px and tilt about 18.5-21 deg. With that, the rectified pizza comes out circular (horizontal and vertical diameters
  agree to within 2%).
- Camera motion: slow vertical drift (about 4 px/frame for frames 0-20), estimated with ORB + partial affine on the table and board, and
  compensated for in the velocity.

## Measurements
- Pizza outer crust (11 edge points read by hand, frame 24): 1010 px horizontal, 947 px vertical. Rectified diameter = 44.5 cm.
  Naive pixel ratios: 50.2 (500 bill, horizontal), 47.0, 43.3 (1 bill), 40.6. Answer 46 (blend).
- Wine glass rim (outer): 244 px wide x 223 px tall. Bowl widest part about 276 px. Naive: 12.1 (500 bill) / 10.5 (1 bill).
  Planar-rectified rim: 11.5 cm. Answer 12.0.
- Pepperoni: radial a*-threshold ellipse fits on about 19 slices give a median of about 130 px (about 4 px outward bias), and
  hand-read slices are 123-133 px, so about 127 px. Naive 6.3 / 5.4, rectified 5.6. Answer 5.9.
- Pizza cutter at t=0.2 s (frame 5): tracked the dark cap blob. Speed is about 36-38 px/frame, which is 880-905 px/s after
  compensating camera motion (quadratic fit over frames 2-8). Naive 44 (500 bill) / 38 (1 bill), ground-rectified 41-43 cm/s.
  Answer 42.

## Confidence
- The main risk is the prior convention (short vs long side): about a 70/30 judgement in favour of the short side.
- Given the short side: pizza +-8%, glass +-15% (rim vs bowl ambiguity), pepperoni +-10%, velocity +-10%.
