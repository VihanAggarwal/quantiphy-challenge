# simulation_0098 (V2MS: boat on water surface, shark below, both moving left; static camera)

Prior: shark speed = 3 m/s (applied to shark origin = body centreline).

## Measurements (code: track2.py, feat2.py, fintip.py, edges.py, sharkext2.py)
- Video 1920x1080 (looks upscaled from 960x540), 73 frames @24 fps; frames 0 and 1 identical, then constant velocity.
- Fixed-anchor template tracking of individual features shows clear depth parallax:
  - Shark centreline features (dorsal top, back, tail tip, snout): 10.745 px/frame; near-side gills 10.871,
    pectoral fin 10.876, pectoral fin tip 10.91-10.95 (delta = 1.5-1.9% closer than centreline).
  - Boat centreline features (bow stem 17.87, stern pole 17.878, rudder 17.873, mast top 17.95): ~17.88-17.95 px/frame;
    near-side hull letters 18.72, cabin wall 18.32, railing 18.46.
- Scale at shark centreline: 3 / (10.745*24) = 0.011633 m/px.
- Shark depth vs boat depth cannot be fixed geometrically (snout "hole" is a material artefact: shark is not yawed,
  so it is not a clipping plane). Assumed same depth plane (2D design). Strong support: boat speed then = 4.99-5.01 m/s
  and boat length = 10.00 m, both round numbers.

## Answers
- 179 boat speed @1.0 s: 17.89 px/fr * 24 * 0.011633 = 5.0 m/s (constant velocity). Confidence: medium-high (depends on same-plane assumption, supported by round numbers).
- 180 boat length: bow stem tip -> stern rub strake (both centreline) = 860 px -> 10.0 m. Confidence: medium-high.
- 181 shark length: snout tip (faint outline of transparent snout material) -> upper tail-lobe tip = 279.5-280 px -> 3.26 m. Confidence: high.
- 182 shark height: dorsal top 851.7 to pectoral fin tip 955.5 = 103.7 px; fin tip is ~1.7-1.9% nearer than centreline,
  so its image is pushed ~7 px down (horizon ~560): corrected ~96.5-97 px -> 1.13 m (uncorrected would be 1.21). Confidence: medium.
