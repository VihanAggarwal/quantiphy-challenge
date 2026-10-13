# QuantiPhy Challenge (NeurIPS 2026), Track A: everything tried so far, and what is still open

Purpose: a briefing for an outside researcher. We want NEW ideas that could add +0.04 overall (to beat #1).
Please do not re-propose the items in "Tried and failed" unless you have a specific reason our test was wrong.

## 1. The task and metric (short)
- Each question: a 1-10 s video, one exactly-true "prior" for one object (a size, speed or acceleration; lab clips
  often "Gravity acc = 9.8 m/s^2"), for 3D clips a `depth_info` text (object-to-camera distances at 1-2 times), and a
  question asking a size, distance, speed at t, or acceleration at t in a stated unit.
- Metric: Mean Relative Accuracy. Item score = fraction of thresholds th in {0.1..0.9, 0.95} with |pred-gt|/gt < 1-th
  (<5% error = 1.0, 5-10% = 0.9, 10-20% = 0.8, ... >= 90% = 0). Category means (S2, D2, S3, D3) averaged equally.
  S = size prior, D = motion prior, 2 = planar 2D video, 3 = 3D video.
- Test: 3,289 questions / 568 videos (sources: simulation (Blender) 1,633, lab 806, internet 420, segmented 430).
  140 questions overlapping the public validation set are no longer scored (scored N: S2 553, D2 1137, S3 538,
  D3 933). Validation: only 159 labelled questions from 24 videos (all 24 are also test videos).
- 5 leaderboard uploads per UTC day across both tracks. Deadline Oct 23.

## 2. Where we stand
- Best scored: **.811** (S2 .817, D2 .859, S3 .766, D3 .803). Leaderboard #1 = .8525; 5th was ~.8195 (Oct 12).
- To reach .8525 we need +.042 overall, e.g. about +.08 on both S3 and D3.
- Per-subset item means (decoded from complementary "zero-a-subset" diagnostic uploads, Oct 12):

| Category | subset (scored n): item mean | subset (scored n): item mean |
|---|---|---|
| S2 | simulation+segmented (362): .828 | internet (191): .796 |
| D2 | simulation, static targets (719): .851 | everything else (418): .857 |
| S3 | **non-lab: simulation+segmented (221): .742** | lab (317): .782 |
| D3 | lab, static targets (334): .799 | lab motion + all non-lab (599): .805 |

  Earlier diagnostics: motion targets are the weaker kind in S2/S3/D3; losses are spread over all subsets, no
  single subset collapses. On validation 12% of rows score < .5 (gross misses), the rest are small errors.

## 3. Our pipeline (Track A, any model)
1. Claude Opus (high reasoning) sees 16 uniform frames + frames at every asked time (max 32, 854 px, labelled with
   frame index and time) and all of a video's questions at once. Returns a question spec (object, dimension,
   time), pixel tracks (points / boxes / segments per frame) and its own direct numeric answer.
2. Geometry solver: 2D = one image scale from the prior (size, px/s or px/s^2 on the fitted track); 3D = pinhole
   with depth_info as Euclidean range, f solved so the prior reproduces its stated value (lab: known f ~722 px at
   1280 px). Motion from robust local polynomial fits (speed at t = derivative of a +-0.5 s quadratic fit, etc.).
3. Routing: 2D -> geometry; 3D non-lab (simulation/segmented) -> Claude's direct answer (median of 3 runs);
   lab 3D -> geometry for sizes/distances, direct (+ label-noise emulation) for motion.
4. Model-free post-rules using test INPUTS only (never labels): ~60 "scene families" (segmented twins, lab
   re-renders with replaced backgrounds, multiple cameras of one Blender scene, shared depth_info) covering 1,723
   questions: a question asking what another family clip states as its prior takes the stated value; per-clip
   scale correction of direct 3D-sim answers from family facts; pooling one object's answers across the family;
   lab prop sizes pooled; segmented twin = original's answer.

## 4. What WORKED (with leaderboard gains)
- Scene families (facts, per-clip scale K, pooling P): probe 5 +.026 overall (D3 +.043, S3 +.028, D2 +.025).
  Leave-one-fact-out on 71 D3 facts: raw .790 -> K .855 -> P .908 -> K+P .951.
- Turning OFF optical-flow refinement of the prior's pixel speed: D2 +.025 (it lagged on large/articulated movers).
- Median of 3 Claude runs on 3D non-lab: +.02 per question there (more runs saturate: 5 runs +.001, 7 runs +.005).
- Lab label-noise emulator (Monte Carlo of the paper's label process: clicked centre + ToF depth + forward
  difference at 25 fps; noise fitted on stated test priors): S3 +.015. Same on D3: +.001.
- Internet "physical scale" convention (self-filmed internet clips are labelled on the physical scale even when the
  stated motion prior is off; rescale by family anchors): D2 +.009, extended version D2 +.006.
- Lab size fixes (table measured by rectifying its top in 6 views, ball identities from stated props), lab distance
  fixes, sim motion facts across cameras of one scene: +.001..+.005 per category.

## 5. Tried and FAILED (do not repeat), with the reason
Models / ensembles
- GPT-6 Astra as direct answerer or extra vote: validation .747 vs Claude .757; answers correlated with Claude's
  (median |log ratio| .045), geometric mean .759, no ensemble gain.
- Gemini 3.1 Pro (native video and frames): .565 on validation vs .786 pipeline; mixing it in hurts (-.075).
- More Claude runs beyond 3; higher reasoning effort (xhigh worse than high); a Claude agent loop with measuring
  tools (4x cost, not better); targeted paid re-asks of flagged rows (a fresh sample scores within +-.02).
- Oracle analysis: a perfect per-video scale is worth only ~+.017 (per-video offsets are shared by every model);
  best-of geometry/direct per question has a +.031 ceiling but every leave-one-video-out router loses .017-.047.
Measurement
- Dense CPU tracking (GrabCut + templates, KLT): sizes slightly worse, motion neutral. The pipeline's prior pixel
  motion is already within 0.44% (median) of exact segmented-twin masks.
- Zoomed full-resolution re-measurement of extents: within-5% rate .736 -> .826 vs masks, but only ~+.003 overall.
- Camera-motion compensation in internet clips: 34 of 36 tracks change < 5%.
- Segmented-twin masks as extents: SAM-style cut-outs (halo, missing thin parts), not better than Claude's.
- Generic 3D reconstruction of lab motion: predicts stated lab motion priors at MRA .60; independent views disagree 2x.
- Geometry instead of direct on 3D simulation: per changed answer -0.19 (sizes), -0.09 (S3 motion), -0.13 (D3
  motion). Cause: unknown, varying camera FOV (8-103 deg) solved from a noisy prior.
Conventions / label emulation
- Blender label emulation (backward-difference speed, tangential acceleration): S2 -.002, D2 0.
- Depth as optical-axis Z instead of range: worse (.569 vs .652 on 3D sim geometry).
- Uniform lab speed factors (x1.15/1.25/1.40 on D3): net 0 (D3 lab objects move fast; emulator factor ~1.00 on 107
  of 150 D3 lab motion rows; 43 rows unmodelled).
- Lab "near-surface depth" (ToF reads the ball's front surface, so sizes read small): refuted; stated lab ball sizes
  already read 1.056x stated with the current convention, near-surface makes it 1.091x.
- Lab timing shifts (forward difference at t+1/50 s, +-1 frame, strict discrete differences): no gain (us and an
  independent Gemini/Jules study).
- Per-scene ratio "stated prior speed / measured prior speed" applied to other rows: only 8 lab events state a speed;
  ratios 0.96-1.04 except captured_0054a (1.37) / 0054b (1.10); negligible coverage.
- Constant +5 cm lab depth bias: tuned on ~18 validation rows, contradicts the stated-size evidence.
- Container fps vs dataset fps: dataset fps is right (83 videos differ; checked with free-fall anchors).
- Dimension words (width/length/height/diameter): median truth/prediction ~1; misses are label errors / ambiguity.
- captured_0018: 30 D3 questions ask about t = 3.0-3.4 s in a 2.04 s clip (trimmed); unanswerable.
Layers on top of the answers
- MRA-optimal shading (shrinking answers, uniform or driven by the 3-run spread): every variant loses on validation
  (-.005 to -.021) and on 110 exactly-known test facts (-.001 to -.009).
- Cross-clip "asset table" (a size stated anywhere answers the same noun elsewhere): 4 of 10 validation hits right;
  generic nouns (boat, ball, cup) are different assets.
- Kinematic consistency smoothing across a video's speed answers: ~+-.003, too few rows.
- Per-category method switches in 2D (direct vs geometry vs geometric mean): Claude's 2D direct ~= its geometry.
- Size "envelope" rules: S2 +.002 at best.

## 6. Currently running / open
- Foundation-model camera FOV for the 3D simulation clips (MoGe-2 on CPU: FOV estimated for all 94 sim clips; the
  segmented copies reuse them), then geometry with that FOV as a prior (several strengths; Blender stock-lens
  snapping; gated / geometric-mean blends with Claude's direct answer). Being scored now on validation and exact
  family facts. Literature says single-image FOV error is ~1.6-5 deg median (MoGe best on renders), i.e. 15-40%
  focal error at narrow FOV, so we expect at most a gated gain on the S3 non-lab subset (.742, 221 rows).
- Facts from the paper's appendix we rely on: sim depth = Euclidean range to the Blender object origin (humans: pelvis;
  some vehicles: a rig-root empty); sim sizes = world bounding-box dimensions; sim speed = backward difference of the
  origin; sim acceleration = change of speed magnitude; sim camera fixed per clip; lab labels = hand-clicked centres
  on >= 5 frames "for smoothing", depth picked by hand from Orbbec ToF maps, forward differences; occluded frames use
  the other three cameras.

## 7. What we would like from you
1. Ideas that could plausibly add >= +.02 overall, ideally on S3 non-lab (sim/segmented, .742), S3 lab (.782),
   D3 (.80) or S2 internet (.796). Each with a cheap way to validate on test INPUTS (stated facts in families,
   cross-camera consistency) or the 159 validation labels (24 videos: gains < .03 there are noise).
2. Anything in our reasoning above that looks wrong.
3. If you know how top Track A teams reach .85 (write-ups, code, talks), point us to it.
Constraints: no test labels in any form; answers must come from the test inputs; paid API budgets are small
(Claude ~$60, OpenAI ~$33); a Colab GPU (96 GB) is available for open models; ~10 days left.
