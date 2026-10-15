# internet_0038 (top-down MacBook Pro + Magic Mouse, 15 frames @26 fps)
Static top-down camera (laptop edges identical in frames 0 and 14). Planar scale from prior.
- Mouse (frame 14, fully visible): width 68.7 px, length 133.8 px (half-max subpixel). Scale 5.71/68.72 = 0.0831 cm/px.
- 3041 mouse length: 133.8 px -> 11.12 cm (spec 11.35). Answer 11.2. High confidence.
- MacBook base: 425 px wide (x 436-861), 290 px deep (y 239-529). -> 35.3 x 24.1 cm (spec 35.89 x 24.71, ratio matches).
  3042 "length" = long side -> 35.5; 3043 "width" = depth -> 24.4. Medium confidence (length/width naming could be swapped).
- 3044 spacebar: 107.4 px (stable over frames 0-9) -> 8.9-9.1 cm. Answer 9.0. High confidence.
- 3045 right hand: skin-mask centroid (988.4,532.5) f0 -> (713.6,436.4) f14; displacement 291 px (path 295 px)
  = 24.2 cm over 14/26 s -> 0.45 m/s average. Medium-high confidence.
Cross-check: laptop-spec scale (0.0845 cm/px) gives values 1.6% larger; answers set between the two.
