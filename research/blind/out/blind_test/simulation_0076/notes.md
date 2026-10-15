# simulation_0076 notes

Video: 1920x1080, 24 fps, 72 frames (frames 0 and 1 are identical). Camera looks straight down at a gray ground plane;
two men walk leftwards side by side: black shirt / red trousers (upper, y~410) and white shirt / jeans (lower, y~600).
Their gait cadence is the same, but the white-shirt person takes longer strides.

## Method
- Background = median of frames. Foreground = big difference from the background or high saturation.
- Per person and per frame: a hair blob (brown HSV, the largest component near the previous position), and a torso centroid
  (shirt pixels plus hair inside a 75 px disk around the head). The shirt centroid alone was used as a cross-check.
- Perspective check: the gap between head and torso grows linearly with distance from the image centre (x=960, y=540)
  and is about 5% (head vs shoulder plane). That fits a camera looking straight down from roughly 6-7 m. Each height
  plane is just a uniform scale, so ratios taken within one feature plane (speeds and distances) do not depend on the
  plane. That makes them valid for the pelvis plane as well.
- Scale: black-shirt speed = 1 m/s. Linear fit over frames 1-71 gives a black torso speed of 275.9 px/s (hair 291.6, shirt 274.0).
- White-shirt speed, by linear fit: torso 361.3 px/s, so the ratio is 1.310 (shirt 1.311, hair 1.298). Windowed ratios around t=1 s are 1.28-1.30.
  Answer: 1.30 m/s.
- Distances: pixel distance between the two people / black speed in px/s, in the same feature plane.
  t=1.0 s (frame 24): hair 0.754, torso 0.757, shirt 0.755; 5-frame smoothed and linear fits agree (0.756-0.760). Answer: 0.757 m.
  t=2.0 s (frame 48): hair 0.937, torso 0.940, shirt 0.945; linear fit 0.915-0.938. Answer: 0.94 m.
- Plausibility: lateral separation 0.69 m, shoulder width about 0.47 m, white walks at 1.3 m/s. All are realistic.

## Confidence
- Q67 (white speed): medium-high. The ratio is robust at ~1.30 ± 0.02. Unknown: whether the ground truth is the pelvis's instantaneous speed or the mean speed (gait oscillation of ±5-10%).
- Q68 / Q69 (distances): high. All features agree within 1-2%. The answer depends on the 1 m/s prior being the black person's mean speed.
