# internet_0018: top-down drone view of a clay tennis court (3840x2160, 51 frames at 30 fps)

## Scale
- Prior: singles court width = 8.23 m. The singles sidelines are 920-927 px apart (fitted line profiles).
- Cross-checks: doubles/singles width ratio is 1.334 (true 1.333). Baseline to baseline is 2675-2681 px for 23.77 m. Service line to service line is 1437-1442 px for 12.8 m.
- Scale is about 0.00889 m/px along x and 0.00891 m/px along y. It is nearly uniform, with a slight drift from left to right (923 px at the left, 927 px at the right).
- Camera: ECC affine relative to frame 0 gives a total drift of about 11 px and a 0.3% scale change. Motion is about 0.3 px per frame near t=1.5 s, which is negligible.

## Q2089: distance between the players at the start (frame 0)
- P1 (left, just behind the baseline): feet at about (795,678), body at (780,650), head at (768,635).
- P2 (right, serving): feet midpoint at about (3588,1188), hips at (3635,1190), head at (3692,1213). Viewing from the side stretches the figure outward from the nadir.
- Distances: feet to feet 2839 px = 25.2 m, body to body 2906 px = 25.8 m, head to head 2981 px = 26.5 m.
- Answer: 25.5 m. Confidence: medium-high.

## Q2090: distance from the benches to the court
- The benches are at the top edge of the frame. Their leg bottoms on the ground are at y of about 97 (left bench) and 86 (right bench). The front edges of the seats are at about 85 and 72.
- The doubles sideline (court boundary) is at y of about 430 near x 2000-2400.
- Gap: 334-358 px, which is 2.98-3.19 m. Measured to the bench centre it would be about 3.4 m. Measured to the singles sideline it would be about 4.4 m.
- Answer: 3.1 m (bench front to the outer court line). Confidence: medium, because it is unclear which reference points the question means.

## Q2091: ball speed at 1.5 s (frame 45)
- The ball was tracked by colour in frames 38-47 (serve from the right player toward the net). Step sizes per frame were 150, 146, 141, 135, 132, 127, 124, 119 and 115 px. The ball slows steadily, which is consistent with air drag.
- Speed at frame 45: backward difference 124.1 px/frame = 33.2 m/s; central difference 32.5 m/s; quadratic or cubic fit 32.4 m/s at frame 45 and 33.0 m/s at frame 44.5.
- A 3D height/perspective correction (estimated drone height about 30 m, ball height 1-2 m) would give about 30.6 m/s. The label is probably a 2D measurement.
- Answer: 32.5 m/s. Confidence: medium-high.
