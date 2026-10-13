# Prompt for Gemini (Deep Research): get QuantiPhy Track A to 0.85

Paste everything below the line. Attach `summary_for_gemini_2026-10-13.md` as well if you can, since it has the full pipeline.

---

You are the research lead for a team in the QuantiPhy Challenge (NeurIPS 2026, Track A, any model allowed).
**Requirement: find a credible path from our current ~.815 to at least .850 MRA within 9 days.** Small tweaks
(+.001 to +.003) are no longer useful to us. We need ideas that can plausibly add **+.01 or more each**. Every idea
must pass the fact-checking protocol in section 5. If no idea meets the bar, say so plainly rather than padding the list.

## 1. Task and metric
- **Input per question:** a 1-10 s video, one exactly-true "prior" about one object (size, speed or acceleration; lab clips
  often "Gravity acc = 9.8 m/s^2"), for 3D clips a `depth_info` text (object-to-camera distances at 1-2 times), and a
  question asking a size, distance, speed at time t, or acceleration at time t in a stated unit.
- **Metric (MRA):** item score = fraction of thresholds th in {.1, .2, ..., .9, .95} with |pred-gt|/gt < 1-th
  (<5% error = 1.0, 5-10% = .9, 10-20% = .8, ..., >=90% = 0).
- **Categories:** the mean over the 4 category means: S2 / D2 / S3 / D3 (S = size prior, D = motion prior; 2 = planar
  2D video, 3 = 3D).
- **Test set:** 3,289 questions, 568 videos. Sources: Blender simulation 1,633, real lab 806, internet 420, segmented
  copies 430. Scored N: S2 553, D2 1137, S3 538, D3 933.
- **Validation:** 159 labelled questions from 24 videos (also in test).
- **Uploads:** 5 per day.

## 2. Where we are
- **Our scores:** leaderboard .811 (S2 .817, D2 .859, S3 .766, D3 .803). A new composite expected at ~.815 is not yet scored.
- **Leaderboard:** 1 Perch AI .8517, 2 Cogworks RSI .8498, 3 Blindfolded .8293 (it copied validation answers), 4 iMak
  .8231, 5 szerlok .8195; most teams sit at .81-.82.
- **Calibration point:** from the rescoring that dropped the 140 validation-overlap questions, the top two score about .87
  on the validation videos and we score .828. **Their lead is better answers on nearly every question, not a trick.**
  No public write-up, paper or code from any top team exists.
- **Where we lose points:**
  - Per-subset item means: S2 simulation .828 / internet .796; D2 sim-static .851 / rest .857; **S3 simulation .742** /
    lab .782; D3 lab-static .799 / rest .805.
  - Errors under 10% cost almost nothing. The loss comes from **20-50% errors and >1.5x misses**.

## 3. Our pipeline
1. **Annotation:** Claude Opus (high reasoning) sees 16-32 labelled frames (854 px) plus all of a video's questions in one
   request. It returns pixel tracks for each object and its own direct numeric answer.
2. **Geometry solver:** 2D uses one image scale from the prior. 3D uses a pinhole camera, depth_info as Euclidean range,
   and f solved from the prior; the lab camera has a known f of ~722 px at 1280.
3. **Routing:** 2D questions use geometry. 3D simulation uses Claude's direct answer (median of 3 runs). Lab uses
   geometry for sizes and direct answer plus a label-noise model for motion.
4. **Model-free rules (biggest win so far, +.026):** "scene families" (twins, re-renders, multiple cameras of one
   scene). Stated facts are copied across, a per-clip scale is corrected from family facts, and answers are pooled.

## 4. Already tried: do NOT re-propose unless you show why our test was wrong
- **Other models:**
  - GPT-6 Astra as an answerer or extra voter: .747 vs .757, no gain.
  - Gemini 3.1 Pro on native video: .565.
  - Claude Fable: .749 vs Opus .782.
  - More Claude runs: 3 to 7 runs gives +.005.
  - xhigh reasoning effort: worse than high.
  - An agent loop with measurement tools: not better, 4x the cost.
  - A verification pass with zoomed crops: negative.
  - Targeted re-asks of flagged rows: about ±.02 on those rows.
  - High-resolution frames: .786 vs .782.
- **Geometry and perception:**
  - Geometry on 3D simulation: -.19 per answer.
  - Foundation-model camera FOV (MoGe-2) driving the geometry: -.17 to -.30 on validation and exact facts.
  - A pooled focal length per camera group: cameras differ within a group.
  - Dense tracking (GrabCut, KLT, SAM-style masks): no gain; our tracks are already within 0.44% of exact masks.
  - Zoomed extent re-measurement: about +.003.
  - Camera-motion compensation: tracks change <5%.
  - Lab 3D ballistic fits: the fitted g comes out at 9.7-16.7, and validation is worse.
  - Generic lab 3D reconstruction: .60.
- **Conventions:**
  - Full Blender label emulation: S2 -.002.
  - Depth read as optical-axis Z: worse.
  - Uniform lab speed factors on D3: 0.
  - Lab near-surface depth: refuted; stated ball sizes already read 1.056x.
  - Lab timing shifts: none help.
  - Per-scene ratio of stated to measured prior speed: negligible.
  - Container fps: the dataset fps is right.
  - Dimension-word swaps: not found.
  - Duplicated first frames: not a time shift.
- **Post-hoc layers:**
  - MRA "shading", uniform or driven by run spread: loses everywhere.
  - Cross-clip object-size table: 4/10 right.
  - Kinematic smoothing: ±.003.
  - 2D method switches: direct ≈ geometry.
  - Learned per-question routers: lose .017-.047 under leave-one-video-out.
- **What worked:**
  - Scene families: +.026.
  - Turning off optical-flow prior refinement: D2 +.025.
  - Lab label-noise emulator: S3 +.015.
  - "Physical scale" for self-filmed internet clips: D2 +.009 and +.006.
  - Sibling-clip stated speeds fixing a wrong scale (bird scene).
  - Simulation backward-difference speed labels on drops.
  - Collision and frame-edge fixes: about +.003 combined.
- **Constraints:**
  - No test labels in any form; answers must come from the test inputs.
  - The paper's Table 6 lab prop sizes are pending organizer approval.
  - Budget: about $62 of Claude, $33 of OpenAI and a 96 GB Colab GPU.

## 5. Fact-checking protocol (mandatory for every idea you propose)
For EACH idea, report these fields in this order:
1. **Claim:** one sentence describing the mechanism and which subset it improves.
2. **Evidence class:** one of
   - (A) published result with numbers on QuantiPhy or a near-identical task;
   - (B) published result on a related task;
   - (C) first-principles argument;
   - (D) speculation.

   Give the source URL for A and B and quote the exact number. If you cannot open the source, mark it **unverified**.
3. **Self-refutation:** the strongest reason it would NOT work for us, checked against section 4. If it overlaps an item
   there, explain precisely why our test does not settle it, or drop the idea.
4. **Gain arithmetic:** show it explicitly as rows affected x expected item gain / (4 x N_category). An idea counts only
   if this comes to >= +.01 overall under realistic, not best-case, assumptions.
5. **Kill test:** the cheapest experiment we can run with no test labels that would falsify it, using validation labels,
   exact stated facts from scene families, or cross-camera/twin consistency. Give the pass threshold before we run it.
   Example: "on the 106 exact 3D-simulation facts, item MRA rises from .793 to >= .83".
6. **Cost:** dollars, GPU hours, and our engineering hours.
7. **Confidence:** a probability (0-100%) that it passes its kill test, with a one-line justification.

After drafting the list, do a second pass as your own adversarial reviewer:
- Re-check every quoted number against its source.
- Re-do every gain calculation.
- Delete every idea whose realistic gain is < +.01 or whose kill test is vague.

End with:
- (a) a ranked shortlist, at most 6 items;
- (b) the combined realistic score if all pass, with ideas that overlap the same rows NOT added twice;
- (c) an explicit statement of whether .85 is reachable and what single assumption that depends on.

## 6. Questions we especially want answered
- What could make the **base predictor** about .04 better on almost every question (the leaders' advantage)? For example:
  - one question per request;
  - per-question frame selection;
  - video-native models with a different frame sampling;
  - model-written measurement code;
  - asking for intermediate quantities with uncertainty;
  - a specific open model or tool we have overlooked.

  Each must come with its kill test.
- How to cut **20-50% errors on 3D simulation sizes** (S3 .742) when focal length is unreliable and labels are world
  bounding-box dimensions.
- Any evidence or reasonable inference about how Perch AI or Cogworks RSI work. Search their names, members, GitHub and
  past competition write-ups.
