# internet_0056 notes
- 58 frames @30fps, 1920x1080. Small camera pan (~-7 px over clip, phase correlation on building/ground).
- Scooter wheels: front 330->946, rear 235->846 px over 57 frames; +7 px pan correction => ~620 px / 1.9 s = 326 px/s.
  Scale at rider plane: 2.64/326 = 0.0081 m/px.
- Q3159 rider height: cap top to soles 189 px (f0), 198 px (f57), avg ~193 px -> 1.57 m. Confidence medium-high.
- Horizon from two bollards (heights 167 px @ base 845, 92 px @ base 742) => y_h ~ 616; rider feet 126 px below horizon.
- Q3161 leftmost (fully visible) big palm: base y~682 (66 px below horizon => ~1.9x rider depth), top of crown ~y 0 (cut at frame top), 685 px.
  Naive 5.5 m; perspective-corrected ~10.5 m. Answer 10.0 (leaning perspective). Confidence low.
- Q3160 two foreground big palms at x~490 and ~1490 (1000 px). Naive 8.1 m; perspective 3D estimate (f~1370 assumed) ~14 m. Answer 13.0. Confidence low.
