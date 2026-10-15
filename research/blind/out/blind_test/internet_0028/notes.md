# internet_0028 — luggage carousel, top-down handheld 4K view (93 frames)

Prior: belt velocity 0.5 m/s. Questions: length of the blue/grey (deuter) backpack (2995), length of the orange suitcase (2996).
Note: dataset fps = 24, but the container plays at 20.53 fps (1088/53). I used 24 as the main convention and shaded the answers up a little to allow for 20.53.

## Measurements (full-res px, chained template tracking at half resolution: track.py)
- Everything on the belt moves to the right (+x). Speed depends on depth and image row, because the camera is tilted and the bag tops sit closer to the camera:
  - belt emboss marks (y~770): 48.5 px/frame; belt near the top (y~300): 45; belt pads (y~1100): 53; y~1400-1900: ~61
  - orange suitcase top face: 68 (y~1065), 74.5 at the tag (y~1575), 77 (y~2030)
  - blue backpack top: 67 at the top contour, 70 at the logo, 76-78 at rows 1450-1900 (frames 0-5), mean over frames 0-20 ~74.5
- The suitcase's extent grows down the image (2130 px at y=1100, 2372 at y=2100, frame 48), in proportion to its local speed. So extent/speed per row stays about constant at ~30.5-31.5 frames of motion.
- Orange body extent at the tag row: ~2240 px (frames 48-50). Not included: the grey trolley-grip housing on the left (~225 px) and the carry handle on the right (~60-80 px).
- Blue bag extent at frame 0: lid edge x≈495 to blue edge x≈3079, giving 2584 px (dangling strap excluded; with the strap ~2790).

## Answers
- Own-speed scale at 24 fps: blue = 2584/75.5 = 34.2 frames × (0.5/24) = 0.71 m; orange = 2240/74 = 30.3-31 frames, giving 0.63-0.65 m.
- Alternatives: 20.53 fps gives 0.83 / 0.75. A belt-plane scale (if the annotators tracked the belt rather than the bags) gives 0.88/0.77 at the bag rows and 1.11/0.97 at the emboss row. A 3D-corrected real size is ~0.78 / ~0.70.
- Final answers were picked to maximise expected score over these hypotheses: blue 0.76 m, orange 0.70 m.
- Confidence: medium-low for both. The main risks are which pixel speed the annotators used (bag vs belt) and the 24 vs 20.53 fps question.
