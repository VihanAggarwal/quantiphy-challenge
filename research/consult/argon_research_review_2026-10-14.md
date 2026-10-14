# Review of Gemini 4 Argon's research report (argon_research_2026-10-14.md)

Call: Batch API, medium thinking, $0.70 at the assumed price. Two earlier attempts dropped or ran out of output tokens
and are logged as placeholder spend.

## Fact checks we ran

**Sources:**
- arXiv 2609.29073, "Seeing Is Not Measuring": EXISTS (title confirmed via the arXiv API). We did not re-read its
  numbers.
- arXiv 2512.19526 (QuantiPhy): exists.
- Several of its other "verified" citations have placeholder IDs (2609.xxxxx, 2603.xxxxx, 2610.xxxxx) or cite only
  ResearchGate/alphaXiv snippets. Treat them as UNVERIFIED.

**Rules:**
- The quote matches the competition page.
- The page sets no limit on external or synthetic training data. Track B needs "publicly available model weights and
  tools".

**Idea 5 (lock lab f = 722 px):** premise false.
- Lab 3D geometry already uses the lab camera field of view (84 deg, so f ≈ 711 px at 1280 px; `qp/claude_annotate.py`
  LAB_FOV_DEG) as the prior on f.
- The table-top rectification is already in (labsize).

**Idea 7 (exact d|v|/dt on 350 rows):** wrong row count.
- Only 150 test questions ask for acceleration in total: simulation 90, segmented 32, lab 18, internet 10.
- Tangential-acceleration emulation was already tested (S2 −.002, D2 0).
- The simulation backward-difference fix is already in combo2.
- Realistic gain is about +.001.

**Idea 1 (multi-camera law-of-cosines solver):**
- Across cameras of one scene this is our scene-family scale correction plus pooling, already in the score.
- Within one clip, solving f from two ranges and a speed prior is what our 3D geometry already does, and it loses on
  simulation (−.19 per row) because the tracks and priors are noisy.
- Low expected gain.

**Idea 8 (physics factor graph):** overlaps the kinematic smoothing already tested (±.003) and the free-fall scale used
in physb.

## Its .848–.864 forecast is not credible

The forecast counts Ideas 1, 5, 7 and 8, which are mostly already in our .817 or were refuted. Without them, it rests on
Idea 4 (prompt), Idea 6 (ruler overlay) and Idea 2 (fine-tune). Each is unproven and each needs a pilot.

## Worth testing (ranked)

1. **Idea 4: world-bounding-box / yaw prompt for S3 simulation sizes** (221 rows at .742).
   - New: our prompt asks for tight *pixel* boxes but never explains that labels are world-axis bounding boxes, which
     come out larger for rotated objects.
   - Pilot: about $3 of Claude on the 52 validation questions.
   - Kill test: +.015 over val_hr_v1_high, better on most of the 6 clips.
2. **Idea 3 (Track B):** stronger open-weight pointing (Molmo / Qwen-72B) plus SAM-2 tracks into our geometry solver.
   - Track B S2 is .558 vs .827 on Track A, so its tracks are the gap.
   - Colab GPU work; kill test on the 24 validation videos.
3. **Idea 2: fine-tuning on synthetic Blender data that copies QuantiPhy's label conventions.**
   - The only "drastic" lever.
   - Most useful for Track B.
   - High engineering risk in 9 days.
   - Its literature gains come from other benchmarks (VSI-Bench).
4. **Not tested by Argon:** Argon itself as the answerer. Its report dismissed this without data. It is still the
   cheapest test of a possibly much better base model, but only about $3 of the Gemini budget is left.
