# internet_0004 - wood block, ruler, pencil, jigsaw (960x540, 25 fps, 428 frames)

## Scale (ruler, prior 1 cm)
- Ruler laid across the board top, front edge flush with the end face (pencil tip touches the face corner at (755,240)).
- Tick-row intensity profile (frames 40/50/95), sub-pixel minima, linear fit of tick index -> x: 5.294-5.307 px per small tick,
  no perspective trend across 740 px. Long ticks (autocorrelation on rows above tick row) every 53 px -> small ticks are mm.
- Scale: 53.0 px/cm at the end-face plane.

## Sizes
- End-face width (edge profiles, frames 0-160): 547-549 px, stable throughout video -> 548.5/53.0 = 10.35 cm (length).
- End-face height (zoomed crops frame 130, left/mid/right): 107.5 / 108.5 / 110 px -> ~108.7 px -> 2.05 cm (thickness).

## Pencil (qid 2028)
- Blue paint segmented in HSV, PCA axis, tip = blue end + 68 px along axis (verified on frames 62/75/82 where graphite tip visible).
- Tip rests at x=755 (block right edge) frames 59-64, moves left from frame 65, at x=237 on frame 82, past left edge (208) by frame 83
  (crossing ~82.3). Distance ~547 px = 10.3 cm in ~18 frames (0.72 s) -> ~14.4 cm/s. (Jerky per-frame steps suggest frame-rate
  conversion; average is unaffected.)

## Saw (qid 2029)
- Red plunger housing centroid tracked (HSV), referenced to block left edge (block drifts ~+10 px in image).
- Blade at left edge, stationary until ~frame 221 (motor on ~208), moves right ~2-3.3 px/frame, off-cut drops at frame ~411-413.
- Relative travel 529 px; cut plane is ~5% deeper than the front face (new face after off-cut: 519 px vs 545 px) so travel ~ board width ~10.35-10.5 cm.
- Time 7.6 s (221->411) gives 1.36; from motor start 208 gives 1.27; front-face scale gives 1.31. Answer 1.33 cm/s.

## Confidence
- 2026 length 10.35 cm: high. 2027 thickness 2.05 cm: medium-high (edge choice +-3%).
- 2028 pencil 14.4 cm/s: medium (start/end frame choice +-6%). 2029 saw 1.33 cm/s: medium (start definition +-5%).
