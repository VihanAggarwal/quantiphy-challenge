# qid 1063: simulation_0011 bird wingspan, independent re-measurement (measurer 2)

Scripts and scratch: `research/next/sim3audit/group2/q1063_m2/`. I did not read any other file in group2/.
Current answer: 5.8 (an agent measurement). **My value: 4.4 m.** Plausible range 3.9-5.1. Confidence: low-medium.

## Camera and trajectory (0011)
- **Focal length.** Vanishing points from LSD lines on the house (`vp.py`):
  - facade horizontals (19 inliers) give VA = (-1622, 1271);
  - verticals (39 inliers) give a vertical VP at y = -12638.
  - Estimates: f(VA, Vvert) = 2010; f(VA, VB) = 1846, but VB has only 7 inliers; f(horizon, Vvert) = 1907.
  - I used f ≈ 1980 ± 80. The nest drop with its initial velocity also gives about 2000.
- **Nest fall.** A plain parabola fit to the nest's centroid gives an acceleration that is too low (770-950 px/s²). That implies f ≈ 1300-1600, so f values taken from nest gravity in this family (0013 and 0014 used 1600) are probably biased low.
- **Bird path.** I fitted a smooth track (cubic plus flap harmonics, period 17.2 frames) and used Euclidean ranges at t=0 and t=1.
  - The flight is exactly level when the horizon is at y = 1277, which matches the VP horizon (1271-1283). This supports the range convention.
  - The path heading is 38 ± 2° toward the camera from the image plane. The image path is straight to within 1 px.

## The trajectory heading is not usable as the bird's yaw
- The horizontal image extents along the wing axis stay constant across flap cycles:
  - top-phase tip-to-tip: 110, 119 and 109 px in cycles 2, 3 and 4;
  - level-phase tip-to-tip: 127-142 px in cycle 2 and 142-145 px in cycle 3.
- With yaw = 38° these should shrink to 0.73-0.89× as the bird moves right.
- Vertical extents do scale exactly as 1/Z: the wing-up height is 1.35-1.43 m in every cycle and the wing-down depth is 1.19-1.22 m.
- Beak-to-tail length grows 90 → 100 → 120 px (frames 19, 36, 53). That needs a small yaw, while the constant wing extents need yaw ≈ 60°.
- So the body yaw is not the path heading, and it probably turns from about 45° to 50° during the clip.
- The direct tip-to-tip route with yaw = 38° gives 5.3-7.0, and it is internally inconsistent between cycles. I did not use it. This is probably why the earlier answer was 5.8-6.4.

## Routes used
1. **Cross-clip chain anchored on the stated fact in 0010 (bird length 1.19 m).** S = r × (L/D)_0010 × D_0011.
   - r = 1.96: wingspan / beak-to-tail from the top-down clip 0012 (frame 0: 259/132 px; frame 49: 252/128).
   - (L/D)_0010 = 0.83: the bird is in profile, beak-to-tail is about 141 px at Z ≈ 34.0, and the near wheel is 202 px at Z ≈ 28.6.
   - D_0011 = 2.40-2.72 m: the near wheel is 172 px. The range depends on the near-wheel depth and on whether depth is range or Z.
   - Result: **S ≈ 3.9-4.4**.
2. **Vertical sweep route, which does not depend on heading.**
   - Wing-tip vertical travel V is 2.58 m raw. After correcting for near-tip and far-tip perspective (about 0.13 m each) it is about 2.31-2.40 m.
   - Flap angles come from the 0012 span ratios at the matching phases: top about 40-45°, bottom about 32-36°. The hinge-to-tip length is about 0.46 S.
   - Result: **S ≈ 4.2 (3.9-4.6)**.
3. **0013 profile clip.** V/L ≈ 0.90-0.97 after the perspective correction, giving L_0011 = 2.38-2.57 and **S ≈ 4.6-5.0**.
4. **Yaw-varying fit inside 0011.** Using the beak-tail and tip-to-tip ratios per cycle with r = 1.96, L ≈ 2.45-2.58, so **S ≈ 4.8-5.05**.
5. **Yaw = 38° with r × L.** Beak-tail lengths of 92, 100 and 133 px at frames 22, 40 and 58 give L = 2.12-2.35, so **S ≈ 4.1-4.6**.

The routes cluster at 4.2-4.9, so I chose 4.4. Main risks:
- f is uncertain by about 4%, and every route scales with it.
- The bird yaw model.
- The cart near-wheel depth (track width) used in route 1.
- The flap-phase mapping between 0011 and 0012 used in route 2.

Cross-family note: 0010 is at about 0.54× the world scale of 0011, 0013 and 0014. The bird in 0010 is 1.19 m long against about 2.2-2.4 m in 0011, and the door and wheel show the same ratio. Relative sizes are preserved but absolute sizes are not, so the "same size in every clip" premise fails for 0010.
