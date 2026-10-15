# simulation_0040 - eagle over beach + walking man (S3MC, 24 fps, 1080x1080, 72 frames)

## Scene / camera
- Static camera, aerial oblique view. The man is seen from above-front (face, shirt, legs visible; head 36-37 px
  above the stance foot, shoulders ~16 px), walking toward the camera (down in the image).
- Camera tilt from nadir theta estimated from: man's height/width projection (~36-38 deg), gait step/height (~34 deg),
  eagle wing-axis vs flight direction (perpendicular for ~37-41 deg), and eagle range-rate for level flight (37.4 deg).
  Used theta ~ 36.5 deg.
- Scale: eagle body (beak-tail) 28-29 px (50% / 30% alpha threshold), foreshortening 0.975 -> ~29.5 px for 0.8 m
  -> k_e ~ 36.5 px/m at t=1 (f ~ 6500 px if R ~ 179 m, FOV ~ 9.5 deg).
- Shadows (sun lamp): eagle->shadow offset (365,-55) px vs man's head->head-shadow (88,-11.5) px => eagle ~4.1x
  the man's height above ground (~7 m). This is NOT consistent with the depth_info (eagle only 3.65 m closer than
  the pelvis), and the man's depth_info (+0.09 m/s) contradicts his visible approach to the camera (should be
  ~ -0.8 m/s). So depth_info is internally inconsistent; I used image geometry + the size prior instead, and took
  k_h = k_e / 1.049 (man ~8.8 m farther than the eagle).

## Measurements
- Eagle track (background-subtracted centroid, averaged over whole flap periods of ~24.5 frames):
  (390, 102) px/s in the image, steady.
- Man (white-shirt centroid): 36.4 px/s mean down the image, 38 px/s locally at t=1 (gait phase), 2.6 px/s in x.
- Eagle max tip-to-tip (Feret) on sand frames 5 and 31: 56.5-57.4 px, direction (-23,51).

## Answers
- 1160 wingspan: ground-plane de-foreshortened tip-to-tip ~68-69 px / 36.6 px/m = 1.87-1.90 m at max flap spread;
  ratio W/L ~2.35 -> 1.88; nudged up for possible not-fully-flat wings / thin tips -> 1.95 m. Confidence medium.
- 1161 eagle speed at 1 s: sqrt((390/36.5)^2 + (102/(36.5 cos36.5))^2) = 11.24 m/s; depth-rate route
  sqrt(10.68^2+2.82^2+2.17^2) = 11.26. -> 11.25 m/s. Confidence medium-high (k_e +-4%).
- 1162 man's speed at 1 s: 38/(34.8*cos36.5) = 1.36 (local), 1.30 with mean image speed -> 1.33 m/s.
  Risk: if GT followed the (inconsistent) depth_info, it would be ~1.07 m/s. Confidence medium-low.
