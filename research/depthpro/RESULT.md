# Depth Pro FOV head as the camera focal for 3D-simulation geometry (2026-10-14)

## Pre-registered kill test (written 2026-10-14 before any Depth Pro output existed)

Hypothesis (Gemini): Apple Depth Pro's dedicated FOV head (median over frames) gives the focal length of the
Blender camera accurately enough that pinhole geometry (depth_info as range) beats Claude's direct answers (dmed,
log-median of the 3 cached runs) on 3D simulation S3/D3 rows. MoGe-2 failed this (research/simfov: focal biased
~0.66x the prior-implied focal, 19% of clips within 10%, geometry -.17..-.30 item MRA).

Clip set (stage 1): the 35 original simulation clips that carry the 106 exact stated-fact rows (32 clips) or the
44 matched validation rows (6 clips: 0009 0015 0034 0060 0170 0300); segmented twins reuse the original's focal.
List: research/depthpro/out/clips_stage1.txt. Frames at 0.15 / 0.5 / 0.85 of the clip (0.5 first; median over frames).

**Stage 1 (focal accuracy).** Error per clip e = |log(f_DP / f_ref)|, focal in pixels at the clip's resolution.
- Primary reference f_ref ("fact/val-implied"): on size-target rows with an exact fact or a validation label, the
  focal that makes the existing geometry reproduce the truth, f_ref = f_used * geo / truth, using the simfov replay's
  geo_fix column (f fixed to MoGe's focal; tracks are Claude's) and only rows where the geometry is proportional to
  1/f (checked empirically: |log(geo_old*f_old / (geo_fix*f_fix))| < 0.02 in the same run). Per clip: log-median over
  rows and runs.
- Secondary reference: prior-implied focal of fov_check.py (ii) (size prior with depth, well-conditioned old solve).
- PASS stage 1 iff, on the clips having a primary reference, median e <= 0.10 AND share(e <= 0.10) >= 0.60.
  If there are fewer than 8 such clips, the per-clip reference is the log-median of the primary and secondary rows.
- MoGe-2 on the same clips is reported next to it (context, not part of the bar).
- Reference noise escape (fixed now): if stage 1 fails only marginally (median e in (0.10, 0.15]) AND the two
  independent references disagree by a median |log| >= 0.10 on common clips (i.e. the reference, not the model,
  limits the test), stage 2 is run anyway and decides. If median e > 0.15: FAIL, stop.

**Stage 2 (geometry vs direct).** research/simfov/replay.py (SIMFOV_FAST=1, Claude's own tracks, no API) with the
Depth Pro FOV file, then research/simfov/evaluate.py, which reports cam05/cam15/fix/snap05/camZ05 and the a-priori
gm_/gate_/gmgate_ blends. PASS iff some variant V has (a) item-MRA(V) - item-MRA(dmed) >= +0.02 on the 106 stated
facts AND (b) >= -0.01 on the validation rows (44 matched rows from evaluate.py; the 52-question 3D non-lab set of
research/perq/evaluate.py reported where the rows match). To guard against picking the best of ~25 variants, V must
also have a clip-bootstrap 90% lower bound > 0 on the facts. If PASS: extend to all 94 sim clips and build
submissions/trackA_cand_depthpro_on_combo3.csv with merge_skip.py on top of trackA_combo3_on_combo2.csv.

Budget: < 2.5 h CPU, no paid API calls. Weights in /home/user/.cache (outside the repo).

## Results

**Verdict: FAIL at stage 1.** Depth Pro's focal is not more accurate than MoGe-2's on these Blender renders.
On this clip set it is about as wrong (median |log f error| .33 vs MoGe .23 against the fact/val-implied focal) and
noisier across views of one camera. Per the pre-registered rule (median e > 0.15), stage 2 (the replay) was not run
and no candidate was built. Paid API: $0. CPU: Depth Pro inference 64 min (35 mid frames, median 82 s/frame at
1536x1536, 4 threads, shared cores) + 19 min for 2 extra frames (stability check below); total ~1.5 h wall.

### Setup (what was run)
```
pip --no-cache-dir --no-deps install timm safetensors          # into /home/user/venv-depth (numpy 2 kept)
git clone --depth 1 https://github.com/apple/ml-depth-pro /home/user/.cache/depthpro/src
hf_hub_download('apple/DepthPro', 'depth_pro.pt') -> /home/user/.cache/depthpro/checkpoints  (1.9 GB)
/home/user/venv-depth/bin/python -I research/depthpro/fov_depthpro.py --out research/depthpro/out/fov_depthpro.csv \
    --videos $(cat research/depthpro/out/clips_stage1.txt) --fracs 0.5          # 35 clips; copy: fov_depthpro_mid.csv
.venv/bin/python research/depthpro/stage1.py research/depthpro/out/fov_depthpro_mid.csv   # -> out/stage1_mid.txt
.venv/bin/python research/simfov/fov_check.py research/depthpro/out/fov_depthpro_mid.csv research/simfov/out/replay.csv
.venv/bin/python research/depthpro/oracle.py research/depthpro/out/fov_depthpro_mid.csv    # -> out/oracle.txt
```
`fov_depthpro.py` runs upstream's inference path (RGB in [-1,1], bilinear resize to 1536x1536, encoder + decoder + FOV
head; the depth head is skipped since the FOV head does not read it). Upstream's convention is fov = horizontal FOV,
f_px = 0.5 W / tan(fov/2). Output columns match `fov_moge.csv`, so `fov_check.py` / `replay.py` / `evaluate.py` read
it unchanged.

### Stage 1: focal accuracy (out/stage1_mid.txt)
Reference quality: the primary (fact/val-implied) reference has 80 size rows over 29 clips. f_ref differs by 3.9%
(sd log) across the 3 Claude runs of a row and by 11% across rows within a clip, so the per-clip median is good to
roughly 5%. The two independent references disagree by a median 16% on 6 common clips.

| reference | clips | Depth Pro: median log(f/f_ref) | median abs | share <= .10 | MoGe-2 (same clips): median abs | share <= .10 |
|---|---|---|---|---|---|---|
| **primary: fact/val-implied** | 29 | -0.221 | **0.334** | **0.14** | 0.229 | 0.24 |
| secondary: prior-implied (fov_check ii) | 11 | -0.109 | 0.328 | 0.27 | 0.417 | 0.09 |
| pooled | 34 | -0.165 | 0.335 | 0.12 | 0.251 | 0.21 |

Bar: median <= 0.10 and share >= 0.60. Result: **0.334 / 0.14 -> FAIL**. This is not marginal, so the
reference-noise escape does not apply.

Cleanest evidence: simulation_0058-0065 (8 clips, 2160x1080). Their fact-implied FOVs are 51.3-57.7 deg (sd log f
across clips 0.041, median 53.3 deg; a 35 mm Blender lens gives 54.4 deg), so the reference is tight there. Depth
Pro: 54.2-74.1 deg (sd 0.133, median 68.2 deg, median |e| .28). MoGe-2: 54.8-66.7 deg (sd 0.083, median 60.0 deg,
median |e| .14). Depth Pro is biased toward wide (typical phone/real-camera) FOVs on mid/long Blender lenses and
scatters more than MoGe.
Other label-free checks (fov_check.py): same-view pairs (thumbnail NCC >= .97) differ by a median 12.1% in Depth Pro
focal (MoGe 4.9%). Stock-lens snapping: 46% of Depth Pro focals fall within 5% of a stock lens (uniform-in-log
chance ~42%), so there is no lens signal to snap to.
Gross clip errors (|e| > .4): 0009 (+.43), 0025 (-.85), 0026, 0035, 0036, 0039 (-1.50), 0042 (-1.64), 0065, 0066,
0067, 0300 (+.60). In both directions, so this is not a simple global bias that a calibration could remove.
Robustness: the 0039/0042 references (11 and 8 deg) may be wrong, since both models say ~45 deg. Without them,
Depth Pro gets median |e| .313, share .15 (MoGe .205, .26), still FAIL.

### Diagnostic beyond the bar: would ANY clip-level FOV make geometry win? (out/oracle.txt)
`oracle.py` (evaluation only; truths build the focal, never an answer). For each of the 71 size rows with a truth
and 1/f geometry, the focal is the log-median f_ref of the OTHER truth rows of the same clip (leave-one-row-out).
This is the best clip-level focal any FOV estimator could return, given Claude's tracks. The analytic
geometry at a focal f is geo = geo_fix * f_fix / f.

| 71 size rows (20 clips) | dmed | old (f from prior) | **oracle clip focal** | gm(dmed, oracle) | MoGe focal | **Depth Pro focal** |
|---|---|---|---|---|---|---|
| all | .752 | .663 | .727 | .754 | .496 | **.499** |
| facts (44) | .755 | .695 | .786 | .775 | .443 | .461 |
| validation (27) | .748 | .611 | .630 | .719 | .581 | .559 |

- Oracle-focal geometry minus dmed: -.025 (clip bootstrap 90% -.120 .. +.088). Median |log error| is .143 vs dmed's
  .140. Even a perfect per-clip focal leaves geometry no better than Claude's direct answers. The geometric mean
  with the oracle is +.002. The facts-side oracle gain comes almost entirely from simulation_0025 (4 rows, dmed 0.0
  vs oracle .825); those rows already hold the stated value in the submission.
- The Depth Pro focal as a size-row proxy for stage 2: .499 vs dmed .752 (-.253), the same as MoGe (-.256), which
  matches simfov's measured -.25..-.30 on the facts. A full replay would not change the sign.
- Conclusion: on 3D simulation, focal length is not the bottleneck. The residual geometry error is per object
  (extents vs world-bounding-box dimensions, foreshortening, origin vs visible centre; 11% row-to-row spread of
  f_ref within a clip). Any monocular FOV model (MoGe-2, Depth Pro, UniDepth, GeoCalib...) is capped by the oracle
  row above. This closes the "better FOV model" line for 3D simulation.

### Temporal median (Gemini's "median over frames")
A 0.15 frame was added for 2 validation clips (planned for 6 clips x 2 frames; stopped after 2 frames because shared
CPU load pushed one frame to 983 s). Frame-to-frame |log f| difference: 0009 .070 (58.3 -> 54.9 deg), 0015 .017.
That is small next to the .33 median clip error, so a temporal median cannot rescue the estimate. With the
multi-frame median the stage-1 numbers are unchanged (out/stage1_final.txt: .334 / .14).

### Decision
- FAIL (stage 1). No stage-2 replay (pre-registered stop), no candidate file, no submission change. Expected gain 0.
- Together with research/simfov (MoGe-2) this closes the monocular-FOV route for 3D simulation. The oracle row
  above bounds every FOV model: a perfect clip focal gives geometry .727 vs direct .752 on 71 size rows.
- Disk: depth_pro.pt (1.9 GB) was deleted after the run (disk at 96%). Re-download with
  `hf_hub_download('apple/DepthPro','depth_pro.pt', local_dir='/home/user/.cache/depthpro/checkpoints')`. The source
  clone (5 MB) stays in /home/user/.cache/depthpro/src, and timm/safetensors stay installed in /home/user/venv-depth.

### Files
- `fov_depthpro.py` (inference; same CSV format as fov_moge.py), `stage1.py` (pre-registered stage 1),
  `oracle.py` (oracle clip-focal bound + Depth Pro / MoGe size-row proxy).
- `out/fov_depthpro_mid.csv` (35 mid frames), `out/fov_depthpro.csv` (+2 frames at 0.15), `out/clips_stage1.txt`,
  `out/stage1_mid.txt`, `out/stage1_final.txt`, `out/stage1_per_clip.csv`, `out/fov_check_dp.txt` (+ its
  fov_per_clip.csv), `out/oracle.txt`, `out/oracle_rows.csv`, logs.

### What this suggests for the 3D-simulation gap (S3 non-lab .742)
The error that remains after a perfect focal is per object (median |log| .143, equal to Claude's .140). So the
levers are object-level, not camera-level. Examples: a world-bounding-box / yaw-aware extent prompt (Argon idea 4;
the oracle says sizes are where geometry loses), or using exact family facts to calibrate per-object extent ratios
rather than a camera. Camera-group focal pooling was already killed in path85b (7/27 held-out priors within 7%).
