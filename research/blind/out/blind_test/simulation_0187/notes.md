# simulation_0187 (A2SS, truck side view, static camera, 60 frames @30fps)
Method: frame-to-frame horizontal shift of truck region (masked template SAD, subpixel) frames 8-50 -> shift(i)=2.0726*i-0.606 px/frame,
residual 0.28 px; constant accel 2.0726 px/frame^2 = 1865.4 px/s^2. Scale = 10.757/1865.4 = 0.005767 m/px.
- Speed (backward diff): v(t=1s, f30)=61.6 px/f -> 10.29 m/s; v(1.5s, f45)=92.6 px/f -> 15.67 m/s. Confidence high.
- Length: truck never fully in frame; front extreme (mirror/rail) x=1382 @f38, rear extreme (tail-lift plate) mapped to f38 ~ -138 px
  (drifts -122..-146 depending on frame) -> 1523 px -> 8.78 m. Confidence medium.
- Height: top of roof rail y=353 to tire bottom ~935 -> 582 px -> 3.36 m. Medium.
- Tire diameter: ~134 px (front wheel f30, both axes) -> 0.773 m. Medium.
