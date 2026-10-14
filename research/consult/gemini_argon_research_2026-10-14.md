# Research prompt for Gemini Argon (Deep Research): how to reach .85+ on QuantiPhy

Paste everything below the line. **Attach these two files from the repo**
(https://github.com/VihanAggarwal/quantiphy-challenge):
- `research/consult/summary_for_gemini_2026-10-13.md` (full pipeline, what worked and failed, and why);
- `docs/HANDOFF_SUBHI.md` (setup and rules).

---

You are the research lead for our team in the **QuantiPhy Challenge (NeurIPS 2026)**. We have **9 days** (deadline
**Oct 23, 2026, 23:59 AoE**). I want a deep, source-backed research report answering three questions:

1. **How do we get Track A from .817 to at least .855?** First place is .8536.
2. **Can fine-tuning get us there, and how exactly?** Both for Track A, where any model is allowed, and for Track B,
   where only open weights are allowed. Track B is at .621 and needs about .667 for the top 10.
3. **What would *drastically* improve the system?** I mean redesigns worth +.03 or more, not +.002 tweaks.

Be bold in generating ideas and ruthless in checking them. If the honest answer is that something can't work in 9
days, say so.

## 1. The task

Each test question gives you:
- a short video (1 to 10 s);
- one exactly-true **prior** about one object, e.g. `speed of the bird = 6 m/s`, `height of the table = 0.75 m`, or
  `gravity acc = 9.8 m/s^2`;
- for 3D videos, `depth_info`, the object-to-camera distances at one or two times;
- a question asking for an object's **size, distance, speed at time t, or acceleration at time t** in a stated unit.

The scoring metric is **MRA.**
- An answer scores the fraction of tolerances {<90%, <80%, ..., <10%, <5%} relative error it meets.
  - Under 5% = 1.0, 10 to 20% = .8, 50% = .4.
- Answers are averaged within S2/D2/S3/D3, then over the four. S = size prior, D = motion prior; 2 = 2D video, 3 = 3D.
- Scored questions: S2 553, D2 1137, S3 538, D3 933.
- What a fix is worth overall: `rows x average gain per row / (4 x N_category)`.

The data:
- **Test:** 3,289 questions, 568 videos. Sources: Blender simulation 1,633, real lab 806 (4 calibrated cameras,
  Orbbec ToF depth), internet 420, segmented copies 430.
- **Validation:** 159 labelled questions from 24 videos, all 24 also in test.
- How the labels were made (from the dataset paper):
  - **Simulation:** depth = Euclidean range to the Blender object origin; sizes = world bounding-box dimensions;
    speed = backward difference; acceleration = d|v|/dt. Camera FOV varies 8 to 103 degrees.
  - **Lab:** hand-clicked centres, ToF depth, forward differences at 25 fps.

## 2. Where we are

| | S2 | D2 | S3 | D3 | Overall |
|---|---|---|---|---|---|
| Track A best (scored) | .827 | .863 | .767 | .811 | **.817** |
| Track A next upload (expected) | ~.834 | .863 | ~.770 | ~.814 | ~.820 |
| Track B best (Qwen-family open VLM + rules) | .558 | .663 | .620 | .641 | .621 |

- **Track A leaderboard:**
  1. ~.8536
  2. Cogworks RSI .8498
  3. Blindfolded .8293
  4. iMak .8231
  5. szerlok .8195
- On the validation videos the top two score about **.87** and we score **.828**.
  - **Their lead is slightly better answers on nearly every question.** The base predictor is the gap.
  - No write-up, paper or code from any top team exists. Look anyway.
- **Weakest subsets (average score per question):**
  - S3 Blender simulation: .742 (221 rows)
  - S3 lab: .782 (317)
  - S2 internet: .796 (191)
  - D3 lab static: .799 (334)
- Under-10% errors cost almost nothing. **The loss is in 20 to 50% errors and >1.5x misses.**

**Our pipeline (Track A):**
1. Claude Opus (high reasoning) sees 16 to 32 labelled frames and all of a video's questions in one request. It returns
   pixel tracks plus a direct answer.
2. A geometry solver turns tracks into metric answers on 2D clips and lab sizes.
3. 3D simulation uses the median of 3 direct answers.
4. Model-free "scene family" rules (+.026, our biggest win) copy stated facts across camera views of one scene, fix
   per-clip scale and pool answers.

The attached summary lists **everything that failed**. Do not re-propose those items unless you show our test was
wrong. The main ones:
- **Other models and ensembles:** GPT-6 Astra, Gemini 3.1 Pro (.565), Claude Fable; more runs; xhigh effort.
- **Other ways of asking:** agent tool loops; verify passes; one question per request (−.073); extra camera views in
  the prompt (−.064).
- **Camera and 3D methods:** foundation-model FOV / MoGe-2 (−.17 to −.30); geometry on 3D simulation; lab 3D
  reconstruction.
- **Tracking and post-hoc fixes:** dense tracking / SAM masks; MRA shading; learned routers.

## 3. Resources and hard rules

- **Compute:** a Colab GPU with 96 GB VRAM (about 9 days of use).
- **API budget:**
  - Claude about $50;
  - OpenAI about $33;
  - Gemini about $7.50;
  - more is possible if the case is strong.
- **People:** 1 to 2 people plus AI coding agents.
- **Rules:**
  - No test labels in any form. Answers must come from test inputs plus models and code.
  - **Never train or tune on validation videos.** All 24 are test videos, so that would be leakage.
  - No use of the paper's lab prop size table (pending organizer approval).
  - Track B: open-weight models plus model-free code only. No closed-model outputs, not even as training labels.
  - **Check the competition rules** (https://quantiphy.stanford.edu/competition/index.html) for what training data is
    allowed, and quote them.

## 4. Research questions

### A. Path to .855 (Track A)
- What could make the base answers about 4% better nearly everywhere? Survey 2025-2026 work on:
  - metric measurement from video with VLMs;
  - test-time scaling for visual quantitative reasoning;
  - model-written measurement programs;
  - visual prompting / marking;
  - monocular metric depth and scale;
  - newer frontier models, Gemini Argon included.
- How do we cut 20 to 50% errors on **3D simulation sizes** when the focal length is unknown and labels are world
  bounding boxes?
- Any evidence about how Perch AI or Cogworks RSI work: names, members, GitHub, past competition write-ups.

### B. Fine-tuning (both tracks)
1. **Training data:**
   - Is there an official QuantiPhy training split, or other released data in the same format? Check Hugging Face, the
     paper and the site.
   - If not, how fast can we **generate synthetic Blender clips** that copy the dataset's label conventions?
     - The same priors and question templates.
     - Depth to the object origin, world bounding-box sizes, backward-difference speeds, FOV from 8 to 103 degrees.
     - Give concrete tools: Kubric, BlenderProc, Infinigen, or others.
     - Estimate clips per GPU-hour and how many clips are needed.
   - Which public datasets with metric scale or velocity labels could be converted (driving, sports tracking, physics
     benchmarks)?
2. **Model and method:**
   - Which open VLM fits on 96 GB for LoRA/QLoRA on video or multi-frame input (Qwen3.5-VL / Qwen3.5-27B, InternVL,
     others)?
   - Should we use supervised fine-tuning on numeric answers, or RL with an MRA-shaped reward (GRPO-style)?
   - Should we train the model to output **pixel measurements** that our geometry turns into answers, or the final
     numbers?
   - Give hyperparameters, sequence lengths and time per epoch.
3. **Evidence:**
   - Published gains from fine-tuning VLMs on quantitative spatial or physical reasoning (e.g. SpatialVLM, SpatialRGPT,
     VSI-Bench follow-ups, metric-depth or physics-video fine-tunes). Quote the exact numbers.
   - How much did synthetic-to-real transfer cost in those papers?
4. **Track A angle:** can a fine-tuned open model beat or usefully ensemble with Claude on our weak subsets? Can any
   closed model (Gemini, GPT) be fine-tuned through an API in time?
5. **A 9-day plan:**
   - day-by-day steps;
   - a go/no-go checkpoint by day 3;
   - what to cut if it slips.

### C. Drastic redesigns
Propose 3 to 5 redesigns that could each add +.03 or more. Starting points, not limits:
- **Program synthesis:** the model writes and runs its own measurement code per clip.
- **Multi-camera scene reconstruction:** the Blender scenes have up to 4 cameras with stated depths.
- **Physics-model fitting:** projectile, free-fall and collisions as constraints.
- **Learned calibration** of answers from synthetic data.
- **A fine-tuned checker model** that flags gross misses for a second pass.

For each redesign: why it beats what we have, why our past failures don't apply, and how to test it in under a day.

## 5. Fact-check protocol (mandatory for every idea)

1. **Claim:** the mechanism and the subset it improves, in one sentence.
2. **Evidence class:** one of
   - (A) a published result on QuantiPhy or a near-identical task;
   - (B) a published result on a related task;
   - (C) a first-principles argument;
   - (D) speculation.

   For A and B, give the URL and the exact quoted number. Mark anything you could not open as **unverified**.
3. **Self-refutation:** the strongest reason it fails for us. Check it against our failure list.
4. **Gain arithmetic:** `rows x item gain / (4 x N_cat)`, realistic not best-case.
5. **Kill test:** the cheapest experiment without test labels (validation, or the 106 exactly-known stated facts in
   test scene families), with the pass bar set in advance.
6. **Cost:** dollars, GPU-hours and engineering hours.
7. **Confidence:** 0 to 100% that it passes, with one line of justification.

Then do a second pass as your own adversarial reviewer:
- re-check every quoted number against its source;
- re-do every gain calculation;
- delete ideas worth under +.01 or with vague kill tests.

## 6. Output format

1. **Executive summary (10 lines):** is .855 reachable in 9 days, and what single result does it depend on?
2. **Ranked shortlist (at most 8 ideas)** across A, B and C, each with all 7 protocol fields.
3. **Fine-tuning plan:** data source, model, method, compute, day-by-day schedule, day-3 go/no-go test, and expected
   score for each track with an honest range.
4. **Combined forecast:** the score if the top ideas pass, without double-counting ideas that touch the same rows.
5. **Sources:** every URL cited, marked verified or unverified.
