# Deep research (workflow) on the two 3D problems, 2026-10-12

For the synthetic 3D renders, the research found no ready-made way to make pixel geometry beat the VLM's direct guesses. Every off-the-shelf focal-length estimator has a few degrees of FoV error on benchmarks: about 1.6-5 deg median for GeoCalib, AnyCalib and MoGe, and about 13 deg hFoV for VGGT's camera head. On real video whose focal length changes, the error grows to 45-65% in focal length, and pinhole-derived metric sizes and speeds would carry about that much error. The most usable recipe has three steps. (1) Get an affine-invariant point map from MoGe-2, or a GeoCalib joint fit over many frames of one shot, and solve a single focal length per clip. (2) Throw away the network's metric scale and replace it with the clip's own anchors, meaning the known object quantity and the sparse distances. Those distances are Euclidean range to the object origin, not z-depth. (3) Use the geometric estimate only where it is well conditioned, for example as a check on the VLM or blended with it, never as a blanket replacement. For the lab clips, the paper confirms the label pipeline: hand-clicked centres, depth values picked by hand from ToF maps, back-projection, then forward differences, with some smoothing and multi-camera averaging when the object is occluded. The paper does not itself say the labels are biased upward. The metric is MRA: a bounded, stepwise score against the noisy labels. Each 3D category is a fixed 25% of the total, so fitting a per-category multiplicative correction toward the label bias on the train split is the most direct lever. None of the verified sources measured gains on QuantiPhy itself; every expected gain has to be confirmed on the train split.

## [high, vote 2-1 / 3-0]

Single-image focal/FoV estimators have errors of a few degrees on standard benchmarks, and their ranking changes from dataset to dataset. On rendered data, MoGe was the most accurate in one comparison. Median vFoV error on Stanford2D3D: AnyCalib-pinhole 2.55 deg, GeoCalib 3.23, MoGe 4.33, DUSt3R 5.34. On TartanAir (photo-realistic renders): MoGe 1.61, AnyCalib 3.62, GeoCalib 4.91, UniDepth 32.16. GeoCalib's own paper reports 3.0-4.9 deg median across four unseen datasets, but only 13.6-19.1% of images fall within 1 deg (AUC@1). AnyCalib needs no horizon or gravity cue and recovers intrinsics in closed form from per-pixel ray fields, so it can be run on each frame.

Evidence: Table numbers were checked against the PDFs (AnyCalib Table 2, GeoCalib Table 1). The votes were 2-1, 3-0 and 2-1, and the splits concerned how well the results transfer, not the numbers. A fixed error of a few degrees is a much larger relative focal error at narrow FoV. At hfov around 8-20 deg, 3 deg of FoV error is roughly a 15-40% focal error. TartanAir images all share one FoV, so no benchmark here tests FoV that varies between images across 8-103 deg.

Sources: https://arxiv.org/pdf/2503.12701, https://arxiv.org/pdf/2409.06704

## [medium, vote 3-0]

On harder footage, per-frame focal estimates are too coarse to serve as a pinhole scale. On real videos with changing zoom/focus (the InFlux benchmark), mean fx error is 45.6% for WildCamera, 50.6% for UniDepthV2, 56.5% for GeoCalib and 64.6% for Perspective Fields. Only about 53% of GeoCalib's frame-point pairs land within 300 px. On ETH3D, VGGT's native camera head has about 12.9 deg median / 16.6 deg mean hFoV error from a single image, and fastVGGT is about the same; MoGe-2 with VGGT's solver was far worse (~32 deg). Since metric size and speed scale linearly with focal length in a pinhole model, these errors pass almost one-for-one into the answers. This is consistent with what was observed: pinhole geometry did worse than the VLM's direct guesses.

Evidence: Votes were 3-0 on all three claims, but transfer is limited. InFlux is real cinema-zoom footage weighted toward telephoto (~6-20 deg hFoV), reports means rather than medians, and includes lens distortion. StereoVGGT is a single non-peer-reviewed preprint tested on real DSLR images. Neither covers clean Blender pinhole renders. The InFlux text says 54.1% while its Table 1 says 52.9%.

Sources: https://arxiv.org/html/2510.23589v1, https://arxiv.org/pdf/2603.29368

## [medium, vote 3-0 / 2-1]

If intrinsics are fixed within a shot, sharing one focal length across many frames reduces error noticeably, so solve one focal per clip rather than per frame. GeoCalib can jointly optimise one set of intrinsics over N non-overlapping images, and its FoV AUC improves steadily from N=1 to 32. That joint fit beats averaging the per-frame FoVs. ViPE (NVIDIA) starts from GeoCalib on 4 uniformly sampled frames, then refines one shared focal (principal point centred, square pixels) in full bundle adjustment. On TUM this gets 1.8/0.6 deg FoV error, against 4.1/4.3 deg for GeoCalib-only DROID-SLAM and 10-12 deg for VGGT and MegaSAM. On RDS, where focal varies across clips (30-70 deg), ViPE's error rises to 7.9 deg and VGGT does better at 5.9 deg. Bundle adjustment can only improve on the GeoCalib prior when the camera translates enough to create parallax.

Evidence: The GeoCalib multi-frame result (3-0) used random TartanAir images, not consecutive video frames, which are more correlated, so the gain on video may be smaller. The ViPE numbers (votes 3-0, 2-1, 2-1) are the authors' own. The GeoCalib-only versus ViPE comparison is confounded by different frame sampling and by ViPE's depth priors. ViPE also uses metric-depth priors that are re-predicted once the focal changes. QuantiPhy clips are short and often shot from a static camera, so bundle adjustment may add nothing beyond the GeoCalib prior.

Sources: https://arxiv.org/pdf/2409.06704, https://arxiv.org/pdf/2508.10934

## [medium, vote 3-0 / 2-1]

Implementable recipe: decouple relative geometry from metric scale. MoGe-2 predicts an affine-invariant point map, recovers focal length and z-shift from it with a small solver, and predicts global metric scale with a separate MLP head on the DINOv2 CLS token. Keeping the scale separate gave better metric and relative accuracy in the authors' ablation. Focal can be solved from any point map, assuming unit aspect ratio and a centred principal point, by minimising the weighted reprojection error ||(u,v) - f*(X/Z, Y/Z)|| with a few Weiszfeld/IRLS iterations. The residual does not change with scale, so the point map need not be metric. To apply this to QuantiPhy: keep the network's relative shape and focal, drop its learned scale, and fit the scale to the clip's own anchors (the known object size or speed and the given object-to-camera distances). Then read off sizes and displacements in metric units and difference them at the true fps.

Evidence: Votes: Weiszfeld focal recipe 3-0, MoGe-2 description 3-0, decoupling advantage 2-1. Swapping in an external scale anchor is an engineering inference, not something the paper tested. Anchoring to distances also needs the z-shift to be right. No paper benchmarks MoGe-2 focal at hfov of about 8 deg, where the view is nearly orthographic and focal trades off against depth. A related claim that MetricAnything's Student-PointMap reaches 2.55 deg median hFoV was refuted 0-3, so treat it as unverified.

Sources: https://arxiv.org/pdf/2507.02546, https://arxiv.org/pdf/2601.22054

## [high, vote 3-0]

Synthetic-label conventions that any geometric pipeline must match. The given 'depth' is the 3D Euclidean range ||p_obj - p_cam|| from the object origin to the camera origin, not z-depth along the optical axis. It is given only at a few shared reference times (e.g. t=1 s, 2 s, sometimes 1.5 s), and the queried object's own distance may be withheld. Ground-truth velocity is a one-frame backward difference of obj.matrix_world.translation (the object origin, which may not be its visual centroid) at the render fps; human rigs use a pelvis/hip bone. Practical consequences (inferred, not from the sources): (a) convert range to depth with Z = d*f/sqrt(f^2 + r^2), where r is the object's pixel offset from the image centre. (b) If one object has both a range d and a known physical size S with pixel size s at the same time, then sqrt(f^2 + r^2) = d*s/S. This gives a per-clip focal estimate f = sqrt((d*s/S)^2 - r^2) without any learned calibrator. It is ill-conditioned when r is close to d*s/S, and it relies on accurate pixel measurements of size. (c) For motion parallel to the image plane, metric speed is pixel speed times S/s at the object's depth, so focal cancels. Focal matters mainly for motion toward or away from the camera, and for carrying scale between objects at different depths.

Evidence: Vote 3-0, checked against Appendix D.1 of the QuantiPhy paper and its Blender script. The paper's own appendix is the authoritative source for label conventions. Consequences (a)-(c) are my geometric derivations and were not verified by any source; test them on the train split, where the true hfov is known.

Sources: https://arxiv.org/abs/2512.19526

## [high, vote 3-0]

How the lab labels were made, and what that implies. The 3D lab labels come from hand-clicked 2D object centres on the main camera plus metric depth that annotators chose by hand from Orbbec Femto Mega ToF maps (850 nm, RGB 25 fps). The authors picked depth by hand because the depth map is 'often incomplete and ambiguous, especially at pixels with high motion'. The clicked points are back-projected with calibrated intrinsics; velocity is a forward difference v_k = (x_{k+1} - x_k)/dt and acceleration a second difference. Centres were clicked over at least 5 adjacent frames 'for smoothing purpose'. When the object is occluded in the main camera, the position is the average of the other three cameras. FoundationPose was dropped because it could not localise objects stably. The paper confirms the labels are manual and noisy but does not say they are biased upward. That bias is an inference, supported indirectly: frame-to-frame jitter in clicks and depth adds to the true displacement, which inflates speeds in expectation.

Evidence: Vote 3-0, checked against Appendix D.2 and Table 5. The main-text Section 3 describes a multi-view stereo / 4D reconstruction pipeline, which contradicts the appendix; the appendix is the more detailed account. No verified source covered ToF failure modes on small, round or moving objects (flying pixels, multipath, mixed pixels at edges). That part of the research question went unanswered.

Sources: https://arxiv.org/abs/2512.19526

## [medium, vote 3-0 / 2-1]

Under the scoring metric, matching the label bias pays off directly, and the two 3D categories are fixed half of the score. MRA counts a prediction as correct at threshold theta when |y_hat - y|/|y| < 1 - theta, with theta in {0.10, 0.20, ..., 0.90, 0.95}. Score is 1.0 under 5% error and drops 0.1 per bin down to 0 at 90% or more. Predictions pass through abs(), and a blank answer scores 0. The final score is the unweighted mean of the four category means (S2, D2, S3, D3), so 3S and 3D are each worth 25% regardless of question count. The score is bounded and stepwise, so an outlier costs at most one item. The labels are the reference, so a multiplicative correction toward their systematic bias raises the score. That is consistent with the +0.015 seen on S3. Implementable step (inferred): fit a separate log-scale multiplier for each category and source (lab vs synthetic, and speed vs acceleration vs size) by directly maximising train-split MRA, with cross-validation to avoid overfitting. Blend the geometric and VLM estimates in log space with weights also tuned on MRA. Where the pinhole conditioning is poor (narrow FoV, near-constant depth, missing anchor for the queried object), fall back to the VLM.

Evidence: The macro-average claim was 3-0. The MRA formula claim was 2-1: the definition was confirmed against the official evaluator and the local mra.py, but the original gloss ('rewards within about 5-50%', 'does not penalise error size') was wrong and is corrected here. A competing claim that thresholds run 0.5-0.95 was refuted 0-3. The calibration and blending procedure is my recommendation, not something a source evaluated.

Sources: https://quantiphy.stanford.edu/competition/, https://raw.githubusercontent.com/Paulineli/QuantiPhy/main/evaluator.py, /home/user/quantiphy-challenge/qp/mra.py

## caveats

No verified source reports any result on QuantiPhy itself. No competitor or leaderboard write-up survived verification, so every 'expected gain' is unknown until tested on the train split, where hfov and labels are known. All focal-accuracy numbers come from real imagery or photo-realistic renders with moderate FoV. None covers clean Blender pinhole renders spanning hfov 8-103 deg, and the narrow-FoV end is where every method should degrade most. Several benchmarks are the method authors' own results (AnyCalib, GeoCalib, ViPE, MoGe-2), and StereoVGGT is an unreviewed preprint. Newer focal estimators (MoGe-2, UniDepthV2/V3, Depth Pro, VGGT variants) appear only in scattered tables, so the rankings may be out of date. The second half of the research question (ToF biases such as flying pixels, multipath and mixed edge pixels, plus label-noise-aware prediction literature) produced no claims that survived verification; that gap is not evidence that those effects are absent. The upward bias in the lab labels is an inference from the pipeline plus the observed +0.015, not something the paper states, and bias corrections tuned on a small train split may overfit. Refuted claims to avoid relying on: the Revaud et al. calibration from known-size objects as stated, the MetricAnything 2.55 deg hFoV figure, the 'one global scale explains 92-97%' claim, and the scale-and-shift claims based on blog-quality depth sources. Several sources (arXiv, the quantiphy.stanford.edu page) were reached only through curl fallbacks or search excerpts, so a few table values could not be fully checked.

## openQuestions

[
 "On the QuantiPhy train split with known hfov, what per-clip focal error do MoGe-2, AnyCalib and GeoCalib (multi-frame joint mode) actually reach, binned by hfov (8-20, 20-60, 60-103 deg)? Is any bin below about 10% focal error, the level at which geometry could beat the VLM?",
 "Does the closed-form check f = sqrt((d*s/S)^2 - r^2), from one object having both a known size and a given range, or simply scaling lateral motion by S/s with focal cancelling, beat learned calibrators on clips where the anchors fall on the same object as the query?",
 "How large and how consistent is the lab-label bias across object size, speed and the quantity asked (speed vs acceleration)? Does the 'at least 5 adjacent frames for smoothing' step reduce it? Does a per-category MRA-optimised multiplier generalise under cross-validation, or does it overfit the +0.015 on S3?",
 "Are synthetic hfov and camera pose constant within each clip, which would justify per-clip joint focal estimation, or do some clips zoom or move the camera mid-shot?"
]

## refuted

[
 {
  "claim": "MetricAnything's distilled 'Student-PointMap' (MoGe-2 fine-tuned on MetricAnything pseudo-labels) recovers horizontal FOV from a single image with average mean/median error of 3.12/2.55 degrees on ETH3D+iBims-1. That beats DUSt3R (4.80/3.07), Depth Pro (5.65/4.46), MoGe-2 (6.42/4.91), UniDepth (11.3/7.96) and Perspective Fields (12.1/10.6). This makes it a candidate per-frame focal estimator for the synthetic clips with unknown, varying intrinsics.",
  "vote": "0-3",
  "source": "https://arxiv.org/pdf/2601.22054"
 },
 {
  "claim": "Relative (affine-invariant) monocular depth can be converted to metric depth by a global least-squares scale-and-shift fit against sparse metric depth points; this is the base step of the pipeline. It could be adapted to QuantiPhy, where sparse object-to-camera distances at 1-2 times anchor the scale.",
  "vote": "0-3",
  "source": "https://arxiv.org/abs/2303.12134"
 },
 {
  "claim": "The full camera calibration, including the unknown focal length and the metric scale, can be recovered from tracked detections of objects whose 3D shape and size are known. The method parameterizes the camera by only 3 values (focal, tilt, height) and minimizes a box or mask reprojection error against a 3D prior shape. This applies directly to the unknown-hfov synthetic setting, where one object of known size is available.",
  "vote": "0-3",
  "source": "https://openaccess.thecvf.com/content/ICCV2021/papers/Revaud_Robust_Automatic_Monocular_Vehicle_Speed_Estimation_for_Traffic_Surveillance_ICCV_2021_paper.pdf"
 },
 {
  "claim": "Focal length can be estimated only through perspective effects. Weighting the reprojection error by box area (so larger, nearer objects count more) improves the focal estimate. This implies that focal recovery is ill-conditioned when perspective variation is small, for example with a narrow FOV or objects at nearly constant depth.",
  "vote": "1-2",
  "source": "https://openaccess.thecvf.com/content/ICCV2021/papers/Revaud_Robust_Automatic_Monocular_Vehicle_Speed_Estimation_for_Traffic_Surveillance_ICCV_2021_paper.pdf"
 },
 {
  "claim": "A single global scale accounts for most of the scale error. The leading eigen-direction of the anchor embeddings holds 92-97% of the energy (median \u03b71) and lines up with the constant global channel (median similarity of about 0.985-0.991). So one metric anchor, such as a single known object distance, already recovers most of the metric scale.",
  "vote": "0-3",
  "source": "https://arxiv.org/pdf/2605.07418"
 },
 {
  "claim": "Depth Anything v2's absolute (metric) depth is badly off, but its relative depth is nearly linear in true depth on ground-level scenes (R^2 0.971 to 0.998 across 4 football-field images). So a single scale factor from one known reference distance can turn it into metric depth. Evidence is limited: one depth model, flat outdoor ground, 4 images.",
  "vote": "1-2",
  "source": "https://nhsjs.com/2026/object-average-speed-calculation-in-xz-plane-using-monocular-depth-estimation-and-vanishing-point-geometry/"
 },
 {
  "claim": "Scaling relative depth with one known-size reference object in the frame cut mean depth error from 32.9% (SD 24.2%) to 3.8% (SD 2.8%), over 40 depth samples restricted to under 60 m predicted depth. Error before scaling was bimodal (about 20% and about 90%) because each image has its own scale factor.",
  "vote": "1-2",
  "source": "https://nhsjs.com/2026/object-average-speed-calculation-in-xz-plane-using-monocular-depth-estimation-and-vanishing-point-geometry/"
 },
 {
  "claim": "The score is Mean Relative Accuracy. A prediction earns 0.1 credit for each of 10 thresholds where its relative error |\u0177\u2212y|/|y| is below 1\u2212\u03b8, with \u03b8 in {0.5, 0.55, ..., 0.95}. So credit falls in steps as relative error passes 5%, 10%, ..., 50%, and anything with 50% or more error scores zero. The overall score is the unweighted mean of the four category scores (2S, 2D, 3S, 3D).",
  "vote": "0-3",
  "source": "https://arxiv.org/abs/2512.19526"
 }
]

## unverified

[]

## sources

[
 {
  "url": "https://arxiv.org/pdf/2503.12701",
  "quality": "primary",
  "angle": "Focal length / intrinsics from monocular video",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/pdf/2409.06704",
  "quality": "primary",
  "angle": "Focal length / intrinsics from monocular video",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/pdf/2601.22054",
  "quality": "primary",
  "angle": "Focal length / intrinsics from monocular video",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/html/2510.23589v1",
  "quality": "primary",
  "angle": "Focal length / intrinsics from monocular video",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/pdf/2508.10934",
  "quality": "primary",
  "angle": "Focal length / intrinsics from monocular video",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/pdf/2603.29368",
  "quality": "primary",
  "angle": "Focal length / intrinsics from monocular video",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/abs/2303.12134",
  "quality": "primary",
  "angle": "Metric scale from known object size + sparse depth",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/pdf/2507.02546",
  "quality": "primary",
  "angle": "Metric scale from known object size + sparse depth",
  "claimCount": 5
 },
 {
  "url": "https://ecva.net/papers/eccv_2020/papers_ECCV/html/1337_ECCV_2020_paper.php",
  "quality": "unreliable",
  "angle": "Metric scale from known object size + sparse depth",
  "claimCount": 0
 },
 {
  "url": "https://openaccess.thecvf.com/content/ICCV2021/papers/Revaud_Robust_Automatic_Monocular_Vehicle_Speed_Estimation_for_Traffic_Surveillance_ICCV_2021_paper.pdf",
  "quality": "primary",
  "angle": "Metric scale from known object size + sparse depth",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/pdf/2605.07418",
  "quality": "primary",
  "angle": "Metric scale from known object size + sparse depth",
  "claimCount": 5
 },
 {
  "url": "https://nhsjs.com/2026/object-average-speed-calculation-in-xz-plane-using-monocular-depth-estimation-and-vanishing-point-geometry/",
  "quality": "primary",
  "angle": "Metric scale from known object size + sparse depth",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/abs/2512.19526",
  "quality": "primary",
  "angle": "QuantiPhy benchmark and competitor methods",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/html/2609.00658",
  "quality": "unreliable",
  "angle": "QuantiPhy benchmark and competitor methods",
  "claimCount": 0
 },
 {
  "url": "https://quantiphy.stanford.edu/competition/",
  "quality": "primary",
  "angle": "QuantiPhy benchmark and competitor methods",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/pdf/2609.29073",
  "quality": "primary",
  "angle": "Hybrid VLM + geometric estimate fusion",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/abs/2512.19526v1",
  "quality": "primary",
  "angle": "Hybrid VLM + geometric estimate fusion",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/pdf/2509.25413v2",
  "quality": "primary",
  "angle": "Hybrid VLM + geometric estimate fusion",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/pdf/1805.12440",
  "quality": "unreliable",
  "angle": "ToF depth artifacts and noisy velocity labels",
  "claimCount": 0
 },
 {
  "url": "https://arxiv.org/pdf/1807.10376",
  "quality": "primary",
  "angle": "ToF depth artifacts and noisy velocity labels",
  "claimCount": 5
 },
 {
  "url": "https://arxiv.org/pdf/1505.05459",
  "quality": "primary",
  "angle": "ToF depth artifacts and noisy velocity labels",
  "claimCount": 5
 }
]

## stats

{
 "angles": 5,
 "sourcesFetched": 21,
 "claimsExtracted": 90,
 "claimsVerified": 25,
 "confirmed": 17,
 "killed": 8,
 "unverified": 0,
 "afterSynthesis": 7,
 "urlDupes": 0,
 "budgetDropped": 9,
 "agentCalls": 103
}
