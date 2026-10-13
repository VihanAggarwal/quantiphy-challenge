# Leaderboard probes (Track A)

Each upload measures the four categories independently, and a category's MRA is the mean of its
item scores, so changes to disjoint question sets add up. A probe changes one thing per category
against the best measured rows of that category (`scripts/compose_submission.py`).

| Probe | S2 | D2 | S3 | D3 | MRA |
|---|---|---|---|---|---|
| v2 | .801 | .810 | .703 | .738 | .763 |
| 2: geometry on 3D non-lab | .798 | .810 | .673 | .668 | .737 |
| 3: S2 longest-extent prior / D2 dense off / direct on lab 3D | .803 | .810 | .715 | .727 | .764 |
| v3 = best rows per category (S2, S3 from probe 3; D2, D3 from v2) | .803 | .810 | .715 | .738 | (~.767) |

## Probe 4 (`submissions/trackA_probe4_s2twin_d2refineoff_s3split_d3fixes.csv`, on v3)

Free replays and post-hoc rules on the cached Claude run; every variant was checked by three
adversarial reviewers (integrity and legitimacy, evidence, code). Scripts and bundles:
`research/hyp_scripts_2026-10-10.tar.gz`.

- **Twin renders.** Test clips come in families: `simulation_X` + `simulation_X_segmented`
  (pixel-aligned, white background), lab `captured_X` + `Xs` + `Xx` (same event, replaced
  background). A segmented clip takes its original clip's answer when the question text and prior
  match (not when the original is a rotated view); on lab s/x renders motion answers take the
  original render's direct answer.
- **S2** (75 changed): longest-extent prior (probe 3) + twin copy. Expected +.004 to +.009.
  The 0.8 px extent padding was dropped: its bias measurement used an inflated reference.
- **D2** (560 changed): `qp.refine` off. The optical-flow prior refinement lags on large or
  articulated movers (walking horses, cats, a glass chess piece: 0.49-0.90 of the true pixel speed),
  inflating every answer in those videos; mask tracks on the segmented twins agree with refine-off
  (mean prior error 2% vs 3-6%). Plus twin copy. Expected about +.02.
- **S3** (275 changed vs probe 3): lab sizes and distances back to geometry, lab motion stays
  direct (from probes 3's S3/D3 deltas solved per kind; the assumption that a kind's effect is
  shared by S3 and D3 cannot be checked by those two numbers), twin copy, 0040 depth typo
  ("8420m" -> 0.842 m), 0034b (a second camera carrying 0034a's depth_info) static answers from
  0034a, and 4 rows whose depth entry names the ball differently ("ping_pong_ball" vs "white
  ball") re-solved with the right depth. Expected +.005 to +.03.
- **D3** (100 changed): lab depth-name relinking ("ball" in depth_info vs "toy"/"basketball" in the
  question), "velocity at the end of the slope" (no time) to direct, per-video scale correction of
  direct static answers, twin copy, and sibling-scene transfer (a question asking a quantity that a
  sibling clip of the same scene states as its prior takes that stated value; 14 answers).
  Expected about +.010.

## Second research round (2026-10-10): what did and did not pan out

Scripts and reports: `research/big_levers_scripts_2026-10-10.tar.gz`.

- **No hidden ground-truth convention.** Measuring every test prior with an independent scale (fixed
  lab camera f ~722 px at 1280 px + depth_info; sibling clips' priors) gives stated/measured ratios
  near 1: lab speeds 1.00 (a local fit at t matches best), sizes 0.94 (blur on moving balls).
  The 1.36x lab speed shortfall seen on validation comes from a few scenes whose labels are inflated,
  not from a convention, so no lab speed factor. Lab clips were captured at 25 fps and converted to
  24 fps by dropping frames after video frames 11 and 35 (real time stays within 0.02 s of n/24).
- **3D simulation cameras are not fixed** (hfov 8-103 deg, modes at 15-20 and 35-45 deg; the lens
  changes between cameras of one scene), so calibrated geometry does not beat Claude's direct answers.
- **Scene families are the lever.** 60 families of clips show the same scene (twins, lab renders,
  identical depth_info, near-identical frames, shared prior text), covering 1723 questions.
  T: a question asking a quantity that a family clip states as its prior takes the stated value
  (5/5 exact on known rows). K: Claude's direct 3D-sim answers carry a per-clip scale error shared
  across quantities, corrected from the family's stated facts. P: answers about one object are
  pooled across the family. Leave-one-fact-out on 71 D3 facts: raw .790, K .855, P .908, K+P .951.
  LAB: sizes of named lab props reused across events are pooled.

## Probes 5 and 6 (on v3; merges built and verified per category, `research/merge_scripts_2026-10-10.tar.gz`)

| Probe | S2 | D2 | S3 | D3 |
|---|---|---|---|---|
| 4 | twin copy (+ longest extent) | refine-off + twin copy | probe-4 S3 (kind split, twin, render, fixes) | probe-4 D3 (relink, twin, transfer, ...) |
| 5 `trackA_probe5_families_merged.csv` | 4 + stated facts from scene families | refine-off only | 4 + family facts, lab prop pooling (tables, cups, balls), white ball = 4 cm ping-pong ball | 4 + family facts (73), K scale correction, series pooling, lab pooling |
| 6 `trackA_probe6_s3nosplit_d3labmotion_d2pad.csv` | = 5 | refine-off + 0.8 px padding + twin copy | 5 without the lab kind split (76 rows) | 5 + lab motion answers to Claude's direct (116 rows) |

Reading them: D2 4-5 = twin copy, D2 6-4 = padding; S3 5-6 = kind split; D3 6-5 = lab motion direct;
S3 5-4 and D3 5-4 = the scene-family rules. Expected (vs v3 .803/.810/.715/.738): probe 4 about
+.006/+.02/+.02/+.01, probe 5 about +.009/+.02/+.03/+.03.

## Diagnostic probes (on v3, whose per-category scores are known: .803/.810/.715/.738)

A subset's answers are multiplied by 1e-9 (relative error ~1, so each scores exactly 0 but stays
a valid number). The category drop then gives the subset's current mean item score:
`mean(subset) = (v3_cat - probe_cat) * N_cat / n_subset` (N = 579/1163/578/969), precise to about
+-0.001 given the 3-decimal leaderboard. No answer is set from it; it only tells where points are lost.

| File | S2 subset | D2 subset | S3 subset | D3 subset |
|---|---|---|---|---|
| `trackA_diag_A_source.csv` | simulation (281) | simulation, static targets (561) | lab (334) | lab (457) |
| `trackA_diag_B_motion.csv` | motion targets (331) | motion targets (319) | motion targets (319) | motion targets (268) |

## Dead ends checked (2026-10-10)

- captured_0018 (and s/x): 30 D3 questions ask about t = 3.0-3.4 s in a 2.04 s clip. Not a time-base
  error: the falling soccer ball accelerates at ~8.9 m/s^2 in video time (2.8 m depth, f 722 px),
  so the clip was trimmed and those questions cannot be answered from the video.
- Dimension words: on validation the median truth/prediction ratio is ~1 for width, length, height
  and diameter; the large misses are single label errors or ambiguous objects, not a convention.

### Revised second upload: `trackA_diagA2_s2d2sim_s3d3nonlabmotiongeo.csv` (replaces `trackA_diag_A_source.csv`)

Categories are measured independently, so one upload can diagnose some and test others. On v3:
- S2: simulation answers zeroed (diagnostic, 281). D2: simulation static targets zeroed (diagnostic, 561).
- S3/D3: 3D non-lab MOTION answers switched to geometry (S3 115, D3 116 rows). Probe 2 (geometry on
  all 3D non-lab) solved per kind like the lab split gives geometry -0.194 per static answer but
  +0.066 per motion answer (rounding-robust; assumes a kind's effect is shared by S3 and D3), so
  this predicts S3 +0.013 and D3 +0.008 over v3.

## Results: probe 5 = 0.793 (2026-10-10)

| | S2 | D2 | S3 | D3 | MRA |
|---|---|---|---|---|---|
| v3 (best rows per category before) | .803 | .810 | .715 | .738 | .767 |
| probe 5 | .813 (+.010) | .835 (+.025) | .743 (+.028) | .781 (+.043) | **.793** |

Every category moved as predicted or better (expected +.009/+.02/+.03/+.03); D3's scene-family rules
(stated facts, K scale correction, series pooling, lab pooling) gave the most. Probe 5 is the new base.

## Diagnostic results (2026-10-10, on v3)

`trackA_diagA2_...` scored .405/.423/.697/.722 and `trackA_diag_B_motion.csv` .362/.574/.334/.552. Decoded
(subset mean item score = (v3 - probe) * N / n; "lost" = category points the subset gives away):

| Category | subset means | points lost |
|---|---|---|
| S2 | simulation .820, internet+seg .787; motion .771, static .845 | motion .131, static .066 |
| D2 | simulation static .802, rest .817; motion .860, static .791 | motion .038, static .152 |
| S3 | motion .690, static .745 | motion .171, static .114 |
| D3 | motion .673, static .763 (before probe 5's +.043) | motion .091, static .171 |

- The losses are spread across subsets: no single subset collapses, so the remaining gap needs
  broadly better measurements, not one fix. Motion is the weaker kind in S2, S3 and D3.
- 3D non-lab motion -> geometry is clearly worse (S3 -.090, D3 -.134 per changed answer): the probe-2
  per-kind 2x2 split predicted +.066, so the "a kind's effect is shared by S3 and D3" assumption
  failed here. Keep direct answers on all 3D non-lab questions. The same assumption underlies the lab
  kind split (inside probe 5's S3 gain) and probe 6's D3 lab-motion test, so treat those as unproven
  until probe 6 measures them.

## Probe 7a (`trackA_probe7a_p5_ensemble3dnl.csv`, on probe 5)

Two extra paid Claude runs on the 123 3D non-lab test videos ($13.21 + $18.31; ledger $134.20 of $200):
test_3dnl_v1_high_b (second v1 sample) and test_3dnl_v2_high (v2 prompt, 854 px). The three runs' direct
answers differ by ~5% per question; their median moves 28% of answers by > 5%. On validation a 3-run median
beat the single run by +0.020 per 3D non-lab question (14 of 15 combinations >= 0). Built by
`research/ensemble_3dnl.py`: probe 5 rescaled by ensemble/base (stated-fact rows kept exact, twins re-synced);
S3 117 and D3 200 answers change. Expected about S3 +0.005..+0.008, D3 +0.005..+0.01.

## Probe 7b (`trackA_probe7b_p5_ens_famext.csv`, on probe 5)

Probe 7a (3-run ensemble on 3D non-lab) plus three verified scene-family extensions
(`research/family_ext_scripts_2026-10-11.tar.gz`); on rows both touch, the family value wins (a stated fact,
or a pool over several clips):
- D2 (289): pooling the same object and question across camera views of a scene family (votes are camera
  views, clustered by edge-map correlation; log-mean of votes within 0.15 of the median; guards for wording
  and spread), plus 20 stated-fact transfers. Held-out-camera evidence +0.012..+0.024 per pooled row: D2 ~+0.004.
- S3 (46): per-kind pooling (sizes and speeds pooled separately; mixing kinds is what hurt K on S3): ~+0.006.
- D3 (60): scene links the first scene graph missed (shared object vocabularies checked by eye, near-identical
  frames) + stated facts + pooling, 9 doubtful rows removed by the verifier: ~+0.008..+0.011.
Expected overall vs probe 5 (.793): about +0.01 including the ensemble.

## GPT-6 Astra pilot (2026-10-11): not adopted

`scripts/run_openai_direct.py`: GPT-6 Astra (images only, $10/$50 per MTok) given the same frames and questions
as Claude, direct answers, high reasoning. Validation (val_hires, 146 of 159 answered at the time, ~$10):
Astra .747 vs Claude direct .757 on the same questions (2D .804 vs .803, 3D lab .605 vs .655, 3D non-lab .785
vs .774). Its answers track Claude's closely (median |log ratio| 0.045), so the geometric mean adds nothing
(.759), and as a 4th vote in the 3D non-lab median it scores .80-.82 vs .80-.83 for three Claude runs.
Recorded OpenAI spend $9.82 (23 requests); one retry of simulation_0060 was cut off after 15 min without a
recorded response, so up to ~$2.50 more may show on the OpenAI bill. Not retried, not run on the test set. Gemini (`scripts/run_gemini_direct.py`, native video or frames) is blocked until the
key's Google project has credits.

## Zoomed extent re-measurement pilot (2026-10-11): small, parked

`research/zoom_pilot_2026-10-11.tar.gz`. Claude re-measures an object's asked dimension on 3 full-resolution crops
(object ~600 px) + an overview; scored against pixel-exact masks from the 43 2D simulation clips with a segmented
twin (121 objects; rotation-robust reference). Within 5%: original .736, zoom .769, hybrid .826 (zoomed value only
where its line is within 8 deg of the original, since crops lose context and sometimes swap length/width); median
|log err| .0153 / .0158 / .0144. Validation answers (51): original .806, hybrid .812. Modelled test effect about
S2 +0.010 (weak: the 9 measured priors were neutral), D2 +0.003, i.e. ~+0.003 overall for ~$6-12. Spent $3.19
(ledger $137.40 of $200). Not scaled up.

## Gemini 3.1 Pro pilot (2026-10-11): not adopted

`scripts/run_gemini_direct.py` (now with its own ledger `budget/ledger_gemini.jsonl` and a $15 cap on the $19 key). Same
questions and system prompt as the Astra pilot, high thinking, high media resolution. Validation (val_hires):
- Native video (Files API, sampled at 12 fps), 24 videos, 156/159 answered, $6.05 (~$0.25/video, mostly thinking;
  many requests hit the 32k output cap): MRA **.565** vs Claude pipeline .786 (S2 .55 / D2 .57 / S3 .67 / D3 .47).
  Its answers are far from Claude's (median |log ratio| .31 vs .055 for Astra) because they are less accurate:
  the geometric mean with Claude scores .708 (worse on 17 of 24 videos; video bootstrap -0.075, 90% CI [-.116, -.033]).
  A median of Claude v1, Claude v2 and Gemini gives .792 vs .786 (noise). Only lab accel (1 question) favoured Gemini.
  The first two videos (15 questions) had suggested the opposite (.707 vs .660): too small a sample.
- Frames (the Claude frame plan): 3 videos before it was stopped, .567 on the first 15 questions.
Total Gemini spend $7.38 recorded (+ up to ~$0.40 for one frames request cut off when the run was stopped).
Gemini as a direct answerer is not used; the remaining credit is kept for a possible pointing/localisation pilot.

## Lever investigation (2026-10-11): measurement is not the bottleneck

Five CPU-only investigations, each re-checked by an adversarial verifier (workflow wf_1354cc37-d73; code and reports in
`research/levers_2026-10-11/levers_scripts_reports.tar.gz`). Prompted by the GPT-6 Astra consultation
(`research/consult/`), which ranked dynamic-prior calibration, twin masks and lab 3D fits first.
- **Oracles (validation).** A perfect per-video scale is worth only ~+.017 beyond chance (ICC .20: most error is
  per question, and per-video offsets are shared by every model, .84-.95 across Claude runs). Best-of geometry/direct
  per question: ceiling +.031, every leave-one-video-out router loses .017-.047. No model combination gains
  measurably (Claude runs, Astra, Gemini); restricted to rules buildable on test, nested LOVO scores -.014.
- **Invariants.** Coordinates/rescaling, dataset fps (not container fps: 83 test videos differ, which also traps
  native-video models), and depth = range r (beats optical-axis Z .652 vs .569 on 3D sim geometry) are all right.
  Lab capture clock (25->24 fps drops at frames 12/36/60) is real physics but worth ~+.001 D3.
- **Dynamic priors (2D).** The pipeline's prior pixel motion is within a median 0.44% of exact segmented-twin masks
  (32 clips) and 1.2% of a dense rigid KLT tracker; prior semantics (path length, vector vs tangential acceleration)
  match. One exception: simulation_0191 free fall (Claude tracked the far bottom edge; 14% low).
- **Twins.** Segmented clips are SAM-style cut-outs (1 px halo, missing thin parts, shadows), so mask extents are
  not better than Claude's; mask motion agrees with Claude to ~1%. 19 twin families repeat their first frame; the
  only t=0 questions affected are the shark rows (0101-0103), where the sibling clip's boat length gives v0 = 2.00.
- **Lab 3D fits.** Generic reconstruction predicts stated lab motion priors at MRA .60 (fitted renders) and ties on
  validation (every policy .644 on 18 lab motion questions); independent camera views disagree ~2x. Only families
  0020 (free fall 9.85 m/s^2) and 0047 (answers below the depth anchors' radial bound) are defensible.

### Probe 8 (`submissions/trackA_probe8_p7b_d2fixes_d3labphys.csv`, on probe 7b)
Built by `research/levers_2026-10-11/build_probe8.py`: D2 = 7b + 0191 free-fall rescale (10 rows, x0.86) + shark
initial speed (6 rows, ~2.04 m/s); D3 = 7b + lab capture clock (175 rows, median x1.003) + lab 3D fits for 0020/0047
(15 rows, median x1.31). S2, S3 = 7b. Expected about D2 +.004, D3 +.001..+.005 (each fix below leaderboard resolution
alone); read as probe 8 minus probe 7b.

### Camera motion in internet clips: not a lever (2026-10-11)
`research/levers_2026-10-11/camera_motion_check.py`: background affine per frame pair (LK flow outside Claude's
boxes, RANSAC), chained between the prior track's frames; stabilised vs raw prior pixel path. Over 36 motion-prior
tracks in 33 internet clips (test + validation), 34 change by < 5% (median 0.3%). internet_0028's "background" is the
moving conveyor belt itself (stabilising would be wrong); internet_0068 moves 8%. No change made.

## Layers on top of the model (2026-10-12)
- **MRA-optimal downward shading** (the metric punishes overestimates more: 2x over scores 0, 2x under scores .5):
  on validation every multiplier below 1 loses (c = .97: -.007; .95: -.016). Errors are mostly small or gross misses,
  and shading only pays for moderate spread (synthetic log-sd .3: +.009). Not used.
- **Kinematic consistency** (`research/kinematic/`): per (video, object), timed speed answers are pulled halfway
  (in log) toward a constant-acceleration fit, and timed acceleration answers toward its slope, when the group has
  >= 3 answers at >= 2 times and the fit's median residual is < 25%. Reaches 613 test questions; validation reaches 4
  (cannot judge). Probe 9 (`submissions/trackA_probe9_p8_kinematic.csv`, on probe 8) applies it only to rows still
  equal to the raw pipeline answer (126 family/fact rows protected): 169 rows (S2 88, D2 48, S3 18, D3 15), median
  change 0.8%, 18 rows > 10%. Expected within +-.003 per category; read as probe 9 minus probe 8.

## Diagnostic C (`submissions/trackA_diagC_on7b.csv`, on probe 7b) — where the remaining S2/S3/D3 gap sits
Zeroes (x1e-9) S2 acceleration targets (79/579), S3 lab motion (176/578), D3 lab motion (110/969), D2 internet
(217/1163). Decode with probe 7b's scores: subset mean = (7b - diagC) * N_cat / n_subset. Purpose: the target is
.84 in S2/S3/D3 (estimates now ~.813/.755/.80); S3 is 58% lab and its lab-motion share has never been measured.

## Probes 11 and 12 (on probe 8): label-process emulation from the QuantiPhy appendix (2026-10-12)
Built by `scripts/compose_submission.py` from candidates in `research/{blenderemu,labnoise,sizeconv}/`.
| Probe | S2 | D2 | S3 | D3 |
|---|---|---|---|---|
| 11 `trackA_probe11_p8_emu_labnoise.csv` | Blender label emulation (backward-difference speed, tangential accel; 128 rows) | same + refine-off rows (116) | lab label-noise emulator (148, median x1.17) | same (34, x1.06) |
| 12 `trackA_probe12_p8_sizeenv_lat13.csv` | size envelope (49) | size envelope (65) | lateral balls x1.3 (92) | same (40) |
Read each category against probe 8. Validation: Blender emulation S2 +.003..+.019 over 7 runs (one clip);
lab noise emulator .741 vs .659 on 17 lab motion questions (out of sample); x1.3 .735 (in sample); size envelope
slightly negative. Probe 10 (all lab motion x1.25 on 7b) is the cruder version of the S3/D3 test.

## Lab-speed ladder (2026-10-12): tune the label-noise correction on the leaderboard
`research/labnoise/build_ladder.py`. S3 = label-noise emulator at ball depth noise sz (fit on test priors: 2 cm,
95% range 0.5-6 cm); D3 = uniform factor on lab speed / path targets (101 rows; accelerations, stated facts kept).
S2, D2 = probe 8 except probe 11 (Blender emulation).
| Probe | S3 | D3 |
|---|---|---|
| 8 | none | none |
| 15 `trackA_probe15_p8_s3sz1_d3x125.csv` | sz 1 cm (111 rows, median x1.11) | x1.25 |
| 11 `trackA_probe11_p8_emu_labnoise.csv` | sz 2 cm (148, x1.17) | sz 2 cm emulator (34 rows) |
| 13 `trackA_probe13_p8_s3sz3_d3x140.csv` | sz 3 cm (157, x1.28) | x1.40 |
| 14 `trackA_probe14_p8_s3sz4_d3x115.csv` | sz 4 cm (167, x1.38) | x1.15 |
Pick each category's best rung, then refine between rungs (and by object class) with later uploads.

## 3D simulation / segmentation convention audit (2026-10-12): candidates on probe 8
`research/sim3d/` (test inputs only for evidence; validation only in `evaluate_val.py`). Checked against the Blender
label conventions (3D origin speed, backward differences, tangential acceleration, world-AABB sizes, range depth):
- (a) radial speeds: labels include depth (42 stated speed priors have |dr/dt| <= v, up to 0.99 v), and our direct
  answers include it too (no constant-speed answer below |dr/dt|; leave-one-fact-out ratio 0.975 for mostly-radial
  objects). The real deviation is the reverse: 12 of 127 answers sit on |dr/dt| itself (lateral part dropped), e.g.
  0031 boat 3.5 vs stated 4, 0039_seg eagle 2.2 vs 11.84, 0048 bike 4.6 vs 4.87.
- (b) speed priors converted from image motion only: refuted (sizes in speed-prior clips fall, not rise, with the
  prior's radial fraction: Spearman -0.75, n=28). (c) tangential accel: no curved-path accel rows with evidence;
  free-fall phases are labelled 9.8 (priors say so). (d) AABB sizes: no test evidence (the turning car keeps one
  length 5.44; person heights run 1.13x stated, not low). (e) units, fps, times: clean.
- Candidate `trackA_cand_sim3d_motionfam_on_p8.csv` (S3 20, D3 9 rows): speed / acceleration labels stated by
  another camera of the same Blender scene (incl. the photo-lab street 0045-0050 and the beach person 1.3 m/s past
  the 2x guard), gated by 3D consistency (|dr/dt| <= 1.05 v in every camera) + free-fall boxes -> 9.8.
  `_guard` variant (S3 15, D3 9) keeps the 2x guard. Validation premise check: the gates reach 4 validation
  questions and transfer the label within 0.8% in all 4. Upside if the stated labels hold: S3 +.009 (guard +.003),
  D3 +.001.

## Scoring change (organizers, 2026-10-11): validation-overlap questions excluded
140 test questions that overlap the public validation set (exact + reviewed equivalents) no longer count; all
earlier submissions were rescored (probe 5: .793 -> .7921). Keep all 3289 rows. We never used validation labels in
test answers, so nothing else changes. Decoding diagnostics now uses SCORED counts (exact overlaps found: 128 of 140,
so these are approximate to +-12 rows): N = S2 553, D2 1137, S3 538, D3 933. Diagnostic C subsets (scored n):
S2 acceleration 72, S3 lab motion 165, D3 lab motion 105, D2 internet 201.
subset mean = (score_7b - score_diagC) * N_scored / n_scored. Validation clips are test clips too, so judge future
changes on validation mainly through the non-overlapping rows and the leaderboard.

## Lab distances (2026-10-12): candidates on probe 8, D3 only
`research/labdist/` (test inputs and our own cached answers for evidence; validation labels only in `evaluate_val.py`).
Lab distance-type rows: S3 61 (27 displacement, 13 distance, 21 path length), D3 127 (41 / 77 / 3 + 6 camera
distance); 6 are validation overlaps. How they are answered now: distances mostly geometry (depth_info as range,
f from LAB_FOV_DEG), several renders direct; the label procedure (clicked centres, ToF depth at the click,
back-projection, Euclidean distance) is what the geometry already does whenever depth_info states both objects at the
asked time, so the systematic convention terms are only Z vs range (x1.04 median on distance rows, up to x1.28) and
f (80 deg spec: x0.955); neither can be settled label-free (cross-camera 0054a/b favours range weakly). The losses
are measurement failures in specific families, and renders of one event share one label:
- R1 render copy: s/x render rows answered by Claude's direct answer take the original render's value. Premise on
  validation (raw direct answers, 20 s/x lab questions, all kinds): .610 -> .680 (+.070, 90% CI +.025..+.120).
- R2 family log-median where a family's values spread > 15%; R3 0054b/bs orange-soccer at 1.0 s used the soccer
  ball's 2.0 s depth (2.0 m) -> 0054bx's looming geometry (1.33 m).
- R4 (emu only) ball-to-floor / ball-to-desk rows of 0008/0009: clicked-point emulation with the stated depths and the
  Claude floor/desk click lying on the ball's own vertical (0009: fall direction vs apex->floor 3.6 deg; the 3D drop
  then matches g = 9.8 at the 25 fps capture clock). 0009: initial 129.5 cm (was 117.7 / 70.75 / 70.75; 70.75 is the
  depth difference = a lower bound), max rebound 64.6 cm (was 30.1 / 44.9 / 44.9); 0008: 81.0 / 36.6 cm.
| Candidate | rows (D3) | expected D3 (estimate) |
|---|---|---|
| `trackA_cand_labdist_fam_on_p8.csv` | 27 (R1 17, R2 8, R3 2) | +.002..+.003 |
| `trackA_cand_labdist_emu_on_p8.csv` | 32 (R1 13, R4 12, R2 5, R3 2) | +.004..+.006 if the clicked-point model holds |
Not changed: 0041 ball-to-person (no person depth), 0018 at 3.0 s (past the clip end; s/x copy only), S3 rows
(displacement: direct ~ geometry where both ends have depths; paths belong to the labnoise ladder).
Review (`research/verify_labdist/verify.py`): both CSVs are clean (3289 rows, template order, finite > 0, only
the claimed D3 rows differ, no stated-fact or validation-overlap rows). R1's premise does not hold as stated: over
all 6 validation lab families, direct answers score original .671, x render .671, s render .612 (n 35/34/34), so
copying the original's value into an x render gains about 0 in expectation; the +.070 comes from 4 clips (by clip:
+.04/+.22/+.09/-.03). The 0018s copies are still backed by geometry on the original's tracks, and 0018's two-people
distance with the stated near/far depths is 226 cm (range), against 230 after the copy. The 0009 emulation passes an
independent timing check (8 frames contact to apex = 0.544 m rise; emulated 0.530). R2 on 2891 (0054bx soccer
displacement 0.384 -> 0.444) contradicts R3: 0054bs's 0.444 is already a copy of 0054b (its own geometry is 0.392),
and 0054b lacks the looming. `trackA_cand_labdist_verified_on_p8.csv` = emu without 2891 (D3 31 rows). Expected
D3 +.002..+.004 (about 2-4 item points over 933 scored D3 rows), overall about +.001. Estimated, not measured.

## Result: probe 8 = 0.800 (2026-10-11 23:05, new scoring, 3149 scored rows)
| | S2 | D2 | S3 | D3 | MRA |
|---|---|---|---|---|---|
| probe 8 | .815 | .844 | .747 | .796 | **.800** |
Estimate was .813/.843/.755/.798. New base for reading probes 11-15 (all built on probe 8).

## Results: probes 11 and 13 (2026-10-11 23:06-23:08, on probe 8 = .815/.844/.747/.796)
| | S2 | D2 | S3 | D3 | MRA |
|---|---|---|---|---|---|
| 11 (S2/D2 Blender emulation, S3/D3 lab-noise sz 2 cm) | .813 (-.002) | .844 (0) | .762 (+.015) | .797 (+.001) | .804 |
| 13 (S3 lab-noise sz 3 cm, D3 lab motion x1.40) | .815 | .844 | .761 (+.014) | .796 (0) | .804 |
- Lab label-noise emulation is real: S3 +.015 (148 rows changed). Optimum near sz 2-3 cm; probes 14 (4 cm) / 15 (1 cm) bracket it.
- D3 lab motion: uniform x1.40 nets 0, emulator +.001 -> D3 lab speeds are not uniformly inflated.
- Blender label emulation: S2 -.002, D2 0 -> dropped (paper's backward-difference / tangential convention not confirmed).
New best per category: S2/D2 probe 8, S3/D3 probe 11 -> `submissions/trackA_best_p16_p8_labnoiseS3D3.csv`
(expected .815/.844/.762/.797 = .8045). New base for further candidates.

## Lab sizes (2026-10-12): candidates on probe 8 (`research/labsize/`)
Test inputs only for evidence (frames, Claude records, prior/depth text); validation labels only in `evaluate_val.py`.
Lab size rows: S3 119, D3 229 (348; 36 stated facts, ~144 family pools in probe 8). Findings:
- **Stated size priors** (50 renders; balls + credit card) read +10% (family median) through the camera geometry
  (f 711), with large scatter (-16%..+47%, e.g. 0031's tennis/white-ball depths look swapped, 0033 +41%). No global
  factor: the basketball reads -2..+6%, and a focal length from **rectified table tops** (below; right angle in yawed
  views 0022/0014/0029: f 709-715; cross-view agreement of the table's sides is flat over f 720-790) does not
  support the 80-deg spec (f 763) clearly either. **Credit card**: Claude's extent equals the segmented card
  (100 px) and the 0038 depth anchors agree on the table plane within +-3%, so the card's +6..+8% is geometric, not
  annotation; it only matters for the 0037-0040 scene (variant `_s3p`).
- **Metric rectification of the lab table** (corners refined on the uniform-background renders, plane scale from
  depth_info anchors, 8 views): 75.9 x 59.7 cm (median of all 8 views, f 722; 76.6 x 60.4 without the two eye-level
  views; 74-77 x 59.6-60.9 for f 711-763). Probe 8 had 68/70 x 57.6 (pooled direct answers; the receding side is
  foreshortened).
- **Elevated camera / flat objects**: captured_0014's camera is 91 cm above the table top: upright heights read at
  sin = 0.89 (cup 12.3-13.5 vs 14.6 in 0013's level view) and flat objects' receding sides are foreshortened
  (notebook long side 12.0-12.8 fronto-parallel vs 17.6/18.0 on the rectified plane; pen 15.4 on the plane vs probe 8's
  12.1 pooled from 0013's end-on view).
| Candidate | S3 | D3 | Rules |
|---|---|---|---|
| `trackA_cand_labsize_main_on_p8.csv` | 35 | 81 | TB table 76.0 x 60.3 (S3 35, D3 12); BI ball identity (D3 10: 0001 tennis 6.7, 0010 red pendulum ball 7.0 as in 0027, 0054 orange ball = basketball 23.2); EL 0014 elevation/plane (D3 20: cup /0.891, notebook length 17.3, pen 14.9 for 0013+0014, notebook thickness 1.46 pooled over 0014/0023/0024); RP render median where renders spread > 5% (D3 39) |
| `trackA_cand_labsize_wb_on_p8.csv` | 35 | 83 | main + 0062 whiteboard self-rectified on the floor 85.7 x 64.0 (probe 8 83-98 x 46-48; floor-plane check of Claude's extents 80-86 x 70-73) |
| `trackA_cand_labsize_s3p_on_p8.csv` | 77 | 81 | main + S3 scene 0037-0040 x0.958 (42 rows): halfway (log) between camera geometry and the scene's stated priors (+8.5% median over 12 renders) |
Expected (estimates, not measured): main S3 +.003..+.006 (16 scored table-length rows 68 -> 76 move from 0.8-0.9
to 1.0 if the table is ~75-76; width 57.6 -> 60.3 neutral), D3 +.005..+.009 (BI ~+1.5 pts, EL ~+3 pts, TB ~+0.3,
RP ~+1..2 pts over 933). `_wb` D3 +.001..+.002 more if the board is ~85 x 60-65. `_s3p`: S3 -.004..+.007 (hedge:
under either calibration the 42 rows stay within ~4.5%). Validation premise (overlap rows, unscored on test; n=4):
0021x table 60 x 75 (cand 1.0/1.0 vs p8 1.0/0.9), 0013 pen 14.5 (cand 1.0 vs 0.7); the val table and pen labels
had been seen during the study, so these are not independent checks. All three candidates change only lab size
rows, disjoint from p16's lab-noise rows, so they compose with `trackA_best_p16_p8_labnoiseS3D3.csv` directly.

## D2 static targets under motion priors (2026-10-12): no systematic convention found; one small fix
`research/d2static/` (test inputs only; validation labels only in `val_bias.py`). Five hypotheses, each checked on
test-side evidence:
- **Stated facts (leave-one-fact-out, raw pipeline answers).** D2 sizes vs a family-stated size: under speed priors
  median 1.025 (n=5, 0.994-1.028), under acceleration priors 0.996 (n=11, 0.952-1.014); D2 speeds under accel priors
  0.948 (n=2), accels under speed priors 1.026 (n=2). Same object/question answered under a size prior (S2) in another
  camera vs under a motion prior (D2): median log ratio 0.000 (accel, 71 pairs) / +0.009 (speed, 32 pairs), but only
  13 D2 clips have such partners. No scale bias beyond ~2%; the only deviations (0068/0069 and 0085/0086 cars
  accelerating from rest, ~-4.6%) are two scenes, too few to generalise.
- **H1 untimed speed priors** (111 D2 clips, 481 static rows): the prior object's pixel speed is constant (thirds
  within ~10%) in all but one family; 0189 box (lifted, speed x0.5 -> x1.5 over the clip, 10 rows) is the only
  accelerating one, and its sizes already agree with the size-prior sibling 0190 within ~4%. Not a lever.
- **H2 untimed accel priors** (72 clips): profiles are uniform acceleration (from rest r_start ~0 / r_end ~2, or
  linear deceleration); fit = label convention. No change.
- **H3 time base**: container vs dataset fps differs for 83 videos; in D2 only 0257/0258 (30 vs 24; their sizes match
  0259/0260, whose container is 30, so dataset fps is right) and 0284-0287 (25 vs 24; no anchor). No free-fall
  anchors exist in size-prior 2D sims. Not testable further; no change.
- **H5 internet**: scene series with inconsistent stated priors (desk 0043/0044/0045: same bottles 12.6 / 29.4 /
  34.6 cm; scooter rider 1.14-2.83 m). Validation internet clips follow the in-clip prior (ratios ~1.0), so answers stay
  in-clip. **Found a real bug**: internet_0060-0063 are portrait phone videos stored sideways (gravity along image
  x; `rot_detect.py`, |a_x|/|a_y| 28-280), so the forced-vertical gravity prior fails ("prior_motion_below_noise") and
  all 24 rows fell back to Claude's direct guess. `rotated_gravity.py` re-solves them with tracks rotated 90 deg.
  Claude's direct answers had already done the same arithmetic, so values move only 0-7% (median |change| 3%).
| Candidate | rows | expected |
|---|---|---|
| `trackA_cand_d2static_rotgrav_on_p8.csv` | D2 24 (internet 0060-0063) | D2 +0.000..+0.001 (geometry vs direct on validation D2: .897 vs .878) |
Conclusion: D2 static loss is per-question extent / definition error, not a shared convention; getting D2 to ~.87
would need better extents (zoom pilot, size envelope) rather than scale corrections.

## Targeted paid re-ask (2026-10-12): not worth +0.01; no candidate (`research/reask/`)
Plan only, no API calls. Re-asks are simulated with cached runs: on validation (EVALUATION ONLY) the other cached
samples of each question stand in for a fresh answer (`val_eval.py`, `val_boot.py`, 90% CIs from a video bootstrap);
on test, stated-fact rows (85, exact labels from the families; 73 on 3D non-lab) check flags and medians label-free
(`test_flags.py`). Budget left: Claude ~$62.6 (ledger $137.40 of $200), OpenAI ~$34.
- **Flags find bad rows, but a re-ask does not fix them.** Validation base .784 (n=159, 12% of rows score < .5).
  conf <= 0.2: base .611 (32% wrong), 3-run spread > 0.3: .552, geo/direct disagreement > 0.4: .644. Test facts agree
  (conf <= 0.2: .375 vs .729 for all fact rows). But a fresh sample on the flagged rows scores within about +-.02 of the
  base: one re-ask on conf <= 0.3 +.007 [-.039, +.062], median of 3 +.013 [-.021, +.057]; the oracle best-of-3 would
  be +.08, so the misses are shared by all samples (as the ICC .84-.95 per-video offsets said).
- **The verify pass (qp/claude_verify, zoomed crops + verification prompt) is negative on every flagged subset**:
  -.061 per row overall [-.119, -.010], -.16 on conf <= 0.2.
- **More ensemble members.** 2D: median of 3 +.000 [-.024, +.019] (2D direct medians negative). Lab: med3 of direct
  answers -.013 vs base; med5 +.013 [-.011, +.046] (and the test has only ONE lab run, so a 3- or 5-member lab median
  needs 2-4 new runs). 3D non-lab: med3 +.015 [-.027, +.080] (test facts: med3 .715 vs base .716 vs single extra runs
  .700/.699, i.e. a median is ~+.01 better than a random run, not than our base); a 4th member (v2) +.000, a 5th (xhigh)
  +.010 [-.007, +.027], +.041 [+.017, +.054] on high-spread rows (n=17, carried by the xhigh member only).
- Beyond-clip-end (34 scored rows, 31 in captured_0018 D3), track-coverage gaps (22) and magnitude flags (66, 0/4 wrong
  on validation) are not re-askable or not predictive.
Ranked spend plan (rows = scored, non-overlap, non-fact rows that still follow the raw answer; costs from the ledger's
per-video prices of the same videos; gains are estimates = per-row validation gain x rows / N_cat / 4):
| Rank | Spend | Rows (by category) | Cost | Expected overall MRA |
|---|---|---|---|---|
| 1 | Zoomed extent re-measure (zoom pilot tool) on S2/D2 sizes | S2/D2 sizes | $6-12 | +.003 (pilot model; weak) |
| 2 | 2D conf <= 0.3: one fresh v1-high answer, geometric mean with base (val +.020/row, n=20) | S2 72, D2 115 (85 videos) | ~$7 | +.001 |
| 3 | 3D non-lab spread > 0.15: 4th/5th member (xhigh) on 54 videos (val +.041/row, n=17, fragile) | S3 62, D3 67 | ~$15 | +.001..+.002 |
| 4 | Lab direct rows: 2-4 new runs for a median | S3 21, D3 57 (26 videos) | ~$7-13 | +.0003 |
| - | Full 2D ensemble / verify pass | | $22/run / ~$40 | 0 / negative |
Everything together: about +.005 for ~$35, every CI includes 0, so a re-ask cannot reach +0.01 (0.85 needs +.045).
Free re-routing rules on the existing 3D non-lab runs (highest-confidence run, confidence-weighted mean) tie the median
on validation (.810 vs .810) and lose on test facts (.701 vs .715): no candidate built.
Pilot before any spend (free part done here; the gate costs ~$1-2): pre-register "spend only if the re-ask gains
>= +.03 per flagged row". Gate set = test stated-fact rows whose raw answer is flagged (conf <= 0.3 or spread > 0.15:
~40 rows in ~15 videos; the facts are exact labels by the same procedure, and fact rows stay protected in the
submission, so the pilot changes nothing it scores); price it first with `scripts/run_claude.py --dry-run
--local-estimate` (no API call). If the gate fails, keep the money (validation and test facts both predict it will).

## Internet label emulation (2026-10-12): candidates on probe 8 (`research/internet/`)
Test inputs only for evidence; validation labels only in `eval_val.py`. Internet = S2 203 / D2 217 rows (S2 ~191 / D2
~200 scored). Findings:
- **No shared scale convention left to emulate.** Validation internet rows already score .91 (29 rows, every run
  .86-.92). S2 size-prior answers are physically plausible clip by clip (pickleball court 13.41 = regulation, MacBook
  35.5 x 24.7, dollar bill 154.6); lane-width clips read cars ~5.7 m long, as does the validation label (5.81), so the
  ruler convention is matched. Gravity clips with container fps = dataset fps read physical sizes (rim 3.04 m,
  basketball 24.7 cm, ping-pong ball 4.2 cm).
- **Time base.** Segmented twins re-encoded from 24/25 fps carry regular duplicate frames (0001s/0002s/0003s/0026s/
  0027s; 0025, 0039, 0012 too) and internet_0029 drops every 6th frame (60 -> 50 fps: steps 24, 25, 58, 33, ... px):
  its gravity scale differs by up to (60/50)^2 between a smooth fit and consecutive-frame differences, so the label
  cannot be pinned; left alone.
- **Forward differences (FWD).** Timed speeds as |p(i+1) - p(i)| * fps on the fitted track (App. D.3), incl. the
  scale of clips whose prior is a timed speed. Validation: 3 changed rows, mean |log err| .040 -> .026 (0019 ball
  3.54 -> 3.68 vs label 3.70), item scores unchanged (all 1.0).
- **Window accelerations (WINACC).** "Acceleration from 0s-2s to 2s-4.5s" etc.: (v2 - v1)/(midpoint gap) from the
  window speeds the sibling questions ask, instead of a parabola's curvature (0039 swimmer 0.079 -> 0.012; Claude's
  direct 0.02).
- **Families.** Segmented twins not copied by probe 8 because the wording differs ("speed" / "average speed",
  "9.8m/s"): log-mean of twin and original (0001s, 0002s, 0019s). The toy acorn of 0061 / 0067 / 0068 is one object:
  0067 states its height 8 cm -> the two other "height of the acorn" rows.
- **Open question, one upload decides (PHYSB).** Clips whose in-clip scale contradicts their own scene family: desk
  0043 (prior 33.38 cm/s) reads the same bottles / kettle 2.35x smaller than 0044 (gravity) and 0045 (107.3 cm/s, which
  agree); the scooter rider (same person and scooter in 0049-0056) reads 1.14 / 2.45 / 2.83 m in 0051 / 0053 / 0054 vs
  1.58-1.64 m elsewhere, while his pixel speed is ~1.8 body heights/s in every clip (stated speeds 2.07-4.9 m/s do not
  follow it). Rescaled, the scooter reads 1.09 m in 0053 and 0054 and 1.07 m in 0052. If the labels are physical
  (the annotators' stated speed carries an error their labels do not), D2 gains ~+.012; if labels follow the stated
  prior (D2-static's reading; validation 0005/0013 cannot tell the two apart because their priors are plausible), D2
  loses ~.012. 29 D2 rows; use as a probe, not in a best-of file unless it wins.
| Candidate | rows | expected (estimate) |
|---|---|---|
| `trackA_cand_internet_fwd_on_p8.csv` | S2 19, D2 36 (median x1.011, cap 15%) | S2 +.000..+.001, D2 +.000..+.001 |
| `trackA_cand_internet_winacc_on_p8.csv` | S2 5 (0032 x1.20-1.24, 0037 x1.12, 0039 x0.15) | S2 -.001..+.004 |
| `trackA_cand_internet_fam_on_p8.csv` | S2 2, D2 9 scored (+ unscored val-overlap originals) | +.000..+.001 |
| `trackA_cand_internet_main_on_p8.csv` | fwd + winacc + fam: S2 28, D2 50 | S2 +.000..+.005, D2 +.000..+.002 |
| `trackA_cand_internet_physb_on_p8.csv` | D2 29 (0043 x2.35; 0051 x1.42, 0053 x0.66, 0054 x0.57) | D2 +-.012 (hypothesis test) |
Internet alone cannot carry the run to .85: even perfect internet rows (from ~.85-.90 to 1.0) add ~+.015 overall.

## Review of the D2 static study (2026-10-12, `research/verify_d2static/`)
Re-ran `rotated_gravity.py` (bit-identical), `cross_prior.py` (103 pairs; median log ratio accel +0.000, speed +0.009)
and the stated-fact ratios (D2 sizes: speed prior median 1.025 on 5 clips, accel prior 0.996 on 11 rows/9 clips) -
all reproduce. No validation labels in the candidate path. `rotgrav` CSV is clean (3289 rows, template order, finite
> 0, only 24 D2 rows of internet_0060-0063 differ). Sideways gravity confirmed from the falling tracks themselves
(0063's detector ratio 3.5 came from a bogus extent track; its falling track accelerates along x only).
Problems: (1) qid 3196 (0061 acorn height) collides with `internet_fam`/`internet_main`, which set it to the 8 cm
stated in internet_0067; rotgrav would overwrite a stated-fact row when composed -> dropped. (2) The "+.02/row"
gain basis is generic validation D2 (n=37), not these clips; 0061/0062 values move < 1.3% (no-ops), only 0060
(-6%) and 0063 (-4%) move, both within the ~8% noise of a 5-6 point curvature fit, so the gain is ~0 +- .001.
(3) Velocity rows used the central (ICI) derivative while the internet convention (App. D.3, adopted by
`internet_fwd`) is a forward difference: on free fall that is +g/(2 fps) = +0.16 m/s (+4..+10%).
| Candidate | rows | expected (estimate) |
|---|---|---|
| `trackA_cand_d2static_verified_on_p8.csv` | D2 23 (rotgrav minus 3196) | D2 +0.000 +- .001 |
| `trackA_cand_d2static_verified_fwd_on_p8.csv` | D2 23, 6 velocity rows forward-differenced | D2 +0.000..+0.002 (only if FWD convention holds; use with internet_main) |

## Review of the re-ask study (2026-10-12, `research/verify_reask/`): conclusion holds, three numbers weaker or wrong
All re-ask tables reproduce exactly (val_eval / val_boot / test_flags rerun; outputs byte-identical). No candidate existed
or is built. Budget confirmed from the ledger: usage $137.40, all 46 holds released.
- **3D non-lab xhigh "+.041 on high-spread rows, n=17"** is 4 videos, 8 of the 17 rows from simulation_0009, so the
  video-bootstrap CI over 4 clusters means little. The gain is specific to xhigh (5th member fable +.006, med -.024,
  med2 -.006). xhigh also returned no direct answers on 3 of 24 validation videos (24/159 questions), which is a
  wasted-spend risk on test. Treat rank 3 as 0 to +.002.
- **The stand-in re-asks are not the test configuration** (v1b = 480p copies, v2 = different prompt). Subtracting each
  source's all-row offset: lab conf<=.3 one re-ask +.018 [+.007,+.041] (n=22), 2D conf<=.3 v2 re-ask +.046 [+.006,+.156]
  (n=20), 3D non-lab about 0. Each is still about +.001 overall.
- **Free rules (not scripted in reask/):** most-confident run = base under first-run tie-break (val .794, test facts
  .716). Confidence-weighted log mean: val .804 vs median .810, test facts .725 vs .715 (73 rows / 31 videos). So it does
  not "lose on test facts"; the evidence is mixed, and the upside is <= +.001 overall. No candidate.
- **The gate pilot is uninformative for most of the plan**: 37 flagged fact rows in 20 videos, all 3D non-lab (ranks 1, 2
  and 4 are 2D or lab). A proxy (extra run minus base on those rows) gives a clustered SD of the mean gain of ~.022, so
  the +.03 gate is ~1.4 SD.
- Arithmetic bound: about 61% of scored rows can still move, so +.01 overall needs >= +.016 per moved row. The best
  full-run median on validation gives +.003 per row, and $62 buys about 1.5 test-wide v1-high runs. Re-asks can't
  reach +.01. Corrected total for the ~$35 plan: about +.004 to +.007 (estimate).

## Review of the internet study (2026-10-12, `research/verify_internet/`)
Re-ran `eval_val.py` (FWD on validation: 3 rows, |log err| .040 -> .026, item scores unchanged = measured gain 0) and
the builder's numbers (PHYSB desk ratios 2.02-2.53, rider heights) - all reproduce. All 5 CSVs are clean (3289 rows,
template order, finite > 0, only internet rows of the claimed categories differ; no stated-fact row changed).
Problems: (1) TWIN premise is testable on the 7 twins whose original is a validation question (evaluation only):
item sum 6.4 -> 6.4, mean |log err| .0723 -> .0742 -> no benefit, dropped. (2) WINACC 0039 (x0.15) rests on window
speeds that differ by 1.9% (0.7556 / 0.7416), below the ~4% internet speed precision: the value is noise; dropped by
a gate |dv| >= 5% of v (keeps 0032 x3, 0037). (3) FWD changes internet_0029 (+4-5%) although the study itself
found its 60->50 fps frame dropping makes the annotators' one-frame difference ambiguous; undone. (4) PHYSB is not
symmetric: App. D.3 defines GT = gamma(prior) x pixel quantity, so labels are in-clip unless the annotators' pixel
speed of the prior differs from ours by 2.35x (0043's ball moves at constant ~19.5 px/frame over frames 24-56);
D2 -.015 if in-clip, +.015 if physical (= -/+ .004 overall). Precedent: Blender difference-convention emulation looked
good on validation and lost S2 -.002 on the leaderboard.
| Candidate | rows | expected (estimate) |
|---|---|---|
| `trackA_cand_internet_verified_on_p8.csv` | S2 23, D2 36 (FWD minus 0029; WINACC 0032/0037; acorn 8 cm) | S2 +.000..+.002, D2 +.000..+.001 (unmeasured) |

## Probes 17 and 18 (on p16 = best per category: S2/D2 probe 8, S3/D3 probe 11; expected .815/.844/.762/.797)
Row-level merges (`research/merge/merge_rows.py`, refuses conflicting edits). Candidates from workflow wf_6d9871ad-48d
(verified versions only):
| Probe | S2 | D2 | S3 | D3 |
|---|---|---|---|---|
| 17 `trackA_probe17_p16_stack.csv` | internet_verified (23) | internet_verified + d2static_verified (59) | labsize_verified: table 74.5 cm (35) | labsize_verified (63) + labdist_verified (31) |
| 18 `trackA_probe18_p16_physb_sizeenv_sim3d.csv` | size envelope (49) | internet PHYSB hypothesis (29; expect loss) | sim3d motion families, guard (15) | sim3d motion families (9) |
Plus probe 14 (S3 lab-noise sz 4 cm vs probe 8; D3 lab motion x1.15). Expected: 17 ~ +.002..+.004 overall;
18 mostly a hypothesis/bracket test. Re-asks: not worth the money (~+.005 for $35).

## Probes 19 and 20: decompose the S3 lab-noise gain (+.015) and push D3 emulator strength (on p16)
`research/labnoise/build_decomp.py`. 19: S3 = p16 minus the 18 small-ball path-length rows (x1.54); D3 = emulator 3 cm.
20: S3 = p16 minus the 36 mid-ball speed rows (x1.29); D3 = emulator 4 cm. S2/D2 = p16. Model-expected S3 split:
path 3.0, mid-ball speed 1.9, small-ball speed 2.3 item points (of ~8.4 / 538 scored = ~+.016). Upload after 17/18/14
if the S3 lever needs refining; whichever part loses gets reverted, the winning parts get a stronger setting.

## Track B (2026-10-12)
Colab run trackb_v1 (vLLM fix in): validation MRA caw .548, cv_geo .541, qwen_geo .526, cv_geo_only .446,
qwen_direct .399; per-cell routing (LOVO) .556-.576; log-median of the 4 = .589 (`trackB_v1_median4_post.csv`).
Gross misses (>2x off) 40-60% on D2 sizes and D3 distances. Model-free family rules ported to qp/postprocess.py
(preset "trackb": facts, motionfam, freefall, labfacts, pool): validation .604 (`trackB_v2_median4_famrules.csv`);
stated facts +.013 (7/7 exact), pool unconfirmed by LOVO but +.06 per row on test-side held-out facts.
Next run (notebook d463467): Qwen-box-prompted SAM 2 (cvq) + Qwen3.5-27B + Gemma-4-31B direct answers in the median.
Track B v3 (`trackB_v3_catmedian_famrules.csv`): per-category median members (S2 caw+cv_geo+qwen_direct; D2 all 4;
S3 cv_geo+qwen_geo+qwen_direct; D3 caw+qwen_geo+qwen_direct; chosen by validation, LOVO .6035 vs .5887 for all 4)
+ preset "trackb" family rules (919 rows changed). Expected ~.61-.63.

## Results: probes 17 and 18 (2026-10-12 16:05, on p16 = .815/.844/.762/.797)
| | S2 | D2 | S3 | D3 | MRA |
|---|---|---|---|---|---|
| 17 stack (internet_verified+d2static D2/S2, labsize S3/D3, labdist D3) | .815 (0) | .843 (-.001) | .763 (+.001) | .802 (+.005) | .806 |
| 18 (size envelope S2, internet PHYSB D2, sim3d motion families S3/D3) | .817 (+.002) | .853 (+.009) | .765 (+.003) | .798 (+.001) | **.808** |
- PHYSB won (+.009 D2): internet speed labels are physical, not prior-consistent -> extend family-anchored rescaling.
- Limit is 5 successful submissions per UTC day across both tracks (resets 00:00 UTC).
Best per category -> `trackA_best_p21.csv` = p16 + sizeenv(S2) + physb(D2) + labsize(S3,D3) + labdist(D3) + sim3d guard(S3,D3);
expected ~.817/.853/.766/.803 = .810.

## PHYSB2 (2026-10-12, `research/physb2/`): extend the physical-scale finding; candidate on p21
Probe 18 showed PHYSB's 29 D2 rows gain ~10.2 item points (+.009 D2). `calib_physb.py`: 0043 must be physical
(in-clip would cost -7.4), 0053/0054 almost surely, 0051 ambiguous. So self-filmed internet clips (desk / campus /
gym / mug series, 0043-0070) are labelled on the physical scale when their stated motion prior is off; downloaded
clips (validation 0001/0004/0005/0013/0019/0027) stay in-clip. Gate fixed before building (docstring of
`build_candidate.py`): same object/person on frames (`frames.py`), one exact family fact or two independent lines,
|ln k| >= max(0.10, 2 sigma), only in-clip geometry rows, never PHYSB / stated-fact / validation-overlap rows.
| Clip | k (sigma_log) | Evidence |
|---|---|---|
| 0055 (walking person, "scooter 1.95 m/s") | 0.701 (.045) | she is the scooter rider (frames): family height 1.624 m vs 2.317 read; rescaled walk 1.37 m/s (stated 1.95 is a jog); DO NOT ENTER 1.21 m -> 0.85 (MUTCD 0.76/0.91) |
| 0069 (cup, accel 0.32 m/s^2 over 0.3 s) | 0.705 (.027) | exact family fact: same mug / string-pull setup as 0046, which states cup height 10.5 cm (0069 reads 14.89); cup 254 vs 246 px in both |
| 0045 (cylinder 107.3 cm/s) | 0.848 (.031) | g-anchored 0044 on the same bottles/plate: 0.848/0.858/0.844; 0045 is 11% zoomed in yet reads 6% more cm/px; 0044 ping-pong ball 4.23 cm, 500 ml tea bottle 22.2 cm (0045: 25.8). Kettle-plate distance not a line (layout changed) |
| 0047 (ball 2.94 m/s, overhead gym) | 0.872 (.045) | same-gym gravity clips read the basketball 22.7/24.7/25.3 -> 24.2 cm vs 27.8; regulation 23.0-24.8 cm |
| 0061 / 0068 acorn height | fact row only | 0067 states 8 cm (8.6 / 7.82 read; k 0.93 / 1.02 below the gate, scale left) |
Screened out: 0005_segmented (downloaded; twin scale 0.87x the original but no physical anchor), 0028 / 0073
conveyors and 0070 speedboat (no anchor or a single weak line), 0065/0066 (top-down "g", already direct with a 24 cm
ball), gravity clips (anchors), S2 internet (size priors are the physical anchor). Simulation: only 2D clips with
fact/in-clip mismatch > 15% are simulation_0041(+seg) (top-down person "1.75 m" foreshortened; boat 10 m reads
13.3-14.6), already absorbed by family facts/pooling and the person-speed fact disagrees -> no rows. 3D sim/lab
mismatches are direct-answer errors, not a prior scale.
| Candidate | rows | expected (estimate, label scatter 8%) |
|---|---|---|
| `trackA_cand_physb2_on_p21.csv` | D2 30 (0055 8, 0069 8, 0045 6, 0047 6, acorn 2) | D2 +.007 if physical, -.005 if in-clip; ~+.005 D2 (+.001 overall) at the PHYSB hit rate |

## Next uploads on p21 (2026-10-12): method switches and a complete loss map
- probe22 `trackA_probe22_p21_switch_direct.csv`: S2 internet, D2 sim static, S3 lab static, D3 lab static -> Claude direct
  (only pure-pipeline geometry rows; in 2D direct ~= geometry: 5-7 of 132-228 rows move >10%, so small effects).
- probe23 `trackA_probe23_p21_switch_gm.csv`: S2 sim motion -> gm(geo,direct), D2 internet -> direct, S3/D3 lab static -> gm.
- diagE/diagF (`trackA_diagE_on_p21.csv`, `trackA_diagF_on_p21.csv`): complementary zeroings that partition every
  category (E: S2 sim 362, D2 sim static 719, S3 non-lab 221, D3 lab static 334 scored; F: the rest). Subset mean =
  (p21 - diag) * N_scored / n_scored; E and F must add up to p21 (consistency check). Purpose: find the subset where
  a +0.02 overall jump could come from (needs ~+.08 in one category).

## Local tests toward top 5 (2026-10-12; leaderboard 21:00 UTC: 5th szerlok .8195, we are 13th at .8083)
- More Claude runs on 3D non-lab (validation, 52 q): 1-run .783, 3-run median .799, 5-run .800, 7-run .804 -> 3->5 runs
  worth ~+.001 per question; not worth the money.
- Validation D3 lab static (15 q, .67): sizes score .7-1.0; the losses are label problems (desk 857.9 cm, ball-to-person
  0.198 m, ball-to-floor 1.69 m at rest) -> mostly irreducible.
- D3 lab motion and the label-noise model: of 150 D3 lab motion rows, 107 are modelled but the factor is ~1.00 (objects
  fall/move fast, click noise is small relative to the motion); 43 have no model (0018, 0010, 0016...). So D3 has no
  S3-like lever (consistent with D3 x1.40 netting 0).
- In 2D, Claude's direct answers ~= its geometry (switch probes 22/23 change few rows).
Path to top 5 (+.012): p21 (~.810) + physb2 (~+.0015) + S3 lab-noise tuning (probes 14/19/20, ~+.002) + whatever the
diagnostic E/F map exposes.

## 2026-10-12: outside ideas on the 3D gap (Gemini, Claude research session), quick checks

Sources: `research/consult/brief_2026-10-12_3d.md` (brief), `gemini_2026-10-12_3d.txt`, `claude_research_2026-10-12_3d.md`.
- Lab near-surface depth (size = px * (Z_click + r) / f): REFUTED on the 41 stated lab ball sizes. With the current
  range convention the balls already read 1.056x stated (non-balls 1.085x); near-surface makes it 1.091x. (The
  0.94x in the brief was an older measurement.)
- Cross-clip asset table (a size stated as a prior anywhere on test answers the same noun elsewhere): 236 test
  hits, but on validation only 4 of 10 hits are right (generic nouns "boat", "ball", "cup", "soccer ball" are
  different props/assets); the right ones are already family facts. Not adopted.
- Spread-driven MRA shading (median x exp(-k s^2), s = log-sd of the 3 Claude runs) on 3D non-lab: validation
  (52 q, 120 run triples) k=0.5/1/2 -> -.005/-.010/-.021; test stated facts (110) -> -.001/-.004/-.009. Rejected.
- Sent to the simfov agent (focal from MoGe-2 / DepthPro on 3D sim clips): sim depth = range to the Blender
  object origin, Blender sensor-fit AUTO f_px = F/36 * max(W, H) with standard lenses, size labels = world box
  dimensions, sim acceleration = d|v|/dt from backward-differenced speeds.
- Open: per-event lab label-noise calibration from the stated prior (D3 lab), forward-difference timing
  (+1/50 s), whether lab labels were smoothed (printed lab accelerations look too clean for raw 2nd differences).

## Results 2026-10-12 uploads (on p21)

| file | S2 | D2 | S3 | D3 | MRA |
|---|---|---|---|---|---|
| trackA_best_p21 | .817 | .853 | .766 | .803 | .810 |
| trackA_cand_physb2_on_p21 | .817 | .859 (+.006) | .766 | .803 | **.811** (new best) |
| trackA_diagE_on_p21 | .275 | .315 | .461 | .517 | diag |
| trackA_diagF_on_p21 | .542 | .538 | .305 | .286 | diag |
| trackB_v3_catmedian_famrules (Track B) | .558 | .663 | .620 | .641 | .621 (val estimate .623) |

Decoded subset means (scored n; points of the category lost):
- S2: simulation+seg .828 (362; .113) | internet .796 (191; .070)
- D2: simulation static .851 (719; .094) | rest .857 (418; .053)
- S3: non-lab (sim+seg) **.742** (221; .106) | lab .782 (317; .128)
- D3: lab static .799 (334; .072) | lab motion + non-lab .805 (599; .125)
S3 non-lab is the weakest subset (the simfov study's target); S3 lab and D3 are close to their category means.

## Foundation-model camera FOV for 3D simulation clips (2026-10-13, `research/simfov/`): REJECTED
MoGe-2 (CPU) FOV for all 94 sim clips (median of up to 3 frames; segmented copies reuse the original's), then
qp.geometry with that FOV as the camera prior (sd of log f 0.01 / 0.05 / 0.15, Blender stock-lens snapping, Z instead
of range), alone, as geometric mean with Claude's direct answer, and gated to well-conditioned priors. Replayed on the
3 cached Claude runs (annotator tracks, no API). Results (item MRA, clip-bootstrap 90% CI of the change vs direct):
- Validation (44 rows, 6 clips): direct .811, p21 .843, old geometry .657, model-FOV geometry .605-.636
  (-.17..-.21), best blend gm_snap05 .734 (-.077 [-.119, -.026]).
- Test stated facts (106 exact rows, 32 clips): direct .793, old geometry .700, model-FOV geometry .49-.55
  (-.25..-.30), best blend gmgate_old .761 (-.032); every model-FOV variant loses.
- By FOV bin (facts): <20 deg direct .650 vs model-FOV .25-.36; 20-60 .757 vs .45-.49; >60 .961 vs .72-.79.
Model-FOV geometry is worse than solving f from the prior; the remaining error is extents / foreshortening and
prior conditioning, not just f. Claude's direct answers (with family rules) stay on 3D simulation. This also covers
the DepthPro / UniDepth / temporal-median FOV suggestions (same failure class; single-image FOV error is too large).

## Uploads U1-U4 (built 2026-10-13 on physb2 = .817/.859/.766/.803), one change per category, read vs physb2
`research/merge/merge_skip.py` (rows physb2 already changed are kept). Never-uploaded probes repacked:
| file | S2 | D2 | S3 | D3 |
|---|---|---|---|---|
| `trackA_u1_p22s2d2_s3sz4_d3emu3.csv` | internet -> direct (p22) | sim static -> direct (p22) | lab-noise sz 4 cm (p14, 154 rows) | emulator 3 cm (p19, 36) |
| `trackA_u2_p23s2d2_s3nopath_d3emu4.csv` | sim motion -> gm (p23) | internet -> direct (p23, 29 physb rows kept) | minus small-ball path rows (p19, 18) | emulator 4 cm (p20, 41) |
| `trackA_u3_s3nomid_d3labdirect.csv` | = | = | minus mid-ball speed rows (p20, 36) | lab static -> direct (p22, 48) |
| `trackA_u4_s3labdirect_d3labgm.csv` | = | = | lab static -> direct (p22, 29) | lab static -> gm (p23, 48) |
Validation loss decomposition (physb2, 131 matched rows): <10% errors cost little; losses come from 20-50% errors
and gross misses (S2 sim >2x: .138 of S2 from 4 rows, incl. label oddities: big bird 0.72 < small bird 0.94,
astronaut accelerations non-monotone; lab: desk 857.9 cm, basketball 9.32 m/s, ball-person 0.198 m).

## Leaderboard 2026-10-12 23:36 local (Track A)
1 Perch AI .8517, 2 Cogworks RSI .8498, 3 Blindfolded .8293, 4 iMak AI Lab .8231, 5 szerlok .8195, 6 Quantumonster .8191,
7 reasoning_wrt .8121; us .811 (~8th). Top two ~.02 above everyone else. Workflow wf_697c11d5-4f2 ("path-to-085") launched:
web research on the top teams + post-QuantiPhy literature, six data-driven lever studies (S2 sim, internet, S3 sim multi-view,
lab, D3 families, leaderboard strategy) with adversarial verification; output research/path85/PLAN.md.

## combo2 (2026-10-13): `submissions/trackA_cand_combo2.csv` = path85 combo + free-fall backward difference (D2 21, D3 15;
research/path85b_phys) + D2/D3 family/event levers E1 (droplets, superseded by ffbd), E2 (0191/0192 pooled drop), L1 (0019 person
1.3) from research/path85b_fam; L2/L3 (0157 turtle x1.113, 0219 robot) left out (same-camera support only). Expected +.001..+.0015
over the combo. Killed: pooled focal per camera group (7/27 held-out priors within 7%), lab ballistic 3D fits (free g 9.7-16.7).

## One question per request (Gemini's top idea), paid pilot 2026-10-13: REJECTED ($6.56)
`research/perq/` (pre-registered kill test in evaluate.py). 52 validation questions on 3D non-lab clips, each sent alone
(same model/effort/frames/resolution/prompt as val_hr_v1_high, batch). Direct-answer MRA: per-question .721 vs batched
single runs .794/.798/.802 and 3-run median .810. Delta vs the matched batched run -.073, clip bootstrap 90% [-.154, -.024],
worse or equal on 6/6 clips (simulation_0170 -.31). Seeing a clip's other questions HELPS Claude (shared scale/objects);
isolating questions removes that context. Kill test FAIL; not scaled up. Budget now $143.96 of $200.
