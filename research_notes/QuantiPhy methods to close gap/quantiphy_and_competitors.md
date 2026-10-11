# QuantiPhy benchmark, label conventions, follow-up work and challenge competitors (as of 2026-10-11)

Research notes. Sources were fetched on 2026-10-11 unless marked otherwise. "Unverified" means only a search snippet or a self-report backs it.

## Q1. What is the QuantiPhy paper, and how were the videos and ground truth produced? (conventions an optimal predictor must match)

### Takeaway
QuantiPhy is arXiv:2512.19526 (v1, 22 Dec 2025; CVPR 2026) by Puyin Li, Tiange Xiang, Ella Mao, Shirley Wei, Xinye Chen, Adnan Masood, Li Fei-Fei and Ehsan Adeli (Stanford, UST). The labels come from three pipelines with different conventions:
- **Blender:** script readouts. Speed is a **backward** difference of the object **origin**. Acceleration is a backward difference of **speed**. Size is the **world axis-aligned bounding box**. Camera distance is the **Euclidean range from camera origin to object origin**.
- **Lab (3D only):** hand-clicked object centres with ToF depth, back-projected, then forward and central differences.
- **Internet (2D only):** a manual pixel ruler scaled by one reference prior.

The appendix holds most of the detail an optimal predictor has to reproduce.

### Cited Findings
**Identity and venue**
- Title: "QuantiPhy: A Quantitative Benchmark Evaluating Physical Reasoning Abilities of Vision-Language Models". Authors: Puyin Li*, Tiange Xiang*, Ella Mao*, Shirley Wei, Xinye Chen, Adnan Masood, Li Fei-Fei†, Ehsan Adeli† (Stanford; Masood at UST). arXiv:2512.19526 [cs.AI], submitted 22 Dec 2025. Only v1 exists on arXiv. — [arXiv abs](https://arxiv.org/abs/2512.19526); [arXiv HTML v1](https://arxiv.org/html/2512.19526v1)
- Accepted at CVPR 2026, poster 37408. Another paper cites it as CVPR 2026 proceedings pp. 33174–33184. — [CVPR poster page](https://cvpr.thecvf.com/virtual/2026/poster/37408); [arXiv 2609.06190 references](https://arxiv.org/html/2609.06190)
- The paper describes 569 videos and 3,355 questions. The challenge test set has 3,289 QA pairs on 568 videos. — [paper §3.1](https://arxiv.org/html/2512.19526v1); [HF dataset card](https://huggingface.co/datasets/PaulineLi/QuantiPhy)
- Test-set QA pairs by source: simulation 1,633, lab 806, internet 420, segmentation 430.
- Test-set QA pairs by inference type: DS 1,684, SS 597, SD 560, DD 448. — [HF dataset card](https://huggingface.co/datasets/PaulineLi/QuantiPhy)
- Video counts in the paper (Table 4): Blender 300, internet 72, lab-captured 112, segmented 85. That is 328 2D videos and 241 3D videos. All 36 four-letter `video_type` codes appear, with 4 to 51 clips each.
- Lab-captured videos are 3D only. Internet videos are 2D only. — [paper App. B.2.2, C.2, C.3](https://arxiv.org/html/2512.19526v1)

**Task definition**
- The model gets one prior about a source object: a size, a velocity at time t, or an acceleration at time t. It must predict a quantity of a target object in world units.
- The paper's model is one scalar scale γ (world length per pixel) along the motion direction. Pixel velocity and acceleration come from finite differences. — [paper §3.1](https://arxiv.org/html/2512.19526v1)
- 2D means that, at every frame, the moving object, the reference object and every queried object are at exactly equal camera distance. Any other video is 3D. — [paper App. B.2.1](https://arxiv.org/html/2512.19526v1)
- 3D items carry a `depth_info` field. Its values are object–camera distances at chosen timestamps, for the prior object and/or the target. They are "manually reviewed to ensure that, together with the visual information, they are logically sufficient to infer the correct answer". The queried object's own depth is not always given. — [paper App. B.1, D.1.4](https://arxiv.org/html/2512.19526v1)
- The official evaluator sets category = `inference_type[0] + video_type[1]`, so the category is the prior's static/dynamic type plus the video's dimensionality.
- The evaluator also takes the absolute value of `parsed_value`. Blank, non-numeric and zero answers are counted as invalid. Thresholds are C = {0.1,…,0.9,0.95}, and the score is the unweighted mean of S2, D2, S3 and D3. — [evaluator.py](https://github.com/Paulineli/QuantiPhy/blob/main/evaluator.py)
- The paper's Appendix A.2 gives C = {0.5, 0.55, …, 0.95}. The main text, the competition page and evaluator.py all use {0.1,…,0.9,0.95}, and the code is what scores. — [paper App. A.2](https://arxiv.org/html/2512.19526v1); [competition page §04](https://quantiphy.stanford.edu/competition/index.html); [evaluator.py](https://github.com/Paulineli/QuantiPhy/blob/main/evaluator.py)

**Blender (simulation) labels**
- Blender clips are rendered with Cycles/EEVEE at several resolutions (1920×1080, 1080×1080, 480×960 and others). Frame rates include **24, 25, 30, 33, 60 and 120 fps**.
- Export is FFmpeg H.264 MP4 at constant frame rate, "without any interpolation or stabilization, so each frame aligns exactly with the simulated timeline". Camera intrinsics range from wide to telephoto. — [paper App. C.1.3](https://arxiv.org/html/2512.19526v1)
- Motion is either keyframed or physics-driven.
  - Keyframed motion (rigged humans and animals, artist-made curves) "does not necessarily obey real-world physical laws". The lunar-walk scene, for example, is not computed with the Moon's g.
  - Scripted analytic motion bakes s = ½at² or s = vt as keyframes with LINEAR interpolation.
  - Curved paths are re-parameterised by arc length to get constant speed or constant acceleration along the curve.
  - The paper says models should "use only the provided priors, not assumed real-world physics". — [paper App. C.1.2–C.1.3](https://arxiv.org/html/2512.19526v1)
- Some scenes are uniformly scaled up for visibility. An ice cube and cup were enlarged 10×, and the ground truth is in the scaled world. — [paper App. C.1.3](https://arxiv.org/html/2512.19526v1)
- **Size:** "For most objects, size is obtained from the object's axis-aligned bounding box dimensions in world space."
  - For humans the annotators record rest (T-pose) height and the minimum and maximum height while walking. For flying animals they record the minimum and maximum width during flight, and the question names which one it asks for. — [paper App. D.1.1](https://arxiv.org/html/2512.19526v1)
  - The dataset card adds conventions. A bird's wingspan or width is the fully spread tip-to-tip extent, the maximum during flight. An animal's body length (e.g. "length of the small bird") is "the object's axis-aligned bounding-box length in the simulator". — [HF dataset card, Measurement Conventions](https://huggingface.co/datasets/PaulineLi/QuantiPhy)
- **Time to frame:** t = 0 is the render start frame. Frame index = round(f_start + f·t). — [paper App. D.1.2](https://arxiv.org/html/2512.19526v1)
- **Speed at t:** the velocity vector is v_i = (p_i − p_{i−1})·fps, and speed s_i = ‖v_i‖₂. This is a **backward one-frame difference** of the object's **world origin**, and the norm includes the depth component. The answer is read from the per-frame table at frame round(t·fps). — [paper App. D.1.3](https://arxiv.org/html/2512.19526v1)
- **Acceleration at t:** a_i = (s_i − s_{i−1})·fps, a **backward difference of scalar speed** (tangential), not the magnitude of the acceleration vector. It is undefined for the first two frames. — [paper App. D.1.3](https://arxiv.org/html/2512.19526v1)
- **Displacement and distance:** both use object origins. Humans use the pelvis/hip bone. Some rigs use a helper Empty parented to the root.
  - In 3D videos, distance questions default to full 3D Euclidean distance, unless the question says "horizontal" or "vertical", which selects a projection onto the XY, XZ or YZ plane.
  - In 2D videos the planar distance is used. — [paper App. D.1.2, D.1.4](https://arxiv.org/html/2512.19526v1)
- **Depth (Blender):** "the depth as the 3D Euclidean distance" ‖p(o) − p_cam‖₂ between object origin and camera origin. This is range, not Z-depth.
  - It is "never used as evaluation targets". The paper says no questions ask for object–camera distance.
  - Depth is given only as metadata or a prior, at shared reference times such as 1 s and 2 s. — [paper App. D.1.4](https://arxiv.org/html/2512.19526v1)

**Lab labels**
- Rig: four Orbbec Femto Mega ToF cameras. RGB up to 3840×2160 at 25 fps, RGB FOV H80°×V51°. Depth NFOV 640×576 at 30 fps (H75°×V65°) or WFOV 1024×1024 at 15 fps.
- There are two setups (a small desk-scale one and a larger room-scale one). Extrinsics come from checkerboard calibration. A motor pulled some objects to give a controlled initial velocity. — [paper App. C.2, Table 5](https://arxiv.org/html/2512.19526v1)
- Object dimensions were measured with a ruler or caliper. Table 6 lists them, e.g. tennis ball d = 6.7 cm, ping-pong ball 4 cm, basketball 23.2 cm, soccer ball 17.5 cm, yoga ball 52.2 cm, credit card 85.6 × 53.98 mm. — [paper Table 6](https://arxiv.org/html/2512.19526v1)
- Depth readout used a UI tool. Annotators clicked on the RGB frame with the reprojected depth map overlaid, because averaging depth over a mask was unreliable for moving objects. — [paper App. C.2](https://arxiv.org/html/2512.19526v1)
- Trajectories: annotators "manually click on the center of the target object across a sequence of frames". The 2D click plus the main camera's metric depth is back-projected with the intrinsics.
  - At least 5 adjacent frames are annotated "for smoothing purpose".
  - v_k = (x_{k+1} − x_k)/Δt, a **forward** difference. a_k = (x_{k+1} − 2x_k + x_{k−1})/Δt², a **central second difference**. Δt comes from the video frame rate.
  - When the main view is occluded, the position is averaged from the other three cameras. — [paper App. D.2](https://arxiv.org/html/2512.19526v1)
- The depth prior given to models is "the object's metric depth from that viewpoint" (the primary camera). — [paper §3.2](https://arxiv.org/html/2512.19526v1)
- Quality control discarded about 30% of lab data and about 3% of Blender data. — [paper App. C.5](https://arxiv.org/html/2512.19526v1)

**Internet labels (2D only)**
- 42 clips come from open video platforms and 30 were filmed by the authors on smartphones. — [paper App. C.3](https://arxiv.org/html/2512.19526v1)
- Workflow:
  - The annotator confirms or overrides the FPS that OpenCV detects (e.g. 24/25/30/60) and checks the frame count.
  - The annotator records the object's pixel length along the motion direction ("bumper-to-bumper for a car") and the pixel position of a reference point per frame.
  - Pixel velocity is V_k = (x_{k+1} − x_k)/Δt, a **forward** difference. Pixel acceleration is the central second difference.
  - γ = S_world/S_pixel for a size prior, |V_world|/|V_pixel| at t₀ for a velocity prior, or the same ratio of accelerations for an acceleration prior. The ground truth is γ times the target's pixel quantity. — [paper App. D.3](https://arxiv.org/html/2512.19526v1)
- Reference priors include g = 9.8 m/s², credit-card length, road lane width and airport conveyor-belt speed. The authors say this ground truth is "inherently less precise". — [paper App. C.3](https://arxiv.org/html/2512.19526v1)

**Segmented variants**
- These are SAM 2 masks (Grounding DINO 1.5 box prompts, plus manual point prompts when needed) composited onto plain or new backgrounds. They "reuse the original annotations ... without any modification". — [paper App. C.4, D.4](https://arxiv.org/html/2512.19526v1)
- On the dataset card: lab clips with an `s` or `x` suffix are SAM-masked variants, and their `depth_info` may name objects masked out of the variant. — [HF dataset card](https://huggingface.co/datasets/PaulineLi/QuantiPhy)

**Dataset and evaluator changes in 2026**
- Test-set history:
  - 2026-04-01: initial release (3,373 QA pairs, 557 videos).
  - 2026-05-24: priors, typos and video_type fixed; segmented videos added.
  - 2026-09-08: output units fixed in 32 questions.
  - 2026-09-28: 2D/3D labels and depth_info fixed for simulation_0247 and simulation_0022 (31 rows).
  - 2026-10-07: spelling fixes; a wingspan clarification for id 137. — [HF commit history](https://huggingface.co/datasets/PaulineLi/QuantiPhy/commits/main)
- Validation set changes:
  - 2026-10-07: spelling and `segmentaion` fixes.
  - 2026-10-08: removed an unanswerable row (captured_0027s, shoulder breadth), leaving 158 rows. — [HF validation card changelog](https://huggingface.co/datasets/PaulineLi/QuantiPhy-validation)
- Commit ccc9169 (2026-10-07, closes issue #5) changed the GitHub repo:
  - The evaluator now accepts the misspelled `segmentaion`. This only affects the background breakdown.
  - A missing GT file is now an error.
  - The GPT-5.1 sample's GT for id 2168 was corrected from 125 to 1.25.
  - `quantiphy_validation.csv` was added.
  - The refreshed GPT-5.1 validation baseline is 0.4824 (S2 .569, D2 .354, S3 .443, D3 .564). — [GitHub commit ccc9169](https://github.com/Paulineli/QuantiPhy/commit/ccc916990dd9adf9e2c4206414cd232ef87ff174); [mra_results/all_model_results.csv](https://github.com/Paulineli/QuantiPhy/blob/main/mra_results/all_model_results.csv)
- **Scoring change (2026-10-11):** "140 overlapping questions are excluded" from final scoring in both tracks. These are exact matches and reviewed equivalents of public validation questions. All earlier submissions were rescored. Submissions must still contain all 3,289 rows in the same order. — [competition page notice](https://quantiphy.stanford.edu/competition/index.html)

### Inferences
- **To match Blender ground truth:**
  - Speed at t should be the one-frame backward difference of the object's origin at frame round(t·fps), as a 3D norm. For 3D videos this includes motion toward or away from the camera.
  - Acceleration should be the one-frame backward difference of speed. This is d|v|/dt, so for curved or projectile motion it is not |a_vec|, and it can be near zero for uniform circular motion.
  - Size should be the world axis-aligned bounding box. For an object rotated relative to the world axes, the AABB extent can exceed its true length.
  - The tracked point should be the origin or pivot, not the visual centroid. Objects are usually rigid and translating, so this mostly cancels in velocity.
- **For depth:** Blender `depth_info` is range (Euclidean distance to the camera). Lab depth is read from a ToF depth map at a clicked pixel on the object's visible surface.
  - Orbbec/Kinect-style depth maps normally hold Z along the optical axis. So lab "distance" is probably Z-depth to the front surface, not range to the object centre.
  - This is an inference: the paper does not say whether the lab tool shows Z or range.
- **Lab and internet speeds** use forward differences (x_{k+1} − x_k). Lab acceleration uses central second differences of hand-clicked positions, so the labels carry click noise.
  - A smoothed estimate can still be off from a noisy label. The paper's "at least 5 adjacent frames for smoothing" may mean the labels themselves were smoothed, but this is not explicit.
- Internet ground truth is γ times a manual pixel measure along the motion direction, so a pipeline that measures the same pixel extents should be close to exact. The ruler choice matters: for a car, "length" is bumper-to-bumper.
- The competition clips have up to 120 fps, while frame-sampling VLM pipelines typically see 16–32 frames. Timestamps should come from the dataset's `fps` column rather than the container: the ferrousowl repo reports wrong container fps on some full-resolution files (see Q4).
- After the 2026-10-11 rescoring, gains from memorising validation answers no longer count. Leaderboard values from before 2026-10-11 are not comparable with later ones.

### Gaps
- The paper does not say how the 568 test videos split across the four categories, or how many test QA pairs are lab, Blender or internet within each category. Only source totals are on the card.
- It is unclear whether lab "distance" priors are Z-depth or Euclidean range, and whether lab velocity labels use raw forward differences of single clicks or a smoothed fit.
- The issue texts on the GitHub repo (#5 and others) could not be read: GitHub API access was restricted in this session. Only the commit message for #5 was seen.

## Q2. Which baselines were reported, with per-category MRA, and did CoT, tools, prior handling or fine-tuning help?

### Takeaway
In the paper, the best model is GPT-5.1 at 53.1 MRA and humans score 55.6. Chain-of-thought hurt 19 of 21 models. Counterfactual priors cut MRA by about 70–80%, and removing the video changed scores little. No tool-augmented method is benchmarked in the paper; there is only a qualitative case where ChatGPT-5.1 Thinking used OpenCV-style boxes. The challenge leaders are at 0.85, far above every published number.

### Cited Findings
- Paper Table 1, MRA % as 2S / 2D / 3S / 3D / average. — [paper Table 1](https://arxiv.org/html/2512.19526v1)

| Model | 2S | 2D | 3S | 3D | Avg |
|---|---|---|---|---|---|
| ChatGPT-5.1 | 46.3 | 56.2 | 51.5 | 58.3 | 53.1 |
| Gemini-2.5 Pro | 44.8 | 57.5 | 42.4 | 53.7 | 49.6 |
| Gemini-2.5 Flash | 40.3 | 53.2 | 43.6 | 57.4 | 48.6 |
| Grok 4.1 Fast Reasoning | 39.4 | 49.5 | 42.4 | 48.6 | 45.0 |
| ChatGPT-5 | 36.6 | 35.0 | 25.9 | 33.1 | 32.6 |
| Claude Sonnet 4.5 | 19.6 | 23.0 | 19.6 | 29.1 | 22.8 |
| Qwen3-VL-32B | 35.8 | 51.6 | 43.2 | 53.4 | 46.0 |
| InternVL-3.5-30B | 36.7 | 45.4 | 38.6 | 42.0 | 40.7 |
| Qwen3-VL-8B | 26.0 | 47.8 | 35.1 | 46.3 | 38.8 |
| InternVL-3.5-8B | 27.3 | 41.8 | 34.4 | 38.3 | 35.4 |
| Molmo-7B | 30.0 | 43.1 | 24.4 | 36.6 | 33.5 |
| Phi-4-MM | 33.4 | 42.3 | 25.4 | 28.4 | 32.4 |
| Qwen3-VL-2B | 27.1 | 39.0 | 17.6 | 32.1 | 29.0 |
| SmolVLM | 31.6 | 34.4 | 20.0 | 27.8 | 28.5 |
| InternVL-3.5-2B | 25.0 | 31.1 | 16.6 | 27.4 | 25.0 |
| VILA-7B | 23.0 | 29.8 | 14.4 | 23.0 | 22.6 |
| CogVLM2-Video | 19.4 | 28.7 | 12.7 | 27.9 | 22.2 |
| Phi-3-Mini | 17.3 | 14.7 | 19.5 | 18.6 | 17.5 |
| LLaVA-13B | 14.4 | 22.1 | 8.0 | 16.5 | 15.2 |
| MiniCPM-V 4.5 | 27.6 | 26.3 | 0.4 | 0.0 | 13.6 |
| Fuyu-8B | 9.5 | 14.7 | 9.5 | 16.2 | 12.5 |
| Human | 50.0 | 59.1 | 55.2 | 57.9 | 55.6 |

- The human study had participants watch 18 videos and answer 1–3 questions each. The authors say the human score is not a ceiling: "an ideal agent with precise frame-level access to pixel coordinates could recover the world–pixel scale and compute target quantities exactly". — [paper §4.1–4.2](https://arxiv.org/html/2512.19526v1)
- Protocol:
  - Temperature 0–0.1. OpenAI models get up to 10,000 tokens, open models 500–2,048.
  - Each question is retried up to 5 times until the answer parses.
  - The paper's category scores average only **valid** answers. The challenge evaluator instead scores blanks and zeros as 0.
  - The prompt says "provide ONLY the numerical answer with units". — [paper §4.1, App. F](https://arxiv.org/html/2512.19526v1); [evaluator.py](https://github.com/Paulineli/QuantiPhy/blob/main/evaluator.py)
- Ablations on a 161-item 2D subset (paper Table 2). — [paper §5.2–5.3, Table 2](https://arxiv.org/html/2512.19526v1)
  - Video + prior vs prior only: ChatGPT-5.1 56.1 vs 39.0; Gemini-2.5 Pro 60.9 vs 46.1. Row assignment is inferred from the table order.
  - With counterfactual priors (the prior scaled by α ∈ {0.001 … 700}), "most models' MRA drops by 80%, and even the strongest model drops by 70%".
  - A four-step CoT chain (pixel source → scale → pixel target → world target) helped only 3 of 21 models, noticeably ChatGPT-5 and Fuyu-8B. It was worse for the other 19, "sometimes by a large margin".
- Scene context: complex backgrounds (C) score above simple (S) and plain (X) for most models. Multi-object scenes beat single-object scenes. — [paper §5.1](https://arxiv.org/html/2512.19526v1)
- Tool use appears only as a qualitative case. ChatGPT-5.1 Thinking used "OpenCV-style tools to obtain bounding boxes" and treated the long side (135 px) as the 5.67 m car length. Its width answer was 58/135 × 5.67 ≈ 2.44 m, close to ground truth.
  - The same model fails with counterfactual priors. It also outputs 9.8 m/s² for a Blender ball whose acceleration is about 1 m/s². — [paper App. A.1](https://arxiv.org/html/2512.19526v1)
- Code-as-World (arXiv:2608.27549) reran baselines on the **validation** set (2S / 2D / 3S / 3D / average): — [arXiv 2608.27549 Table 1](https://arxiv.org/html/2608.27549)

| Model | 2S | 2D | 3S | 3D | Avg |
|---|---|---|---|---|---|
| Gemini-3.1 Flash | 49.4 | 47.5 | 61.4 | 61.1 | 54.8 |
| ChatGPT-5.1 | 56.9 | 34.6 | 45.6 | 56.4 | 48.4 |
| Gemini-2.5 Pro | — | — | — | — | 46.4 |
| ChatGPT-5 Pro | — | — | — | — | 19.5 |
| Qwen3-VL-32B | — | — | — | — | 40.2 |
| Qwen3.5-4B | — | — | — | — | 31.2 |

### Inferences
- Tool-free VLM scores top out around 0.5–0.55. The challenge leaderboard's 0.80–0.85 (Q4) therefore implies that leading teams measure pixels and convert with explicit geometry, not end-to-end guessing. The user's own pipeline, at 0.79 with Claude Opus 5.5 and geometry, fits this.
- The paper finds models ignore counterfactual priors and leaned on world knowledge. So a strong "direct" VLM answer works partly as a plausibility prior. Where scenes are scaled or physics is altered (scaled ice cube, the ~1 m/s² ball, lunar motion), geometry must override that prior.

### Gaps
- There are no published per-category test-set scores for any tool-augmented or agentic method beyond the self-reported challenge entries in Q4.
- The PDF and HTML table numbering differ: the HTML calls the main table "Table 1" while the text says "Table 2". Cell values match. One ablation table cell was hard to attribute to a model from the HTML extraction, so the per-model ablation numbers above are partly inferred from row order.

## Q3. Which follow-up papers cite QuantiPhy, propose methods and report scores?

### Takeaway
The only published method that targets QuantiPhy directly is Code-as-World (MirroS-Lab, arXiv:2608.27549). Its fine-tuned Code-as-World-VL scores 0.554 (9B) and 0.586 (27B reasoning) on **validation**.
- On the official **test** set, the released 9B scores 0.544 when used alone (kuotunyu, see Q4).
- Other citing papers are diagnostics (NICE FACT, the blind-baseline paper) or general physics VLMs (OmniFysics-Nano-V2), with low QuantiPhy numbers.

### Cited Findings
- Semantic Scholar lists 23 citing papers as of 2026-10-11. The relevant ones are below. — [Semantic Scholar citations API](https://api.semanticscholar.org/graph/v1/paper/arXiv:2512.19526/citations?fields=title,year,externalIds)
- **Code as Worlds (arXiv:2608.27549, MirroS-Lab)**
  - Method: an agentic loop (propose → instantiate → execute → render → verify) builds executable simulated worlds. These worlds supervise VLM training. — [arXiv 2608.27549](https://arxiv.org/html/2608.27549)
  - Training is in two phases. — [arXiv 2608.27549 §5.2–5.4](https://arxiv.org/html/2608.27549)
    - SFT on pixel-space measurement questions. These are built from RefCOCO/+/g, RefCLEF boxes and GOT-10K tracks. The pixel targets use central-difference velocity (c_{t+1} − c_{t−1})/(2Δt) and second-difference acceleration.
    - GRPO on world-level VQA from text-driven and video-driven executable worlds.
    - All variants see 16 uniformly sampled frames.
  - Validation results (2S / 2D / 3S / 3D / average): — [arXiv 2608.27549 Table 1](https://arxiv.org/html/2608.27549)

    | Model | 2S | 2D | 3S | 3D | Avg |
    |---|---|---|---|---|---|
    | Code-as-World-VL-4B | 45.4 | 55.4 | 45.8 | 56.0 | 50.6 |
    | Code-as-World-VL-9B | 55.0 | 52.9 | 55.6 | 58.1 | 55.4 |
    | Code-as-World-VL-27B (reasoning) | 48.7 | 62.4 | 60.5 | 62.8 | 58.6 |

  - The 27B result was taken at training step 60 with one sample at temperature 1.0. It used no self-consistency, voting or tools. — [arXiv 2608.27549 App. B.5](https://arxiv.org/html/2608.27549)
  - Ablation (Table 4) on the 9B, starting from 50.9 with image-space training only:
    - adding text-driven worlds gives 52.5;
    - adding video-driven worlds gives 53.1;
    - adding both gives 55.4.
    - The text says "56.8", which is inconsistent with the table. — [arXiv 2608.27549 Table 4](https://arxiv.org/html/2608.27549)
  - Weights released: `MirroS-Lab/Code-as-World-VL-9B`, Apache-2.0, fine-tuned from Qwen3.5-9B. — [HF model](https://huggingface.co/MirroS-Lab/Code-as-World-VL-9B); [kuotunyu README](https://github.com/kuotunyu/quantiphy-geo-vlm)
- **NICE FACT (arXiv:2605.08452)**
  - This is a diagnostic paradigm, not a solver. FACT probes visual fidelity, physical-law use and temporal grounding. The authors annotate a timestamp-event subset of QuantiPhy for temporal grounding. NICE is a neighbourhood-informed confidence calibration.
  - It evaluates 6 open VLMs (Gemma3-12B, GLM-4.6V, InternVL3.5-8B, Molmo2-8B, Qwen3-Omni-30B, Qwen3-VL-8B) and finds they "fail to identify visual preconditions or utilize necessary physical laws".
  - Its appendix reports average MRA for excluded weak models: Phi-4 27.4, SmolVLM 26.5, Phi-3 17.5, LLaVA-13B 15.2. — [arXiv 2605.08452](https://arxiv.org/html/2605.08452)
- **One Perturbation Is Not Enough (arXiv:2609.06190)**
  - The authors argue that a counterfactual test with one prior scaling, as in QuantiPhy, cannot certify that a model uses its inputs. They derive "blind baseline" scores.
  - On their own test with three perturbations of physical-quantity-from-video, three VLMs score below their blind bound. They "default to one of a small set of round calibration values". — [arXiv 2609.06190](https://arxiv.org/html/2609.06190)
- **OmniFysics-Nano-V2 (arXiv:2609.25738)**
  - A compact omni-modal model trained with physics-aware SFT and two-stage GRPO.
  - It reports leading QuantiPhy among its compared small models, +6.42 over Qwen2.5-Omni-7B.
  - Its SFT ablation gives QuantiPhy 38.72 with full SFT vs 30.20 without physics data. Removing static-attribute data lowers QuantiPhy by 7.47. — [arXiv 2609.25738](https://arxiv.org/html/2609.25738)
- **Asking the World (arXiv:2609.39135)**
  - An agent that calibrates a simulated world from video (Warp-based "PolyWorld Engine", CEM system identification) and then probes it.
  - It is evaluated on CLEVRER, ContPhy and real scenes, not QuantiPhy. With Gemini-3-Flash it gets 80.82% on CLEVRER, +46.5 over direct Gemini-3-Flash. — [Semantic Scholar entry](https://www.semanticscholar.org/paper/5b21085d34d76ab3e0f507633dbc7670c828b62c)
- Other citing papers are benchmarks or position papers without QuantiPhy-improving methods: 4DCodeBench (2610.03715), PhysicsLENS (2610.01162), ChronoPhyBench (2606.07962), RetroHolmes (2607.11044), PhysPlan (2609.13006), and "Position: Video LLMs Must Not Ignore the Pixel Dynamics in Plain Sight". — [Semantic Scholar citations API](https://api.semanticscholar.org/graph/v1/paper/arXiv:2512.19526/citations?fields=title,year,externalIds)

### Inferences
- Fine-tuning alone gets a 9B open model to about the paper's GPT-5.1 level (0.54–0.55). That is far below the challenge leaders. Measurement pipelines matter more than model training here.
- Code-as-World's validation numbers are optimistic for the test set. The validation questions come from test videos (kuotunyu notes all 24 validation videos are in the test set, with 124 identical questions). The test score of 0.544 vs 0.554 on validation agrees with this.

### Gaps
- No paper reporting test-set scores above 0.6 was found.
- The Code-as-World 27B weights were not checked for public release. The HF/GitHub listing of MirroS-Lab was not browsed.

## Q4. What is public about the challenge leaders and other participants?

### Takeaway
No write-ups, papers, repos or posts were found for Perch AI, Cogworks RSI, Blindfolded, iMak AI Lab, Framewise Physics, JX intelligence or IIIXR Lab. Searches return nothing relevant.
- The public code comes from lower-ranked entries: three Track B repos (kuotunyu 0.577, Tangxiaoxiao1992 "QPM" 0.575, ferrousowl 0.603) and some starter repos.
- All three use a "measure in pixels, scale by prior" pipeline fused with VLM answers. Their consistent lesson: measured speed with a static size prior is reliable. Chains through a dynamic prior and 3D depth are where measurement helps least.

### Cited Findings
**Leaderboard snapshot**

The snapshot below is from 2026-10-11 18:41 UTC, after the validation-overlap rescoring. It was read from the page's public leaderboard RPC `get_public_leaderboard_snapshot`. — [competition page leaderboard](https://quantiphy.stanford.edu/competition/index.html)

Track A:

| Rank | Team | MRA |
|---|---|---|
| 1 | Perch AI | 0.8517 |
| 2 | Cogworks RSI | 0.8446 |
| 3 | Blindfolded | 0.8293 |
| 4 | iMak AI Lab | 0.8159 |
| 5 | Framewise Physics | 0.8083 |
| 6 | JX intelligence | 0.8069 |
| 7 | JX bati | 0.8065 |
| 8 | Quantum D | 0.8055 |
| 9 | Shao Tai Tai | 0.8053 |
| 10 | szerlok | 0.8018 |
| 11 | iLearn | 0.8014 |
| 12 | ferrousowl | 0.7982 |
| 13 | Quantumonster | 0.7941 |
| 14 | VihanAggarwal | 0.7921 |
| 15 | reasoning_wrt | 0.7920 |
| 16 | JX Intelligence | 0.7911 |
| 17 | dreads | 0.7897 |
| 18 | Quantum Dominators | 0.7835 |
| 19 | Actuarial Tutor | 0.7726 |
| 20 | solowithclaude | 0.7714 |

Track B:

| Rank | Team | MRA |
|---|---|---|
| 1 | IIIXR Lab | 0.8051 |
| 2 | JX intelligence | 0.7716 |
| 3 | Actuarial Tutor | 0.7617 |
| 4 | Rigidly Grounded | 0.7187 |
| 5 | Perch AI | 0.6837 |
| 6 | trustai | 0.6778 |
| 7 | Cookie | 0.6776 |
| 8 | I'mFromTaiwan | 0.6670 |
| 9 | LBWSquare | 0.6602 |
| 10 | LastNig | 0.6567 |
| 11 | Aing_Quantiphy | 0.6418 |
| 12 | Qol Şärif | 0.6381 |
| 13 | HelloWorld | 0.6365 |
| 14 | LGS | 0.6299 |
| 15 | OolongSTTH | 0.6285 |
| 16 | WaWa | 0.6275 |
| 17 | khoai_tay_chien | 0.6224 |
| 18 | Cliton | 0.6209 |
| 19 | Yameteshka | 0.6202 |
| 20 | Quantum D | 0.6122 |

- The leaderboard updates every 24 hours and "include[s] unverified submissions". — [competition page leaderboard](https://quantiphy.stanford.edu/competition/index.html)
- Scores before rescoring, as given in the assignment: Perch AI 0.8525, Cogworks RSI 0.8453, Blindfolded 0.8374, IIIXR Lab 0.8076. Comparing with the snapshot, Blindfolded fell 0.008 after the 140 validation-overlap questions were excluded, while Perch AI and Cogworks fell under 0.001. — [competition page notice](https://quantiphy.stanford.edu/competition/index.html)
- The "VihanAggarwal" Track A entry is this project's own team. The local repo's origin is github.com/VihanAggarwal/quantiphy-challenge, and its README is byte-identical. — [VihanAggarwal/quantiphy-challenge](https://github.com/VihanAggarwal/quantiphy-challenge)

**Rules relevant to disclosure**
- Track A requires code disclosure from the top 3 only. Track B requires it from all entries.
- The top 3 must publish a reproducibility package within 14 days of notification.
- Top teams will be invited to submit short technical summaries in November 2026.
- The workshop is on Saturday 12 Dec 2026 at ICC Sydney (winner talks; invited talks by Ranjay Krishna and Jiajun Wu). So the leaders' methods are likely to be published only after the deadline. — [competition page](https://quantiphy.stanford.edu/competition/index.html)
- Registration closed 2026-10-09. The deadline is 2026-10-23 23:59 AoE. The limit is 3 scored uploads per day. — [competition page](https://quantiphy.stanford.edu/competition/index.html)
- A search snippet said "submissions close 2026 · Nov 05", which conflicts with the live page's Oct 23. The page fetched on 2026-10-11 is authoritative, and the snippet is probably stale. — [search result for competition page](https://quantiphy.stanford.edu/competition/)
- Prizes: $1,000 / $500 / $250 per track, $3,500 in total. — [organizer post on X (snippet, unverified)](https://x.com/PuyinLi/status/2102862082542883050); [competition page](https://quantiphy.stanford.edu/competition/index.html)

**kuotunyu/quantiphy-geo-vlm (Track B, self-reported official test scores)**

The repo describes the steps as follows. — [kuotunyu README](https://github.com/kuotunyu/quantiphy-geo-vlm)
- Geometry:
  - OWLv2 text-query detection on up to 96 frames, linked into tracks.
  - 2D scale from the prior.
  - 3D: focal length calibrated so the prior matches the given depths, or about 64° HFOV when that fails (392 test questions).
- Qwen3-VL-8B checks each box from P(yes) at 3 frames. Answers route to a Qwen3-VL-8B or 32B VLM when the box check fails.
- `caw`: Code-as-World-VL-9B on every question, using the authors' recipe (16 frames, ≤262,144 px per frame, thinking off).
- `caw_geospeed`: caw, but with geometry answers on 708 speed questions.

Official test scores:

| Version | MRA | S2 | D2 | S3 | D3 |
|---|---|---|---|---|---|
| geometry_v1 | 0.516 | .507 | .522 | .563 | .472 |
| hybrid_v1 | 0.531 | .516 | .559 | .565 | .483 |
| hybrid_v2 | 0.542 | .524 | .584 | .569 | .490 |
| hybrid_v4 | 0.552 | .532 | .593 | .576 | .508 |
| caw (Code-as-World-VL-9B alone) | 0.544 | .479 | .584 | .553 | .562 |
| caw_geospeed | 0.577 | .545 | .594 | .601 | .567 |

- On validation, geometry scored 0.564 on speed questions against Qwen3-VL-8B's 0.336.
- On the test set, swapping in geometry for the speed questions added +0.033 over caw. — [kuotunyu README Notes](https://github.com/kuotunyu/quantiphy-geo-vlm)

**Tangxiaoxiao1992/quantiphy-qpm "QPM" (Track B, 0.575)**

Pipeline (all open weights, run locally): — [QPM README](https://github.com/Tangxiaoxiao1992/quantiphy-qpm)
- Background-subtraction tracks, with Qwen3-VL-8B grounding of which track is the prior or target.
- A geometric solver gives measurement m. A blind Qwen3.5-9B range gate drops implausible m.
- Direct answers: D = √(Code-as-World-VL-9B answer × Qwen3.5-9B thinking answer).
- Routing:
  - speed with a static prior → m;
  - speed with a dynamic prior → D;
  - everything else → √(m·D).
- Final J: 0.575 (S2 .524, D2 .602, S3 .580, D3 .594).

Measured test effects, in MRA points:

| Change | S2 | D2 | S3 | D3 |
|---|---|---|---|---|
| Ensemble vs Code-as-World alone | +0.1 | +0.6 | −0.3 | +3.6 |
| Raw speed measurement | +3.8 | −1.4 | +3.4 | −1.6 |
| Fused measurement on non-speed questions | +0.6 | +1.2 | −0.4 | −0.4 |

- "On validation our full fusion looked far better (+6.5 over CAW alone) than it is on the test set (≈+1)."
- Things that did not help on validation:
  - self-consistency;
  - longer thinking;
  - 27B Qwen3.6 or 3.8 as the answer model;
  - SAM2.1 tracks;
  - per-kind bias correction;
  - confidence-weighted fusion.

**ferrousowl/quantiphy-trackb**

The team "ferrousowl" is also 12th in Track A at 0.7982. The Track A method is not public. — [ferrousowl README](https://github.com/ferrousowl/quantiphy-trackb); [leaderboard](https://quantiphy.stanford.edu/competition/index.html)
- Track B uses Qwen3.5 35B MoE (Q4_K_M, Ollama) on one 16 GB GPU. Official test MRA is 60.3, against 65.5 on validation, which they tuned on.
- Pipeline:
  - Rule-based parsing of question, prior and depth.
  - VLM grounding in the full frame, then in a zoomed crop.
  - Median-background tracking seeded at VLM anchor frames.
  - 3D uses a pinhole model. Focal length comes from the reference object at its stated distance, else the lab camera spec (80° HFOV) or the Blender default lens.
  - Local polynomial fits produce speed and tangential or vector acceleration. They "follow the benchmark's ground-truth conventions: backward differences in simulations and forward differences in lab recordings".
  - Identical questions across renders or releases of the same scene are pooled with a log-median.
  - Combination: measured values for speed and acceleration, the geometric mean of measured and direct for sizes, and direct for inter-object distances. A video's measurements are dropped when the median measured/direct ratio is beyond 2×.
  - "Time stamps use the template's fps column, because some full-resolution files carry a wrong container fps."
  - Depth-Anything-V2-Small fills in 3D objects without a stated distance.

**prarabdhmisra/quantiphy (team "Vector Syndicate")**
- A geometric-solver plan that is "verified on synthetic fixtures only". Notes from the README: — [prarabdhmisra README](https://github.com/prarabdhmisra/quantiphy)
  - "Overshooting is fatal, undershooting is cheap" (pred ≥ 1.9× scores 0; 0.5× scores 0.4).
  - 25% of GPT-5.1's validation rows score exactly 0, and 57% of those are overshoots.
  - Aggregate in log space.
  - In-sample shrinkage calibration on validation overfit (0.493 in-sample vs 0.463 leave-one-out).
  - The validation 95% CI is about ±5.7 points.
  - The paper's A.2 threshold set is a typo.

**Other repos**
- OxyzGiaHuy/quantiphy: a Qwen2.5-VL-3B baseline that plans agentic measurement. No scores. — [OxyzGiaHuy README](https://github.com/OxyzGiaHuy/quantiphy)
- khufia/QuantiPhy and khang1108/neurips-quantiphy: copies of the official README. — [GitHub search](https://github.com/search?q=quantiphy&type=repositories)

**Searches for top teams**
- WebSearch for "Perch AI" + QuantiPhy, and for "Cogworks"/"Blindfolded"/"IIIXR" + QuantiPhy, returned nothing relevant. — [web search results]

### Inferences
- Open-weight measurement pipelines with 8–35B models land at 0.55–0.60 on test. IIIXR Lab's 0.805 in Track B and JX intelligence's 0.772 therefore suggest much stronger open components or much better geometry/convention matching. Candidates are large open VLMs (Qwen3.5/3.6 large MoE) and point trackers. This is speculative, since no write-ups exist.
- Perch AI is 1st in Track A (0.852) and only 5th in Track B (0.684). Its Track A edge most likely comes from a closed frontier model, not from geometry alone.
- The public entries agree on these points:
  - Speed from a static size prior is where pixel measurement clearly wins.
  - Dynamic priors compound two measurement errors.
  - 3D needs a depth or focal estimate and gains least from geometry.
  - Validation tuning overstates gains by about 5 points.

### Gaps
- No public information was found on the methods of Perch AI, Cogworks RSI, Blindfolded, iMak AI Lab, Framewise Physics, JX intelligence/JX bati, IIIXR Lab or Rigidly Grounded.
- The Discord #quantiphy channel and LinkedIn were not accessible to search.
- Per-category scores for leaderboard teams are not public. The widget shows only the overall MRA.

## Q5. Related quantitative video-measurement benchmarks and what tops them

### Takeaway
QuantiPhy borrows MRA from VSI-Bench (static indoor spatial measurement). Close relatives are STI-Bench (numeric velocity and acceleration), IRIS and PhysicsMind (real or simulated mechanics) and VSI-Super / Cambrian-S. Methods that help on those benchmarks follow two patterns: tool or expert-model agents (such as ViSRA) and spatial fine-tuning (Cambrian-S, ViCA2, Spatial-MLLM). No leaderboard snapshot found for this run shows a clear 2026 state of the art on metric distance or size.

### Cited Findings
- VSI-Bench ("Thinking in Space", Yang et al., CVPR 2025) introduced MRA for numerical spatial answers (distance, size, room size) on about 290 indoor videos with more than 5,000 QA pairs. QuantiPhy says it "follow[s] VSI-Bench" in using MRA. — [VSI-Bench arXiv 2412.14171](https://arxiv.org/pdf/2412.14171); [QuantiPhy §4.1](https://arxiv.org/html/2512.19526v1)
- QuantiPhy cites Cambrian-S / VSI-Super (arXiv 2511.04670) as showing that VLMs with numerical spatial understanding can help embodied AI. — [QuantiPhy §2.1](https://arxiv.org/html/2512.19526v1)
- ViSRA (May 2026) is a training-free video spatial reasoning agent that uses explicit spatial information from expert models, evaluated on VSI-Bench. Its per-task numbers were not seen. — [ViSRA on alphaXiv](https://www.alphaxiv.org/abs/2605.10106)
- ViCA2-7B reports 56.8 average on VSI-Bench (2025). This is unverified beyond the search snippet. — [search summary citing alphaxiv 2505.12312](https://alphaxiv.org/overview/2505.12312v4)
- A survey names STI-Bench as one of few benchmarks that require numerical velocity and acceleration estimates from video. OmniSpatial asks only qualitative speed questions. — [arXiv 2509.18905](https://arxiv.org/pdf/2509.18905)
- IRIS (real-world inverse recovery of physical dynamics from monocular video, arXiv 2603.16432) and PhysicsMind (sim and real mechanics, arXiv 2601.16007) are cited next to QuantiPhy as related quantitative probes. — [arXiv 2609.06190 references](https://arxiv.org/html/2609.06190)
- "PhysVista" (NeurIPS 2026) is reported to show frontier VLMs at 18–43% on physical scale estimation. This comes from a secondary blog only and is unverified. — [aiweekly blog](https://aiweekly.co/editors-blog/found-first-neurips-2026-physvista-finds-frontier-vlms-score-18-43-on-physical)
- PhysBench: GPT-4o and Gemini-1.5 Pro score about 60% against about 95% for humans. It is multiple-choice and qualitative. — [QuantiPhy §2.2](https://arxiv.org/html/2512.19526v1)

### Inferences
- The methods that transfer from spatial benchmarks are expert-tool agents and measurement-supervised fine-tuning. The QuantiPhy-specific evidence (Q2–Q4) shows explicit pixel measurement plus prior scaling beats both pure fine-tuning (Code-as-World, about 0.54 on test) and CoT prompting.

### Gaps
- No current (October 2026) leaderboard was found for VSI-Bench, STI-Bench or SpatialScore with per-task MRA on absolute distance or size. SpatialScore was not researched in this run.
- PhysVista's primary paper was not located.
