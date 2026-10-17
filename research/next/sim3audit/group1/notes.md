# sim3audit group1: notes

Scripts are in `scripts/` and frames/crops in `frames/` (PNG only, about 115 MB). 59 scored rows checked.

The group holds four unrelated scene families:
- box drop: 0182, 0184, 0186
- bird / house / cart: 0010 and 0010_seg (siblings 0011, 0012, 0013 belong to group2)
- street: 0045, 0048, 0048_seg, 0049 (siblings 0046, 0047, 0050)
- corridor walker: 0141, 0143

## Fixes proposed (5 rows)

| qid | clip | question | current | new | routes |
|---|---|---|---|---|---|
| 1383 | 0143 | man speed at 1 s | 1.35 | 2.35 | 0141-camera f (exact priors) 2.3-2.46; 0143 depth_info f 2.26-2.33; agent kinematics rescaled 2.67-2.81 |
| 1384 | 0143 | man speed at 2 s | 1.52 | 2.75 | same routes: 2.6-2.92 / 2.54-2.75 / 3.01-3.09 |
| 1192 | 0048 | telephone booth width | 1.42 | 1.17 | family 1.17 / 1.20 / 1.23 (0046 / 0047 nadir / 0050); 0048 cap geometry with family booth height 1.05-1.15 |
| 1754 | 0048_seg | telephone booth width | 1.42 | 1.17 | same footage as 1192 |
| 1647 | 0010_seg | average flight speed of bird | 4.8 (pre-agent) | 4.0 | 0010 track, net 965 px / 48 frames at f=4140 → 4.0 (3.8 if mp4 dropped frames); depth-anchored 3D displacement over 0-1 s = 3.5 |

### 0143 corridor: the agent used f=955, but the camera is the 0141 camera with f≈1900

- `bg_compare.py`: the median backgrounds of 0141 and 0143 match pixel for pixel (median abs diff 1.2 grey levels). The floor joints fall on the same rows in both clips (1064/1003/955/916) at the same lateral pitch, so it is the same camera, the same f and the same Hc.
- 0141 measurements (`track2.py`, `feet.py`):
  - Planted-foot staircase steps of 3.62e-4 in 1/(y-yh), period 12.56 frames.
  - Head/foot ratio 1.399 at mid-stance.
  - The 0141 prior speed 1.693 m/s (exact) gives K = f·Hc = 2446.
  - The stated height 1.8 m gives Hc = 1.28 m.
  - So **f ≈ 1890-1930** (a 35 mm lens). Cross-check: the tiles come out at 0.61 x 0.91 m, i.e. 0.6 x 0.9.
- At f=955, 0141's own walker would move at 0.85 m/s, against the stated 1.693. So 955 is impossible for this camera.
- The 0143 agent rejected f≈1723 (its depth_info scale) because the man's steps would be 1.1-1.6 m long, which it judged anatomically impossible. But this man's steps really are 1.6x the 0141 walker's, measured as a ratio within the same camera. He is a fast, long-stride walker, about 2.8 m/s.
- Human depth_info in this scene sits about 0.6-0.8 m short of the visible body (0141 shows the same offset at any f), so it is a weaker scale route.
- My 0143 track (`speed0143b.py`, head-peak frames plus torso x, f=1890):
  - Stride means: 1.91 (0.5 s), 2.46 (1.0 s), 2.70 (1.5 s), 2.79 (2.05 s), 2.91 (2.56 s).
  - Cubic fit: v(1)=2.45, v(2)=2.92.
  - Planted-foot strides agree: about 2.2 at 0.9 s, 2.76 at 1.4 s, 2.7-3.0 at 2 s.
  - Frames 24 and 48 are at mid-stance (head peaks 24.5 and 49), where pelvis speed dips, so I hedged slightly low: **2.35 / 2.75**.
- Not changed:
  - 1385, accel at 2.5 s (1.2). Neither the sign nor the magnitude is measurable: the trend is about -0.2, and gait oscillation could give ±2-4. The agent's own model rescaled would say 2.4.
  - 1382 tile (0.9) vs 0141's 1510 (0.62). The tile is 0.6 x 0.9 m, so each answer is one side. The label is one value for both clips, but which side is a definitional coin flip, so I left both.

### 0048 booth width: the agent assumed a booth height of 2.5-2.6 m

- The 0048 agent derived w = 0.695·(Hs − z_top). The booth base is out of frame, so it guessed z_top ≈ 2.5-2.6.
- Four siblings measure the booth height at 3.0 / 3.02 / 3.04 / 3.09 (0045 / 0046 / 0050 / 0049).
- My cap back-projection (`booth0048.py`, f=1830, pitch 13.9) gives sides of 0.64-0.70·(Hs − z_top).
- With Hs = 4.55-4.68 and z_top = 3.04, w = 1.03-1.15.
- Direct sibling widths are 1.17 (0046), 1.20 (0047 nadir, roof square 111 x 111 px) and 1.23 (0050).
- Adopted **1.17**.

### 1647 bird average speed (0010_seg, pre-agent value 4.8, no notes)

- Same footage and calibration as 1057 (agent: 4.29 for 0.5-1.0 s, which I confirm at 4.15-4.39).
- The bird starts slow: 156 px in frames 0-12, against 253-265 in 12-24, 308 in 24-36 and 248 in 36-48.
- Net displacement 350.6 → 1315.5 px over 48 frames is 20.1 px/frame. At Z≈34 and f=4140, that is 3.96 lateral, or about 4.0 m/s with the radial term. The mp4 is 22.89 fps with 59 frames, so if frames were dropped the true value is about 3.8.
- The depth_info points at t=0 and t=1, combined with the image rays, give a displacement of 3.52 m over the first second.
- 4.8 exceeds every 12-frame window except 24-36.

## Families checked and kept

### Bird family: 0010 is NOT scaled 2x off; the sibling clips are at a different scale

- Siblings measure objects 1.6-1.9x larger than 0010:
  - 0011 (VP f=2046 and gravity): door 5.3, wheel 2.55, eaves 16.6
  - 0013 (gravity f≈1600): wheel 2.7
  - 0012: eaves 15.4
- But the siblings' bird beak-to-tail is also 2x: 2.4 (0011), 2.85 (0013), 2.11 (0012), against the 0010 prior of 1.19. The bird/door and bird/wheel ratios match across clips. So the sibling worlds are uniformly about 2x the 0010 world, rather than 0010 misreading its scale.
- Independent in-clip check of the 0010 focal length (`wheel_rim.py`, `wheel_fit.py`, `wheel_model.py`):
  - The near cart wheel's outer-face ellipse has aspect 0.985 (rms 0.4 px, tread side excluded).
  - The axle vanishing point lies at x≈700-800, from the wheel-bottom line and the handle tips.
  - An exact projection model predicts aspect 0.946-0.965 for f=2100 and 0.986-0.990 for f=4140.
  - So the in-clip geometry supports the agent's f≈4140 (bird-prior scale).
- 1053-1056 and 1643-1646 are kept, as is 1057.
- **Flag for group2:** the 0011/0013 bird body length rows hold 1.19 (pre-agent, transferred from the 0010 prior). If those clips' own VP/gravity scales are right, the bird there is about 2.4-2.85. Transferring sizes between 0010 and 0011/0013 is unsafe in either direction.

### Street family (0045-0050)

| quantity | 0045 | 0046 | 0047 | 0048 | 0049 | 0050 |
|---|---|---|---|---|---|---|
| booth height | 3.0 | 3.02 | | | 3.09 | 3.04 |
| booth width | | 1.17 | 1.20 | **1.42 → 1.17** | | 1.23 |
| pillar distance | 3.5 | 3.6 | | 3.9 | 4.1 | 3.45 |
| bike height | 0.99 | 0.985 | | 0.95 | | 1.03 |
| bike length | 1.74 | 1.66 | 1.76 | | | 1.67 |
| wheel diameter | 0.65* | stated 0.65 | | 0.69 | 0.65* | 0.65* |
| walker speed | 1.23 | 1.24 | stated 1.236 | 1.13 (at 1 s) / 1.236* | 1.236* | stated 1.236 |
| walker height | 1.8* | 1.8 | | stated 1.8 | 1.8* | 1.8* |
| bike speed | stated 4.87 | 4.83 | 4.88 | 4.75 / 4.87* | stated 4.87 | 4.86 |
| first step | 0.15 | 0.155 | | | | 0.165 |

(* = transferred family fact)

The family is self-consistent: 0047's bike speed from the walker prior is 4.88, against the stated 4.87.

Rows not changed (under the 15% bar):
- 1196/1758 wheel 0.69 vs the stated sibling fact 0.65 (6%). Setting 0.65 is a free small gain if the merge allows stated-sibling facts.
- 1200 pillars 4.1 vs 3.45-3.6 in same-direction views (0045, 0046, 0050), about 14%. This is a soft flag: the 0049 agent's facade offset X = 4.0-4.2 was weakly constrained, and the answer scales with X.
- 1191 walker at 1 s, 1.13 vs 1.236 (9%; mid-stance hedge).

### Box drop (0182 / 0184 / 0186)

- Different boxes on the same ramp and camera: f 2121-2137, ramp 28.5°.
- v(1.5) − v(1.0) equals 0.5·a_prior in all three: 1.18 vs 1.17, 0.79 vs 0.79, 1.59 vs 1.59.
- The size conventions are ambiguous (local vs AABB, bow or flap included), and no second route exists. All kept.

### Corridor 0141

- 1509 (4.26 vs 1.693 x 2.458-2.5 = 4.16-4.23), 1510 (0.62, matches 0.61) and 1511/1512 (scale with Hc 1.28 vs 1.296, about 1%) are all kept.
