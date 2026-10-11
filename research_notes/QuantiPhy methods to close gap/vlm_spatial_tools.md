# Making VLMs better at quantitative spatial and physical measurement: tools, prompting, test-time scaling, fine-tuned models (as of Oct 2026)

Scope note: the papers were read as full text (arXiv PDFs pulled with curl and converted with pdftotext). WebFetch could not resolve arxiv.org or quantiphy.stanford.edu from this sandbox. Every number below comes from the paper's own tables or text unless it is marked as an inference. Context: our pipeline (README) already scores 0.793 MRA on the QuantiPhy test set, and the published numbers below are far lower. The literature is therefore most useful for what it says about mechanisms (what helps and what hurts), not as a ceiling.

## 1. Tool-augmented / program-aided VLM agents for spatial measurement

### Takeaway
Agents that measure in code with geometry tools beat end-to-end VLMs on metric questions by large margins, but only when perception is good. With ground-truth perception the gains are huge (tens of MRA points). With realistic depth, detection and reconstruction the gains shrink to a few points or turn negative on some subtasks. Perception quality (localising the right pixels or boxes) is the bottleneck, not program logic. This matches QuantiPhy's own claim: an agent with exact pixel access "could recover the world–pixel scale and compute target quantities exactly".

### Cited Findings
- **VADAR (CVPR 2025, training-free, GPT-4o agents write a dynamic Python API).** Tools: Molmo pointing, GroundingDINO, SAM, UniDepth metric depth. Omni3D-Bench total: VADAR 40.4 vs GPT-4o 42.9, Claude 3.5 Sonnet 32.2, ViperGPT 26.7, VisProg 13.5. On "numeric (other)" floating-point answers, scored with MRA, VADAR gets 35.5 vs GPT-4o 35.5 vs Claude 3.5 Sonnet 20.6. So the program agent ties GPT-4o on metric answers and does not beat it — [VADAR, arXiv 2502.06787](https://arxiv.org/abs/2502.06787)
- With oracle vision specialists, VADAR reaches 94.4% on an Omni3D-Bench subset (numeric-other MRA 82.3) vs GPT-4o 53.7 and Claude 3.5 Sonnet 59.3. The authors conclude that "its main limitation is the vision specialists' performance" — [VADAR](https://arxiv.org/abs/2502.06787)
- **pySpatial (ICLR 2026).** GPT-4o or GPT-4.1-mini writes code against 3D reconstruction, camera pose and novel-view rendering tools. Omni3D-Bench total 44.2 vs VADAR 40.4 vs GPT-4o 42.9; numeric-other MRA 38.6 vs 35.5 for VADAR and for GPT-4o, a gain of about 3 MRA points. On MindCube it beats GPT-4.1-mini by 12.94% — [pySpatial, arXiv 2603.00905](https://arxiv.org/abs/2603.00905)
- **SpatialAgent** (in the SpatialScore paper) has 12 open tools: Rex-Omni detection, SAM2, DetAny3D, RAFT optical flow, VGGT camera intrinsics and extrinsics, SIFT homography, Depth-Anything-V2 metric depth, OrientAnything, MapAnything. It runs in Plan-Execute or ReAct style. On SpatialScore with Qwen3-VL-8B as the core, overall accuracy goes from 45.48 (zero-shot) to 52.75 (PE) and 53.81 (ReAct). Obj-Dist goes from 37.22 to 43.57 and 43.67; Obj-Size from 52.12 to 58.72 and 56.52; Obj-Motion from 55.90 to 61.45 and 60.96. SFT on their corpus gives similar overall gains (+9.23) but causes forgetting on some tasks — [SpatialScore, arXiv 2505.17012](https://arxiv.org/abs/2505.17012)
- In the same table, few-shot in-context examples alone help. Qwen3-VL-8B goes from 45.48 zero-shot to 49.00 four-shot, and Obj-Size from 52.12 to 56.76. Qwen3-VL-4B goes from 42.52 to 46.59, with Obj-Dist moving from 33.40 to 38.19 — [SpatialScore](https://arxiv.org/abs/2505.17012)
- **RieMind** gives an LLM agent geometry tools over a 3D scene graph built from ground-truth annotations, so it is an upper bound under ideal perception. On VSI-Bench with GPT-4o: Absolute Distance 5.3 → 93.2, Object Size 43.8 → 96.5, Room Size 38.2 → 83.5, average 35.3 → 85.2 — [RieMind, arXiv 2603.15386](https://arxiv.org/abs/2603.15386)
- **GraFT** (training-free; symbolic size and distance tools over a 3D scene graph, plus a BEV render) on VSI-Bench metric subtasks with GPT-o3:
  - Raw video: AbsDist 40.6, ObjSize 70.0, RoomSize 51.4.
  - Ground-truth perception: AbsDist 97.5, ObjSize 99.5.
  - Realistic perception: AbsDist 43.2, ObjSize 66.5 (down), RoomSize 83.4.
  - With realistic perception, the average over the 5 metric subtasks moves only from 53.2 to 58.0.
  - [GraFT, arXiv 2609.03892](https://arxiv.org/abs/2609.03892)
- **AlloSpatial / World2Mind** is a training-free harness that adds an allocentric map tool through prompting. On VSI-Bench-tiny, overall scores:
  - Claude-4.6-Opus: 38.4 → 56.0 (+17.7).
  - GPT-5.2: 46.7 → 54.0 (+7.3).
  - Gemini-3-Pro: 55.2 → 61.0 (+5.8).
  - Per-task deltas, assuming the column order of their Table 2 (Count, AbsDist, ObjSize, RoomSize, ...):
    - Claude: AbsDist +15.8, ObjSize +5.2, RoomSize +28.0.
    - GPT-5.2: AbsDist −1.5, ObjSize −4.2.
    - Gemini-3-Pro: ObjSize −13.5.
  - The authors say gains concentrate on allocentric tasks, and "tasks solvable from local visual evidence show smaller or occasionally negative changes".
  - [AlloSpatial, arXiv 2606.08952](https://arxiv.org/abs/2606.08952)
- **Skill-3D:** existing tool agents "often misuse tools and exhibit biased tool preferences", giving "only marginal gains over non-agentic strategies". Learned scene-aware skills raise correct tool use from 39% to 78% on VSI-Bench. Absolute distance needs depth evidence, but agents default to detection and reconstruction tools — [Skill-3D, arXiv 2606.07436](https://arxiv.org/abs/2606.07436)
- **Think3D** (GPT-4.1 and Gemini 2.5 Pro with point-cloud viewpoint tools) on VSI-Bench-tiny: GPT-4.1 relative distance 43.30 → 46.00, Gemini 50.67 → 54.00. The paper reports no absolute metric tasks. An open 4B model *drops* with tools (rel. dist 35.33 → 29.33) — [Think3D, arXiv 2601.13029](https://arxiv.org/abs/2601.13029)
- **QuantiPhy follow-up "Code-as-World".** Agents build executable physics worlds (propose → execute → render → verify). These are used only to generate training data for a VLM. The trained model's reasoning trace does "Image-Space measurement" and then "World-Space calibration" (pixel extent → scale γ = prior / pixel → answer), which is the same structure as a geometry-in-code pipeline — [Code-as-World, arXiv 2608.27549](https://arxiv.org/abs/2608.27549)
- In Code-as-World's pixel-measurement evaluation, open VLMs are weak at measuring pixel motion in video. On GOT-10K extent+motion MRA: Qwen3-VL-32B 15.8, Qwen3.5-27B 6.1, and their trained 9B model 26.6. On static referring-expression extents (RefCOCO etc.) the same models score 30–68 — [Code-as-World](https://arxiv.org/abs/2608.27549)

### Inferences
- For QuantiPhy specifically, the right decomposition is already known: the VLM localises (points, boxes, endpoints), and code does the metric conversion and finite differences. The literature's biggest gains (RieMind, GraFT-GT, VADAR-oracle) all come from that pattern. Their realistic-perception results show that the remaining error is localisation and tracking error, not arithmetic. Spend effort on verifying and refining the pixel annotations: zoom crops, re-pointing, optical-flow tracking, consistency across frames. Open-ended agent loops are a weaker use of effort.
- Frontier-model agent loops do not dominate direct answers on metric subtasks. Both AlloSpatial (GPT-5.2 and Gemini on AbsDist and ObjSize) and GraFT (o3 ObjSize 70.0 → 66.5) show regressions. This matches our own result: the agentic loop scored 0.743 on validation vs 0.782 for single-call high effort (README). A per-category or per-source router that picks geometry vs direct is supported by the literature.
- Claude benefits most from structure. Claude-4.6-Opus gained +17.7 with AlloSpatial vs +5.8 to +7.3 for GPT and Gemini, and its baseline was the weakest. Claude-specific scaffolding is likely worth more than it would be for GPT.

### Gaps
- No paper reports a tool-augmented frontier agent evaluated on QuantiPhy itself. Code-as-World uses agents only for data generation.
- I found no reported numbers for "Thinking with images"-style zoom/crop tools on metric (MRA) tasks. Those papers (DeepEyes, V-Thinker, etc.) report on fine-grained perception or MCQ benchmarks. I did not read TACO or Visual Sketchpad in full; Sketchpad's depth-tool gains are on CV-Bench MCQ, not metric outputs, as far as I know.

## 2. Training-free prompting that improves metric estimates

### Takeaway
Reference-object prompting is the one technique with large, replicated gains on metric distance and size (Q-Spatial: +2 to +47 points δ≤2 success). The gain is smallest for the strongest model (GPT-4o +2). Generic CoT is unreliable to harmful for metric tasks: it hurts 19 of 21 models on QuantiPhy, and costs 8–21% on VSI-Bench size tasks. Set-of-Mark visual marks hurt GPT-4V on most SpatialRGPT-Bench metric items. Cognitive maps help relative distance (+10) but are untested on absolute metric.

### Cited Findings
- **SpatialPrompt on Q-Spatial Bench** (δ≤2 success rate, ScanNet / Q-Spatial++ splits):

  | Model | Standard | Zero-shot CoT | SpatialPrompt |
  |---|---|---|---|
  | GPT-4o | 69.41 / 61.06 | 70.2 / 59.74 | 71.96 / 62.71 |
  | GPT-4V | 28.24 / 18.81 | 56.47 / 46.53 | 54.9 / 53.47 |
  | Gemini 1.5 Pro | 0.59 / 0.99 | 2.94 / 4.16 | 53.65 / 43.17 |
  | Gemini 1.5 Flash | 20 / 26.73 | 18.53 / 26.11 | 52.71 / 38.42 |

  — [Liao et al., EMNLP 2024, arXiv 2409.09788](https://arxiv.org/abs/2409.09788). The near-zero Gemini 1.5 Pro standard-prompt number suggests refusals or format failures, so part of the "gain" is getting an answer at all.
- SpatialPrompt-Single wording: "Let's think step by step and start by finding good reference objects or object parts in the image." SpatialPrompt-Steps:
  1. Analyze the question.
  2. Identify up to 10 reference scales in the image, ranging from large to small sizes.
  3. Propose a step-by-step plan using the reference scales.
  4. Focus on the image and follow the plan.

  Gemini follows Steps better; GPT-4V is fine with Single — [Liao et al.](https://arxiv.org/abs/2409.09788)
- GPT-4o used a reference object in only 23.4% of responses. When it did, success was 83% (45/54) vs 64% without. A logistic regression controlling for split and GT distance gives about 2.7× odds of success with a reference (p<0.05). The correlation between reference use and success across models is ρ=0.69 / 0.61 — [Liao et al.](https://arxiv.org/abs/2409.09788)
- **QuantiPhy 4-step CoT** (pixel source property → pixel/world scale → pixel target property → world target), queried sequentially. It improved only 3 of 21 models (ChatGPT-5 rose from 34.2 to 53.7 on the 161-item 2D subset). It hurt 19, e.g. ChatGPT-5.1 from 56.1 to 27.7 and Gemini 2.5 Flash from 49.8 to 22.4. The authors say it "mainly amplifies and propagates early errors" because models cannot solve the intermediate numeric subproblems (pixel measurement) — [QuantiPhy, arXiv 2512.19526](https://arxiv.org/abs/2512.19526)
- **VSI-Bench (Thinking in Space):**
  - Zero-shot CoT and Tree-of-Thoughts cut Gemini-1.5 Pro's average by about 4%.
  - Self-consistency (5 runs at T=1.0, majority) was −1.1% vs baseline.
  - Room-size and object-size tasks "suffer a large 8% to 21% decrease"; absolute distance improved slightly.
  - "Linguistic prompting techniques ... are harmful for spatial reasoning."
  - [Yang et al., arXiv 2412.14171](https://arxiv.org/abs/2412.14171)
- **Cognitive-map prompting** (VSI-Bench): having Gemini-1.5 Pro first output object centres on a 10×10 grid raised relative-distance accuracy from 46.0 to 56.0. A ground-truth map gives 66.0 (78.0 at 20×20). Map accuracy is 64% for adjacent objects and drops sharply with distance ("local world models") — [Yang et al.](https://arxiv.org/abs/2412.14171)
- **Set-of-Mark on SpatialRGPT-Bench** (success % / abs. relative error), GPT-4V → GPT-4V+SoM:
  - Direct distance: 29.7/0.92 → 25.7/1.02.
  - Horizontal distance: 25.4/2.75 → 22.1/2.36.
  - Width: 51.1/0.37 → 45.8/0.70.
  - Height: 68.4/1.57 → 62.4/1.08.
  - Direction: 43.9 → 54.2.

  SoM helps direction but hurts most metric success rates. For LLaVA-34B, SoM collapses performance — [SpatialRGPT, arXiv 2406.01584](https://arxiv.org/abs/2406.01584)
- **QuantiPhy scene context:** scenes with multiple objects give consistently higher MRA than single-object scenes ("extra reference targets ... implicit comparison standards"). Visually complex backgrounds often score *higher* than simple-texture ones (tiles, windows and road markings act as scale cues) — [QuantiPhy](https://arxiv.org/abs/2512.19526)
- **Prior faithfulness (QuantiPhy):** prior-only (no video) MRA is close to video+prior for strong models. Under counterfactual priors (×0.001 to ×700), most models lose about 80% of their MRA and the best loses 70%. "VLMs (mostly) do not reason but memorize" — [QuantiPhy](https://arxiv.org/abs/2512.19526)
- **Equivariance follow-up:** rescaling every world quantity by α should multiply the answer by α. The median response slope s is 0.69–0.94 across 8 models; Claude-Sonnet-4.5 is at 0.86. A slope near 0.7 means a 10× scale change moves the answer about 5×.
  - Slope is lowest on in-the-wild internet clips (pooled median 0.42) and highest on background-removed renders (0.93).
  - On questions that give a speed or acceleration and ask for a size, 6 of 8 models have slope below 0.4. Slopes are lower still when the reference is an acceleration.
  - Their system prompt explicitly says: "Always trust the reference values you are given, even when they differ from typical real-world magnitudes."
  - [Tan et al., arXiv 2609.00658](https://arxiv.org/abs/2609.00658)
- **Reported MRA conflicts for Claude Sonnet 4.5 on QuantiPhy:** 22.8 MRA on the test benchmark in the QuantiPhy paper ([QuantiPhy](https://arxiv.org/abs/2512.19526)) vs 50.2 MRA on the 159-question validation set with the equivariance paper's prompt and parsing ([Tan et al.](https://arxiv.org/abs/2609.00658)). Different splits and protocols, but the 2× gap suggests the prompt and parsing protocol alone can swing Claude by tens of points.

### Inferences
- For a pipeline where Claude produces pixel annotations and code converts them, generic "think step by step" decomposition is not the lever. QuantiPhy shows CoT hurts because VLMs cannot do the pixel subproblems, and code already does the arithmetic.
- What transfers is reference-scale prompting. Ask Claude to list several scene objects with known sizes (tiles, doors, wheels, people, lane markings) and use them to cross-check the given prior's implied scale. This helps most on 3D or in-the-wild clips and on dynamic-prior→size questions, where the slope data shows models ignore the supplied scale most.
- For the "direct estimate" branch, the equivariance data argues for adding the explicit "trust the reference values even if atypical" instruction. Also flag disagreement between the direct answer and the geometry answer as a signal of prior-dominated guessing, not as a reason to average.
- Cognitive maps (top-down grids) are only shown to help relative judgements. For 3D depth-varying motion they might help Claude reason about depth ordering, but there is no metric evidence.

### Gaps
- No study found tests SpatialPrompt-style reference prompting on video kinematics (speed, acceleration) or on Claude models.
- No published ablation of visual marks (drawn boxes or rulers overlaid on frames) on QuantiPhy-style metric questions with frontier models. The SpatialRGPT-Bench SoM data is GPT-4V era.

## 3. Test-time scaling: self-consistency, median aggregation, best-of-N, ensembles for numeric output

### Takeaway
There is little direct evidence that sampling more and aggregating improves metric spatial estimates for frontier VLMs. VSI-Bench self-consistency (majority of 5) was slightly negative. The one label-free test-time correction tried on QuantiPhy-style data (equivariance-based rescaling) *lowered* accuracy by 4.7 MRA. Test-time scaling methods with positive results (MindJourney, CoV, Think3D) are about gathering new views, not resampling answers, and their benchmarks are MCQ or EQA rather than metric.

### Cited Findings
- **Self-consistency on VSI-Bench:** 5 runs at T=1.0, majority consensus, Gemini-1.5 Pro → −1.1% average vs no prompting — [Thinking in Space](https://arxiv.org/abs/2412.14171)
- **Equivariance test-time correction.** The method queries a frozen model at several prior scales α, fits ŷ(α)=c·α^s, and reads off the corrected ratio.
  - Applied to every question, it lowers accuracy by 4.7 MRA vs a single direct query, "because the variance of the estimate grows as 1/s²".
  - Restricting it to high-slope questions reduces the loss to −0.2 MRA with no gain.
  - In training, using a 5-scale probe grid with a median in log space ("robust to occasional responses with a wrong format or magnitude") was slightly worse than one query (MRA 30.0 → 28.0, CI includes 0).
  - [Tan et al.](https://arxiv.org/abs/2609.00658)
- **QuantiPhy's own protocol** re-queries up to 5 times only to get a parseable number, not for aggregation — [QuantiPhy](https://arxiv.org/abs/2512.19526)
- MindJourney (world-model video diffusion to imagine new views) gives +7.7% average on SAT (MCQ) — [MindJourney, arXiv 2507.12508](https://arxiv.org/abs/2507.12508)
- Chain-of-View (active view selection) gives +11.56% LLM-Match on OpenEQA, and +2.51% more with a bigger action budget — [CoV, arXiv 2601.05172](https://arxiv.org/abs/2601.05172)
- A crowd of 12 LLMs was statistically indistinguishable from 925 human forecasters on 31 binary questions. This is evidence for model ensembling in general, but the task is binary probability, not metric estimation — [Schoenegger et al., arXiv 2402.19379](https://arxiv.org/abs/2402.19379)

### Inferences
- MRA rewards being within 5–10% relative error, and the scoring is in log-ratio terms. When samples are independent and unbiased in log space, the median of N direct estimates should reduce variance. However, the QuantiPhy and equivariance results show the dominant error is *bias* toward typical magnitudes (slope < 1), which resampling the same model does not remove.
- Ensembling is therefore most likely to pay off where samples are diverse and the error is variance-like. Examples: repeated *pixel annotation* runs (median endpoint positions or median per-frame tracks), or cross-model ensembles (Claude + GPT) on 3D non-lab direct answers. It is less likely to pay off on prior-dominated guesses.
- Our own paid ensemble (median of extra Claude runs on 123 3D non-lab videos, task #24) is the best evidence available for this exact setup.
- With about $60 Claude and $34 OpenAI left, a cheap check: compute MRA on validation for 1 vs 3 vs 5 Claude samples (Batch API), median vs geometric mean, before spending on the test set.

### Gaps
- No paper found measures median-of-N or best-of-N with verifiers on a metric spatial or kinematic benchmark for GPT-5.x, Gemini 3.x or Claude 4.x.
- No published study of cross-model (Claude+GPT+Gemini) ensembles on QuantiPhy or VSI-Bench numeric tasks.

## 4. Video physical reasoning benchmarks and what scores best on quantitative kinematics

### Takeaway
QuantiPhy is the main quantitative kinematics benchmark. Published scores are about 50–59 MRA, versus 55.6 for humans. The best published result is a fine-tuned 27B model trained on simulated "executable worlds" at 58.6 MRA on validation. VLMs are poor at verbalising speed: driving-VLM probes show speed is internally encoded far better than it is verbally reported. What helps is converting the problem to pixel measurement plus calibration, either through training (Code-as-World, EquiSD) or code.

### Cited Findings
- **QuantiPhy test-set leaderboard** (MRA: 2S / 2D / 3S / 3D / avg):
  - ChatGPT-5.1: 46.3 / 56.2 / 51.5 / 58.3 / 53.1
  - Gemini-2.5 Pro: 49.6
  - Gemini-2.5 Flash: 48.6
  - Grok 4.1: 45.0
  - ChatGPT-5: 32.6
  - Claude Sonnet 4.5: 22.8
  - Qwen3-VL-32B: 46.0 (best open-weight)
  - Human: 50.0 / 59.1 / 55.2 / 57.9 / 55.6

  — [QuantiPhy, arXiv 2512.19526](https://arxiv.org/abs/2512.19526)
- QuantiPhy scaling is most pronounced on dynamic categories. Qwen3-VL goes 29.0 (2B) → 38.8 (8B) → 46.0 (32B) — [QuantiPhy](https://arxiv.org/abs/2512.19526)
- **On QuantiPhy-validation** (159 questions; Code-as-World Table 1):
  - Gemini-3.1 Flash: 54.8
  - ChatGPT-5.1: 48.4
  - Gemini-2.5 Pro: 46.4
  - Code-as-World-VL-9B: 55.4 (direct answers)
  - Code-as-World-VL-27B (reasoning): 58.6 (48.7 / 62.4 / 60.5 / 62.8)
  - ChatGPT-5 Pro: 19.5 (very low)

  — [Code-as-World, arXiv 2608.27549](https://arxiv.org/abs/2608.27549)
- EquiSD (label-free scale-equivariance self-distillation, 3B model trained only on synthetic video) raises QuantiPhy-validation from 17.1 to 23.4 MRA. That is 93% of the gain from exact simulator labels (23.9) — [Tan et al., arXiv 2609.00658](https://arxiv.org/abs/2609.00658)
- **Equivariance-paper validation numbers at nominal scale:**
  - Gemini-3.1-Flash-Lite: 52.6
  - Claude-Sonnet-4.5: 50.2
  - GLM-4.6V: 45.4
  - Qwen3-VL-235B: 43.5
  - GPT-5.1: 42.0
  - Gemini-2.5-Flash: 29.5

  — [Tan et al.](https://arxiv.org/abs/2609.00658)
- **Speed from driving video (nuScenes, open-weight VLMs):** linear probes recover ego speed at 4.7–5.8 km/h MAE vs 10.2–16.8 km/h MAE for verbal outputs. Multiple frames give "inconsistent verbal gains" over a single frame, and "frame order is rarely exploited"; surrounding-agent speed is weakly encoded — [Speed in the Blind Spot, arXiv 2609.37046](https://arxiv.org/abs/2609.37046)
- In a scale-free (ratio) form, Gemini-2.5-Flash and Qwen3-VL-8B match closed-form physical scaling laws on 86% and 84% of items. When the same answer must be given in metres, they change it by >10% on 95% and 77% of zero-exponent items. "The two models thus know the relevant law but do not apply it when the answer must be a metric quantity" — [Tan et al.](https://arxiv.org/abs/2609.00658)
- The QuantiPhy competition is a NeurIPS 2026 competition with an open-weight track. A search snippet of the official page says submission closes 2026-11-05 AoE, which conflicts with the 2026-10-23 deadline in our README. The site was unreachable from this sandbox, so this was not verified — [NeurIPS 2026 competitions blog](https://blog.neurips.cc/2026/07/28/neurips-2026-competitions-announced/); [competition page](https://quantiphy.stanford.edu/competition/)

### Inferences
- All published end-to-end results (≤ 58.6 MRA on validation) are far below our 0.76–0.79 test MRA. Pixel measurement plus code calibration (our approach) already captures what the best papers try to teach models. The top public leaderboard teams (0.85) are most likely doing the same with better localisation and tracking, or better handling of 3D depth.
- VLMs (including Claude) should not be asked for speed or acceleration directly when pixel tracks are available. The verbal-readout gap and the frame-order insensitivity both argue for tracker or optical-flow based kinematics, with the VLM used only to identify targets and time windows.
- Acceleration-reference questions have the lowest prior faithfulness. Geometry should dominate there; avoid blending in the direct answer.

### Gaps
- I did not read PhysBench, Physion, PhyX or other video-physics benchmarks in detail. They are largely MCQ or qualitative and have no kinematic MRA numbers comparable to QuantiPhy.
- No public write-up of the QuantiPhy competition's top Track A methods was found.

## 5. Fine-tuned spatial VLMs vs frontier models on quantitative distance and size

### Takeaway
Spatial fine-tunes (SpatialRGPT, SD-VLM, VLM-3R, Spatial-MLLM, SpatialAgent-SFT) beat older frontier models (GPT-4V/4o) on in-domain metric benchmarks, sometimes by large margins. Absolute accuracy stays modest: about 33–56% δ≤2 success, or about 35–50 MRA on absolute distance. Newer frontier models plus tools close most of the gap. None of these models is evaluated on video kinematics, and they would not slot into a Claude API pipeline except as an extra Track B or ensemble voter.

### Cited Findings
- **SpatialRGPT-Bench quantitative** (success % / abs. rel. error):
  - SpatialRGPT-VILA-1.5-8B: direct distance 45.9/0.31, width 48.9/0.28, height 61.7/0.41.
  - GPT-4V: 29.7/0.92, 51.1/0.37, 68.4/1.57.

  Fine-tuning mainly reduces relative error, while success on width and height is similar — [SpatialRGPT, arXiv 2406.01584](https://arxiv.org/abs/2406.01584)
- **SD-VLM** (LLaVA-1.5-7B + depth positional encoding, trained on 700K MSMU QA). δ≤2 success on Q-Spatial++ / SpatialRGPT-Bench (quan.):

  | Model | Q-Spatial++ | SpatialRGPT-Bench (quan.) |
  |---|---|---|
  | SD-VLM | 56.2 | 33.3 |
  | GPT-4o | 52.0 | 13.0 |
  | Gemini-2 | 51.0 | 23.0 |
  | InternVL-3-78B | 53.6 | 23.5 |
  | SpatialRGPT | 43.5 | 28.7 |
  | SpatialBot | 33.7 | 13.2 |

  Feeding depth "as image" *hurt* MSMU-Bench (46.73 → 22.64); depth "as prompt" helped slightly (48.78) — [SD-VLM, arXiv 2509.17664](https://arxiv.org/abs/2509.17664)
- **VSI-Bench** (MRA: Count / AbsDist / ObjSize / RoomSize):

  | Model | Count | AbsDist | ObjSize | RoomSize | Avg |
  |---|---|---|---|---|---|
  | VLM-3R-7B | 70.2 | 49.4 | 69.2 | 67.1 | 60.9 |
  | Spatial-MLLM-4B | 65.3 | 34.8 | 63.1 | 45.1 | 47.0 |
  | Gemini-2.5 Pro | 43.8 | 34.9 | 64.3 | 42.8 | 51.5 |
  | GPT-4o | 46.2 | 5.3 | 43.8 | 38.2 | 34.0 |

  — [VLM-3R, arXiv 2505.20279](https://arxiv.org/abs/2505.20279)
- **VSI-Bench-tiny, 7 frames** (Count / AbsDist / ObjSize / RoomSize):
  - AlloSpatial-4B (RL-trained agent): 54.1 / 42.3 / 68.8 / 60.0, overall 53.5
  - Qwen3-VL-32B: 60.6 / 35.1 / 71.5 / 54.0
  - GPT-5.2: 28.6 / 24.3 / 52.3 / 40.6
  - Gemini-3-Pro: 29.4 / 12.6 / 38.3 / 48.4

  — [AlloSpatial](https://arxiv.org/abs/2606.08952)
- **Test-time learning on Q-Spatial-ScanNet (TTL-SR):** geometric-consistency auxiliary queries plus pseudo-labels update weights at test time. Gains: +6.47 (Qwen3-VL-4B) and +9.41 (SpatialRGPT-8B). It requires weight access, so it does not apply to closed APIs — [TTL-SR, arXiv 2609.06004](https://arxiv.org/abs/2609.06004)
- SpatialScore: SFT on SpatialCorpus gives +10.47 / +9.23 overall for Qwen3-VL-4B / 8B, but gains "concentrate on already optimized task types" with forgetting elsewhere. The training-free SpatialAgent recovers most of that gain (+6.4 to +8.3) — [SpatialScore](https://arxiv.org/abs/2505.17012)
- SpaceVista (all-scale mm–km spatial reasoning), ViLaSR (drawing-interleaved RL) and SpaceR were downloaded or identified but not mined for metric numbers — [SpaceVista, arXiv 2510.09606](https://arxiv.org/abs/2510.09606); [ViLaSR, arXiv 2506.09965](https://arxiv.org/abs/2506.09965)

### Inferences
- Several numbers show that sheer model size and recency do not guarantee metric accuracy. GPT-5.2 and Gemini-3-Pro score well below Qwen3-VL-32B on VSI-tiny AbsDist and ObjSize with 7 frames, and ChatGPT-5 Pro scores 19.5 on QuantiPhy-val. Calibrating a model per category against validation matters more than which frontier model is used.
- For Track B (open-weight), Qwen3-VL-32B is the strongest general open model on both QuantiPhy (46.0) and VSI metric tasks. Code-as-World-VL weights (9B/27B, github.com/mirros-lab/code-as-world) are the only QuantiPhy-specialised open models published; their licence and availability were not verified. They are a candidate Track B direct-answer voter.
- Depth maps given to a VLM as images hurt (SD-VLM). Depth should feed code, not the prompt image.

### Gaps
- Not verified: whether Code-as-World-VL checkpoints are actually released and usable under the challenge's Track B rules.
- No fine-tuned spatial VLM is evaluated on QuantiPhy test, and none on speed or acceleration other than Code-as-World and EquiSD.

---
Sources consulted (primary): [QuantiPhy 2512.19526](https://arxiv.org/abs/2512.19526), [Code-as-World 2608.27549](https://arxiv.org/abs/2608.27549), [Scale equivariance / EquiSD 2609.00658](https://arxiv.org/abs/2609.00658), [Q-Spatial / SpatialPrompt 2409.09788](https://arxiv.org/abs/2409.09788), [VADAR 2502.06787](https://arxiv.org/abs/2502.06787), [pySpatial 2603.00905](https://arxiv.org/abs/2603.00905), [Thinking in Space 2412.14171](https://arxiv.org/abs/2412.14171), [SpatialScore/SpatialAgent 2505.17012](https://arxiv.org/abs/2505.17012), [RieMind 2603.15386](https://arxiv.org/abs/2603.15386), [GraFT 2609.03892](https://arxiv.org/abs/2609.03892), [AlloSpatial 2606.08952](https://arxiv.org/abs/2606.08952), [Skill-3D 2606.07436](https://arxiv.org/abs/2606.07436), [Think3D 2601.13029](https://arxiv.org/abs/2601.13029), [SpatialRGPT 2406.01584](https://arxiv.org/abs/2406.01584), [SD-VLM 2509.17664](https://arxiv.org/abs/2509.17664), [VLM-3R 2505.20279](https://arxiv.org/abs/2505.20279), [TTL-SR 2609.06004](https://arxiv.org/abs/2609.06004), [Speed in the Blind Spot 2609.37046](https://arxiv.org/abs/2609.37046), [MindJourney 2507.12508](https://arxiv.org/abs/2507.12508), [CoV 2601.05172](https://arxiv.org/abs/2601.05172), [Silicon Crowd 2402.19379](https://arxiv.org/abs/2402.19379).
