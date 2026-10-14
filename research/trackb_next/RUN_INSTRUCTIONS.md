# Track B next Colab run: `RUN_PRESET = "ctx"` (context-aware open annotation)

What it does (details and evidence: `research/trackb_next/RESULT.md`): an open model, Qwen3.6-27B (Apache-2.0,
FP8), annotates every video the way the Track A pipeline does (labelled frames + all of the video's questions -> spec,
pixel tracks, its own answer), then measures each asked size / distance segment again with the full question on single
frames and zoomed crops, then SAM 2 is prompted with its boxes. Our geometry turns them into answers. No closed model
is involved anywhere. GPU only: no API keys needed.

## 0. Before Colab: put the new code on GitHub (`main`)
The notebook clones `VihanAggarwal/quantiphy-challenge` (branch `main`), so these files must be committed and pushed
from your checkout first:

    git add qp/open/ctx_annot.py qp/open/run_ctx.py qp/open/ctx_merge.py \
            notebooks/_build_notebook.py notebooks/colab_pipeline.ipynb research/trackb_next
    git commit -m "Track B: ctx preset (context-aware open annotation)"
    git push origin main

(`qp/open/*` and the two notebook files are required; `research/trackb_next` holds the diagnosis, tests and the
evaluation script.) Nothing else in the repo changed.

## 1. Start the run
1. Open `notebooks/colab_pipeline.ipynb` in Colab (File > Open notebook > GitHub, or upload the file).
2. Runtime > Change runtime type: the **96 GB GPU** (RTX PRO 6000 / H100 class), High-RAM if offered. The stage needs
   >= 44 GB (`CTX_MIN_GB`); on a smaller GPU it is skipped.
3. Colab secrets as for the earlier runs: `GH_TOKEN` (required), `HF_TOKEN` optional (Qwen3.6 is ungated).
4. In the configuration cell (section 1) change ONE line:

       RUN_PRESET = "ctx"

   Leave everything else as it is. The preset sets `RUN_NAME = "trackb_ctx"`, `SPLIT = "val+test"`, turns every other
   stage off, `MAX_HOURS = 7` (hard cap: the runtime is released after 7 h at the latest) and pushes the val + test
   records. Use the same Google Drive as the trackb_v1 run: the stage reuses `outputs/trackb_v1/{val,test}/caw/caw.csv`
   (fallback answers) and `outputs/trackb_v1/{val,test}/cvq/annotate` (SAM 2 tracks). If they are missing the run
   still works (the model's own answers are the fallback and the `cvqcx` variant is skipped).
5. Optional smoke test (about 20 min, recommended): also set `LIMIT_VIDEOS = 2`, Run all, check section 13d prints
   `loaded Qwen/Qwen3.6-27B-FP8 (vllm)`, `ta 2/2 videos: 2 written, N/N questions answered` and `[ctx/val] ok`,
   `[ctx_merge/val] ok`. Then set `LIMIT_VIDEOS = 0` and Run all again: finished videos are skipped.
6. Runtime > Run all. You can close the tab; `AUTO_TERMINATE` releases the GPU at the end or on an error.

## 2. Expected runtime (96 GB GPU; estimated from the trackb_v1 stage times)
| step | val (24 videos) | test (568 videos) |
|---|---|---|
| install + data sync | ~15 min (once) | |
| ctx (model load ~5 min each split; ta = one thinking request per video, cx = pointing + zoom) | ~10 min | ~1.5-2 h |
| ctx_merge (CPU geometry on ta / tacx / cvqcx) | ~1 min | ~5 min |
| SAM 2 on the ta boxes (+ geometry, samcx) | ~5 min | ~1 h (trackb_v1 cvq took 58 min) |
| **total** | | **~3-3.5 h (cap 7 h)** |

The log prints a line per chunk of 48 videos (`ta k/568 videos: ... questions answered, n retried, s`): if most
videos are "retried" the thinking replies are being cut (they are then asked again without thinking; the run still
completes).

## 3. What to send back
The notebook pushes everything needed to the GitHub branch **`colab-outputs`**, folder `outputs/trackb_ctx/`
(interim pushes after val, after test, after SAM 2, and a final one), including:
- `val/` and `test/`: `ta/` (specs, annotate, direct records + `direct.csv` + `geometry.csv`), `cx/*.json`,
  `tasam/annotate` + `tasam/geometry.csv`, `tacx/geometry.csv`, `cvqcx/geometry.csv`, `samcx/geometry.csv`,
  config files;
- `val/scores.csv` (validation MRA of each new method) and `colab.log`.
Just tell us when the run finished (or paste the "failed stages" summary). If the push failed, zip the Drive folder
`MyDrive/quantiphy/outputs/trackb_ctx` (the `*/tasam/cv_cache` folders can be left out) plus
`MyDrive/quantiphy/logs/trackb_ctx.log` and send that.

## 4. If something fails
- `could not load Qwen/Qwen3.6-27B-FP8` -> the stage tries the bf16 `Qwen/Qwen3.6-27B` by itself. If both fail, set
  `CTX_MODEL = CTX_FALLBACK = "Qwen/Qwen3.5-27B"` (same architecture, already run with this vLLM in trackb_v1) and Run
  all again.
- Out of memory: the FP8 default needs ~31 GB of weights plus cache (`run_ctx --gpu-mem 0.88`, `--max-model-len
  65536`); on a GPU below 80 GB keep the FP8 model and, if needed, add `--max-model-len 49152` to the `run_ctx` line of
  section 13d.
- A disconnect: Run all again; every finished video (ta, cx, SAM 2) is skipped.

## 5. Afterwards (CPU, us)
`.venv/bin/python research/trackb_next/evaluate_ctx.py --root <pulled outputs/trackb_ctx> --lovo` applies the
pre-registered kill test (RESULT.md); only on PASS is `submissions/trackB_cand_ctx.csv` built.
