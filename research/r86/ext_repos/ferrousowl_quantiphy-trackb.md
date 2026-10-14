# QuantiPhy Challenge 2026: Track B (open-weight) entry

This entry measures kinematic quantities from video instead of asking a model to guess them. An open-weight
vision-language model, served locally by Ollama, handles only the steps that need language and vision: it finds
the object a question refers to and returns its bounding box, and it gives a direct estimate used for some
question types and as a fallback. Deterministic code does the rest.

The submitted run used **Qwen3.5 35B** (mixture-of-experts; `qwen3.5:35b` in Ollama, Q4_K_M, Apache-2.0) on one 16 GB consumer GPU.
Qwen3-VL instruct builds (`qwen3-vl:8b-instruct`, `qwen3-vl:30b-a3b-instruct`) also work.

| | Validation MRA (tuned on it, optimistic) | Test MRA (official) |
|---|---|---|
| Qwen3.5 35B, `--kind-policy v1 --video-check 2:drop` | 65.5 | 60.3 |
| Qwen3-VL-30B-A3B-Instruct | 57.9 | |
| Qwen3-VL-8B-Instruct | 54.0 | |
| Code only, no model | 36.9 | |

The pipeline:

1. **Parsing.** Rules turn each question, reference fact and depth note into structured records with SI units
   (`qpb/parse.py`).
2. **Localisation.** Qwen3-VL grounds the object first in the full frame and then in a zoomed crop. Boxes are
   snapped to foreground masks when the object moves (`qpb/ground.py`, `qpb/locators.py`).
3. **Tracking.** The camera is static, so tracking uses a per-pixel median background, colour-difference foreground
   masks and blob association. Tracks are seeded at up to three VLM anchor frames, and the track that agrees with
   the most anchors wins (`qpb/motion.py`, `qpb/solver.py`).
4. **Scale.**
   - 2D videos: metres per pixel come from the reference object's size, its pixel speed or its pixel acceleration.
   - 3D videos: a pinhole camera is used. Its focal length is calibrated from the reference object at its stated
     camera distance, or from its motion between two stated distances. Without either, the lab camera's
     specification (80° horizontal FOV) or the Blender default lens is used (`qpb/geometry.py`).
5. **Kinematics.** Local polynomial fits give speed, the tangential or vector acceleration, average speed,
   displacement and path length. They follow the benchmark's ground-truth conventions: backward differences in
   simulations and forward differences in lab recordings (`qpb/kin.py`).
6. **Pooling.** Identical questions on several renders of the same scene, or on several releases of the same
   recording, are pooled with a log-median (`qpb/pool.py`).
7. **Fallbacks.** If a measurement fails, the answer comes from a direct VLM estimate using the frames and the
   reference fact. If that also fails, a text-only estimate is used (`qpb/direct.py`).

No proprietary model is used anywhere. All model calls go to a local Ollama server and are cached on disk
(`work/vlm_cache/`), so a re-run reproduces the same answers.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# data (CC-BY-4.0): test videos + template, validation set
python - <<'EOF'
from huggingface_hub import snapshot_download
snapshot_download("PaulineLi/QuantiPhy", repo_type="dataset", local_dir="data/test")
snapshot_download("PaulineLi/QuantiPhy-validation", repo_type="dataset", local_dir="data/val")
EOF
# template.csv: the official submission template from the competition site (Sep-14 version)
# model server (any machine with a GPU; 16 GB is enough for qwen3-vl:8b)
ollama pull qwen3.5:35b      # submitted model; qwen3-vl:8b-instruct / qwen3-vl:30b-a3b-instruct also work
export QPB_OLLAMA=http://127.0.0.1:11434
# depth model for 3D objects without a stated distance (Apache-2.0, ~95 MB, runs on CPU):
#   hf: onnx-community/depth-anything-v2-small -> work/models/depth-anything-v2-small/onnx/model.onnx
```

## Run (reproduces the submitted file)

```bash
python tests/check_vlm.py --model qwen3.5:35b              # endpoint + box-coordinate convention check
python run.py --split val  --model qwen3.5:35b --tag q35 --methods measure,direct,text --workers 2
python combine.py --split val --tags q35 --kind-policy v1 --video-check 2:drop   # validation MRA per category
python run.py --split test --model qwen3.5:35b --tag q35t --methods measure,direct,text --workers 2 \
       --videos-file config/test_priority.txt
python combine.py --split test --tags q35t --kind-policy v1 --video-check 2:drop \
       --out submissions/trackB_q35_v1.csv                  # validated against the template
```

`config/test_priority.txt` only sets the processing order (videos with the most metric weight first), so a partial
run covers the most valuable videos; it does not affect any answer. All model calls are cached under `work/`, and
re-running continues where it stopped. The full test set took about 6 GPU hours on an RTX 4080 with two requests
in flight. `run.py --methods motion` runs a code-only diagnostic that needs no model.

`--kind-policy v1` takes measured values for speeds and accelerations, the geometric mean of the measured and
direct values for sizes, and the direct estimate for distances between objects. `--video-check 2:drop` drops a
video's measured values when, over its size and distance questions, the median ratio of measured to direct
estimates is beyond 2x.

## Notes

- Time stamps use the template's `fps` column, because some full-resolution files carry a wrong container fps.
- The validation videos are also test videos. The pipeline always reads the full-resolution test copy.
- Validation answers were used to tune the pipeline, so validation scores are optimistic.
- No proprietary model or API is used to produce predictions. The code was written with the help of an AI coding
  assistant.

## Licence

Code: MIT (see `LICENSE`). Models: Qwen3.5 (Apache-2.0), Depth-Anything-V2-Small (Apache-2.0). Data: QuantiPhy (CC-BY-4.0),
not included here.
