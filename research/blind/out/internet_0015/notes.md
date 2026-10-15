# internet_0015 - top-down drone view of a 2-lane road, 4 vehicles moving left in the upper lane

Vehicles at frame 0 (left to right): white sedan A, black car B, white hatchback C, motorcycle D (red/white).
"Car before the motorcycle" = C (white hatchback directly ahead of the motorcycle).

## Camera
Phase correlation of the off-road background: drift < 1 px in x over 143 frames, so the camera is effectively static.
Mild pincushion-like distortion: lower lane lines bow ~3 px at the image edges, and px speeds are ~4% higher near the edges than at the centre.

## Scale (prior: lane width = 3.66 m)
Sub-pixel line centres from the median background (image centre column): top edge line 520.1, double centre line 564.3 / 572.2, bottom edge line 617.5 (620.5 at the edges).
Lane width in px depends on the convention: 44.3 (edge line to nearest stripe), 45.3 (lower lane), 48.2 to 48.7 (to the centre of the double line, or road/2), ~50 at the image edges.
Used 47 px, which keeps the main conventions within about 5%: s = 3.66/47 = 0.0779 m/px.
Plausibility: car C, a Golf-class hatchback, is 59 px, so 4.6 m at this scale (4.4 m at 49 px).

## Measurements
- Tracks: background-median subtraction (the shadow-free rear edge) and template matching, both agreeing.
  Speeds in px/frame: A 12.25, B 11.85, C 11.94 (avg), D 12.1 (avg).
- Spacing at frame 0: centres A 481, B 890, C 1305, D 1682, mean spacing 400 px (rear-to-rear 394, front-to-front 406, bumper gap 344).
  At frame 30 the mean spacing is also about 399 px.
- Black car length: 58-60 px on 8x ruler zooms at f0/f10/f20, using 58.5 px. The front is merged with its shadow, so it was read visually.
- Motorcycle length: 26-33 px (f0 33, f20 32, f40 29, f60 26-28), using 30 px.
- Car C at t = 1.0 s (frame 30): local linear fit over +/-5 frames gives 11.70 (rear edge) and 11.75 (template), using 11.73 px/frame.

## Answers
- 2075 spacing: 400 px x 0.0779 = 31.2 m centre-to-centre, hedged slightly toward the bumper-gap reading (26.8 m), giving 30.5 m. Confidence: medium.
- 2076 black car: 58.5 px, giving 4.55 m. Confidence: medium (scale convention).
- 2077 motorcycle: 30 px, giving 2.34 m. Confidence: low-medium (blur and shadow at the front).
- 2078 motorcycle average speed: 12.09 px/frame x 30 = 362.6 px/s, giving 28.2 m/s. Confidence: medium.
- 2079 car C at 1.0 s: 11.73 x 30 = 352 px/s, giving 27.4 m/s. Confidence: medium.
