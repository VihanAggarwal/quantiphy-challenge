# sim3audit group3: simulation_0014, 0032_segmented, 0046, 0050, 0144

35 scored rows. **Result: no fixes proposed.** No row has two independent routes that agree within 8% and differ from the current answer by 15% or more.
The family label groups three unrelated scenes and two singletons:
- the street pair 0046 + 0050 (bicycle, walker, telephone booth, houses)
- the rocket pair 0144 + 0145 (0145 rows are not in this item; used only as a cross-check)
- the singletons 0014 (house, cart, nest) and 0032_segmented (basketball). 0032_segmented turns out to have a sibling outside this group, 0020; see section 4.

## 1. Street pair 0046 / 0050 (same Blender scene, different cameras)

| quantity | 0046 | 0050 | spread |
|---|---|---|---|
| walker speed | 1.24 (t=1 s) | 1.236 (stated prior) | 0.3% |
| walker height | 1.80 | 1.80 (pipeline; agent 1.78) | 0 |
| booth height | 3.02 | 3.04 | 0.7% |
| booth width | 1.17 | 1.23 | 5% |
| pillar distance | 3.60 | 3.45 | 4% |
| bike height (handlebar) | 0.985 | 1.03 | 4.5% |
| bike length | 1.66 | 1.67 | 0.6% |
| first step height | 0.155 | 0.165 | 6% |
| bike speed 1-2 s | 4.83 | 4.86 | 0.6% |
| wheel diameter | 0.65 (stated) | 0.65 (transfer) | 0 |

- Every pair agrees within 8%. No clip is scaled off, and no object was measured as a different object.
- Pillar question: I viewed frames 33 of both clips (`frames/bike_cmp.png`). The grey/stone arched-door house clearly projects toward the street (its stair base and pillars are nearer) in both views.
  - So the near door is the right-hand stone door and the far door is the green door, and the inner-pillar reading (~3.45 m) is the right one in both clips.
  - The alternative reading, 6.67 m, would require the green door to be the near one, which the frames contradict.

## 2. Rocket 0144 (cross-check with 0145)

| quantity | 0144 | 0145 |
|---|---|---|
| tyre diameter | 1.18 | 1.196 |
| rocket speed at t=1 s | 19.4 | 18.85 |
| rocket acceleration at t=1 s | 11.9 | 13.45 |
| average speed | 14.05 (35 frames) | 11.97 (29 frames, different window) |

- Both clips show the same launch (frame 24 comparison in `frames/rocket_cmp.png`).
- The two acceleration estimates differ by 12%. Each comes from a different Bezier-smoothstep fit (T=3.33 s vs 4.5 s). That is under the 15% bar, and neither value can be shown wrong. Keep.
- Vehicle width 2.41 and road width 2.6 are single-clip values. I found no clear error. The road is a narrow dirt track under the truck.

## 3. simulation_0014 (singleton)

Every size answer scales with 1/f. The agent used f=1700 with Euclidean depths.
- Its routes were: nest free fall plus range, giving 1600; house vanishing points, 1640-2150; vertical vanishing point, 1800.
- My own check (`scripts/s14_beams.py`) uses the convergence of the front-facade beams.
  - The mid-beam lower edge has slope -0.0115 (rms 0.27 px). The eave beam is about -0.019 and the low beam about -0.005.
  - The slope change with image row gives a front vanishing-point offset K of about 15-17k px. With the agent's side vanishing point (x=1241), that means f of about 2100, which would make sizes about 19% smaller.
- But gravity (f/Z = 338 px/m, so f ≤ 1900 for any origin) disagrees with that by about 30%. The side vanishing point rests on a narrow (~60 px) side face.
- So there are no two agreeing routes. Keep all six rows. The scene is at about 2.3x real-world scale under f=1700: door 6 m, barrels about 2.6 m, cart wheel 2.6 m.
- The cargo box height of 1.25 is the box's own height (local). The world AABB of the tilted box would be about 2.3.
  - The cart is one model, and a label for a sub-part cannot come from the object AABB. This is a question of interpretation, not an error I can show. Keep.

## 4. simulation_0032_segmented. Its sibling is simulation_0020 (not in this group)

- **simulation_0020 (1080x1080, 30 fps) is the centre crop, x offset 420, of the same render.**
  - Under the 0032 person/ball mask, the 0020 pixels equal the 0032 pixels: the median |difference| is about 15 (summed BGR) in every frame, against 485 outside the mask (`scripts/crop_check.py`).
  - The ball positions match: 0032 frame 60 is (799.7, 448.6), and 0020 has the ball at about (380, 447).
- Segmented 0032 shows only the person and the ball. The cars do not appear in 0032 (segmented out) or in 0020 (outside the crop).
  - So 1714 (orange car acceleration = 1.0) and 1715 (green car average speed = 6.0) cannot be re-measured. Both look like placeholders.
  - The 0020 background is a different street (concrete wall, barred windows, basketball stand), not the white-brick "MEOW" street of the 0033/0052-0057 family that states a = -2.86 for its orange car.
  - The 0032 green-car ranges (4.32 m at 2.5 s, 6.91 m at 3 s) are also hard to reconcile with that family's 12 m/s car crossing in front of the camera: it would have to appear in 0020, and it does not.
  - So I did not transfer -2.86. Keep both rows.
- The ball is keyframed, not ballistic. The flight y-acceleration is 0.19 px/frame^2 and x-velocity runs at a constant -10.7 px/frame until the hoop. Gravity would need f of about 245 px (hFOV about 150 deg, outside 8-103 deg).
  - The drop after the hoop saturates at 12.8 px/frame. So the gravity prior cannot set the scale.
  - The current 1711/1712/1713 values (1.762 m, 2.638 m/s, 0.278 m) come from the pipeline's default 60-deg FOV (f=1663).
    - 2.638 equals the ball speed just after release, frames 24-26 (about 10.6 px/frame at Z=13.8).
  - The 0020 agent, by an independent route (early drop), got person 1.78 and ball 0.30. These agree within 8%. Keep.
- Out-of-scope observation for whoever owns simulation_0020: its q9 ("velocity of the ball at 0.0 s") = 123 m/s (a wrap-around guess) is inconsistent with 0032 1712 ("initial velocity", 2.638). The two are the same render; they may or may not share a label.

## Files
- `scripts/`: extract.py, s32_cc.py, s32_ball.py (`s32_ball.json`), s32_person.py (`s32_person.json`), s20_rows.py, s20_vp.py, s14_beams.py, crop_check.py
- `frames/`: PNG crops and contact sheets, about 60 MB
