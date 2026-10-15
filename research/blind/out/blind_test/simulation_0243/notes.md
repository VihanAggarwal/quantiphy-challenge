# simulation_0243 (V2MC, antelope crossing road, prior speed 1.277 m/s)
- Static camera (sky diff ~0.8). Antelope walks left->right at constant depth (hoof y ~1546 throughout).
- Torso template-matching track: x 281 -> 713 px over 74 frames => 175 px/s (linear fit 170-172). Scale s = 1.277/175 = 0.0073 m/px.
- Mask (composite background frame74-left / frame0-right) frames 20-50: height horn-top 1126..hoof 1546 ~ 407-421 px (median ~415);
  x-extent tail..nose 461-497 px (median ~480).
- Q817 height = 415*0.0073 = 3.03 m (conf medium-high). Q818 length = 480*0.0073 = 3.50 m (medium; tail swing).
- Q819 left tree: top y~360, base hidden behind bushes (bush front line y~1545, trunk visible to y~1370). Horizon ~1390 (far road / terrain).
  Tree at antelope depth -> 8.7 m; slightly behind bushes (depth ratio ~1.2-1.3) -> 10-11 m. Answer 10.0 m (low confidence).
