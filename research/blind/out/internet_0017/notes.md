# internet_0017 - desk top-down (keyboard, card, pin tin, clipboard+pen), 4096x2160, 28 frames @22 fps

## Camera / scale
- Camera static (phase correlation on plant/clipboard/tin/mouse: < 1 px jitter). Top-down view.
- Two credit cards: one HELD in the left hand (tilted ~35 deg about its long axis: 353 x 181 px, ratio 1.95 -> foreshortened width),
  one LYING FLAT on the table under the right wrist. Flat card measured from the union of dark pixels over all frames
  (wrist occludes middle) with 4 edge-line fits: short side 216.4 px, long 343.1 px, ratio 1.587 (ID-1 = 1.586) -> clean.
- Table-plane scale s = 5.4 / 216.4 = 0.02495 cm/px.
- Sanity: keyboard is an Apple Wireless Keyboard A1314 (battery tube), spec ~27.9 x 13.0 cm; table scale gives 28.5 x 13.35
  (silhouette incl. raised tube -> +2%); held-card scale (0.0298) would give 34 x 16 cm -> rejected as physically wrong.
- Lens distortion small (clipboard edge sagitta 0.6 px over 1037 px; card ratio exact).
- Raised objects magnified slightly (held card 353 vs 343 px long side -> ~3% at a few cm height => camera ~1 m up).

## Measurements
- Keyboard: gradient line fits to the four outer edges (median over frames): 1143 x 535 px -> 28.5 x 13.35 cm.
- Pen (on clipboard): end-to-end 570 px -> 14.2 cm (pen axis ~1 cm above table -> ~14.0 cm physical).
- Round tin: polar unwrap; rim ellipse ~390 (tangential) x 372 (radial) px, wall crescent ~45 px toward image centre
  (rim ~2.5% magnified). Rim diameter -> 9.3-9.7 cm; full silhouette incl. wall 403-418 px -> 10.0-10.4 cm.
- Middle fingertip (right hand, right of the two extended fingers): manual + automatic (skin chroma top point) track frames 5-13.
  Per-frame displacement (px): 25, 58-67, 87-97, 91-98 (8->9), 66-70 (9->10), 40, 29, 25.
  t=0.4 s = frame 8.8. Backward diff @9: 50-54 cm/s; central @9: 44-45; smoothed poly: 44-48; interp at 8.8: ~47.

## Answers (slight upward hedge toward the held-card-scale interpretation, still within ~4% of physical estimate)
- 2084 tin diameter: 9.8 cm (medium confidence; rim vs silhouette ambiguity)
- 2085 keyboard length: 28.9 cm (high-medium)
- 2086 keyboard width: 13.5 cm (high-medium)
- 2087 pen length: 14.4 cm (medium-high)
- 2088 fingertip speed @0.4 s: 49 cm/s (medium; motion blur at frames 8-9, convention unknown)
Main risk: if GT used the held (tilted) card's apparent width (~181 px), all answers would be ~19% higher.
