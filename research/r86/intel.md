# Competitor and leaderboard intel (2026-10-14, ~21:30 UTC)

Role: competitor and leaderboard intel (web). No test labels were used. Validation labels were used only to score
the Track B pseudo-label check in section 7, never to choose anything. No repo code was changed.

## 0. Bottom line
1. **Our repo is public and it holds our test predictions.** github.com/VihanAggarwal/quantiphy-challenge is public:
   159 commits, last push today 21:14 UTC.
   - `submissions/` has 91 CSVs, including `trackA_cand_combo2.csv` (scored .817) and `trackA_combo3_on_combo2.csv`.
   - `research/PROBES.md` maps every file to its leaderboard score. All family rules, and the Track B `trackb`
     preset in `qp/postprocess.py`, are public.
   - The repo is the 5th web-search hit for "QuantiPhy challenge NeurIPS 2026 leaderboard".
   - Our leaderboard team name "VihanAggarwal" is the GitHub user name.
   - Making it private does not break Colab: the notebook clones and pushes with a fine-grained GITHUB_TOKEN.
   - Only the owner can see clone and view counts: https://github.com/VihanAggarwal/quantiphy-challenge/graphs/traffic
     (our integration gets 403).
2. **The board moved a lot in 48 h** (Oct 12 21:00 to Oct 14 21:00 UTC).
   - Track A: the top 7 gained +.008 to +.032; we gained +.009 and are 8th at .8169. 5th place is now .8348 and 1st
     is .8596.
   - Track B: top-10 now needs .7128 (was .667). The top-20 cutoff is .6392, so our .621 is off the board.
3. **Two video-capable frontier models came out in that window.** Meta Muse Wonder was released Oct 12. Gemini 4
   Argon reached general API availability Oct 13 (on OpenRouter Oct 13; our own ledger called it Oct 14).
   - Argon's vendor-reported LVBench is 91.7, against 83.7 for Opus 5.5.
   - Track B also jumped (+.02 to +.046 for several teams), and Track B cannot use Argon. So the jumps are not only
     Argon. Some of it is ordinary end-of-competition activity. Copying from our public repo is possible but cannot
     be shown.
4. **The FAQ explicitly allows building Track B on Track A work** (verbatim, competition page section 09): "Can I use
   Main Track submissions to bootstrap an Open-Weight Track submission? You may, provided the Open-Weight pipeline at
   inference time uses only publicly available weights and tools. Closed-API outputs used during method development
   must be disclosed in the technical report."
   - Tested here (section 7): picking Track B members per cell by agreement with our Track A test predictions gives
     validation .615-.634, using no validation labels. Validation-tuned v3 gives .612 in-sample and .6035 LOVO.
5. **Competitor evidence that an open-weight pipeline can match a closed one:** JX intelligence scores Track A .8157
   and Track B .8042, a gap of only .0115. IIIXR Lab is at Track B .8076. So Track B's gap to .71-.80 is the
   pipeline, not the open-model ceiling.
6. **No method information exists for any top-7 team** (searched names, GitHub users and orgs, HF, arXiv, X, Reddit).
   The rules say top-3 packages come only after the deadline.

## 1. Leaderboard (public RPC `get_public_leaderboard_snapshot`, the same call the page makes)
- Endpoint: found in `https://quantiphy.stanford.edu/competition/assets/leaderboard.js` (Supabase URL and the
  publishable anon key are in `assets/supabase-config.js`).
- How to call it: POST `{SUPABASE_URL}/rest/v1/rpc/get_public_leaderboard_snapshot` with headers
  `apikey: <anon key>` and `Content-Type: application/json`, body `{}`.
- Snapshot saved: `research/r86/leaderboard_snapshot_2026-10-14T2100Z.json`. updated_at 2026-10-14T21:00Z; next
  scheduled update 2026-10-15T09:00Z (refreshes 09:00 and 21:00 UTC).
- Page text: "Top 20 teams · Best submission per track", "Both tracks include unverified submissions. Ties favor the
  earliest best submission." Up to 5 successful submissions per team per UTC day, shared across tracks.

| Track A rank | team | Oct 14 21:00 | Oct 12 21:00 | change |
|---|---|---|---|---|
| 1 | Perch AI | 0.8596 | 0.8517 | +0.0079 |
| 2 | Cogworks RSI | 0.8576 | 0.8498 | +0.0078 |
| 3 | Quantumonster | 0.8440 | 0.8191 | +0.0249 |
| 4 | Blindfolded | 0.8395 | 0.8293 | +0.0102 |
| 5 | iMak AI Lab | 0.8348 | 0.8231 | +0.0117 |
| 6 | szerlok | 0.8345 | 0.8195 | +0.0150 |
| 7 | dreads | 0.8221 | 0.7897 | +0.0324 |
| 8 | VihanAggarwal (us) | 0.8169 | 0.8083 | +0.0086 |
| 9 | JX intelligence | 0.8157 | 0.8114 | +0.0043 |
| 10 | JX bati | 0.8157 | 0.8121 | +0.0036 |
| 11 | Quantum D | 0.8154 | 0.8114 | +0.0040 |
| 12 | Shao Tai Tai | 0.8148 | 0.8112 | +0.0036 |
| 13 | reasoning_wrt | 0.8121 | 0.8121 | 0 |
| 14 | Framewise Physics | 0.8083 | 0.8083 | 0 |
| 15 | JX Intelligence | 0.8049 | 0.7911 | +0.0138 |
| 16 | bibilalu | 0.8045 | 0.8045 | 0 |
| 17 | PumpkinChicken | 0.8033 | new | |
| 18 | iLearn | 0.8014 | 0.8014 | 0 |
| 19 | ferrousowl | 0.7982 | 0.7982 | 0 |
| 20 | Quantum Dominators | 0.7835 | 0.7835 | 0 |

| Track B rank | team | Oct 14 21:00 | Oct 12 21:00 | change |
|---|---|---|---|---|
| 1 | IIIXR Lab | 0.8076 | 0.8051 | +0.0025 |
| 2 | JX intelligence | 0.8042 | 0.7829 | +0.0213 |
| 3 | Actuarial Tutor | 0.7659 | 0.7636 | +0.0023 |
| 4 | JX Intelligence | 0.7604 | 0.7362 | +0.0242 |
| 5 | ZZXP | 0.7362 | new | |
| 6 | Principia | 0.7306 | new | |
| 7 | Cookie | 0.7288 | 0.7134 | +0.0154 |
| 8 | Rigidly Grounded | 0.7187 | 0.7187 | 0 |
| 9 | LastNig | 0.7140 | 0.6703 | +0.0437 |
| 10 | I'mFromTaiwan | 0.7128 | 0.6670 | +0.0458 |
| 11 | CICO | 0.7121 | new | |
| 12 | khoai_tay_chien | 0.6952 | 0.6589 | +0.0363 |
| 13 | trustai | 0.6929 | 0.6778 | +0.0151 |
| 14 | Aing_Quantiphy | 0.6907 | 0.6633 | +0.0274 |
| 15 | Code42 | 0.6871 | new | |
| 16 | Perch AI | 0.6837 | 0.6837 | 0 |
| 17 | Qol Şärif | 0.6753 | 0.6431 | +0.0322 |
| 18 | LBWSquare | 0.6669 | 0.6602 | +0.0067 |
| 19 | Cliton | 0.6585 | 0.6283 | +0.0302 |
| 20 | HelloWorld | 0.6392 | 0.6365 | +0.0027 |

**Forecast to Oct 23.** This is only a pace extrapolation, at half the last 48 h pace.
- Track A: #1 about .87-.88; 5th about .845-.855. So .86 is roughly a top-3 finish at the deadline, and top 5 likely
  needs about .85.
- Track B: 10th about .74-.76.

## 2. Rules and FAQ facts that matter (competition page, fetched today)
- Track B: "Every model invoked at inference time must be based on publicly available weights and tools at the time of
  submission."
  - So a hosted endpoint serving open weights (Kimi K3 or Qwen3.8 via OpenRouter, or vLLM on Colab) is allowed.
- Bootstrap clause (verbatim in section 0.4): Track A outputs may be used during Track B development if disclosed.
  - My reading: choosing routing, calibration constants or prompts with Claude's test predictions is allowed.
  - Feeding Claude outputs into the Track B pipeline at inference is not allowed.
  - Fine-tuning an open model on Claude's test-set answers is a grey area. **Email quantiphybench@gmail.com before
    doing anything like it.**
- The leaderboard shows the best submission per track. Ties go to the earliest best.
  - So a losing hypothesis upload costs nothing on the board.
  - The final ranking is "verified, bootstrap CIs". Whether it is the best or the last submission is not stated; ask
    by email.
- Top-3 entries publish a reproducibility package within 14 days of notification. Organizers and direct collaborators
  are not eligible for prizes.
- Test ground truth is never released. Validation overlap questions are excluded from scoring.
- Organizers: Puyin Li, Tiange Xiang, Ella Mao, Shirley Wei, Paprika (Xinye) Chen, Shikang Liu; advisors Fei-Fei Li and
  Ehsan Adeli. Sponsor: GenRobot AI.

## 3. Our public exposure (details)
- The repo is public. GitHub MCP `search_repositories` lists it with `private:false`, and an unauthenticated
  github.com fetch shows "Public".
- `submissions/` holds 91 files. Among them:
  - every probe and diagnostic (diagE and diagF reveal our subset means);
  - `trackA_cand_combo2.csv` (.817 scored) and `trackA_combo3_on_combo2.csv` (expected about .820);
  - `trackB_v3_catmedian_famrules.csv`.
- The commits to `submissions/` give exact timestamps: combo2 at Oct 13 07:58 UTC, combo3 at Oct 14 01:39 UTC.
- What a competitor could do with it:
  - **(a) Copy the input-only family rules.** These gave us +.026 overall in probe 5 and apply to any base model.
  - **(b) Blend our CSV with their own.** Our own Astra/Claude test suggests little gain from this when errors are
    correlated (validation .747/.757 to .759).
  - **(c) Read our per-subset loss map.**
- Quantumonster (+.025) and dreads (+.032) gained about the size of the family-rule lift. That fits the copying
  hypothesis but does not prove it. Track B teams jumped similarly, and that track is driven by other factors.
- Action for the user (not done; it is a settings change): make the repo private now. Then add teammate Subhi
  (`docs/HANDOFF_SUBHI.md`) as a collaborator if needed. Publish the reproducibility package after Oct 24.

## 4. Team-by-team (searches: web, GitHub users and orgs, HF, arXiv, X). Confidence is my own estimate
| Team | Found | Likely method (confidence) |
|---|---|---|
| Perch AI (A .8596, B .6837 flat) | Nothing tied to QuantiPhy. Earlier unconfirmed lead: perchai.app, a multi-model agent product. | Closed frontier VLM plus a measurement pipeline. Its open-weight path is weak and has not been updated since Oct 12 (B .6837), so the lead is model-driven (medium). |
| Cogworks RSI (A .8576) | Nothing. "RSI" plausibly means recursive self-improvement. | Automated agent research loop on a closed model, like our workflows (low). |
| Quantumonster (A .844, +.025 in 48 h) | No GitHub user, no web hits. | A large step change in 48 h means a new base model (Argon, from Oct 13) or new input-only rules (low). |
| Blindfolded (A .8395) | Nothing. Before rescoring it scored about 1.0 on validation overlap rows (copied validation answers); earlier analysis put its real level at .8293. | — |
| iMak AI Lab (A .8348) | Nothing. | — |
| szerlok (A .8345) | GitHub user `szerlok` exists (id 80120360) with no QuantiPhy repo; earlier check agrees. | — |
| dreads (A .8221, +.032) | Nothing. | Same reasoning as Quantumonster (low). |
| reasoning_wrt (A .8121, flat) | Nothing. | Inactive since Oct 12. |
| JX intelligence (A .8157, B .8042) | No team page. "JX Luxventure" and "JX Press" are unrelated companies. | Open pipeline nearly equals its closed one, gap .0115. So mostly measurement and model-free code, or distillation. This is the best evidence that Track B .80 is reachable (medium). |
| IIIXR Lab (B .8076) | No hits. | Open-weight pipeline at .80 (no detail). |
| ZZXP .7362, Principia .7306, CICO .7121, Code42 .6871 (new Track B entries) | No hits. | — |

## 5. Public code, discussions and papers
- **YumengHe/QuantiPhy-web** (public; last commit Oct 13 17:18 PDT, "depth-guidance section").
  - Chinese-language documentation of a weak team's method: validation .514 (v1: SAM 2 tracks plus metric 3D); GPT-5.1
    baseline .486.
  - Its `QuantiPhy.csv` is test inputs only (no answer column).
  - Useful facts from it:
    - Depth Anything V2 relative depth with scale plus shift fitted to the `depth_info` anchors, leave-one-anchor-out
      on 12 validation 3D videos (48 anchors): median error 7.4%, 74% within 10%. Depth Pro raw: 62% median error;
      Depth Pro with one scale: 17%. Depth Pro's focal estimates on simulation range 401-7620 px.
    - PhysMind (world-model agent: SAM 3, SAM 3D, FoundationPose): MRA .25 on the 17 questions it measured, against
      .55 for the same VLM (Gemini 3 Flash) answering directly. FoundationPose loses fast objects.
    - Gemini 3 Flash direct scored .603 on their 35-question subset.
  - Relevance: low for Track A. Depth anchors matter only for distance questions on Track B, which are few
    (D3 103, S3 44, D2 79 rows; at most about +.006 on Track B).
- **Other public repos** (all Track B, .55-.60, no top-team hints): kuotunyu/quantiphy-geo-vlm (.577),
  ferrousowl/quantiphy-trackb, prarabdhmisra/quantiphy, Tangxiaoxiao1992/quantiphy-qpm, OxyzGiaHuy/quantiphy,
  khang1108 and khufia (README copies). Mr-QB/QuantiPhy is now 404.
- **HF.** Dataset discussions show nothing new since Aug (only #3, "Missing question_id"). Both datasets were last
  modified Oct 9. `qqqkai/QuantiPhy` is a mirror, not inspected for labels on purpose. No QuantiPhy models or Spaces.
- **New papers** citing QuantiPhy (Semantic Scholar):
  - 2609.39135 "Asking the World" (an agentic world-model plus simulator; results on CLEVRER/ContPhy, none on
    QuantiPhy).
  - 2609.06190, on blind baselines: VLMs default to round calibration values, which supports our measurement-first
    approach.
  - 2609.25738 OmniFysics-Nano-V2 (a compact physics omni-model).
  - 2605.08452 NICE FACT (confidence calibration).
  - None gives a usable lever beyond what is already in the repo.
- **Gemini share link** https://share.gemini.google/3raSAhUem3uK: DNS does not resolve here (ENOTFOUND), so it could
  not be read.

## 6. Model landscape (OpenRouter listing saved by a sibling agent at `research/r86/openrouter_models.json`)
- **Closed, new in the jump window:** meta/muse-wonder (Oct 12; text, image, video; $4/$20 per M) and
  google/gemini-4-argon (Oct 13; native video; $2/$10, batch $1/$5).
- **Open-weight VLMs with video:**
  - moonshotai/kimi-k3 (2.8T MoE, released Jul 16; $0.5/$15 per M);
  - qwen/qwen3.8-27b (fits a 96 GB GPU in bf16);
  - z-ai/glm-5.3-flash;
  - xiaomi/mimo-v2.6-pro;
  - stepfun/step-5-preview;
  - gemma-4-31b.
- **Argon cost estimate** from our Gemini 3.1 Pro ledger: native video on 24 validation videos used 292K prompt and
  494K output-plus-thinking tokens.
  - At Argon prices that is about $5.5, or about $2.8 batch. Thinking dominates.
  - With a thinking cap of about 4-6K tokens per video: about $1.3-2.5 for all 24 validation videos, about $0.5 for
    the six 3D non-lab clips, about $6 for 123 3D non-lab test videos, about $29 for the full test.

## 7. Track B bootstrap check (scripts and data in `research/r86/intel_tb_pseudolabel/`)
- **Pseudo-labels:** `submissions/trackA_cand_combo2.csv` (Track A, scored .817).
- **Fit set:** the 3,137 test rows of the 544 non-validation videos.
- **Members:** the trackb_v1 Colab outputs (caw, cv_geo, cv_geo_only, cvq_geo, qwen_geo, qwen_direct, qwen35, gemma4).
  The original directory, `/tmp/claude-0/tb3/x/trackb_v1`, is temporary; flattened copies are in `members/`.
- **Method:** for each cell (category x source x target kind), the log-median member set with the best MRA against
  the pseudo-labels. Validation labels were used only to score the result.

Per-member check (pseudo-MRA on test vs true validation MRA):

| member | pl_S2 | val_S2 | pl_D2 | val_D2 | pl_S3 | val_S3 | pl_D3 | val_D3 |
|---|---|---|---|---|---|---|---|---|
| caw | .480 | .531 | .586 | .511 | .522 | .558 | .552 | .579 |
| cv_geo | .612 | .559 | .659 | .511 | .640 | .672 | .541 | .404 |
| cvq_geo | **.649** | **.581** | **.710** | **.562** | **.658** | .660 | .567 | .445 |
| qwen_geo | .580 | .419 | .637 | .527 | .639 | .656 | .559 | .487 |
| qwen35 | .459 | .472 | .593 | .459 | .460 | .419 | .602 | .572 |
| gemma4 | .485 | .403 | .593 | .446 | .525 | .426 | .615 | .543 |

Rank correlation between pseudo-MRA and validation MRA: S2 .69, D2 .66, S3 .93, D3 .55. **cvq_geo is not in v3 at all,
but it is the top member by pseudo-labels in S2/D2/S3, and also on validation.**

Validation macro results (raw members, before family rules):

| strategy | val macro |
|---|---|
| v3 per-category sets (chosen on validation, in-sample) | .612 (LOVO .6035) |
| pseudo per-category set | .596 |
| **pseudo per-cell sets, minimum 25 rows, up to 3 members** | **.626** |
| pseudo per-cell, up to 2 members | .631 (.634 with the 4 dense Qwen members added) |
| pseudo per-cell, single member | .618-.626 |
| coarser cells (category x source) | .58-.61, worse |
| per-cell calibration toward the pseudo-labels | +.001, no gain |

- Fine-cell routing versus v3: +.015, video-clustered 90% CI [-.023, +.054].
- Pseudo-MRA on the 3,137 fit rows: v3 sets .642, routing .69-.71. This is in-sample selection and biased toward
  Claude's errors, so expect less on the real test.
- The routing table is `intel_tb_pseudolabel/routing_base8_min25_k2.csv`. It must be disclosed per the FAQ.

## 8. Proposals (details in the structured output)
1. Make the repo private now (rank protection; zero cost).
2. Gemini 4 Argon validation pilot as direct answerer and annotator, gated by a 3D non-lab kill test (about $1-3).
3. Track B: pseudo-label per-cell routing plus the existing `trackb` family preset. A free upload; expect +.01 to +.03
   on Track B.
4. Track B: run the Track A v1 prompt, geometry and family pipeline on an open frontier VLM (Qwen3.8-27B on Colab
   vLLM via an OpenAI-compatible adapter; Kimi K3 if a hosted budget is approved). JX intelligence's B-A gap of .0115
   says this is how to reach .70+.
