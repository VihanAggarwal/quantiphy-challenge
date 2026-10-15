# simulation_0197 (S2MS, 2560x2560, 50 frames @30fps)
Scale: "skynova" text runs vertically on the left of the bottle (rotated 90 deg); its horizontal image extent (white-letter mask, x 1106-1185) = 80 px = 0.00188 m -> 2.35e-5 m/px.
- 497 plunge tube diameter: rotated image so tube horizontal (30.7 deg); outer edges 1317..~1537 -> ~218 px -> 0.0051 m (medium).
- 498 droplet width: hanging drop widest ~110 px -> 0.0026 m (medium; ambiguity whether the tip blob counts).
- 499 text vertical height: interpreted as word length (world vertical AABB). Letters A,V,O at pitch ~143 px, glyph ~128 px; 7 letters -> ~986 px -> 0.0232 m. Word partly off-frame -> extrapolated (low-medium). Alt (letter cap height) would equal prior.
- 500 neck diameter: threads ~700 px, bottom flange ~780 px -> 740 px used -> 0.0172 m (medium).
- 501 body diameter: edges ~1004..2160 -> ~1160 px -> 0.0273 m (good).
- 502-504 bubble speed: template-matched bubble in pipette, backward differences px/frame ~10.7 / ~12.6 / ~12.4 -> 0.0076 / 0.0088 / 0.0087 m/s (medium-good).
Real-world sanity: neck ~18 mm (18-415 finish), body ~27 mm, pipette ~5 mm -> consistent with real dropper bottle.
