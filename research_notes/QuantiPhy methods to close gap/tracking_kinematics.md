# Precise object/point tracking and kinematics (speed, acceleration) estimation from short videos

Scope: which trackers and estimation recipes give the most accurate trajectories and derivatives for short clips (renders, fixed-camera lab recordings, internet videos), with numbers; best practice for instantaneous v(t) / a(t) from noisy tracks. Current as of Oct 2026. Note: arxiv.org was reachable only via curl (WebFetch DNS failed), so the tracker tables below were read from the arXiv HTML versions directly. Some physics-education sources were only seen as search snippets and are flagged.

## 1. State-of-the-art point / object trackers (2024-2026): accuracy, speed, sub-pixel precision, failure modes

### Takeaway
On standard TAP-Vid benchmarks, the top open 2D point trackers (CoTracker3, AllTracker, TAPNext/TAPNext++, Track-On) are within about 2-3 AJ points of each other on DAVIS (AJ about 63-67, δ_avg about 76-80). AllTracker has the best multi-benchmark position accuracy, and it is the only one that keeps improving at high resolution (69.5 avg δ_avg at the highest tested resolution vs 66.9 for CoTracker3). It is small (16M params), dense, and runs on a single 40 GB GPU. The δ thresholds are 1-16 px at 256x256, so these benchmarks measure "about 1-px class" accuracy, not sub-pixel precision. For kinematics, the dominant failure modes are fast, tiny, blurred objects (SAM2-family VOS trackers lose the target for 1-4 frames during blur) and re-detection after occlusion.

### Cited Findings
**Online trackers, same table (TAPNext++ paper, Table 1). Each cell is AJ / δ_avg / OA.**
- CoTracker3 (online): DAVIS 63.8 / 76.3 / 90.2; RGB-Stacking 71.7 / 83.6 / 90.2; RoboTAP 66.4 / 78.8 / 90.8; Kinetics 55.8 / 68.5 / 88.3 — [TAPNext++ (arXiv 2604.10582)](https://arxiv.org/html/2604.10582v1)
- Track-On: DAVIS 65.0 / 78.0 / 90.8; RGB-Stacking 71.4 / 85.2 / 91.7; RoboTAP 63.5 / 76.4 / 89.4; Kinetics 53.9 / 67.3 / 87.8 — [TAPNext++](https://arxiv.org/html/2604.10582v1)
- BootsTAPNext-B: DAVIS 65.2 / 78.5 / 91.2; RGB-Stacking 66.2 / 78.3 / 86.8; RoboTAP 62.6 / 74.3 / 88.4; Kinetics 57.3 / 70.6 / 87.4 — [TAPNext++](https://arxiv.org/html/2604.10582v1)
- TAPNext++ (2026): DAVIS 66.6 / 79.9 / 92.1; RGB-Stacking 73.4 / 84.8 / 95.1; RoboTAP 61.1 / 75.2 / 89.6; Kinetics 54.4 / 68.7 / 89.0. The authors note it stays SOTA on DAVIS (AJ 65.3) even without roll augmentation — [TAPNext++](https://arxiv.org/html/2604.10582v1)
- CoTracker2 for reference: DAVIS 62.2 / 75.7 / 89.3 — [TAPNext++](https://arxiv.org/html/2604.10582v1)
- Speed at 256 query points on an H100: LocoTrack-B (window) 452 FPS; CoTracker3 (online) 102 FPS; Track-On (frame) 28 FPS; TAPNext (frame) 189 FPS; TAPNext++ (frame) 193 FPS — [TAPNext++, Table 2](https://arxiv.org/html/2604.10582v1)
- Re-detection failure mode: in a re-entry test, BootsTAPNext and Track-On fail to re-detect an object that leaves and re-enters the frame. CoTracker3 re-detects it but "fails to track static points on the texture-less table". With juggled objects that repeatedly leave and re-enter, all competing methods fail. Window-based CoTracker3 also drops in re-detection AJ after 256 undetectable frames — [TAPNext++](https://arxiv.org/html/2604.10582v1)
- TAPNext (2025) frames tracking as next-token prediction and processes frame by frame. CoTracker3 by contrast needs 8-frame window buffers — [TAPNext (arXiv 2504.05579)](https://arxiv.org/pdf/2504.05579)

**Offline / other comparisons**
- TAP-Vid DAVIS (AJ / δ_avg / OA): TAPTR 63.0 / 76.1 / 91.1; LocoTrack 62.9 / 75.3 / 87.2; CoTracker3 64.4 / 76.9 / 91.2; DELTA 62.7 / 76.7 / 88.2; SpatialTracker 61.1 / 76.3 / 89.5; SpatialTrackerV2 64.9 / 77.5 / 91.0 — [SpatialTrackerV2 (arXiv 2507.12462), Table 4](https://arxiv.org/abs/2507.12462)
- Naively adding a 3D head to CoTracker3 drops DAVIS AJ from 64.4 to 51.6 and δ_avg from 76.9 to 65.2. Joint 2D+3D heads can hurt 2D precision — [SpatialTrackerV2](https://arxiv.org/abs/2507.12462)

**AllTracker (ICCV 2025; code and weights at alltracker.github.io)**
- Dense all-pixel long-range flow from a query frame to every other frame. 16.48M params (Tiny: 6.29M). Tracks 768x1024 on a 40 GB GPU. Trained jointly on optical-flow and point-tracking datasets, which the authors call "crucial for top performance" — [AllTracker (arXiv 2506.07310)](https://arxiv.org/html/2506.07310v2)
- δ_avg across 9 benchmarks (BADJA, CroHD, DAVIS, DriveTrack, EgoPoints, Horse10, Kinetics, RGB-Stacking, RoboTAP) at base resolution, given as average (DAVIS):
  - AllTracker 66.1 (76.3)
  - CoTracker3 (Kubric+15k pseudo-labels) 65.0 (77.1)
  - LocoTrack 61.5 (68.0)
  - BootsTAPIR 60.9 (67.9)
  - DELTA 59.7 (75.3)
  - PIPs++ 49.3
  - RAFT 48.3
  - SEA-RAFT 48.7

  [AllTracker, Table 1](https://arxiv.org/html/2506.07310v2)
- At higher resolutions AllTracker keeps improving (avg 68.3, then 69.5; DAVIS 78.8, then 80.6). CoTracker3 plateaus (67.5, then 66.9) and needed a 96 GB GPU at the top resolution — [AllTracker, Table 2](https://arxiv.org/html/2506.07310v2)
- AJ: AllTracker vs CoTracker3 on DAVIS 63.3 vs 62.9; Kinetics 59.1 vs 53.5; RGB-Stacking 81.1 vs 69.5; RoboTAP 71.9 vs 66.3. AllTracker's strongest gains are on textureless regions (RGB-Stacking) — [AllTracker, Table 3](https://arxiv.org/html/2506.07310v2)
- In streaming/real-time mode AllTracker runs at 57.9 FPS with avg δ 62.6 (vs 66.1 offline). The BootsTAPIR real-time variant runs at 21.4 FPS with 62.2 — [AllTracker](https://arxiv.org/html/2506.07310v2)
- Caveat: AllTracker evaluated CoTracker3 with all queries at once plus a sparse grid, a setup they say over-estimates CoTracker3's accuracy relative to the authors' own numbers. CoTracker3's accuracy also depends on how query points are grouped, since it uses support points — [AllTracker](https://arxiv.org/html/2506.07310v2)
- As optical flow, AllTracker scores Sintel test EPE 1.673 (clean) / 3.244 (final), vs SEA-RAFT 1.309 / 2.601. Its frame-to-frame flow is coarser than a dedicated flow model — [AllTracker](https://arxiv.org/html/2506.07310v2)
- Metric definition: δ_avg averages the fraction of points within 1, 2, 4, 8 and 16 px at 256x256 evaluation resolution — [AllTracker](https://arxiv.org/html/2506.07310v2)
- Older baseline: CoTracker (Kubric-24) DAVIS AJ 61.8, δ_avg 76.1; TAPIR AJ 56.2 — [TAPTRv3 (arXiv 2411.18671)](https://arxiv.org/pdf/2411.18671)

**Video object segmentation (VOS) trackers on fast-moving objects (SAM 2 family)**
- A Dec 2025 benchmark of SAM2, EfficientTAM, DAM4SAM and SAMURAI on fast-moving-object datasets (FMOv2, TbD, TbD-3D):
  - Tiny/small objects with minimal box overlap between frames significantly hurt all trackers.
  - Trackers often lose the target during motion blur. EfficientTAM sometimes stays lost for 3-4 frames; the others usually recover in 1-2.
  - DAM4SAM is generally strongest, SAMURAI is best on FMOv2, and SAM2 is best on TbD-3D.
  - Speed order: EfficientTAM, then SAMURAI, then DAM4SAM / SAM2.

  [Benchmarking SAM2-based Trackers on FMOX (arXiv 2512.09633)](https://arxiv.org/abs/2512.09633)
- SAMURAI adds a Kalman-filter motion model and motion-aware memory selection to SAM 2. DAM4SAM splits memory into recent-appearance and distractor-resolving parts — [FMOX benchmark](https://arxiv.org/abs/2512.09633); vendor summary that SAMURAI improves fast-target tracking by about 10% over SAM 2 on a LaSOT-based benchmark (not verified against primary): [Sieve](https://sievedata.com/resources/exploring-sam2-variants)

### Inferences
- For kinematics on short, fixed-camera clips, the choice between CoTracker3, AllTracker and TAPNext++ matters less than (a) running at high input resolution and (b) the downstream fitting. Their DAVIS δ_avg spread is about 4 points, and these are mostly 1-4 px-scale errors at 256 px. AllTracker is the best single default: open, 16M params, dense, scales with resolution. Running it at about 768x1024 means a small object still covers enough pixels. CoTracker3 (offline, with a support grid) is a strong second and the easiest to install.
- For trajectory centroids, use an object mask or box (SAM 2.1 / DAM4SAM / SAMURAI) and take the mask centroid, or the median of many point tracks inside the mask. That averages out per-point jitter (roughly σ/√n for independent errors) and is robust to a single point slipping. Single-point tracks on tiny, blurred objects (balls) are the weakest link. During blur frames, expect 1-4 lost frames from SAM2-type trackers; treat these as missing data rather than interpolating blindly.
- For blurred fast objects, a mask/box centroid lies at the middle of the exposure-time streak. That corresponds to the mid-exposure time, which is fine for velocity, but the blur length itself encodes speed × exposure time.
- No benchmark directly reports sub-pixel RMS on rigid textured targets. For synthetic renders with clean edges, classical sub-pixel methods (template/phase correlation, mask centroids) likely reach well under 0.5 px. This is an inference, not measured in these sources.

### Gaps
- No official SAM 3 / SAM 3.1 VOS numbers on fast or small objects were found. LocoTrack, TAPTR, DELTA and Track-On numbers come from third-party tables (AllTracker, SpatialTrackerV2, TAPNext++), not their own papers.
- The PointOdyssey columns of the TAPNext++ table could not be unambiguously parsed and are omitted.
- No study found that measures sub-pixel trajectory precision (px RMS) of learned trackers vs classical template matching on rigid objects.

## 2. Measuring speed and acceleration from video (physics education, sports science): achievable accuracy and recommended fitting

### Takeaway
Careful fixed-camera lab video (Tracker-style) typically recovers g within about 1-2% on average, but individual runs and classrooms vary from about 0.15% to over 10%. The main error sources are scale/perspective calibration (camera distance to the motion plane), contrast/marker localisation, compression/frame timing, and rolling shutter, not the differentiation method. Never use raw finite differences for acceleration. Either fit a physical model (a global quadratic for constant acceleration) or use a low-pass filter (zero-phase Butterworth with a residual-analysis cutoff, or splines) before differentiating. Conventional filters underestimate impact peaks by 30-70%.

### Cited Findings
**Physics-education video analysis**
- Tracker free-fall classroom study: g = 9.984 ± 0.611 m/s², a 1.82% error vs 9.806 — [EPJ Web of Conf. (BPU12, 2026) "Teaching Motion Concepts Through Tracker-Based Video Analysis"](https://www.epj-conferences.org/articles/epjconf/pdf/2026/21/epjconf_bpu12congress_07008.pdf) (seen via search snippet; PDF not opened)
- Falling-object study (Tracker): the error depended on ball-background contrast. Average g from early frames on a yellow background deviated by 11.76%; later frames on a white background deviated by 1.47%. Low colour contrast was named the main error source — [Rev. Bras. Ensino Fís., "Digital video analysis of falling objects in air and liquid using Tracker"](http://www.scielo.br/j/rbef/a/FcfVyHXVfVwZ9VQM7L43pyC/?lang=en) (search snippet; page unreachable from this sandbox)
- In a drop-from-1.0 m study, the best run was within 0.15% of standard g, but the mean over repeats was 10.06 m/s² (about 2.6% high). Camera-to-plane distance affected the error more than drop height; drag and sideways motion did not explain it — reported in search results for the Tracker literature (exact paper not verified; see Gaps)
- Tracker forum: a high-school class got fitted g of about 11-12 m/s² instead of 9.8. Suspected causes were video compression and frame rate (wrong nominal fps or duplicated frames) — [Tracker forum, ComPADRE](https://www.compadre.org/osp/bulletinboard/TDetails.cfm?FID=57&TID=3000&ViewType=2)
- Lab guidance: use an unchanging plain background and a known-length object next to the setup, in the plane of motion, for calibration — [Univ. Jyväskylä Tracker guide](https://www.jyu.fi/sites/default/files/2023-06/Tracker%20guide%20and%20pre-lab%20assignment%20example_English.pdf)

**Sports-biomechanics methodology**
- Differentiating displacement amplifies digitising error "considerably" unless smoothed (Winter 1979). The accepted approaches are a digital filter followed by finite differences, or fitting splines / Fourier series — [ISBS proceedings (uni-konstanz)](https://ojs.ub.uni-konstanz.de/cpa/article/view/1728/1628)
- Conventional low-pass filters underestimated impact peaks by about 30-70% in football kicking. A fractional Fourier filter came within about -5% of an accelerometer. Non-impact phases were fine with a 12-20 Hz cutoff — [Augustus et al., J. Biomech (Chichester eprint)](https://eprints.chi.ac.uk/5020/1/AugustusAmcaHudsonSmith%20JoB%20SC_Revised_Final.pdf)
- Sampling-rate effect on peaks: Winter's example shows peak acceleration dropping from about 14 to 12.5 m/s² when going from 50 to 25 Hz. Nyquist is the minimum to avoid aliasing, not enough to reproduce peak amplitudes — [Clinical Gait Analysis discussion](https://clinicalgaitanalysis.com/teach-in/acceleration/responses.html)
- Filter review (Crenna et al., Sensors 2021): the zero-phase Butterworth low-pass "presents the most robust performance in all differentiation conditions". Savitzky-Golay is valid but performs differently at different frequencies and needs tuning to derivative order, signal type and frequency. RMS error is a weak criterion when peaks matter — [Sensors 21(13):4580](https://www.mdpi.com/1424-8220/21/13/4580)
- Numerical differentiation comparison: spline derivatives beat finite differences, especially at fine sampling. Savitzky-Golay derivatives on noisy synthetic data were "not smooth" and deviated heavily — [arXiv physics/0510176](https://arxiv.org/pdf/physics/0510176)
- Savitzky-Golay is biased on peaky signals: it systematically underestimates saccade peak velocity, which motivated a nonlinear S-G generalisation — [J. Vision](https://jov.arvojournals.org/article.aspx?articleid=2648985)
- Frame-rate timing error (jump videos resampled from high speed): technical error 3.4 / 1.8 / 1.2 / 0.8 ms at 120 / 240 / 480 / 1000 Hz, i.e. 1.4% / 0.7% / 0.5% / 0.3% in jump height — [MyJump frame-rate study (PMC10108745)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10108745/)
- Kinovea notes that time-based measures (speed, acceleration) require knowing the true capture frame rate, and that smartphone Long-GOP encoding is less suited to frame-by-frame analysis — [Kinovea glossary](https://kinovea.readthedocs.io/en/latest/userinterface/glossary.html)

### Inferences
These are my own error-propagation calculations, checked numerically in numpy.

**Fit noise for a smooth track.** Assume N uniformly spaced samples over a duration T, with i.i.d. position noise σ (px).
- A global quadratic fit x = c0 + c1·t + c2·t² gives SD(a) ≈ √(720/N)·σ/T² and SD(v at the window centre) ≈ √(12/N)·σ/T. The exact least-squares values are slightly smaller: 0.84 vs 0.87 for N=60, T=2 s, σ=1.
- Example: 60 frames over 2 s at σ = 1 px gives SD(a) ≈ 0.84 px/s². A 9.8 m/s² fall at 100 px/m is 980 px/s², so fit noise is about 0.1%.
- A raw 3-point central-difference second derivative has SD = √6·σ·fps². At 30 fps and σ = 1 px that is about 2200 px/s², bigger than the signal itself.
- Conclusion: for constant-acceleration motion, tracking noise is negligible once a global model is fitted. The residual error budget is dominated by scale (metres per pixel, perspective), timing (true fps, dropped or duplicated frames) and model mismatch (drag, rolling, bounces).
- Acceleration error scales as 1/T², so halving the fit window costs about 5.7× (√8 for N, × 4 for T). Use the longest window over which the motion model holds, i.e. between events (bounces, collisions, pushes).

**Recipe for instantaneous v(t) and a(t).**
1. Decode real per-frame timestamps (PTS) and drop or merge duplicate frames.
2. Track the object as a mask centroid or a robust median of points.
3. Segment the track at detected events.
4. Within each segment, fit the lowest-order physically justified model (linear for constant v, quadratic for constant a, or a drag/rolling ODE). Report v(t) = c1 + 2·c2·t and a = 2·c2.
5. If no model applies, use a zero-phase Butterworth filter (cutoff chosen by residual analysis) or a smoothing spline (generalized cross-validation, GCV), and differentiate the smooth curve.
6. Use Savitzky-Golay only with a window covering at least about 1/3 of the segment and polynomial order 2-3, accepting peak bias.
7. Estimate uncertainty by bootstrap or by the residual-based covariance of the fit, plus a scale-uncertainty term.

**Peak quantities.** Peak values (impact accelerations, max speed) will be biased low by any smoothing. Low frame-rate internet video (24-30 fps) cannot resolve impact accelerations at all. Report the pre- and post-impact velocities from separate fits instead.

### Gaps
- The "0.15% best run / 10.06 m/s² mean / camera distance dominates" study and a "rolling shutter produced a 4% overestimation of g" claim appeared in search summaries, but I could not confirm which primary paper they come from. Treat them as unverified.
- Walker (1998, J. Exp. Biol.), a simulation comparison of differentiation algorithms, and Woltring's GCV spline papers are the canonical references, but neither was retrieved.
- No study found that directly benchmarks Savitzky-Golay vs spline vs Kalman/RTS acceleration error on video tracks with known ground truth.

## 3. Physics-informed estimation: model fitting, collisions/bounces, gravity as scale calibration, frame-time irregularities

### Takeaway
The literature supports a physics-first approach: fit constant-acceleration or ODE models per segment, split at events, and use known physics to calibrate. Free-fall lets g = 9.81 m/s² supply the metres-per-pixel scale (a fitted vertical a_px divided by 9.81 gives px/m). Frame-timing errors (wrong nominal fps, variable frame rate (VFR), duplicates) and rolling shutter are documented sources of percent-level bias, and a nominal-vs-actual fps mismatch scales acceleration by the square of the ratio.

### Cited Findings
- Free-fall g recovered from video ranges from about 1.5-2% error (good contrast) to over 10% (poor contrast, early frames), so per-frame localisation quality directly affects fitted acceleration — [EPJ Web Conf. 2026](https://www.epj-conferences.org/articles/epjconf/pdf/2026/21/epjconf_bpu12congress_07008.pdf); [RBEF Tracker falling-objects study](http://www.scielo.br/j/rbef/a/FcfVyHXVfVwZ9VQM7L43pyC/?lang=en)
- Compression and frame-rate issues produced fitted g of 11-12 m/s² (a 12-22% overestimate) in a classroom, and verifying timing against a stopwatch was suggested — [Tracker forum](https://www.compadre.org/osp/bulletinboard/TDetails.cfm?FID=57&TID=3000&ViewType=2)
- Smartphone and screen-recorded files often contain several frame rates within one clip (VFR). Converting to constant frame rate (CFR) duplicates or drops frames — [VideoHelp forum](https://forum.videohelp.com/showthread.php?p=2762390)
- Conventional filters smear impacts (30-70% peak underestimate), so impacts should be handled as discontinuities rather than smoothed through — [Augustus et al.](https://eprints.chi.ac.uk/5020/1/AugustusAmcaHudsonSmith%20JoB%20SC_Revised_Final.pdf)
- SAMURAI-style Kalman motion models are already used inside trackers to bridge blur frames on fast objects — [FMOX benchmark](https://arxiv.org/abs/2512.09633)

### Inferences
**Timing**
- If a clip is played or labelled at fps_nom but was captured at fps_true, then v scales by fps_true/fps_nom and a by (fps_true/fps_nom)².
  - Slow motion: a 240 fps capture played at 30 fps gives an 8× speed error and 64× acceleration error if uncorrected.
  - Free fall makes this checkable. If a fitted vertical acceleration in "m/s²" is about 9.81/k², the clip is slowed by a factor k.
- To detect duplicates, flag frames where the track displacement is about 0 between two frames with non-zero motion on either side, or where image differences are about 0. Remove those frames and re-index by true PTS. A duplicate mid-segment produces a characteristic +/− spike pair in the second difference, so a residual spike test after the quadratic fit catches it.

**Events: bounces and collisions.** Fit a piecewise quadratic with unknown breakpoints. Choose the number and location of breakpoints by minimum BIC or residual change-point detection; signs are a velocity sign flip or a jump in residuals. Then report:
- the velocity just before and after an event by evaluating each segment's fit at the breakpoint, not by smoothing across it;
- the coefficient of restitution, as the ratio of post- to pre-impact vertical velocity, from the same fits.

**Scale calibration**
- With a known gravity direction and a free-flight segment, the fitted vertical acceleration in px/s² divided by 9.81 gives px/m in the plane of motion. That works independently of any size prior and can cross-check a given prior.
- On an incline, a rolling solid sphere has a = (5/7)·g·sinθ, a solid cylinder (2/3)·g·sinθ, and a sliding block g·(sinθ − μ·cosθ). Fitting a and knowing θ also constrains scale.

**Projectile under perspective**
- When motion is not in a fronto-parallel plane, image-plane x(t), y(t) are not quadratic: perspective division by depth Z(t) adds curvature.
- For short clips with small depth change (ΔZ/Z < about 5%) the error is second order. Otherwise fit a 3D parabola projected through the camera, or work in back-projected 3D (section 4).

**Uncertainty.** Report the residual-bootstrap SD of a, plus the scale uncertainty (relative error in px/m adds one-for-one to relative v and a error), plus timing uncertainty (2× the relative fps error for a).

### Gaps
- No peer-reviewed quantification of duplicated-frame or VFR error in smartphone kinematics was found.
- No published end-to-end "physics-informed video kinematics" benchmark with % errors on v/a for internet videos was found. The recipe above is engineering inference.

## 4. Monocular 3D trajectory estimation (back-projection with depth; TAPIP3D, SpatialTrackerV2, MegaSaM) and error propagation

### Takeaway
Monocular 3D point tracking is still far from metrically precise. The best TAPVid-3D average 3D AJ is about 21 (SpatialTrackerV2) and APD3D about 31%, versus 2D AJ of about 65. Depth quality is the bottleneck: CoTracker3 lifted with MegaSaM depth scores AJ3D 17.3 vs 12.8 with UniDepthV2 and 9.3 with COLMAP. For speed/acceleration along the camera axis, relative depth error maps one-for-one into relative velocity error, and depth jitter is amplified by differentiation. Prefer in-plane motion plus a scale prior, or strong temporal smoothing of depth.

### Cited Findings
**TAPVid-3D (AJ3D / APD3D / OA, average over Aria, DriveTrack, PStudio)**

| Method | Depth / pose source | AJ3D | APD3D | OA |
|---|---|---|---|---|
| BootsTAPIR | COLMAP | 9.3 | 14.9 | — |
| CoTracker3 | COLMAP | 9.3 | 15.0 | — |
| CoTracker3 | UniDepthV2 | 12.8 | 19.4 | — |
| CoTracker3 | MegaSaM | 17.3 | 25.9 | 87.8 |
| SpatialTracker | MegaSaM | 13.0 | — | — |
| DELTA | UniDepthV2 | 13.1 | 20.6 | — |
| TAPIP3D | MegaSaM | 18.8 | 27.4 | 86.4 |
| SpatialTrackerV2 (feed-forward) | UniDepthV2 | 17.7 | 26.0 | — |
| SpatialTrackerV2 (feed-forward) | MegaSaM | 18.7 | 27.9 | — |
| SpatialTrackerV2 (full) | — | 21.2 | 31.0 | 90.6 |

Source for all rows: [SpatialTrackerV2, Table 1](https://arxiv.org/abs/2507.12462)

- TAPIP3D tracks in a persistent 3D world frame using MegaSaM depth and pose. TAPIP3D-world beats TAPIP3D-camera, and on the camera-moving ADT subset it beats DELTA by +2.5 AJ3D / +3.5 APD3D. On DexYCB-Pt with sensor depth it reaches AJ3D 30.3 vs DELTA 26.4 — [TAPIP3D (arXiv 2504.14717)](https://arxiv.org/abs/2504.14717)
- TAPIP3D reports that SpatialTracker and DELTA drift seriously under large 3D object motion, and that SpatialTracker's tri-plane representation falls below depth-lifted CoTracker3 even with accurate sensor depth — [TAPIP3D](https://arxiv.org/abs/2504.14717)
- TAPIP3D Table 2 compares MegaSaM depth with GT depth on LSFOdyssey and DynamicReplica and shows large gains with GT depth. The authors attribute much of the remaining error to input depth quality — [TAPIP3D](https://arxiv.org/abs/2504.14717)
- TAPVid-3D: more than 4,000 real videos (4,569 per TAPIP3D) from Aria Digital Twin, DriveTrack and Panoptic Studio, 25-300 frames each. AJ3D combines 3D position accuracy (scale-normalised thresholds) and visibility — [TAPVid-3D (NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/9566607d423f8c32a2d5ce09a8b62232-Abstract.html); [TAPIP3D](https://arxiv.org/abs/2504.14717)
- Code: TAPIP3D, SpatialTrackerV2 and MegaSaM are open-source and single-GPU. SpatialTrackerV2 comes in feed-forward and optimisation ("full") variants — [SpatialTrackerV2](https://arxiv.org/abs/2507.12462)

### Inferences
**How depth error propagates**
- For a point at depth Z, metric lateral position is X = (u − c_x)·Z/f. A relative depth or scale error ε gives a relative error ε in X, v and a for in-plane motion. So a globally mis-scaled depth map biases speeds proportionally. A known size or speed prior removes this.
- For motion along the optical axis, v_Z = dZ/dt comes directly from depth differences. Per-frame depth jitter σ_Z then enters as √2·σ_Z·fps for raw velocity and √6·σ_Z·fps² for raw acceleration.
- Example: at 5 m depth with 2% frame-to-frame depth jitter (σ_Z = 0.1 m) and 30 fps, raw v_Z noise is about 4 m/s. Depth must be fitted with a smooth model, e.g. a linear or quadratic Z(t), or the apparent-size method below.
- For an object of roughly fixed size moving in depth, apparent size s(t) ∝ 1/Z(t). Tracking the mask's √area or bounding-box size gives Z(t) up to scale, with relative precision σ_s/s. That is usually much better than per-frame monocular depth for a single rigid object. With a known real size, it gives metric Z(t) directly.

**Recommended 3D pipeline for an object approaching or receding:**
1. Get the mask with SAM 2.1 / DAM4SAM.
2. Take the centroid (u, v) and apparent size s(t).
3. Compute Z(t) = f·S/s(t), with f from metadata or an estimate (e.g. from MegaSaM / UniDepth / MoGe). Note that f errors scale lateral and depth components differently.
4. Back-project: X = (u − c_x)·Z/f.
5. Fit a physical model in 3D.
6. Use MegaSaM / SpatialTrackerV2 only when the camera moves or the object is non-rigid.

### Gaps
- No published numbers were found for velocity or acceleration error of monocular 3D trackers (benchmarks report position AJ3D/APD only).
- Exact TAPIP3D Table 2 values (GT vs MegaSaM depth) were only partially parsed.
- MegaSaM's own video-depth error numbers were not retrieved here.

## 5. Learned "video physics" estimators that regress velocity / physical parameters directly

### Takeaway
I found no open, general-purpose learned model that regresses metric velocity or acceleration directly from arbitrary video with reported accuracy competitive with track-then-fit. The closest benchmark is QuantiPhy itself. It finds that VLMs are "linguistically plausible but numerically systematically incorrect", which supports the track-then-fit plus scale-from-prior decomposition.

### Cited Findings
- QuantiPhy (Stanford, arXiv 2512.19526) evaluates VLMs on estimating size, velocity and acceleration from video given one physical prior. It has more than 3.3K instances: test set 3,289 QA pairs over 568 videos, plus 159 validation QA pairs. It notes these quantities are related through one unknown pixel-to-world scale factor that the prior determines. VLMs show a consistent gap between qualitative plausibility and numerical correctness — [QuantiPhy arXiv](https://arxiv.org/abs/2512.19526); [HF dataset](https://huggingface.co/datasets/PaulineLi/QuantiPhy); [paper note](https://en.papernotes.org/CVPR2026/vlm_reasoning/quantiphy_a_quantitative_benchmark_evaluating_physical_reasoning_abilities_of_vi/)
- Point Prompting (arXiv 2510.11715) uses video diffusion models for zero-shot counterfactual point tracking. It reaches DAVIS AJ 42.21, far below supervised trackers (about 63-67). Generative-video "physics" priors are not yet precise trackers — [Point Prompting](https://arxiv.org/pdf/2510.11715)

### Inferences
- For a benchmark scored by relative error (QuantiPhy MRA), the expected best practice is an explicit pipeline: segmentation/point tracking, then a physics fit for the pixel-space quantity, then a ratio with the prior's pixel-space counterpart. Use direct VLM or learned regressors only as a fallback or sanity check, e.g. to pick the object, the event window and the motion model.
- Because QuantiPhy answers are ratios, a pixel-space size prior divided into a pixel-space speed, a global metric scale error cancels for same-plane quantities. Errors then come mainly from tracking the right points, picking the right time window, and perspective or depth change between where the prior is measured and where the target quantity is measured.

### Gaps
- I did not find (within the search budget) accuracy figures for dedicated learned velocity regressors, such as vehicle-speed-from-dashcam networks or "physical parameter estimation from video" models (e.g. differentiable-simulation fitting). These are a known literature but were not retrieved, so no numbers are claimed.
- QuantiPhy per-model scores were not extracted here (other researchers or the repo README cover the leaderboard).
