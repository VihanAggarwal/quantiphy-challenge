# Handoff prompt for a second coding agent (Gemini / Jules)

Paste everything below the line into the agent, with the GitHub repo VihanAggarwal/quantiphy-challenge connected.

---

You are joining a team working on the QuantiPhy Challenge (NeurIPS 2026), Track A, in the GitHub repo
VihanAggarwal/quantiphy-challenge. Another agent (Claude) works on `main` at the same time, so follow the
coordination rules exactly.

## Coordination rules (hard)
- Work ONLY on a new branch `gemini/lab-motion`. Never push to `main`, never merge, never rebase or force-push
  other branches. When done, open a pull request from your branch and stop; Claude reviews and merges.
- Write files ONLY under `research/gemini/`. Do not edit `qp/`, `scripts/`, `submissions/`, `runs/` or
  `research/` outside your folder. If you need a library change, copy the function into your folder.
- No paid API calls of any kind. No keys exist in the repo; do not ask for any.
- Never use test labels (there are none) and never copy validation answers into test answers. Do not use the
  prop sizes from the paper's Table 6.
- Nothing here gets uploaded to the leaderboard by you.

## Read first
1. `research/consult/brief_2026-10-12_3d.md`: the problem (read "Problem 2: lab clips" closely).
2. `research/PROBES.md`: the full experiment log. Search for "lab", "label-noise", "emulator", "FWD", "25 fps".
3. `research/labnoise/` (`labmodel.py` label-process emulator, `fit_noise.py`, `emulate.py`, `eval_val.py`,
   `build_candidate.py`) and `qp/geometry.py` (docstring explains the solver).
4. `docs/TRACK_A.md` (pipeline and how to replay cached runs; cached Claude annotations are in `runs/*/*/records/`).
Data: `python scripts/download_data.py` (Hugging Face datasets PaulineLi/QuantiPhy-validation and the test set).

## Task: lab motion answers (S3 and D3 lab clips)
Lab motion targets (speed at t, path length, displacement) score only ~.67-.69 per item, the weakest subset
(S3 lab 334 rows, D3 lab 457 rows on test). The labels come from hand-clicked object centres + ToF depth at the
click + forward differences at 25 fps (paper arXiv:2512.19526, App. D). Our emulator of that process gave
S3 +.015 on the leaderboard but ~0 on D3. Find what is still mis-modelled or mis-measured. Ideas to test (not
limited to these):
- Is "speed at t" the forward difference from the 25 fps frame at or before t, after it, or centred? Is time
  t mapped through the 25->24 fps frame-drop correctly (see PROBES.md)?
- ToF depth read at the clicked pixel on small/round/moving objects (edge pixels mixing with background, flying
  pixels, motion blur): does a depth bias that grows with distance or shrinks with object size explain the
  validation lab rows and the stated lab priors better than our Gaussian noise?
- Per-object-class or per-scene noise levels fitted on the stated priors (each lab clip states one exact
  quantity; `research/labnoise/fit_noise.py` uses them), then applied to other rows of the same scene.
- Better physical speed estimates from the cached tracks (e.g. physics-constrained fits for falling, rolling,
  sliding-on-ramp motions) before the label emulation.

Validate every idea on (a) the lab rows of the 159 validation questions and (b) the stated lab priors used as
held-out labels (leave-one-out), reporting MRA deltas per kind with row counts. Small n: say so honestly.

## Deliverables (in `research/gemini/`)
- Scripts that run from the repo root with the repo's `.venv` (`pip install -r requirements.txt`).
- `NOTES.md`: what you tried, the numbers (validation and stated-prior checks), and what did NOT work.
- If something is clearly positive on both checks: a CSV `research/gemini/lab_candidate.csv` (columns `id,
  parsed_value`) that changes only lab S3/D3 rows of `submissions/trackA_best_p21.csv` (force-added in git; if
  missing, use the newest `submissions/trackA_best_*.csv`), plus the list of changed ids and the predicted
  per-category effect (scored N: S3 538, D3 933).
- Open a PR from `gemini/lab-motion` titled "Gemini: lab motion study", body = NOTES.md summary.
