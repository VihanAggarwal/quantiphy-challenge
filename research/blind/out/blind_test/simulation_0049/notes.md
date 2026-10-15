# simulation_0049 — notes

## Camera
- Static camera looking straight down the street. Street vanishing point from LSD + RANSAC on 47 street-parallel segments: (960.5, 535.5-537.7), i.e. the image centre, so zero pitch/yaw and principal point (959.5, 536.5).
- Focal length from the near manhole cover, assumed circular on a flat road. I fitted an exact projective circle model to 405 ring-ridge points: f = 1841 px. Edge-based fit with blur correction: about 1854. Approximate tangent formula: 1864. 35 mm on a 36 mm sensor gives 1867. Adopted f = 1860 (horizontal FOV about 55 deg).
- Cross-check: with f = 1860 the rider has normal proportions (shoulders 0.41 m, saddle 0.97 m, head 1.8 m above the road).

## Bike (prior 4.87 m/s)
- Depths 14.1134 / 18.9543 m with constant speed 4.87 m/s parallel to the optical axis give Z(t=1) = 14.000 m. The perpendicular offset b is about 1.79 m, which is consistent with an origin near ground level.
- Rear-tyre ground contact tracked over about 70 frames. 1/(v-cy) is linear in t, giving f*Hc = 3063 px*m. The rear contact is 0.33 m in front of the origin. This confirms the depth data and the constant speed. Hc = 1.647 m.
- Wheel: rack-strut / dropout ends sit 71.6, 72.1 and 70.6 px above the tyre contact in frames 0-2 (rear Z 8.80-9.10 m), so the radius is 0.344 m and D is about 0.69 m. The fender top lies about 3 cm above the predicted tyre top, which is consistent.

## Walking person
- The ground plane does not agree with the human depth_info (19.04 / 20.27 m). Feet at v = 770 (t=1) would need the sidewalk 0.7 m below the road. The image size ratio Z2/Z1 is 1.105, against 1.065 for the given ranges. Conclusion: the reported human origin is offset from the visible body. I used the body measured from the image.
- Sidewalk height from the left-curb face: hs/Hc is about 0.06-0.11; used 0.08, so camera height above the sidewalk is 1.515 m. Body Z(t=1) = 2818/233.5 = 12.07 m.
- Speed: the height and feet scale ratio for t = 1 to 2 is 1.104-1.105, so dZ is about 1.27 m/s. Lateral motion is negligible. The range rate of the reported origin is 1.23 m/s, which is a lower bound. Answer 1.27.
- Height: (v_feet - v_head)/(v_feet - cy) is 1.226 on average over 4 frames (range 1.200-1.231). 1.226 x 1.515 = 1.86 m.

## Telephone booth
- Base v = 663.7 and top v = 404.6, measured from intensity profiles. Height = 259.1/127.2 x 1.515 = 3.09 m (Z about 22.3 m, width about 1.2 m).

## Door pillars (right-hand brownstones)
- Near door: the arched doorway. Its left (far-side) pilaster is centred at u ≈ 1500.
- Far door: the pedimented doorway further along. Its right (near-side) column is centred at u ≈ 1377.
- Facade lateral offset X is about 4.0-4.2 m. Evidence: the bush extends to at least X = 4.1 at Z about 8, stoop outer faces sit at about 1.9-2.0 m, and the implied door sizes are plausible.
- dZ = f*X*(1/417.5 - 1/540.5), about 1.0*X, giving roughly 4.1 m.

## Confidence
- 1197 speed: medium (1.23-1.30 band).
- 1198 person height: medium (±5%, through f and hs).
- 1199 booth height: medium (±5%).
- 1200 pillar distance: low. The pillar identification and the facade offset are both uncertain (±20%).
- 1201 wheel diameter: medium (±6%).
