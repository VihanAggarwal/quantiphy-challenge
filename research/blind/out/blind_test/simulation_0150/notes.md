# simulation_0150 — yellow RX-7-like car crossing a parking-garage aisle (S3MC)

## Camera and scale
- The camera is static and level. The vanishing point of the aisle is at (959.5, 539.4), measured from the light strips and the curb lines, so the optical axis runs along the aisle.
- Car tracking: rim circles fitted to the hull of the white-rim mask, front and rear wheels. The wheelbase is 709.5 px.
- Motion model: the track fits a Blender Bezier smoothstep almost exactly (rms 0.08 px), with start at frame 0.00, duration 59.05 frames and amplitude 4040 px. Z is constant (rim v and radius are constant).
- Tire diameter is 183.5 px (horizontal silhouette 182-185 px; bottom radius 92 px), so the scale is 0.00417 m/px at the tire plane. Speeds use this scale and do not depend on f.
- Camera height h = 1.429 m, from the wheel centre (v=791.9), the contact point (v=884) and R = 0.382 m.
- Depth convention: Euclidean (range) fits the scene and optical-axis Z does not.
  - The back-wall base is at v≈698.3. The third pillar's side face reaches it, and that pillar's front face sits at v=704.5. So the bright floor line at v=705-707 is not the wall base.
  - With B1 at 23.44 m: f·h = 3724, giving f ≈ 2606 px (HFOV ≈ 40°).
  - Tire with Euclidean depth: Z_origin = 10.95 m. With f/Z_t = 240 this gives f ≈ 2600, which is consistent. Optical-axis Z would need f ≈ 2730, which is inconsistent with the wall.

## Answers
- **Speed** uses the backward difference of the fitted track at frame round(t·24).
  - v(0.5) = 6.44 m/s and v(1.0) = 9.85 m/s.
- **Acceleration** varies linearly in time, so it depends on the difference convention.
  - At t=0.5: backward second difference 10.48, central 10.20, instantaneous 9.92. Answer **10.3**.
  - At t=1.0: backward 3.69, central 3.41, instantaneous 3.13. Answer **3.6**. Medium confidence, because both the convention and the frame index are ambiguous.
- **Car width**: depth ratios come from slopes of image feature motion against wheel motion.
  - Licence plate centre gives about 1.09·Z_w. The spoiler fins give a far-outer/near-inner average of 1.091. The pop-up lids give about 1.09.
  - The body arch lip is at the rim plane (ratio 1.0007).
  - Half-width ≈ 0.987 m plus a small allowance for the tire/fender, so width ≈ 2.0-2.07 m. A 1.2x-scaled RX-7 FD would be 2.11 m (length 5.13 m, height 1.48 m and wheelbase 2.94 m all match 1.2x).
  - Answer **2.05**. Medium confidence.
- **Hazard marking height** is the stripe top to floor, using X = (u-cx)·h/(v-v0) and H = Δv·h/(v_floor-v0), so it does not depend on f.
  - The three pillars give 0.751, 0.755 and 0.759. Answer **0.755**. High confidence.
- **Pillar width** is the front-face extent, 160.7 px and 161 px at v_floor=772.5, giving 0.985-0.987 m. Answer **0.99**. The pillar depth along the aisle is about 1.08 m.
- **B1 lettering**: 180.5 x 168 px at Z = 23.44 m with f = 2606, giving **1.62 x 1.51 m**. If the optical-axis Z convention were right instead, it would be 1.55 x 1.44 m.
- **Pillar spacing**: the clear gap is 5.51 and 5.46 m, and centre-to-centre is about 6.59 m. The answer **6.3** hedges between the two readings. Medium-low confidence.
