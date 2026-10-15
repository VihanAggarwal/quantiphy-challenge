# simulation_0241 (V2MC, top-down static camera, 24 fps, 49 usable frames; frame 49 is a loop artifact)
Scene: nadir view of a house (cross-gabled roof) with brown horse (upper, trailing = "horse at the back"), white horse and rabbit walking +x.
Scale: brown horse centroid (colour mask) moves 2.684 px/frame nearly constant (lin/quad fits agree) = 64.4 px/s
 -> s = 0.874/64.4 = 0.01357 m/px at animal level.
Tracks: white horse (bg-sub centroid + template match) mean 4.5-4.65 px/f, local at t=1s 4.8-4.9 -> 4.72 used.
 rabbit mean 4.49-4.54, local 4.46-4.88 -> 4.52 used. All three show ~5% faster second half.
Lengths (x extents on 4x crops, several frames): brown ~145-160 px (tail) -> 150 px; white ~174-178 px; rabbit ~35 px.
House: roof edges measured on grid; cross-wing gables x 650..1382 at eave level (618..1424 at apex), main-wing gables y 95..718
 eave level (20..745 apex). Apex/eave radial ratios 1.10 (cross) / 1.16 (main) -> roof is well above ground, so house px extents
 must be shrunk by (H-h_eave)/H. Camera height not identifiable (needs roof pitch); assumed plausible f~1000-2200 px, eaves 3-5 m
 -> factor ~0.78-0.85. X (cross wing, longer) ~ 7.8 m -> length; Y ~ 7.0 m -> width.
Confidence: speeds/animal lengths medium-high (assuming brown = back horse); house dims low-medium (perspective assumption, width/length naming).
