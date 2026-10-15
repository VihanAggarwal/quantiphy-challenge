# simulation_0300 - car accelerating away from fixed camera (A3SX)

Prior: a = 5 m/s^2 (exact). Depth: d(t=1)=17.8278 m, d(t=2)=23.1989 m.

## Motion / timing
- Median background (static camera) -> clean car masks; 9 rigid features (tail lights, exhausts, wheel hubs, mirror,
  fuel cap, badge) template-tracked frames 24-71; all tracks are straight lines (rms <0.2 px) meeting at one
  vanishing point VP_D = (-1121,-470) -> pure translation, no rotation.
- Early frames (2-8): image displacement vs frame 1 follows k(i^2-1) almost exactly (1:2.67:5:8 measured
  1:2.70:5.01:8.00); frames 0 and 1 are identical (frame 0 held). => s_i = 2.5*(i/24)^2 m, starts from rest at video
  frame 0, constant a = 5 (1/rho-vs-t fits are quadratic, free-a 3D fits give a = 4.98-5.03).
- Which video frame is "t = 1.0 s"? Solving for the origin from the two depths (range convention confirmed; Z convention
  is 3.5 deg inconsistent) puts it 0.2-0.5 m BELOW the ground if t=1 <-> frame 24, but at mid-car, axle height
  (x~2.0 m ahead of the tail lights, z~-0.35) if t=1 <-> frame 23. So the dataset clock looks like t = (i+1)/24.
- Speed (backward difference): frame 23 -> 4.69 m/s, frame 47 -> 9.69 m/s (frame 24/48 alternatives: 4.90/9.90;
  analytic a*t: 5/10). Answered 4.72 and 9.72 (within 4% of every candidate).

## Camera
- f from orthogonality: tail-light pair, exhaust pair and rear-flap pair (all symmetric) become exactly perpendicular
  to the wheel line / motion direction at f = 3530-3556 px -> f = 3556 px (= 50 mm lens on 36 mm sensor, HFOV 39.6 deg).
  Horizon through VP_D and VP_lat is horizontal (roll ~0).

## Sizes (car frame from motion-metric triangulation; longitudinal coordinates do not depend on f)
- Wheelbase 2.46 m (about 0.93 x a real LaFerrari). Hub z=-0.37; front tyre bottom z=-0.70 (relative to tail-light centre).
- Grey rear "flaps" (part of the car mesh, move with it): outer corners at lateral +-1.11 m, bottom z=-0.57.
- Body: front-left headlight corner x=3.71, front-left bumper corner x=3.40 (lateral -0.95); rear fin x=-0.23.
  The visual hull limits the nose to x<=4.30 (z=-0.35). Nose estimated at ~4.1 from real proportions -> L ~4.33.
- Roof: centreline features at the back of the roof z=0.32-0.34; hull bound <=0.40-0.44; peak ~0.37 -> H = 0.37+0.70 = 1.07.
- Width = AABB including the flaps: 2.22 m (the body alone is ~1.9 m and the mirrors ~2.0 m).

## Confidence
- 1453/1454 speeds: high (the clock offset changes them by at most 4%).
- 1456 width: medium (2.22 if the flaps count toward the AABB, which seems most likely; ~1.9-2.0 if they don't).
- 1457 height: medium (+-5%). 1455 length: medium-low (+-6%, the nose position is not directly observed).
