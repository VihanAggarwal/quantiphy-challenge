# Verification of research/depthpro (Depth Pro FOV head for 3D-simulation geometry): FAIL confirmed

Verifier, 2026-10-14/15. Free replays only. $0 API (the ledger was a scratch path and was never written).
All verifier outputs are in /tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/vdp/.
I changed none of the agent's files. This file is the only addition.

## 1. Numbers reproduce
I copied the two FOV CSVs to scratch so the scripts' side outputs land outside the agent's directory, then ran:
```
.venv/bin/python research/depthpro/stage1.py <scratch>/fov_depthpro.csv      # identical to out/stage1_final.txt (diff empty)
.venv/bin/python research/depthpro/stage1.py <scratch>/fov_depthpro_mid.csv  # identical to out/stage1_mid.txt
.venv/bin/python research/depthpro/oracle.py <scratch>/fov_depthpro_mid.csv  # identical to out/oracle.txt
.venv/bin/python research/depthpro/oracle.py <scratch>/fov_depthpro.csv      # geo_dp .497 (all) / .556 (val), vs .499 / .559 in out/oracle.txt
```
Stage 1 (primary reference, 29 clips): Depth Pro median |e| .334, share <= .10 .14, signed -.221. MoGe-2 on the same
clips: .229 / .24. The secondary and pooled references match RESULT.md. Oracle (71 size rows, 20 clips): dmed .752,
old .663, LOO oracle .727, gm .754, MoGe .496, DP .499. Bootstrap -.025 [-.120, +.088]. All of these match.
Minor point: out/oracle.txt came from the mid-frame file, as RESULT.md's command list says. With the 2-frame file,
geo_dp is .497 instead of .499, which does not matter.

## 2. Pre-registration and how the kill test was applied
- There is no git history, so I can only use file mtimes. stage1.py, which hard-codes the bar (median <= .10 AND
  share >= .60), was last written at 21:22. oracle.py was last written at 21:24. The Depth Pro inference log ends at
  22:25, after about 64 min of compute, so it started around 21:20. RESULT.md was last modified at 22:47, when the
  results were appended. This fits the bar being fixed before the outputs existed. I cannot prove that the
  pre-registration text was not edited afterwards. That does not matter here: the miss is .334 against a .10 bar,
  and any sensible bar fails.
- The bar was applied as written. The noise escape needs median e in (.10, .15], so it did not apply, and stopping
  at stage 1 was the pre-registered action.
- Truths (facts and validation labels) are used only to build the reference focal and the evaluation-only oracle.
  No answer is written, no candidate exists, and no row is selected per row. This is Track A only, with no Track B
  use of closed-model outputs. Leakage: none.

## 3. Inference code check
fov_depthpro.py matches upstream DepthPro.infer/forward in /home/user/.cache/depthpro/src: ToTensor, then
Normalize(0.5, 0.5), a bilinear resize to 1536^2, encoder, decoder, and fov.forward(x, features_0). Weights load
with strict=True, so a silent random-weight failure cannot happen. f_px = 0.5 W / tan(fov / 2), which is upstream's
convention. All 37 frames came from the original (non-segmented) clips. The reference construction is also right:
for 1/f rows, f_ref = f_fix * geo_fix / truth; proportionality was checked within the same run; rotated twins are
handled in consistent pixel units. The clean 0058-0065 group gives about 53 deg, close to Blender's 35 mm lens
(54.4 deg), which supports the reference.

## 4. False-negative check: I ran the skipped stage 2
The only false-negative route I could see: stage 1 scores focal agreement against a reference built from Claude's
own tracks. Depth Pro's and MoGe's errors correlate at r = 0.83, so part of the stage-1 "error" may be reference
error and not model error. So I ran the pre-registered stage 2 end to end, which does not depend on the
reference:
```
SIMFOV_FAST=1 ... .venv/bin/python <scratch>/replay_dp.py --fov <scratch>/fov_depthpro.csv --out <scratch>/replay_dp_fast.csv
   (wrapper = research/simfov/replay.py restricted to the 35 Depth Pro clips + twins; 1104 rows; ~35 min CPU)
.venv/bin/python research/simfov/evaluate.py <scratch>/replay_dp_fast.csv    -> <scratch>/evaluate_dp_fast.txt
```
dmed and old come out identical to simfov (.811 / .657 val, .793 / .700 facts), so the replay is consistent.
- Facts (106 rows, 32 clips): dmed .793. cam05 .542 (-.252), cam15 .579, fix .526, snap05 .544, camZ05 .518.
  The best variant is gmgate_cam15 .731 (-.062, 90% [-.122, -.009]). **Every variant is below dmed.**
- Validation (44 rows, 6 clips): dmed .811. The best is gmgate_cam15 .741 (-.070, [-.114, -.022]). Every variant
  loses.
- The stage-2 bar (>= +.02 on facts and a bootstrap LB > 0) fails by a wide margin. Depth Pro is slightly less bad
  than MoGe in the full replay (cam05 facts .542 vs .514), but the sign and size are the same.
- Post-hoc subgroup, not actionable: the bin with Depth Pro FOV < 20 deg holds only 2 clips (0031, 0034). There,
  Depth Pro geometry gets .850 vs dmed .767 on 12 fact rows and 1.000 vs .967 on 6 validation rows. It is a 2-clip
  pick made after looking at the results. Right above the cut, Depth Pro is badly wrong on 0170 (21 deg vs ~38) and
  0300 (26 vs ~45). The fact rows already hold their stated values, so it is worth < .001 overall even if it is real.
  Do not adopt it without a fresh pre-registered test.

## 5. Caveat on the oracle claim (does not change the verdict)
RESULT.md says "even a perfect clip focal does not make geometry beat dmed". The LOO oracle (.727) is
pessimistic: clips with 2-3 truth rows give a noisy LOO focal. The in-sample oracle (the clip's focal from all of
its truth rows, including the scored one) is optimistic, and it gives .789 vs dmed .752 (+.037) on the same 71
rows. So the true perfect-focal ceiling lies somewhere in [.727, .789], and the oracle does not prove that no FOV
model could ever help. In practice the route is still closed: Depth Pro scores .497, a leave-one-clip-out
global-bias-corrected Depth Pro scores .590, and MoGe scores .496. These are far from either oracle number, and a
real FOV model would need |log f error| well under .10 to approach them. Follow-up 1 ("closed for any model") is
fair as a priority call. It is not a proof.

## Verdict
FAIL confirmed. There is no leakage or rule issue. The skipped stage 2, now run, also fails on both held-out sets,
so a false negative is very unlikely. Expected gain 0, and no candidate.
