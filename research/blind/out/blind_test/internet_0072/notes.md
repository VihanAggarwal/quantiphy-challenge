# internet_0072 - credit card moved by hand (static camera, 2160x3840, 39 frames @30fps)
Method: HSV mask of the saturated red card (hue>168 or <2, sat>130), largest component per frame; bbox top-left + centroid tracks.
Scale: card length 8.56 cm = ~422 px (stable frames 28-38, minAreaRect 418-426 px) -> 0.0203 cm/px.
- 3271 width: card height ~290-293 px vs length ~422 px -> 8.56*291/422 = 5.87 cm (measured ratio 1.45, not ISO 1.586; ISO would give 5.40). Confidence medium.
- 3272 v(0.5s, f15): smoothed 32.3 (top-left) / 32.4 (centroid) cm/s; raw ~31. Confidence medium-high.
- 3273 v(1.0s, f30): smoothed 7.6 / 6.9; raw backward 9.0. Answer 7.6. Confidence medium.
- 3274 a(0.5s): card decelerating after peak at f13-14; smoothed |a| 55-80, raw central diff ~130. Answer 90. Confidence low.
