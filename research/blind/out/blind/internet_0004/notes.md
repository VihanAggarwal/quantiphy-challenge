# internet_0004 - wood block marked with pencil + ruler, then cut with jigsaw (25 fps, 960x540, 428 frames)

## Scale
- Ruler (square blade) lies on the block top at the front edge in frames ~10-97. Its mm ticks were located on a 4x-upsampled
  profile (mean of frames 44-55): 108 ticks from x=174 to 741 with a uniform spacing of 5.29 px. A linear fit has 0.26 px residual,
  and fits over the left and right halves agree (5.293 vs 5.293). Every 10th tick is long (cm), so 1 cm = 52.9 px.
- Sanity check: the blue pencil body is ~36 px wide, which is 0.68 cm. That is plausible for a standard pencil.
- The camera zoom is the same in every shot: the block width is ~548-549 px in the ruler shot, the empty shot and the saw shot.

## Answers
- 2161 length (horizontal width of the end face): edges from per-frame gradient profiles are x=208.5 and x=757 (548.5 px), so 10.37 cm. Confidence high.
- 2162 thickness: top edge ~237 and bottom ~345.5 at mid-columns, and the corners give 105-110 px. 107.5 px gives 2.03 cm. Confidence medium-high, since the top edge is low-contrast and the bottom has fibres.
- 2163 pencil tip: the tip comes to rest at the right corner (x~755) in frames 59-64. It starts moving at about frame 64.6 and leaves the
  left edge (x=208) at about frame 82.6, then drops off the corner. 10.37 cm in 18 frames (0.72 s) gives 14.4 cm/s. A cross-check
  (64 -> 86, 645 px, 0.88 s) gives 13.9. Confidence medium; it depends on how the annotator chose the start and end times.
- 2164 saw: the motor starts at frame 206 (8.24 s), with the blade already at the block's left edge. The cut-off piece starts falling at
  frame 410.5 (16.42 s). The block width over 8.18 s gives 1.27 cm/s. The template-tracked roller wheel moves 539 px (8.5 px of that
  is block shift), i.e. 10.0-10.2 cm, giving 1.23-1.25 cm/s. Answer 1.25. Confidence medium-high.

Scripts are in scripts/ (ruler3.py, block.py, thick.py, blue.py, sawtrack.py).
