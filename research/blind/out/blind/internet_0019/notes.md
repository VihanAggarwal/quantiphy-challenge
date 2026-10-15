# internet_0019 - beach silhouettes, ball passed from left kicker (A) to right receiver (E)

Video: 1280x720, 40 frames, dataset fps 30 (1.33 s). Static camera (median-background subtraction is clean).
People at t=0 (left->right): A passer (bicycle-kick pose, x~465), B girl (~525), C tall middle (~590), D kid (~750), E receiver (~835, walks left, heads the ball at frames 38-39).

## Scale (prior g = 9.8 m/s^2)
Ball tracked frames 3-38 by median-background subtraction (area ~280 px, bbox 19x19), weighted centroids.
Quadratic fit of y(t): a = 833.8 px/s^2 (two centroid variants 834.2 / 833.5; rms resid 0.65 px; window fits 770-875).
x(t) nearly linear, 166.4 px/s. Scale s = 9.8/833.8 = 0.011753 m/px (single planar scale, 2D video).
Ball apparent diameter ~constant (18.5 -> 18.8 px), so little depth motion.

## Measurements
- Ball diameter: integrated-darkness area -> 18.7 px, bbox 19 px; used 18.8 px -> 22.1 cm (soccer ball, plausible).
- C middle: head top 212.3 (sub-px threshold), feet ~361 (legs cross foam line to 360-361; sand below is black) -> 148.7 px -> 174.8 cm.
- A passer (measured upright, frames 18-25): head top ~230.8, feet ~357 (glare region, uncertain) -> 126.2 px -> 148.3 cm.
- E receiver (frame 0, walking): head top 213.3, feet ~362 -> 148.7 px -> 174.8 cm.
- Distance A-E at t=0: silhouette centroids A~465-467, E~835 -> ~370 px -> 4.35 m (range 4.30-4.42 by reference point choice).
- Ball speed at t=1.00 s (frame 30): fit instantaneous 3.50 m/s, backward-diff 3.37-3.40, central raw 3.55 -> 3.44 m/s.
- Average horizontal velocity: linear fit of x(t) 166.4 px/s -> 1.956 m/s (endpoint method 1.958).

## Confidence
ball size: medium-high; velocities: high (given 30 fps); heights: medium (feet hidden in dark sand, +/-2-3 px; A depends on frame choice);
distance: medium (reference point ambiguity).
