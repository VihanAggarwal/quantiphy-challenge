# internet_0033 notes
- Top-down table scene, 47 frames @25fps; slow camera drift ~0.8 px/frame up (SIFT affine), compensated.
- Fork scale ambiguous: fork on table at top 138 px (fully visible), fork at bottom-centre >=160 px (end under hand). Used compromise 150 px = 20.3 cm -> 0.1353 cm/px. Plates ~230-248 px (slight perspective).
- Tomato bowl tracked via red-tomato centroid. f0->f13: 280 px -> 539 px/s -> 0.73 m/s. f25->f40: ~115 px (hand occlusion biases centroid) -> 0.26 m/s.
- Avocado halves 91-107 px long -> ~13.8 cm. Baguettes 336/384/406 px -> used 384 -> 52 cm.
- Confidence: medium on speeds (fork choice +-10%), low-medium on sizes (which object instance).
