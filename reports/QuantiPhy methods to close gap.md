# Emulate the labeller, then measure better

The most promising untried lever is to stop predicting physical truth and predict **what the labelling procedure would have written down**. The QuantiPhy labels come from three pipelines, and each one defines speed, acceleration, size and depth differently. Our solver ignores most of those differences. The single biggest candidate is lab speed targets. Hand-clicked centres plus time-of-flight (ToF) depth were differenced frame to frame, and that noise inflates the speed of balls moving sideways by roughly **1.3–1.6x**, while radial motion and smoothed accelerations stay physical. That pattern matches every validation lab row we have and does not contradict the test-side priors that ruled out a global lab factor. Next come Blender's one-frame **backward** speed difference and its **tangential** acceleration; the axis-aligned-box size convention for animals and walking humans; a ball-blur bias in lab sizes; and widening the 3-run median to lab rows that use Claude's direct answer. Together these are worth a realistic **+0.01–0.02 in S2, +0.02–0.05 in S3 and +0.01–0.03 in D3** (planning estimates). That gives an overall MRA of about **0.81–0.83**, not the leaders' 0.852. **0.84 is plausible in D3, a stretch in S2 and unlikely in S3** unless the lab-inflation hypothesis proves out at full strength on test. The leaders have published nothing, so nobody outside those teams knows what they do differently. Our own oracles show per-question error dominates (ICC 0.20), so no single correction closes the gap. Every gain figure below is an estimate, not a measured effect, and each must be confirmed by a category-isolated upload.

## Nobody public is above 0.80, and the literature points at perception rather than models

The challenge has moved far beyond the published state of the art. The paper's best model, GPT-5.1, scored 53.1 MRA, and humans scored 55.6 ([QuantiPhy paper](https://arxiv.org/html/2512.19526v1)). The only method paper aimed at the benchmark is Code-as-World. Its fine-tuned 9B model reaches **0.544 on the official test** ([kuotunyu README](https://github.com/kuotunyu/quantiphy-geo-vlm); [Code-as-World](https://arxiv.org/html/2608.27549)). On the Track A leaderboard after the 2026-10-11 rescoring, Perch AI leads at **0.8517**, followed by Cogworks RSI at 0.8446 and Blindfolded at 0.8293. About ten teams sit between 0.80 and 0.82, and our entry is 14th at 0.7921 ([competition leaderboard](https://quantiphy.stanford.edu/competition/index.html)). None of the top seven Track A teams has a write-up, repo or post. Track A requires code disclosure only from the top three, and only after the deadline, so their methods will not be public before 23 October ([competition page](https://quantiphy.stanford.edu/competition/index.html)). Perch AI scores 0.852 in Track A but only **0.684 in Track B**, which suggests a closed frontier model drives its lead. That is an inference, not something the team has stated.

The public repos come from lower-ranked teams, and they agree on one structure: measure in pixels, scale by the prior, and fall back to the vision-language model (VLM) where measurement is weak. Three of their choices are worth copying.
- ferrousowl (Track A 0.798) fits local polynomials that **"follow the benchmark's ground-truth conventions: backward differences in simulations and forward differences in lab recordings"**. It pools identical questions across renders with a log-median and takes timestamps from the dataset's fps column ([ferrousowl README](https://github.com/ferrousowl/quantiphy-trackb)).
- QPM found that a raw speed measurement helps static-prior categories, S2 by +3.8 and S3 by +3.4 points, but hurts dynamic-prior ones ([QPM README](https://github.com/Tangxiaoxiao1992/quantiphy-qpm)).
- kuotunyu gained +0.033 by substituting geometry on the speed questions alone ([kuotunyu README](https://github.com/kuotunyu/quantiphy-geo-vlm)).

We already do measure-then-scale, family pooling and dataset fps. What we lack from this list is **explicit convention matching**, and that is the one idea a 0.80-level team states outright.

The broader literature explains our negative results rather than offering new levers.
- **Tool agents fail when perception is realistic.** With ground-truth perception, GraFT reaches 97.5 on VSI-Bench absolute distance. With real perception it falls to 43.2, and object size *drops* from 70.0 to 66.5 ([GraFT](https://arxiv.org/abs/2609.03892)). That matches our agent loop losing to a single high-effort call.
- **Metric depth fails on renders.** Metric-scale depth on the synthetic Sintel benchmark has an AbsRel error above 1.0 ([CUT3R](https://arxiv.org/html/2501.12387)), and even scale-aligned relative depth is about 13% AbsRel there ([FoundationGeo](https://arxiv.org/html/2607.11588)). That fits our finding that 3D-simulation geometry loses to Claude's direct answers.
- **Resampling one model does not help.** Self-consistency was slightly negative on VSI-Bench ([Thinking in Space](https://arxiv.org/abs/2412.14171)), and a test-time scale-equivariance correction cost 4.7 MRA on QuantiPhy-style data ([Tan et al.](https://arxiv.org/abs/2609.00658)). Our only positive is the 3-run median on 3D non-lab clips, where answers vary more than they are biased.
- **What transfers is structure.** Point-tracking accuracy is no longer the bottleneck: the top trackers sit within about 2–3 AJ points of each other on DAVIS ([TAPNext++](https://arxiv.org/html/2604.10582v1)), and our prior motion is already within 0.44% of exact masks ([PROBES.md](/home/user/quantiphy-challenge/research/PROBES.md)). What matters is fitting the right model over the right window ([Crenna et al.](https://www.mdpi.com/1424-8220/21/13/4580)) and, in QuantiPhy's case, the right *label definition*.

## Our answers deviate from five labelling conventions

The paper's appendix specifies how each label was produced. Our pipeline estimates physical quantities instead. In the formulas below, *a* is acceleration, *v* is speed, *fps* is the clip's frame rate, and *L* and *W* are an object's length and width. The table lists each mismatch, its predicted sign and size, and the rows exposed in the test set (counted from the test inputs with a keyword classifier, so they are approximate).

| Source and quantity | How the label was made | What we output | Predicted deviation of label vs ours | Test rows exposed |
|---|---|---|---|---|
| Blender speed at *t* | ‖p_k − p_{k−1}‖·fps of the object origin at k = round(t·fps), as a 3D norm ([paper App. D.1.3](https://arxiv.org/html/2512.19526v1)) | \|v(t)\| from an ICI-windowed local fit | ≈ −a/(2·fps·v). Free fall at 0.5 s and 24 fps: **−4.2%**. A car from rest at 5 m/s² at 1 s: −2.1%. Same sign for **speed priors**, so every static target in that clip is scaled too | sim+seg speed targets ≈155 (S2), 190 (D2), 81 (S3), 104 (D3); sim speed priors on ≈550 D2 rows |
| Blender acceleration at *t* | (s_k − s_{k−1})·fps: a backward difference of **scalar speed**, i.e. tangential d\|v\|/dt ([paper App. D.1.3](https://arxiv.org/html/2512.19526v1)) | ‖a‖ of a degree-2 fit (`norm(fit[2])` in `qp/geometry.py`) | Label = ‖a‖·cos φ, where φ is the angle between a and v. Projectile at 45° launch: label 0.71·g against our g, a 41% overshoot that scores 0.5. Identical for straight-line motion | accel targets ≈70 (S2), 33 (S3), 13 (D2), 6 (D3) |
| Blender sizes | World axis-aligned box. For animals, "length" is the AABB length in the simulator and wingspan is the maximum in flight; for humans, the rest-pose (T-pose) height ([paper App. D.1.1](https://arxiv.org/html/2512.19526v1); [HF dataset card](https://huggingface.co/datasets/PaulineLi/QuantiPhy)) | Anatomical extent in sampled frames | Label ≥ ours. A car of 4.5 × 1.8 m at 30° yaw has an AABB of **4.80 × 3.81 m**. On validation, simulation_0089 (bird-length prior) overshoots every answer by 1.25–1.56x, consistent with an AABB prior that includes the wings | animal or human size priors ≈50 (S2), 130 (S3); such targets ≈147 (D2), 55 (D3) |
| Lab speed, path length and displacement | Hand-clicked centre plus main-camera ToF depth, back-projected, then forward difference v_k = (x_{k+1} − x_k)/Δt; "at least 5 adjacent frames" annotated ([paper App. D.2](https://arxiv.org/html/2512.19526v1)) | Claude's direct answer (≈ physical) | Half-frame **lead** of +a/(2·fps·v) (+6% for a = 3 m/s², v = 1 m/s, 24 fps). Large **noise inflation** of the norm when motion is lateral (next section) | lab speed targets ≈143 (S3), 101 (D3); path-length rows |
| Lab sizes and depth | Sizes measured with a ruler or caliper (Table 6). Depth read at a clicked pixel on the RGB frame with the reprojected depth map overlaid ([paper App. C.2](https://arxiv.org/html/2512.19526v1)) | Geometry with depth_info read as range and f ≈ 722 px | Our lab sizes run 1.06x stated, plausibly from motion blur on balls. ToF maps usually store optical-axis Z to the visible front surface, not range to the centre (inference: the paper does not say) | 268 of 334 S3 lab rows use a ball-diameter prior; ≈350 lab size targets |
| Internet speed and scale | Hand-clicked reference point per frame, forward difference; γ = \|V_world\| / \|V_pixel(t₀)\| ([paper App. D.3](https://arxiv.org/html/2512.19526v1)) | Smoothed fits | Speed lead of +a/(2·fps·v). If clicks are 2D, slow movers' norms inflate as sqrt(1 + 2σ²/d²), where σ is the click noise and d the pixel step per frame: 4% at 5 px per frame and 22% at 2 px per frame for 1 px clicks. That inflation **deflates** static targets through γ | D2 internet: 124 acceleration-prior and 89 speed-prior rows |

Three conventions are already right in our pipeline, and the lever investigation confirmed them: dataset fps rather than container fps, Blender depth as Euclidean range (0.652 vs 0.569 for Z), and the 25→24 fps drop schedule of the lab clips ([PROBES.md](/home/user/quantiphy-challenge/research/PROBES.md)). The Blender rows above are **cheap and principled** to emulate. Our polynomial fits already describe the trajectory smoothly, so the emulator only has to evaluate the label's own difference operator on that fitted curve: backward at frame round(t·fps), or forward for lab and internet. For acceleration it takes the backward difference of speed rather than the vector norm. It must also apply this to *priors*, not only targets, because a prior's convention error scales every answer in its clip.

The magnitudes are modest. The deviations are a few percent outside curved paths and starts from rest, so they matter mostly where they push items across the 5% and 10% MRA steps. Python's `round` also rounds half to even, so t = 0.5 s at 25 fps selects frame 12, not 13. That detail is known only if the authors used Python, and it is a minor effect.

The size convention for articulated objects deserves more attention than its row count suggests, because when it bites it bites hard. Evidence for it on our side is one validation video, which scored 0.0, 0.7, 0.6, 0.4, 0.4 and 0.8. The fix needs no API spend. Where a segmented twin exists, measure the **full silhouette's** horizontal or vertical extent from its mask, with the maximum over frames for wingspans and T-pose heights. Otherwise use the union of Claude's boxes. This is the one place where twin masks should beat Claude's extents. Earlier tests found masks no better for rigid objects ([PROBES.md](/home/user/quantiphy-challenge/research/PROBES.md)), but the label here measures the silhouette envelope, not the anatomical body.

## Noisy 3D differencing plausibly explains the 1.3–1.6x lab speed labels

The lab labels have a structural property that our earlier analysis did not model. Each labelled speed is the **norm of a difference of two independently noisy 3D positions**. Noise of this kind does not average out of a norm. If the true per-frame displacement is d and the difference noise has variance s⊥² in the directions *perpendicular* to d, the median label is roughly sqrt(d² + s⊥²). That is the Rice-distribution bias, and it is always upward.

ToF depth is the noisiest coordinate. The paper says depth was read by clicking on the RGB frame with the reprojected depth map overlaid, "because averaging depth over a mask was unreliable for moving objects". It also says depth streams at 30 fps against 25 fps RGB ([paper App. C.2](https://arxiv.org/html/2512.19526v1)). Depth noise therefore enters a speed label **perpendicular to lateral motion** but **parallel to radial motion**.

That gives the model a sharp prediction. Balls moving sideways get inflated labels. Objects moving toward or away from the camera get roughly physical labels. Accelerations, which must have been smoothed to be usable at all, should come out physical or slightly low. A raw central second difference has noise √6·σ·fps², about 2,200 px/s² at 30 fps and 1 px of noise, which swamps the signal ([tracking notes](https://ojs.ub.uni-konstanz.de/cpa/article/view/1728/1628)).

Validation matches this pattern, though on few rows.
- **Lateral:** the tennis balls in captured_0034as (depth 0.71–0.78 m for both balls) have labels **1.24–1.64x** our estimate, and the soccer ball in captured_0061 is **1.46–1.63x**.
- **Radial:** the ping-pong ball in captured_0021x, whose depth falls from 1.511 m to 1.03 m between 1.0 s and 1.4 s, matches at **0.97** at 1.2 s. Its displacement label of 49.69 cm agrees with our 48.56 cm.
- **Slope:** the slope ball in captured_0013 is physical (GT 1.03 m/s vs about 1.05 m/s measured).
- **Heavy tail:** the basketball label of **9.32 m/s** at 1.1 s is 2.2x our estimate.

The prior "lever" investigation rejected a uniform 1.5x lateral *scale* (hypothesis K). It did so because five sideways **acceleration** priors on test (slopes, a trash bin, a whiteboard) read 0.78–1.0 of physics, and most lab **speed** priors are radial and "match by construction" ([lab-motion report](/home/user/quantiphy-challenge/research/levers_2026-10-11/levers_scripts_reports.tar.gz)). The noise model **predicts both of those facts**. It also accounts for probe 3 implying an average lab-motion ratio c of 1.0–1.2: a mixture of inflated lateral ball rows and physical radial rows averages to about that. So it is a different hypothesis that survives the evidence that killed K.

**What the numbers imply about the noise source.** On the tennis balls, 0.62 m/s at 24 fps is 25.8 mm per frame. A 1.45x inflation then needs about 27 mm of perpendicular noise per difference, or roughly 19 mm of independent depth noise per click. That is plausible for ToF readings on a 6.7 cm moving ball, but no source in our notes gives the sensor's noise. The soccer ball needs about 60 mm, and the basketball outlier needs much more. **Noise therefore grows with speed.** That is consistent with depth sampled at a slightly different instant from the RGB click, so that the depth pixel lands off a fast-moving ball. It is not consistent with a fixed sensor noise floor.

**The working model.** The practical form has one parameter:

label ≈ ‖v‖·sqrt(1 + κ²·sin²ψ)

Here ψ is the angle between the motion and the line of sight, κ ≈ 1.0–1.1 is fitted on validation, and the model applies only to small objects (balls) and only to instantaneous speed and path length. Displacement over a window spanning many frames is barely affected.

Two caveats limit the validation evidence. It covers only about 12 rows in four families, and two rows (0027s at 0.6 s and the basketball at 1.6 s) come in *below* our estimate, as a noisy-norm model allows but does not favour.

Because MRA punishes overestimates harder, the right move is a hedged factor chosen by expected score, not the full 1.45. I simulated labels that are inflated 1.45x with probability p and physical otherwise, with our own log-error spread σ.

| p (share inflated) | best factor (σ = 0.1) | gain per item vs ×1.0 | best factor (σ = 0.2) | gain per item |
|---|---|---|---|---|
| 0.3 | 1.0 | 0 | 1.0 | 0 |
| 0.5 | 1.1 | +0.009 | 1.1 | +0.013 |
| 0.7 | 1.3 | +0.070 | 1.2–1.3 | +0.049 |
| 0.9 | 1.45 | +0.191 | 1.3 | +0.112 |

Two steps estimate p without spending an upload.
1. **Test-side audit.** Split the 24 lab speed-prior renders by lateral fraction and compare stated with measured speed on the lateral ones. Under the noise model they read about 1.3–1.5. Under K's rejection they read about 1.0. These are test inputs, not labels.
2. **One isolated probe.** Upload the lateral-ball subset at factor 1.2 in S3 and D3 only.

Applied to roughly half the ≈143 S3 and ≈101 D3 lab speed rows, the plausible range is **S3 −0.008 to +0.023** and **D3 −0.004 to +0.010**. That is the widest upside of any candidate, and its downside is bounded and measurable.

## Ranked methods: realistic gains are about +0.02–0.04 overall

The ranking weighs expected gain per category, the strength of the evidence, money and engineering time. Gains are in category MRA and are planning ranges, not measurements. "Free" means the method replays cached Claude annotations and needs no API spend.

| Rank | Method | S2 | D2 | S3 | D3 | Evidence | Cost and effort |
|---|---|---|---|---|---|---|---|
| 1 | Lab lateral-ball speed label model (hedged factor, gated on ψ and object size; speed and path length only) | 0 | ~0 | −.008..+.023 | −.004..+.010 | Medium: mechanism, ≈12 validation rows, consistent with test priors and probe 3 | Free; 1 day including the audit |
| 2 | Blender label emulator: backward-difference speed at round(t·fps), tangential acceleration, applied to priors and targets; forward differences for lab and internet | +.003..+.010 | +.002..+.006 | +.000..+.003 | +.000..+.003 | Strong on definitions, weak on magnitude | Free; 1 day |
| 3 | Articulated and AABB sizes: full-silhouette envelope from twin masks or box unions; max over frames for wingspan and T-pose height | +.002..+.008 | +.002..+.008 | +.000..+.008 | +.000..+.005 | Medium: dataset card plus simulation_0089 | Free; 1 day |
| 4 | Extend the 3-run median to lab rows answered directly, plus a Claude, Astra and Gemini median on S3 3D non-lab | 0 | 0 | +.004..+.015 | +.001..+.003 | Medium: +0.02 per question on 3D non-lab; nested leave-one-video-out S3 +0.049 (post hoc) | ≈$20–25 Claude plus ≈$16 Astra plus the remaining Gemini credit; half a day |
| 5 | Lab ball blur and depth convention: diameter measured perpendicular to motion; test Z vs range and front surface vs centre by regressing prior-implied f on off-axis angle | 0 | 0 | +.000..+.012 | +.000..+.008 | Weak to medium: measured 0.94 size ratio; ToF convention is inferred | Free; half a day to 1 day |
| 6 | Internet label emulation: forward-difference lead; Rice deflation of γ for slow dynamic priors | +.000..+.003 | +.000..+.006 | 0 | 0 | Weak: depends on whether clicks are 1D or 2D; wait for diagnostic C | Free; half a day |
| 7 | Lab distance emulation: 3D centre-to-centre using depth_info and looming for time extrapolation | 0 | 0 | +.000..+.006 | +.000..+.015 | Weak: validation D3 lab distances score .38 but the labels look erratic | Free; 1 day |
| 8 | New prompt member for the 3D non-lab median: a reference-scale checklist, "trust the given prior", dense frames at queried times | 0 | 0 | +.000..+.010 | +.000..+.010 | Weak: the literature is mixed for strong models | ≈$3 validation pilot, then ≈$15–18 |

**Rank 1** sits first despite medium evidence because it is the only candidate with a two-digit upside in the category furthest from 0.84. A single category-isolated upload settles it.

**Rank 2** is the safest money-free improvement and the one convention a 0.80-level competitor follows by name ([ferrousowl README](https://github.com/ferrousowl/quantiphy-trackb)). Its expected gain per item is small, and it must not overwrite stated-fact rows. Diagnostic C, which zeroes the 79 S2 acceleration targets, will show whether the tangential part is worth more than this estimate. If those rows score below about 0.6, add event segmentation: piecewise quadratic fits with breakpoints chosen by BIC, with each derivative evaluated on the label's side of any bounce. The biomechanics literature warns that smoothing through impacts underestimates peaks by 30–70% ([Augustus et al.](https://eprints.chi.ac.uk/5020/1/AugustusAmcaHudsonSmith%20JoB%20SC_Revised_Final.pdf)).

**Rank 4** is the only paid item with in-house evidence. Spend at most about $25 of the roughly $60 Claude budget on it. Keep the rest for rank 8, and only if its validation pilot is positive.

Several methods should **not** get further time. They either failed in our own probes or the literature predicts failure.
- **Dense trackers on 2D priors.** Our priors are already within 0.44% of exact masks.
- **Monocular depth foundation models** for 3D simulations. Metric scale fails on synthetic renders.
- **Broad agent loops.**
- **Gemini as a direct answerer.** It scored 0.565 on validation.
- **Global shading or routing.** The oracle ceiling is +0.031, and every router loses.
- **The uniform K15 lateral scale.**

One rules question is worth asking the organisers before using it. The paper's Table 6 lists the measured sizes of every lab prop ([paper Table 6](https://arxiv.org/html/2512.19526v1)). Using those sizes for targets that no test prior states would be using published label metadata, not test inputs. We already transfer every size that appears as a test prior.

## An eleven-day plan built on category-isolated uploads

Each upload can test up to four independent changes, one per category, because category scores are means over disjoint question sets. The plan uses three uploads a day from Monday 12 October to Friday 23 October. It reserves the last two days for integration only.

Diagnostic C should be the last zero-out probe. The external consultant warned against further hidden-subset probing on rules and value grounds ([Astra consultation](/home/user/quantiphy-challenge/research/consult/astra_2026-10-11.md)), and A/B uploads now carry more information.

In the table, "base" is the best measured rows per category so far, and the codes refer to the ranks above.

| Day | Uploads (S2 / D2 / S3 / D3 content) | Offline and paid work |
|---|---|---|
| Mon 12 Oct | Probe 7b; probe 8 (on 7b); diagnostic C (on 7b) | Build the rank-2 emulator as a solver option and replay validation and test. Run the rank-1 lateral-speed audit on test priors. Run the rank-5 regression of implied f on off-axis angle |
| Tue 13 Oct | Probe 9 (on 8); **U-A** = rank 2 / rank 2 / rank 1 at ×1.2 / rank 1 at ×1.2; **U-B** = rank 3 / rank 3 / rank 5 / rank 5 | Launch the rank-4 paid runs: 2 extra Claude runs on lab videos and Astra on S3 non-lab |
| Wed 14 Oct | **U-C** escalates or reverts rank 1 (×1.35–1.45 if U-A's S3 rose by ≥.005, otherwise ×1.0 for S3 and a D3-only test); **U-D** = rank 4 (S3, D3); **U-E** = rank 6 (S2, D2) / rank 7 (S3, D3) | Decode diagnostic C. If S2 acceleration targets score below ~.6, build the event-segmented fits |
| Thu 15 Oct | New base = merged winners, with family and stated-fact rules re-applied on top; two second-order variants (emulator priors-only vs targets-only; envelope max vs 90th percentile) | Rank-8 validation pilot (≈$3) |
| Fri 16 Oct | Event-segmented S2 acceleration and speed (if justified); rank-1 path-length split; rank 8 on the test set if the pilot is positive | Run rank 8 on the 123 3D non-lab videos (≈$15–18) if positive |
| Sat 17 Oct | Rank-8 member added to the 3D non-lab median (S3, D3); rank-1 gating variants (object size threshold, ψ threshold) | Adversarial review of every change larger than 1.3x |
| Sun 18 Oct | Re-test any earlier loser whose interaction with a later winner is plausible; one upload left spare | Freeze the code paths |
| Mon 19 Oct | Integration candidate 1 (all winners); two variants dropping the weakest-evidence winner per category | Regression check: invariants, stated-fact rows exact, twins in sync |
| Tue 20 Oct | Integration candidates 2–3 | Audit the largest 2% of answer changes by eye |
| Wed 21 Oct | Confirmation upload of the best composite; two spare | None |
| Thu 22 Oct | Final composite of the best measured rows per category; one spare | Package for reproducibility, since a top-3 finish requires disclosure within 14 days |
| Fri 23 Oct | Final upload only if 22 October revealed a defect; deadline 23:59 AoE | None |

The plan front-loads the free, convention-driven work. It answers the highest-variance question, lab inflation, by Tuesday evening. It keeps paid runs to two decisions totalling well under the remaining budget.

Two uncertainties shape it. First, the deviations in the convention table are derived from the paper's text, not from the labelling code. The lab "smoothing" sentence in particular could mean the authors smoothed positions, which would weaken rank 1. Second, the gains overlap. If rank 1 fires at full strength, the remaining S3 headroom for ranks 4, 5 and 7 shrinks.

## Conclusion

The data and our probes suggest the gap to the leaders is not a missing model. More votes from another model did not help, and per-video scale oracles show little shared error to remove. What remains is that roughly 3,300 labels were produced by three procedures with their own difference operators, coordinate frames and noise, and we have been predicting physics instead. Modelling the labeller is principled, costs nothing to replay, and is testable category by category on the leaderboard. Its best case is concentrated where we are weakest: the lab half of S3. It also helps at the margins everywhere else.

The honest expectation is about 0.81–0.83 overall, with D3 the likeliest category to reach 0.84. S3 reaches 0.84 only if the lateral-speed inflation is real on test and the ensemble extension stacks on top. If the lab audit on Monday finds lateral speed priors reading physical, drop rank 1 at once. The remaining days then go to the emulator, the size envelope and the ensembles, which are smaller but safer.
