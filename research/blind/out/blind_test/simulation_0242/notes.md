# simulation_0242 - notes

Static camera (phase correlation on the house shows ~0 px of motion). The video has 50 frames, but the last one (index 49) is a reset copy of frame 0, so I used frames 0-48. All three animals walk to the right, parallel to the house front. Their image rows stay constant, so they move along the camera X axis at constant camera depth Zc.

## Depth convention
The given distances change over time (brown -0.176 m, rabbit +0.155 m) while the image rows stay constant. That only fits a Euclidean range, not optical-axis Z. It also fits only if each object's origin is at ground level (rig root). Body-centre origins give camera heights that do not agree between the objects.

## Camera model (LM fit in fit.py; data from track3.py, track2.py and manual hoof rows)
Inputs to the fit:
- the six ranges
- the brown-horse speed prior (0.874 m/s)
- pixel speeds from template matching: brown torso 140.5 px/s, white 266.8 px/s, rabbit 270.0 px/s
- ground-contact rows: 545, 688 and 795
- torso template rows

Fit result: f ~ 2426 px (HFOV ~43 deg), tilt 40.5 deg, camera height ~10.35 m.
- The vanishing point implied by the objects alone is y ~ 3377. Window-frame verticals give ~3370 and the wall edges give ~3700-4000.
- Sizes vary by only about 2% across that range. Speeds vary by less than 0.3%.
- A variant that puts the torso features on the near flank (0.2 m toward the camera) gives f ~ 2381 and sizes about 1.8% larger. My answers average the two variants.

## Answers
- 1624 white horse speed: V = pixel speed x Zc_torso / f, which is mostly a ratio to the brown prior. Result 1.549 (1.545 in the near-flank variant), answered **1.55**. High confidence.
- 1626 rabbit speed: 1.557 / 1.577, answered **1.565**. Fairly high confidence.
- 1621 brown horse length: tail to nose. The head is hidden by a flat blob, so I used the blob's front edge. That is 325 px, back-projected onto the horse's midline plane: 2.07-2.11 m, answered **2.09**. Medium-high confidence.
- 1625 white horse length: tail to blob front, 412-432 px (the tail swings), giving 2.35-2.45 m. Answered **2.43**. Medium confidence.
- 1627 rabbit length: 81-100 px depending on hop pose, median ~84 px, giving 0.48-0.49 m. Answered **0.49**. Medium confidence.
- 1622 house width: brick ground floor is 7.02-7.15 m. The jettied timber upper floor is wider: 8.0-8.25 m depending on how far it overhangs. Bounding-box width should include the upper floor, and maybe the roof. Answered **8.2**. Medium-low confidence: the answer would be about 7.1 if only the brick wall counts.
- 1623 window width: outer frame is 112.4 px, or 0.75-0.76 m on the wall plane; inner glass is 103 px, or 0.69-0.70 m. Answered **0.74**, a hedge between the two. Medium confidence.
