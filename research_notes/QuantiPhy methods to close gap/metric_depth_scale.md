# Metric depth, intrinsics and 4D reconstruction for measuring object sizes, distances and speeds in monocular video (2024-2026)

Scope note: numbers below come from the papers' own benchmark tables. I pulled them from arXiv HTML full text (downloaded and grepped), and took licenses from the repos' README/LICENSE files on raw.githubusercontent.com. Benchmarks differ between papers: dataset subsets, alignment protocol and resolution all vary. The same model can therefore get very different scores in different papers, and I flag the conflicts. "AbsRel" is mean |d̂−d|/d. "δ1" is the fraction of pixels with max(d̂/d, d/d̂) < 1.25. Lower AbsRel and higher δ1 are better.

## Q1. Which models give the best metric depth and focal length from a single image or video in 2025-2026, including on synthetic/rendered scenes?

### Takeaway
No model is reliably accurate in absolute metric scale zero-shot. The best single-image models (MoGe-2/MoGe-3, UniDepthV2, DA3-Metric, FoundationGeo, Metric3Dv2 when given GT intrinsics) reach about 7-20% AbsRel depending on the dataset. Errors grow badly on camera or domain shift, including synthetic scenes and unusual focal lengths. Relative (scale/affine-aligned) geometry is about 3-5x more accurate (2-5% AbsRel). For FoV/focal, the best single-image calibrators are MapAnything (about 1.1° mean ray-angle error), MoGe-2 (about 2.0°) and Depth Pro (65-85% of photos within 25% focal error). The practical recipe is to take relative geometry and focal from a strong model and fix the scale with the given priors.

### Cited Findings
**Single-image metric geometry (MoGe-2 paper, NeurIPS 2025, arXiv 2507.02546, July 2025):**
- Metric geometry averaged over 7 datasets (point Rel^p / δ1^p; depth Rel^d / δ1^d):
  - MoGe-2: point 8.19 / 93.6; depth 15.7 / 76.8; with GT camera, Rel^p 13.6 / δ1 87.4.
  - UniDepth V2: point 10.1 / 91.9; depth 21.3 / 75.3.
  - Depth Pro: point 13.7 / 81.9; depth 27.6 / 54.4.
  - UniDepth V1: depth 23.2 / 67.5.
  - DA V2 (metric): depth 29.9 / 56.6.
  - MASt3R: depth 49.7 / 30.3.
  - Metric3D V2 (needs GT camera): Rel^p 18.3 / δ1 73.9.
  — [MoGe-2 arXiv](https://arxiv.org/html/2507.02546)
- Relative (scale-invariant) depth over 10 datasets, Rel^d / δ1:
  - MoGe-1: 5.77 / 94.5
  - MoGe-2: 7.35 / 92.2
  - Metric3D V2: 7.92 / 91.8
  - UniDepth V2: 8.61 / 90.8
  - Depth Pro: 9.81 / 89.1
  - DA V2: 10.7 / 87.6

  The gap between scale-aligned error (~6-8%) and metric error (~16-30%) is the "scale error" that a known prior can remove. — [MoGe-2 arXiv](https://arxiv.org/html/2507.02546)
- Runtime on A100 for single-frame inference, FP16:
  - MoGe-2 ViT-L: 29 ms at 484², 39 ms at 700², 108 ms at 1188²; 326M params; about 1-2 GB VRAM.
  - UniDepth V2: 33-50 ms.
  - Metric3D V2: 87 ms.
  - Depth Pro: 139 ms at 1536², 3.7 GB.
  - DA V2: 24 ms.
  — [MoGe-2 arXiv, Table B.3](https://arxiv.org/html/2507.02546)
- Boundary sharpness F1 (iBims-1/HAMMER/Sintel/Spring): Depth Pro has the best average rank (1.50), MoGe-2 is second (1.75). — [MoGe-2 arXiv](https://arxiv.org/html/2507.02546)
- MoGe outputs a metric point map, metric depth, normals and camera FOV. MoGe code is MIT-licensed (DINOv2 parts Apache 2.0). MoGe-3 (ViT-L and ViT-G checkpoints, e.g. `Ruicheng/moge-3-vitg`) has been released in the same repo. MoGe-3 needs FlexGEMM/Triton and so does not run on macOS. — [MoGe GitHub README](https://github.com/microsoft/MoGe)

**MoGe-3 (arXiv 2607.17967, July 2026):**
- Zero-shot global metric depth Rel^d / δ1, averaged over 9 datasets:
  - MoGe-3 ViT-L: 15.0 / 82.7
  - MoGe-3 ViT-G: 15.8 / 82.7
  - MoGe-2: 15.6 / 77.3
  - DA3: 17.4 / 70.1
  - UniK3D: 17.9 / 77.8
  - UniDepth V2: 23.7 / 71.2
  - Depth Pro: 29.0 / 54.0
- Relative point Rel^p: MoGe-3 ViT-L 7.91, ViT-G 7.43, MoGe-2 8.73.
- Latency on A100 FP16: MoGe-3 ViT-L (3-step) 121 ms, MoGe-2 39 ms, DA3 213 ms, Depth Pro 142 ms.
- Main gain is in local fine-detail metrics (δ0.01^p: 55.9 vs 46.6).
— [MoGe-3 arXiv](https://arxiv.org/html/2607.17967)

**FoundationGeo (HKU/DiDi, arXiv 2607.11588, v3 15 Jul 2026):**
- Per-dataset metric depth AbsRel / δ1 for MoGe-2:
  - NYUv2 7.33 / 96.1
  - KITTI 18.1 / 62.9
  - ETH3D 10.4 / 90.8
  - iBims-1 13.6 / 83.0
  - DDAD 15.8 / 73.0
  - DIODE 17.5 / 66.4
- UniDepth V2 metric AbsRel: NYUv2 10.6, KITTI 8.58, ETH3D 20.7, iBims 9.52, DDAD 18.4, DIODE 43.0.
- FoundationGeo metric AbsRel: 10.2 / 7.86 / 17.8 / 10.4 / 17.6 / 17.5. It has the best average rank (2.32) but is not best on any single dataset.
- Relative depth after alignment: most top models are at 2.4-5% AbsRel on the same datasets. For example, MoGe-2 relative AbsRel is 2.89 (NYU), 3.75 (KITTI), 2.80 (ETH3D), 13.3 (Sintel).
— [FoundationGeo arXiv](https://arxiv.org/html/2607.11588)
- FoundationGeo finds that metric accuracy is strongly tied to whether the test camera's focal length is covered by the training focal distribution. Mismatched benchmarks (e.g. DDAD) show systematic over- or under-scaling, which they partly fix with 23,700 Blender renders at diverse focal lengths. — [FoundationGeo arXiv](https://arxiv.org/html/2607.11588)
- "Scale-collapse": metric foundation models systematically underestimate the depth of distant landmarks and vast landscapes. MetricScenes (Jun 2026) fine-tunes MoGe-2 to mitigate this. — [Honey, I Shrunk the Arc de Triomphe! arXiv 2606.02379](https://arxiv.org/abs/2606.02379)

**Depth Anything 3 (ByteDance Seed, arXiv 2511.10647, Nov 2025):**
- DA3-Metric δ1 / AbsRel:
  - NYUv2 0.963 / 0.070
  - KITTI 0.953 / 0.086
  - ETH3D 0.917 / 0.104
  - SUN-RGBD 0.973 / 0.105
  - DIODE 0.838 / 0.128
- Comparison on the same table:
  - UniDepthV2: 0.968 / 0.064, 0.968 / 0.076, 0.863 / 0.152, 0.977 / 0.111, 0.856 / 0.123
  - Depth Pro on ETH3D: 0.386 / 0.349
— [DA3 arXiv](https://arxiv.org/html/2511.10647)
- The DA3 metric model uses a Metric3Dv2-style canonical-camera transform (GT depth rescaled by f_c/f). Absolute scale therefore depends implicitly on the focal length. — [DA3 arXiv](https://arxiv.org/html/2511.10647)
- Model variants and speed:
  - DA3-Giant (1.13B): 37.6 FPS.
  - DA3-Large (0.30B): 78 FPS; up to about 1,500 images per pass on an 80 GB A100.
  - DA3-Base: 126 FPS. DA3-Small: 160 FPS.
  - Multi-view pose AUC3 on HiRoom: DA3-Giant 80.3 vs VGGT 49.1, π³ 67.0, MapAnything 17.9.
  — [DA3 arXiv](https://arxiv.org/html/2511.10647)
- Licenses: DA3Metric-Large is Apache 2.0, as is DA3-Base. DA3-Large/Giant and the metric any-view model DA3NESTED-GIANT-LARGE(-1.1) are CC BY-NC 4.0. The Nested model combines the any-view giant model with the metric model to give metric-scale multi-view geometry. — [DA3 GitHub README](https://github.com/ByteDance-Seed/depth-anything-3); [DA3METRIC-LARGE HF card](https://huggingface.co/depth-anything/DA3METRIC-LARGE)

**Focal length / intrinsics:**
- Depth Pro focal-length test on EXIF-labelled photos, % of images with relative focal error under 25% / 50%:
  - Depth Pro: DDDP 66.9/85.8, FiveK 74.2/92.4, PPR10K 64.6/88.8, RAISE 84.2/96.4, SPAQ 68.4/85.2, ZOOM 69.8/91.6.
  - UniDepth V1: 6.8-44.2% within 25%.
  - So even the best model misses focal by more than 25% on roughly 15-35% of images.
  — [Depth Pro arXiv 2410.02073](https://arxiv.org/html/2410.02073)
- Single-image calibration, mean angular ray error (ETH3D / ScanNet++v2 / TartanAirV2):
  - MapAnything: 1.06° avg (1.33 / 0.39 / 1.47)
  - MoGe-2: 1.95°
  - AnyCalib: 2.01°
  - VGGT: 4.00°
  — [MapAnything arXiv 2509.13414](https://arxiv.org/html/2509.13414)
- MapAnything single-view metric depth (rel %):
  - Without intrinsics: KITTI 9.69, ScanNet 27.77 (poor indoors).
  - Given K: KITTI 8.48. MoGe-2: KITTI 14.21, ScanNet 10.57. UniDepthV2 with K: 13.70 / 3.20.
  — [MapAnything arXiv](https://arxiv.org/html/2509.13414)

**Synthetic / rendered scenes:**
- On Sintel (synthetic film), video depth with per-sequence scale alignment gives AbsRel π³ 0.233, VGGT 0.299, MonST3R 0.399, CUT3R 0.417. With metric scale and no alignment, CUT3R reaches AbsRel 1.029 (δ1 23.8%) and MASt3R-GA 1.022. Metric scale effectively fails on synthetic renders. — [CUT3R arXiv 2501.12387](https://arxiv.org/html/2501.12387); [π³ arXiv 2507.13347](https://arxiv.org/html/2507.13347)
- Even relative depth is much worse on Sintel than on real data: MoGe-2 relative AbsRel 13.3 on Sintel vs 2.4-3.8 on real datasets; UniDepth V2 13.3; DA3 17.4. — [FoundationGeo arXiv](https://arxiv.org/html/2607.11588)
- AerialMetric (Jun 2026) shows large domain gaps for street/indoor-trained metric depth models on UAV/aerial viewpoints. It studies the effects of viewpoint, altitude and camera parameters and provides 52K real and 16K synthetic pairs. — [AerialMetric arXiv 2606.29716](https://arxiv.org/abs/2606.29716)

**Video metric depth:**
- Video Depth Anything metric models (README) δ1:
  - KITTI: VDA-L-Metric 0.910, UniDepthV2-L 0.982, Depth Pro 0.822, MoGe-2-L 0.415.
  - NYUv2: 0.908 / 0.989 / 0.953 / 0.967 respectively.
  - Temporal alignment error on ScanNet: VDA-L 1.09 (best) vs MoGe-2 2.56.
  - Metric VDA S/B/L checkpoints released (Apr-Aug 2025), streaming mode since Sep 2025.
  — [Video-Depth-Anything README](https://github.com/DepthAnything/Video-Depth-Anything)
- Conflict: VDA's README reports MoGe-2 δ1 = 0.415 on KITTI, but FoundationGeo reports 62.9% and MapAnything reports AbsRel 14.2%. All three agree MoGe-2 is weak on KITTI, but the magnitude depends on protocol. — [VDA README](https://github.com/DepthAnything/Video-Depth-Anything) vs [FoundationGeo](https://arxiv.org/html/2607.11588)

**Licenses:**
- UniDepth (V1/V2) is CC BY-NC 4.0. — [UniDepth README/LICENSE](https://github.com/lpiccinelli-eth/UniDepth)
- Depth Pro uses an Apple sample-code licence (personal, non-exclusive). — [ml-depth-pro LICENSE](https://github.com/apple/ml-depth-pro)
- Metric3D code is BSD-2-Clause. — [Metric3D README](https://github.com/YvanYin/Metric3D)
- MapAnything code is Apache 2.0, with a separate Apache-licensed checkpoint `facebook/map-anything-apache` alongside a CC BY-NC model. — [MapAnything README](https://github.com/facebookresearch/map-anything)
- VGGT relicensed for commercial use on 29 Jul 2025, but only for the `VGGT-1B-Commercial` checkpoint. — [VGGT README](https://github.com/facebookresearch/vggt)
- π³ / Pi3X (Dec 2025): code BSD-3, weights CC BY-NC 4.0. Pi3X adds conditional injection (pose, intrinsics) and approximate metric scale. — [Pi3 README](https://github.com/yyfz/Pi3)
- All of these are open-weight and so eligible for an "open-weight only" track.

### Inferences
- For measurement, the absolute metric scale of any off-the-shelf model is the weakest link: typical errors are 10-30% and can exceed 100% on synthetic renders. Because the task always supplies a scale prior (a known size/speed, or known camera distances), the model should supply relative 3D shape plus focal/FoV, and the scale should come from the prior. Fixing scale this way cuts depth AbsRel from about 15% to about 3-5% (see Q2).
- Best picks for relative geometry and FoV from one frame: MoGe-2 (fast, MIT code, about 40 ms/frame) or MoGe-3 (more accurate fine detail, 3x slower). For multi-frame geometry from a video clip: DA3 (any-view) or π³/VGGT, all feed-forward and fast. For focal specifically: MapAnything or MoGe-2. The Depth Pro focal head is an independent second opinion; averaging or median-ing focal across frames and models is cheap.
- Depth Pro is no longer competitive on metric accuracy in third-party tables (worst of the modern set in MoGe-2, MoGe-3 and DA3 tables) despite its sharpness.

### Gaps
- I found no benchmark that reports focal-length error specifically on rendered or game-engine video like the challenge clips. Sintel is the closest proxy, and only depth (not focal) error is reported there.
- I did not extract UniDepthV2's own per-dataset camera-error tables; its column headers were lost in conversion.
- MoGe-3 and FoundationGeo weight licenses were not confirmed: the MoGe repo states MIT for code only, and FoundationGeo code release status is unknown.

## Q2. How to fuse sparse known depths (2-4 given object distances) or one known object size with a relative/metric depth map, and how much does it help?

### Takeaway
Aligning predicted depth to ground truth with a single global scale (median ratio or least squares) is the standard "w/ alignment" protocol. Across published tables it cuts error by about 3x: MoGe-2 KITTI AbsRel 14.2% → 4.8%, ScanNet 10.6% → 3.8%. With a few anchors, use scale-only least squares in log space (robust) rather than scale+shift, because a shift is poorly constrained with 2-4 points. Dense sparse-to-dense completion models (Prior Depth Anything) reach about 2-4% AbsRel with only 100 random points but are overkill for 2-4 anchors. A known object size gives the same single scale factor, and its accuracy is bounded by how well the object's 3D extent is measured.

### Cited Findings
- On the Robust-MVD benchmark, single-view metric depth rel% (KITTI / ScanNet) without vs with GT-median scale alignment:
  - MoGe-2: 14.21 → 4.82 and 10.57 → 3.77.
  - MapAnything: 9.69 → 6.12 and 27.77 → 4.95.
  - UniDepthV2 (with K): 13.70 → 4.00 and 3.20 → 2.10.
  - Inlier ratio at 1.03% (τ) rises, e.g. MoGe-2 KITTI 6.8 → 47.9.
  — [MapAnything arXiv, Table 4](https://arxiv.org/html/2509.13414)
- Multi-view with alignment is better still: π³ KITTI 3.09 / ScanNet 1.98; VGGT 4.60 / 2.34. — [MapAnything arXiv](https://arxiv.org/html/2509.13414)
- MapAnything natively accepts optional inputs (intrinsics, poses, depth including sparse depth) and outputs a metric scale factor. In two-view tests, adding intrinsics and depth to images cut rel from 0.08-0.13 to 0.02-0.04. Adding intrinsics alone improved pose and depth modestly (rel 0.08 → 0.07). — [MapAnything arXiv, Table 2](https://arxiv.org/html/2509.13414); [MapAnything README](https://github.com/facebookresearch/map-anything)
- Prior Depth Anything (Zhejiang Univ / HKU, arXiv 2505.10565, May 2025) fuses sparse metric priors with relative depth. It does per-pixel kNN least-squares scale+shift alignment of the predicted depth to the K nearest prior points, with distance weighting, then refines with a conditioned depth model.
  - Zero-shot AbsRel with 100 random points ("Extreme") on NYUv2 / ScanNet / ETH3D / DIODE / KITTI: 1.96 / 2.01 / 1.54 / 3.37 / 3.28 (Depth Pro + ViT-B variant).
  - Globally aligned DAv2 on the same data: 4.77 / 4.68 / 6.61 / 14.37 / 9.25. Globally aligned Depth Pro: 4.41 / 4.23 / 6.51 / 8.98 / 6.19.
  - Latency: 157-760 ms per 480×640 frame on A100.
  — [Prior Depth Anything arXiv](https://arxiv.org/html/2505.10565)
- In the same paper, plain interpolation of sparse points gives 7.93 AbsRel vs 2.42 for depth-guided pixel-level alignment. This shows the predicted relative structure carries most of the accuracy and the sparse points mainly fix scale. — [Prior Depth Anything arXiv, Table 6](https://arxiv.org/html/2505.10565)
- PromptDA (LiDAR-prompted DA) generalises poorly to sparse random points in that comparison (AbsRel 15-25). — [Prior Depth Anything arXiv](https://arxiv.org/html/2505.10565)
- Known-size-object scale recovery (UVic MASc thesis, 2026) uses this pipeline: open-vocabulary grounding and segmentation, monocular depth, back-projected object points, an oriented 3D box fit, then a scale factor from canonical real-world size priors. On HOT3D / ScanNet / ARKitScenes / custom iPhone it reaches MRA 68.9% / 88.3% / 75.1% / 89.9%. Per-frame averaging improves stability. Its stated failure modes are size-variable categories, occlusion/truncation and segmentation quality. — [Sultana 2026, UVic thesis](https://dspace.library.uvic.ca/items/a4f799c2-15a4-4e51-9293-8fa95da6b34a)
- Learning scale from object-size priors alone is called "too brittle" in the StableCamH paper. Supervision is only as accurate as the prior. — [arXiv 2312.04530](https://arxiv.org/html/2312.04530v2)
- Video metrics in recent 4D papers align a whole sequence with one shared scale (and shift) before scoring, e.g. SpatialTrackerV2 and π³. A single per-clip scale is therefore the standard, well-tested operating point. — [SpatialTrackerV2 arXiv 2507.12462](https://arxiv.org/html/2507.12462); [π³ arXiv](https://arxiv.org/html/2507.13347)

### Inferences
- Recipe for 2-4 known camera-to-object distances. Back-project each object's mask pixels with predicted depth z and focal f. Take a robust per-object depth, either the median of z over the mask or the mask centroid distance ‖X‖ if the given value is Euclidean range rather than z-depth.
  - Fit the scale only: s = exp(median(log d_true,i − log d_pred,i)). Equivalently, least squares on log-ratios, or s = Σ d_true·d_pred / Σ d_pred² in linear space.
  - With 3 or more anchors you can also fit a shift, or an affine fit in inverse depth for disparity models. Check the leave-one-out residual and keep the shift only if it reduces it.
  - The spread of the per-anchor ratios is a free error estimate. Inconsistent ratios flag bad masks or depth.
- Recipe for a known object size L. Measure the object's predicted 3D extent L̂ along the same physical axis (see Q3); then s = L / L̂, and every distance, size and speed in the scene is multiplied by s.
- Recipe for a known object speed v. Compute the object's predicted 3D speed v̂ from the tracked 3D centroid (see Q4); then s = v / v̂.
- Prefer the anchor whose measurement is most stable: a long, rigid, unoccluded extent, or a long trajectory.
- Focal matters separately from depth scale. Lateral sizes scale as pixel_extent × Z / f. If depth is anchored by given distances but f is wrong by x%, lateral sizes and speeds are wrong by about x%. If the scene supplies both a known distance Z and a known size L of the same object, solve f = pixel_extent × Z / L instead of trusting the model's focal. With a known size alone, the whole (Z/f) ratio is calibrated at once, so focal error cancels for objects at similar depth.
- Expected improvement: from about 15% (zero-shot metric) to about 3-5% AbsRel on real data. On synthetic or game footage, the remaining relative error (Sintel about 13% AbsRel even after alignment) may dominate.

### Gaps
- I found no paper that specifically benchmarks fusion with only 2-4 sparse depth anchors. The closest is "Extreme" = 100 random points. Accuracy with 2-4 points comes from the inference above, not from a cited figure.
- I could not access the UVic thesis's per-category error breakdown (PDF not fetched).

## Q3. How to measure an object's physical dimensions under perspective and oblique orientation (3D boxes from depth + segmentation; learned monocular 3D detectors), and typical errors

### Takeaway
Learned open-vocabulary monocular 3D detectors are still weak zero-shot: AP3D about 9-29 on novel categories, with depth and size the main error sources. They are slow (DetAny3D at 1.5 FPS) and are not the right tool for precise single-object measurement. The practical, more accurate route is geometric: segment the object (SAM 2 / Grounded-SAM), back-project masked pixels using scale-anchored depth and estimated focal, remove outliers, and measure extents. Using PCA/min-area oriented boxes, or better, measuring between specific 3D endpoints, often beats axis-aligned boxes only when the point cloud is clean. SpatialRGPT found PCA-oriented boxes from single-view point clouds noisier than axis-aligned ones.

### Cited Findings
- OVMono3D (arXiv 2411.16833; Omni3D novel categories, AP3D at IoU 0.15 / 0.25): OVMono3D-LIFT 9.61 / 24.08, OVMono3D-GEO (geometric: depth + segmentation + box fitting) 8.48 / 20.63, DetAny3D 9.22 / 21.44, OVM3D-Det 6.74 / 18.30. — [OVMono3D arXiv](https://arxiv.org/html/2411.16833)
- OVMono3D disentangled IoU3D (%) given GT 2D boxes on novel categories:
  - LIFT: XY 52.9, Depth 32.6, Size 49.6, Pose 73.6.
  - GEO: XY 48.0, Depth 31.0, Size 18.7, Pose 37.8.
  - Depth is the largest error source for both. Geometric box fitting is especially poor on size and orientation, being "sensitive to occlusions and noisy depth estimation".
  — [OVMono3D arXiv](https://arxiv.org/html/2411.16833)
- DetAny3D (arXiv 2504.07958): with GT 2D prompts on novel categories it reaches AP3D 28.96 / 39.09 / 57.72 on three splits vs OVMono3D 8.44 / 17.16 / 14.12. With Grounding DINO prompts: 25.73 vs 4.71 (KITTI-type novel classes). Speed on KITTI: Cube R-CNN 33.3 FPS, OVMono3D 7.1 FPS, DetAny3D 1.5 FPS. — [DetAny3D arXiv](https://arxiv.org/html/2504.07958)
- SpatialRGPT builds 3D scene graphs from open-vocabulary detection and segmentation, metric depth and camera calibration. Its appendix reports that PCA-based oriented boxes from single-view point clouds "often lack accuracy due to the incomplete and noisy nature of point clouds". Against Omni3D human-labelled boxes, MSE was width 17.09 vs 8.27 and height 4.83 vs 2.35 (oriented vs axis-aligned). — [SpatialRGPT arXiv 2406.01584](https://arxiv.org/pdf/2406.01584)
- A 2026 thesis pipeline fits an oriented 3D box to object-centric back-projected points to estimate object dimensions, then uses those dimensions for metric scale recovery (MRA up to 0.88-0.90 on ScanNet / iPhone). — [Sultana 2026, UVic](https://dspace.library.uvic.ca/items/a4f799c2-15a4-4e51-9293-8fa95da6b34a)
- MoGe-3's main improvement is fine-detail local geometry, including thin structures and small objects. Local point δ0.01 rises from 46.6 (MoGe-2) to 55.9 (ViT-L). Monocular geometry around small objects is exactly where box-fitting fails. — [MoGe-3 arXiv](https://arxiv.org/html/2607.17967)

### Inferences
- For a "length/height/diameter" question, measure the specific extent rather than fitting a full box:
  1. Get the mask and erode it a few pixels to drop depth-edge "flying pixels".
  2. Back-project with scale-anchored depth.
  3. Find the extreme points along the axis of interest: the object's principal axis by PCA on 3D points, the gravity axis for height, or the 2D principal axis lifted to 3D.
  4. Take robust percentiles (2nd-98th) instead of min/max.

  Diameter of a round object is about the extent perpendicular to the viewing ray at the object's depth. Height of an upright object is the extent along the estimated up vector (from ground-plane normals; MoGe also predicts normals).
- Single-view point clouds see only the visible half of an object. Depth extents along the viewing ray are underestimated, while extents perpendicular to the ray are reliable. Prefer measuring lateral extents in frames where the dimension of interest is most fronto-parallel. Use multiple frames (a max over frames, or a median over the top-k frames) when the object rotates or the camera moves.
- Scale propagates linearly. Any error in the anchoring prior or its measured counterpart shows up 1:1 in every answer, so spend effort on the anchor measurement.

### Gaps
- I did not find published absolute-dimension errors (e.g. % error in object length) for depth+segmentation pipelines on general objects. Papers report box IoU/AP or MSE, not % length error.
- I did not fetch Cube R-CNN or SpatialRGPT full tables beyond the box-type ablation.

## Q4. 3D speed and acceleration from video: back-projecting tracked points with depth; dynamic reconstruction (MegaSaM, Shape of Motion, St4RTrack, TAPIP3D, SpatialTrackerV2) and accuracy

### Takeaway
The current practical option is feed-forward 3D tracking with joint camera estimation. SpatialTrackerV2 (Jul 2025) takes 5-10 s per clip and handles camera motion. It reports TAPVid-3D 21.2 AJ / 31.0 APD3D and video depth AbsRel 0.081 vs MegaSaM 0.093 after scale alignment. MegaSaM is the optimisation baseline: accurate but about 5-10 min per 100 frames. TAPIP3D gives better long-term tracks given depth and poses. For a static camera, a simpler pipeline works: a 2D tracker plus per-frame depth, with a temporally consistent video depth model, back-projected and differentiated. All of them still need the prior to fix metric scale.

### Cited Findings
- SpatialTrackerV2 (arXiv 2507.12462) is a feed-forward model that decomposes world-space motion into scene geometry, camera ego-motion and per-pixel object motion. It "outperforms existing 3D tracking methods by 30%" and matches dynamic-reconstruction accuracy "while running 50× faster".
  - TAPVid-3D: 21.2 AJ and 31.0 APD3D, +61.8% / +50.5% over DELTA.
  - Video depth (shared scale+shift alignment): average AbsRel 0.081 / δ1.25 0.910, vs VGGT 0.104 / 0.881 and MegaSaM 0.093 / 0.894.
  - Runtime: "MegaSAM usually needs 5-10 min for a 100 frames video, while our method only takes 5-10 seconds".
  — [SpatialTrackerV2 arXiv](https://arxiv.org/html/2507.12462)
- The SpatialTrackerV2 camera encoding includes a normalised focal length plus a scale/shift aligning depth to poses, so it estimates intrinsics jointly. The README lists planned support for other depth models (DepthAnything, UniDepth, Metric3D). — [SpatialTrackerV2 arXiv](https://arxiv.org/html/2507.12462); [SpaTrackerV2 README](https://github.com/henry123-boy/SpaTrackerV2)
- TAPIP3D (arXiv 2504.14717) lifts features into a camera-stabilised 3D world space using depth and camera poses (e.g. from MegaSaM). It runs at 11.3 FPS on an L40S for 32 frames × 1,024 queries. Geometry with MegaSaM on a DexYCB sequence took 121.1 s vs 6.4 s for TAPIP3D tracking itself. Optimisation methods such as Shape-of-Motion "require several hours". — [TAPIP3D arXiv](https://arxiv.org/html/2504.14717)
- MegaSaM (arXiv 2412.04463; Apache 2.0 code, CC-BY materials) is deep visual SLAM adapted to dynamic scenes with little parallax and unknown FoV. It uses an uncertainty-aware global BA that decides when to add mono-depth regularisation. It estimates focal length, poses and consistent video depth. — [MegaSaM arXiv](https://arxiv.org/html/2412.04463); [MegaSaM README](https://github.com/mega-sam/mega-sam)
- St4RTrack (arXiv 2504.13152) is a feed-forward model that predicts two pointmaps per frame pair in a shared world frame, giving simultaneous 4D reconstruction and world-frame tracking. It adapts to real video via a reprojection loss without 4D GT. — [St4RTrack arXiv](https://arxiv.org/html/2504.13152)
- Video depth (per-sequence scale alignment) AbsRel on Sintel / Bonn / KITTI, with FPS on A800 for KITTI:
  - π³: 0.233 / 0.049 / 0.038, 57.4 FPS.
  - VGGT: 0.299 / 0.057 / 0.062, 43.2 FPS.
  - CUT3R: 0.417 / 0.078 / 0.122, 7.0 FPS.
  - MonST3R: 0.399 / 0.072 / 0.107, 1.3 FPS.
  — [π³ arXiv, Table 4](https://arxiv.org/html/2507.13347)
- Video Depth Anything gives temporally consistent depth for long videos (tested on 196 s / 4,690 frames). It has metric variants and the lowest temporal alignment error (ScanNet TAE 1.09 vs MoGe-2 2.56), which matters for differentiating depth over time. — [Video Depth Anything arXiv 2501.12375](https://arxiv.org/html/2501.12375); [VDA README](https://github.com/DepthAnything/Video-Depth-Anything)

### Inferences
- Speed recipe:
  1. Track the object's 2D centroid or several surface points, e.g. with a CoTracker / SAM 2 mask centroid.
  2. Get per-frame depth from a temporally consistent model (VDA, π³/VGGT/DA3 on the clip, or SpatialTrackerV2 output).
  3. Back-project with a single focal estimate for the clip. If the camera moves, express points in world coordinates using estimated poses.
  4. Fit a low-order polynomial (constant-velocity or constant-acceleration) to the 3D trajectory over time with robust regression, instead of finite-differencing. Acceleration from double differencing of noisy depth is very unstable.
  5. Apply the scale s from the prior.
- When the prior is the speed of a different object, both objects' speeds share s. The ratio v_target/v_ref measured in the same reconstruction is scale-free, so answer = v_ref,true × (v̂_target / v̂_ref). The same holds for sizes and distances: ratios within one reconstruction cancel scale and much of the focal error.
- Depth-axis motion (toward or away from the camera) carries the largest error, because it depends on frame-to-frame depth consistency. Lateral motion depends mainly on f and depth scale. For objects moving mostly in depth, use the apparent-size change (Z ∝ 1/pixel size) as a cross-check.

### Gaps
- I found no benchmark that reports metric speed or acceleration error (m/s) from these trackers. TAPVid-3D reports AJ/APD on positions, and scale is usually aligned away.
- I did not extract St4RTrack's numerical results or Shape of Motion runtimes beyond TAPIP3D's "several hours" remark.

## Q5. Practical: what runs on a single GPU (e.g. RTX PRO 6000 96 GB on Colab) for about 600 short clips overnight; code and licenses

### Takeaway
All the feed-forward models (MoGe-2/3, DA3, Video Depth Anything, VGGT/π³, MapAnything, SpatialTrackerV2) fit easily in 96 GB and process a short clip in seconds. 600 clips overnight is comfortably feasible for per-frame depth + focal and even for SpatialTrackerV2. Optimisation-based MegaSaM (about 5-10 min per 100 frames) would take roughly 50-100 GPU-hours and is not feasible overnight for all clips. Detector-based 3D boxes (DetAny3D at 1.5 FPS) are feasible only on keyframes.

### Cited Findings
- Per-frame latency on A100 FP16:
  - MoGe-2 ViT-L: 39 ms at 700² (≈1.1-2 GB VRAM).
  - MoGe-3 ViT-L: 121 ms.
  - Depth Pro: 139-142 ms (3.7 GB).
  - UniDepth V2: 33-50 ms.
  - Metric3D V2: 87 ms.
  - DA3: 213 ms at 630×840.
  — [MoGe-2 arXiv](https://arxiv.org/html/2507.02546); [MoGe-3 arXiv](https://arxiv.org/html/2607.17967)
- DA3 throughput: Large 78 FPS, Giant 37.6 FPS, VGGT 34.1 FPS. Max images per forward pass on an 80 GB A100: about 1,500 (Large) and about 450 (VGGT). — [DA3 arXiv, Table 8](https://arxiv.org/html/2511.10647)
- π³ runs at 57.4 FPS and VGGT at 43.2 FPS on KITTI video depth (A800). — [π³ arXiv](https://arxiv.org/html/2507.13347)
- UniDepthV2 on A6000 at 0.5 MP: Small 23 ms, Base 35 ms, Large 65 ms; Depth Pro 271 ms at native 1536². — [UniDepthV2 arXiv 2502.20110](https://arxiv.org/html/2502.20110)
- SpatialTrackerV2: 5-10 s per clip vs MegaSaM 5-10 min per 100 frames. — [SpatialTrackerV2 arXiv](https://arxiv.org/html/2507.12462)
- TAPIP3D: 11.3 FPS for tracking, plus geometry (MegaSaM 121 s per DexYCB sequence). — [TAPIP3D arXiv](https://arxiv.org/html/2504.14717)
- Prior Depth Anything: 157-760 ms per frame. — [Prior Depth Anything arXiv](https://arxiv.org/html/2505.10565)
- DetAny3D: 1.5 FPS. — [DetAny3D arXiv](https://arxiv.org/html/2504.07958)
- Licenses and availability (open weights for all):
  - MoGe: MIT code.
  - DA3: Metric-Large and Base Apache 2.0; Large, Giant and Nested CC BY-NC 4.0.
  - Video Depth Anything: metric S/B/L checkpoints on HF.
  - UniDepth: CC BY-NC 4.0.
  - Depth Pro: Apple sample-code licence.
  - Metric3D: BSD-2.
  - MapAnything: Apache 2.0 code plus an Apache checkpoint.
  - VGGT: commercial checkpoint available.
  - π³: CC BY-NC weights.
  - MegaSaM: Apache 2.0.
  — [MoGe](https://github.com/microsoft/MoGe), [DA3](https://github.com/ByteDance-Seed/depth-anything-3), [VDA](https://github.com/DepthAnything/Video-Depth-Anything), [UniDepth](https://github.com/lpiccinelli-eth/UniDepth), [Depth Pro](https://github.com/apple/ml-depth-pro), [Metric3D](https://github.com/YvanYin/Metric3D), [MapAnything](https://github.com/facebookresearch/map-anything), [VGGT](https://github.com/facebookresearch/vggt), [Pi3](https://github.com/yyfz/Pi3), [MegaSaM](https://github.com/mega-sam/mega-sam)

### Inferences
- Budget estimate (my arithmetic from the latencies above): 600 clips × about 100 frames = 60k frames.
  - MoGe-2 at about 40 ms/frame: about 40 min.
  - MoGe-3: about 2 h.
  - DA3-Large on whole clips: well under 1 h.
  - SpatialTrackerV2 at 5-10 s per clip: about 1-2 h.
  - MegaSaM at 5-10 min per clip: about 50-100 h, so restrict it to a subset (e.g. clips with a moving camera).

  An RTX PRO 6000 (Blackwell) should be at least A100-class, but I found no direct benchmark.
- A sensible overnight stack:
  - SAM 2 / Grounded-SAM masks for the referenced objects.
  - MoGe-2 (or MoGe-3) per frame for relative point maps + FoV, with the median FoV over frames.
  - Optionally DA3 / π³ over the clip for consistent multi-frame geometry and camera motion.
  - SpatialTrackerV2 or a 2D tracker + depth for trajectories.
  - Scale fit to the given distances / size / speed (Q2).
  - Ratio-based answers whenever the prior and target are measured in the same reconstruction.
- For an open-weight-only track, everything above qualifies. For commercial-friendly licenses, use MoGe (MIT code), DA3-Metric-Large/Base, MapAnything-apache, VGGT-1B-Commercial and MegaSaM.

### Gaps
- No published throughput numbers for RTX PRO 6000 / Blackwell. All timings are for A100/A800/A6000/L40S.
- I could not confirm whether Colab's environment builds MoGe-3's FlexGEMM/Triton dependency cleanly, or SpatialTrackerV2's install requirements, without testing.
- I did not search for repository code for FoundationGeo or the UVic thesis pipeline.
