# simulation_0086 — top-down 2D view, Cybertruck-like car (moves left, accelerating from rest) + cyclist (moves right, constant speed)

Method
- Static camera, uniform gray ground. Subpixel edge tracking: car front nose / rear bed edge (rows 600-710), bike wheel tips (rows 476-479).
- Car px acceleration (quadratic fit, frames 2-44): front edge 0.529-0.531, mid 0.525 px/frame^2; parabola vertex at frame ~0
  (video frame k <-> t=k/24; frame 1 is a near-duplicate of frame 0). After frame ~46 the car's acceleration is not constant
  (bump to ~0.79 then ~0.3 px/f^2 near the end); the early regime was used as the prior's acceleration. It gives car length 5.70 m,
  matching a real Cybertruck (5.68 m), which supports this choice. a_px=0.531 -> s=4.03/(576*0.531)=0.01318 m/px at car-feature height (~1 m).
- Perspective: rider's head/handlebars shift relative to the wheel tips as the bike crosses the frame, and template vs tip speeds differ by ~1%
  -> camera height ~55 m (FOV ~28 deg). Scale at bike-wheel-tip height (0.35 m) = s*1.012 = 0.01333 m/px.
- Bike: 16.03 px/frame at the tips (constant) -> 5.13 m/s. Length 126.5 px tip-to-tip -> 1.69 m.
- Car: length 432.3 px -> 5.70 m. Width: mirror-to-mirror 187.6 px -> 2.46 m; wheel flares 160 px -> 2.12; body 146 px -> 1.92.
  Answered 2.40 (AABB most likely includes mirrors; shaded slightly toward body).
- Distances (origin = bbox centres; bike origin offset 0-0.3 m behind bike centre considered; small dz included):
  t=1.0 (frame 24): 5.26-5.53 -> 5.45; t=2.0 (frame 48): 16.08-16.38 -> 16.3.
- Car speed at 1.5 s = a*(35.5+0.1)/24 = 5.98 m/s (backward diff frames 35-36; measured 5.94).

Confidence: car length/speed high; bike speed/length medium-high; distances medium (origin convention, time base); width medium (mirror ambiguity).
