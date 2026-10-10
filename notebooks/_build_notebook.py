"""Generate notebooks/colab_pipeline.ipynb (nbformat v4) from the cell sources below.

    python notebooks/_build_notebook.py          # writes and validates the notebook

Edit the cells here, not in the .ipynb, so the notebook stays reviewable and reproducible.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

OUT = Path(__file__).with_name("colab_pipeline.ipynb")
SAM2_COMMIT = "2b90b9f5ceec907a1c18123530e92e794ad901a4"   # facebookresearch/sam2 main (Dec 2024)

CELLS: list[tuple[str, str]] = []


def md(text: str) -> None:
    CELLS.append(("markdown", textwrap.dedent(text).strip()))


def code(text: str) -> None:
    CELLS.append(("code", textwrap.dedent(text).strip()))


md("""
# QuantiPhy Challenge: Colab GPU pipeline

Runs every GPU stage on Colab and pushes the small outputs back to GitHub:

question specs (Qwen3-VL) -> CV tracks (Grounding DINO + SAM 2) -> Qwen3-VL grounding tracks ->
Qwen3-VL and Code-as-World-VL direct answers -> geometry -> validation scores -> test submission.

**Before Runtime > Run all**
1. Runtime > Change runtime type: **GPU** (A100 / H100 best; an L4 runs the 4B model and skips Code-as-World),
   High-RAM if offered.
2. Colab secrets (key icon in the left bar), with *Notebook access* switched on:
   - `GH_TOKEN` (or `GITHUB_TOKEN`): a fine-grained GitHub token with **Contents: read and write** on
     `VihanAggarwal/quantiphy-challenge` (clones the private repo, pushes the `colab-outputs` and `data` branches).
   - `HF_TOKEN` (optional): only needed if a dataset or model asks for a Hugging Face login.
3. Edit the configuration cell below, then Run all.

Everything persistent lives in Google Drive under `/MyDrive/quantiphy` (datasets, outputs, logs).
Each stage skips videos it already finished, so after a disconnect just Run all again.
Command output is redacted: the token is never printed or logged.

Cost: each stage prints its wall time; Colab's *Resources* panel shows the live compute-unit rate of
the GPU. Run `SPLIT = "val"` first (24 videos, minutes per stage), then `"test"` (568 videos, roughly
24x longer) or `"val+test"` in one go.
""")

md("## 1. Configuration")
code('''
RUN_NAME = "colab_v1"        # outputs/<RUN_NAME>/<split>/... on Drive and on the colab-outputs branch
SPLIT = "val"                # "val" (159 questions, scored), "test" (3,289, builds a submission) or "val+test"
MODEL = "auto"               # Qwen3-VL id, or "auto" = by GPU memory (next cell)
BACKEND = "vllm"             # "vllm" (fast; installed below) or "hf" (transformers, slower)
CAW_MODEL = ""               # "" = run_open_vlm.py default (MirroS-Lab/Code-as-World-VL-9B, pinned revision)
CAW_BACKEND = "vllm"         # the Code-as-World authors run vLLM; "hf" is the fallback
QWEN_EXTENTS = True          # Qwen grounding also returns endpoints of asked size dimensions
DETECTOR = "gdino"           # CV detector: "gdino" (Grounding DINO base) or "owlv2"
SAM_MODEL = "auto"           # "auto" = by GPU memory, or e.g. "facebook/sam2.1-hiera-large"
LIMIT_VIDEOS = 0             # 0 = all videos; e.g. 2 for a smoke run
STAGES = {"specs": True, "cv": True, "annotate": True, "direct": True, "caw": True,
          "geometry": True, "score": True, "submission": True}
SUBMISSION_FROM = "auto"     # "auto" = best method on val, or a METHODS key (see the scoring cell)
POSTPROCESS = True           # model-free rules on the test answers before submitting (scripts/postprocess.py)
SYNC_DATA_TO_GITHUB = False  # push the validation set to the repo's "data" branch (for the offline sandbox)
SYNC_TEST_DATA = False       # ... and the test set too
PUSH_OUTPUTS = True          # push small outputs to the "colab-outputs" branch at the end
PUSH_RECORDS_FOR = ("val",)  # splits whose per-video JSON records are pushed too (test records stay on Drive)
REPO = "VihanAggarwal/quantiphy-challenge"
REPO_BRANCH = "main"
DRIVE_ROOT = "/content/drive/MyDrive/quantiphy"
CACHE_MODELS_ON_DRIVE = False   # True: Hugging Face model cache on Drive (survives sessions, uses Drive space)
GIT_NAME, GIT_EMAIL = "colab-runner", "colab-runner@users.noreply.github.com"
''')

md("""
## 2. GPU check
Shows the GPU and picks the Qwen3-VL size and the SAM 2 checkpoint from its memory when `MODEL` /
`SAM_MODEL` are `"auto"`: >= 70 GB -> Qwen3-VL-32B (FP8 with vLLM), >= 40 GB -> 8B, else 4B (on an L4,
22.5 GiB, the 8B weights leave too little room for vLLM's 16k-token cache). Code-as-World-VL-9B needs
>= 30 GB, so its stage is switched off on smaller GPUs (the geometry fallback then uses Qwen's answers).
""")
code('''
import subprocess

smi = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
print(smi.stdout or smi.stderr)
rows = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                      capture_output=True, text=True).stdout.strip().splitlines()
GPU_NAME, VRAM_GB = (rows[0].rsplit(",", 1)[0].strip(), float(rows[0].rsplit(",", 1)[1]) / 1024) if rows else ("none", 0.0)
assert VRAM_GB > 0, "No GPU: Runtime > Change runtime type > GPU, then Run all again"
if MODEL == "auto":
    if VRAM_GB >= 70:
        MODEL = "Qwen/Qwen3-VL-32B-Instruct-FP8" if BACKEND == "vllm" else "Qwen/Qwen3-VL-32B-Instruct"
    elif VRAM_GB >= 40:
        MODEL = "Qwen/Qwen3-VL-8B-Instruct"
    else:
        MODEL = "Qwen/Qwen3-VL-4B-Instruct"
FALLBACK_MODEL = "Qwen/Qwen3-VL-8B-Instruct" if VRAM_GB >= 40 else "Qwen/Qwen3-VL-4B-Instruct"
if SAM_MODEL == "auto":
    SAM_MODEL = "facebook/sam2.1-hiera-large" if VRAM_GB >= 20 else "facebook/sam2.1-hiera-base-plus"
if VRAM_GB < 30 and STAGES.get("caw"):
    STAGES["caw"] = False
    print(f"Code-as-World-VL-9B skipped: needs >= 30 GB, this GPU has {VRAM_GB:.0f} GB")
print(f"GPU {GPU_NAME} ({VRAM_GB:.0f} GB) -> Qwen {MODEL} ({BACKEND}), SAM 2 {SAM_MODEL}, detector {DETECTOR}, "
      f"Code-as-World {'on' if STAGES.get('caw') else 'off'}")
''')

md("""
## 3. Google Drive (persistent cache)
Datasets, outputs and logs live in `DRIVE_ROOT`, so runs survive disconnects. Model weights go to
local disk unless `CACHE_MODELS_ON_DRIVE` (downloads from Hugging Face are fast on Colab).
""")
code('''
import os
from google.colab import drive

drive.mount("/content/drive")
for sub in ("data", "outputs", "runs", "logs"):
    os.makedirs(f"{DRIVE_ROOT}/{sub}", exist_ok=True)
os.environ["HF_HOME"] = f"{DRIVE_ROOT}/hf_cache" if CACHE_MODELS_ON_DRIVE else "/content/hf_cache"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TQDM_DISABLE"] = "1"                   # SAM 2 / vLLM progress bars would flood the cell and the log
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
LOG = f"{DRIVE_ROOT}/logs/{RUN_NAME}.log"
SPLITS = [s.strip() for s in SPLIT.split("+") if s.strip()]
assert SPLITS and set(SPLITS) <= {"val", "test"}, SPLIT
print("Drive:", DRIVE_ROOT, "| HF cache:", os.environ["HF_HOME"], "| log:", LOG, "| splits:", SPLITS)
''')

md("""
## 4. Clone the private repo and install
The GitHub token comes from Colab secrets (`GH_TOKEN`, else `GITHUB_TOKEN`). `sh()` runs a shell command and redacts the token from
everything it prints or logs (progress bars are off; one redrawn with `\\r` is shown once, in its final
state); `pyrun()` runs Python in a fresh process (the notebook kernel itself never imports torch /
numpy, so upgraded packages need no runtime restart). The repo is cloned to local
disk (not Drive) so the token never lands on Drive; `outputs/` and `runs/` are symlinks to Drive.
SAM 2 comes from its pinned GitHub commit (`--no-build-isolation`, CUDA extension skipped); vLLM is
added when `BACKEND` or `CAW_BACKEND` is `"vllm"` (it pins its own torch, ~3 minutes).
""")
code(f'''
import io, subprocess, sys, time
from google.colab import userdata


def secret(name):
    try:
        return userdata.get(name) or ""
    except Exception:  # secret missing or notebook access off
        return ""


GITHUB_TOKEN, HF_TOKEN = secret("GH_TOKEN") or secret("GITHUB_TOKEN"), secret("HF_TOKEN")
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN
assert GITHUB_TOKEN, "Add GH_TOKEN under Colab secrets (key icon) and switch on notebook access"
REPO_URL = f"https://{{GITHUB_TOKEN}}@github.com/{{REPO}}.git"
REPO_DIR = "/content/quantiphy-challenge"
FAILED = []


def redact(text):
    for s in (GITHUB_TOKEN, HF_TOKEN):
        if s:
            text = text.replace(s, "***")
    return text


def sh(cmd, check=True, cwd=None):
    """Run a shell command; stream its output (token redacted) to the cell and the Drive log. Lines are
    split at newlines only and keep the text after their last carriage return (a progress bar's final
    state)."""
    print("$", redact(cmd)[:400])
    p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with open(LOG, "a") as log:
        log.write(f"\\n$ {{redact(cmd)}}\\n")
        for line in io.TextIOWrapper(p.stdout, encoding="utf-8", errors="replace", newline="\\n"):
            line = redact(line.rstrip("\\r\\n").rsplit("\\r", 1)[-1]) + "\\n"
            print(line, end="")
            log.write(line)
    rc = p.wait()
    if rc and check:
        raise RuntimeError(f"exit code {{rc}}: {{redact(cmd)[:200]}}")
    return rc


def pyrun(src, *args):
    """Run Python source in a fresh process from the repo root -> (exit code, output)."""
    r = subprocess.run([sys.executable, "-c", src, *map(str, args)], capture_output=True, text=True,
                       cwd=REPO_DIR if os.path.isdir(REPO_DIR) else None)
    out = redact(r.stdout + r.stderr)
    print(out[-4000:])
    return r.returncode, out


if os.path.isdir(f"{{REPO_DIR}}/.git"):  # same runtime: the Drive symlinks replace tracked folders (runs/),
    for sub in ("outputs", "runs"):       # so restore them first or the pull refuses to update runs/
        if os.path.islink(f"{{REPO_DIR}}/{{sub}}"):
            os.unlink(f"{{REPO_DIR}}/{{sub}}")
    sh(f"git -C {{REPO_DIR}} ls-files -z --deleted | xargs -0 -r git -C {{REPO_DIR}} checkout -q -- "
       f"&& git -C {{REPO_DIR}} pull -q --ff-only")
else:
    sh(f"git clone -q --depth 1 --branch {{REPO_BRANCH}} {{REPO_URL}} {{REPO_DIR}}")
os.chdir(REPO_DIR)
for sub in ("outputs", "runs"):
    if not os.path.islink(sub):
        sh(f"rm -rf {{sub}} && ln -s {{DRIVE_ROOT}}/{{sub}} {{sub}}")

t0 = time.time()
vllm = ' "vllm==0.19.1"' if "vllm" in (BACKEND, CAW_BACKEND) else ""
sh(f"pip install -q -r requirements-colab.txt{{vllm}}")
sh('SAM2_BUILD_CUDA=0 pip install -q --no-build-isolation --no-deps '
   '"SAM-2 @ git+https://github.com/facebookresearch/sam2.git@{SAM2_COMMIT}"', check=False)
pyrun("import torch, transformers; print('torch', torch.__version__, '| cuda', torch.cuda.is_available(), "
      "'| transformers', transformers.__version__)")
if pyrun("import sam2")[0]:
    print("official sam2 not importable: run_cv.py uses transformers' Sam2Video instead")
if vllm and pyrun("import vllm; print('vllm', vllm.__version__)")[0]:
    print("vLLM not importable: switching to the transformers backend")
    BACKEND = CAW_BACKEND = "hf"
print(f"install: {{(time.time() - t0) / 60:.1f}} min")
''')

md("""
## 5. Datasets and submission template
`huggingface_hub.snapshot_download` into Drive (`data/QuantiPhy-validation`, and `data/QuantiPhy` when the
test split is used), the official submission template (re-downloaded each session; the old copy is kept
if the site is unreachable), then an rsync to the repo's local `data/` for fast reads. Also checks that
the chosen Qwen model id exists on the Hub (falls back to the 8B model).
""")
code('''
DATA_DRIVE = f"{DRIVE_ROOT}/data"
NEED_TEST = "test" in SPLITS or SYNC_TEST_DATA
DOWNLOAD = r"""
import os, sys, urllib.request
from huggingface_hub import snapshot_download
root, need_test = sys.argv[1], sys.argv[2] == "1"
token = os.environ.get("HF_TOKEN") or None
repos = [("PaulineLi/QuantiPhy-validation", "QuantiPhy-validation")]
if need_test:
    repos.append(("PaulineLi/QuantiPhy", "QuantiPhy"))
for repo, sub in repos:
    path = snapshot_download(repo_id=repo, repo_type="dataset", local_dir=f"{root}/{sub}", token=token)
    n = sum(f.endswith(".mp4") for _, _, fs in os.walk(path) for f in fs)
    print(f"{repo} -> {path}: {n} videos")
tmpl = f"{root}/submission_template/quantiphy_submission_template.csv"
os.makedirs(os.path.dirname(tmpl), exist_ok=True)
try:
    urllib.request.urlretrieve("https://quantiphy.stanford.edu/competition/eval/quantiphy_submission_template.csv",
                               tmpl + ".new")
    os.replace(tmpl + ".new", tmpl)
    print("template ->", tmpl)
except Exception as e:
    print("template download failed:", e, "| kept:" if os.path.exists(tmpl) else "| save it by hand to", tmpl)
"""
rc, _ = pyrun(DOWNLOAD, DATA_DRIVE, int(NEED_TEST))
assert rc == 0, "dataset download failed (gated? add HF_TOKEN to Colab secrets)"
sh(f"mkdir -p data && (rsync -a --exclude .cache {DATA_DRIVE}/ data/ || cp -rn {DATA_DRIVE}/. data/)")
pyrun("import sys\\nfrom qp.data import load_split\\nfor s in sys.argv[1:]: print(s, len(load_split(s)), 'questions')",
      *SPLITS)

CHECK_MODEL = "import sys\\nfrom huggingface_hub import model_info\\nmodel_info(sys.argv[1]); print('model ok:', sys.argv[1])"
if pyrun(CHECK_MODEL, MODEL)[0]:
    print(f"{MODEL} not found on the Hub; using {FALLBACK_MODEL}")
    MODEL = FALLBACK_MODEL
''')

md("""
## 6. Optional: sync data to GitHub (branch `data`)
Only when `SYNC_DATA_TO_GITHUB`: pushes the validation set (CSV + videos), the submission template and,
with `SYNC_TEST_DATA`, the test set to an orphan branch `data` of the same repo, so a sandbox that cannot
reach Hugging Face can `git fetch` it. Files must be < 95 MB (larger ones are skipped and listed); the
push goes in commits of <= 1.5 GB. The branch is rebuilt (force-pushed) each time. The datasets' own
`.gitattributes` (Git LFS rules for `*.mp4`) are left out and LFS filters are switched off for the branch,
so the videos are stored as plain git blobs.
""")
code('''
DATA_README = """# QuantiPhy data mirror (generated by notebooks/colab_pipeline.ipynb)

Same layout as the repo's data/ folder. To use it in a checkout of main:

    git fetch --depth 1 origin data
    git worktree add data FETCH_HEAD        # or: mkdir -p data && git archive FETCH_HEAD | tar -x -C data
"""
if SYNC_DATA_TO_GITHUB:
    import shutil
    from pathlib import Path

    SYNC_DIR, LIMIT, CHUNK = "/content/data_sync", 95 * 2**20, 1500 * 2**20
    subs = ["QuantiPhy-validation", "submission_template"] + (["QuantiPhy"] if SYNC_TEST_DATA else [])
    files = [p for s in subs for p in sorted(Path("data", s).rglob("*"))
             if p.is_file() and ".cache" not in p.parts and p.name != ".gitattributes"]
    for p in files:
        if p.stat().st_size >= LIMIT:
            print(f"skipped (>= 95 MB): {p} ({p.stat().st_size / 2**20:.0f} MB)")
    files = [p for p in files if p.stat().st_size < LIMIT]
    total = sum(p.stat().st_size for p in files)
    print(f"{len(files)} files, {total / 2**30:.2f} GB -> branch 'data' of {REPO}")
    chunks, cur, size = [], [], 0
    for p in files:
        if cur and size + p.stat().st_size > CHUNK:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(p)
        size += p.stat().st_size
    chunks.append(cur)
    shutil.rmtree(SYNC_DIR, ignore_errors=True)
    os.makedirs(SYNC_DIR)
    g = f"git -C {SYNC_DIR}"
    sh(f"{g} init -q && {g} checkout -q --orphan data && {g} remote add origin {REPO_URL}")
    sh(f'{g} config user.name "{GIT_NAME}" && {g} config user.email "{GIT_EMAIL}"')
    Path(SYNC_DIR, ".git", "info").mkdir(parents=True, exist_ok=True)
    Path(SYNC_DIR, ".git", "info", "attributes").write_text("* -filter -diff -merge -text\\n")  # no LFS, no EOL rewrite
    Path(SYNC_DIR, "README.md").write_text(DATA_README)
    for i, chunk in enumerate(chunks, 1):
        for p in chunk:
            dst = Path(SYNC_DIR, p.relative_to("data"))
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(p, dst)
            except OSError:
                shutil.copy2(p, dst)
        sh(f'{g} add -A && {g} commit -q -m "data: part {i}/{len(chunks)}"')
        sh(f"{g} push -q {'--force ' if i == 1 else ''}origin data")
    print("data branch pushed")
else:
    print("skipped (SYNC_DATA_TO_GITHUB = False)")
''')

md("""
## 7. Stage helpers
Output folders per split: `outputs/<RUN_NAME>/<split>/qwen` (specs, grounding tracks, direct answers),
`.../caw` (Code-as-World answers) and `.../cv` (CV track records + cache). A failing stage is reported
and the next stages still run (they fall back where they can); the summary cell lists failures.
""")
code('''
LIM = f" --limit-videos {LIMIT_VIDEOS}" if LIMIT_VIDEOS else ""


def out_dir(split, name):
    return f"outputs/{RUN_NAME}/{split}/{name}"


def stage(name, split, cmd):
    if not STAGES.get(name, True):
        print(f"[{name}/{split}] skipped (STAGES)")
        return 0
    t0 = time.time()
    rc = sh(cmd, check=False)
    msg = f"[{name}/{split}] {'ok' if rc == 0 else f'FAILED (exit {rc})'} in {(time.time() - t0) / 60:.1f} min"
    print(msg)
    if rc:
        FAILED.append(msg)
    return rc
''')

md("""
## 8. Question specs (Qwen3-VL)
Parses every question + prior + depth text into a `QuestionSpec` (what to measure on which objects);
the CV and grounding stages read them from `qwen/specs/`.
""")
code('''
for split in SPLITS:
    q = out_dir(split, "qwen")
    stage("specs", split, f"python scripts/run_open_vlm.py --split {split} --task specs --name {RUN_NAME} --out {q} --model {MODEL} --backend {BACKEND}{LIM}")
''')

md("""
## 9. CV tracks (Grounding DINO / OWLv2 + SAM 2)
Detects each spec object on keyframes, propagates SAM 2 masks through the video and writes per-question
RoleTracks to `cv/annotate/` (the format the geometry step reads) plus a detection / mask-feature cache
in `cv/cv_cache/`. `--solve` also writes a geometry-only `cv/cv_geometry.csv`.
""")
code('''
for split in SPLITS:
    q, c = out_dir(split, "qwen"), out_dir(split, "cv")
    stage("cv", split, f"python scripts/run_cv.py --split {split} --specs {q}/specs --out {c}/annotate --detector {DETECTOR} --sam-model {SAM_MODEL} --solve{LIM}")
''')

md("""
## 10. Qwen3-VL grounding tracks
Qwen3-VL points / boxes for the same spec objects on sampled frames (`qwen/annotate/`).
""")
code('''
EXT = " --extents" if QWEN_EXTENTS else ""
for split in SPLITS:
    q = out_dir(split, "qwen")
    stage("annotate", split, f"python scripts/run_open_vlm.py --split {split} --task annotate --name {RUN_NAME} --out {q} --model {MODEL} --backend {BACKEND}{EXT}{LIM}")
''')

md("## 11. Qwen3-VL direct answers")
code('''
for split in SPLITS:
    q = out_dir(split, "qwen")
    stage("direct", split, f"python scripts/run_open_vlm.py --split {split} --task direct --name {RUN_NAME} --out {q} --model {MODEL} --backend {BACKEND}{LIM}")
''')

md("""
## 12. Code-as-World-VL-9B direct answers
The authors' QuantiPhy recipe (`caw/caw.csv`); the strongest direct answer in the public Track B entry.
""")
code('''
CAWM = f" --model {CAW_MODEL}" if CAW_MODEL else ""
for split in SPLITS:
    a = out_dir(split, "caw")
    stage("caw", split, f"python scripts/run_open_vlm.py --split {split} --task caw --name {RUN_NAME}_caw --out {a} --backend {CAW_BACKEND}{CAWM}{LIM}")
''')

md("""
## 13. Geometry
`qp.geometry.solve` on the specs with (a) the Qwen grounding tracks and (b) the CV tracks; where geometry
fails, the Code-as-World answer (else the Qwen direct answer) fills in. Writes `qwen/geometry.csv` and
`cv/geometry.csv`. CPU only.
""")
code('''
for split in SPLITS:
    q, a, c = out_dir(split, "qwen"), out_dir(split, "caw"), out_dir(split, "cv")
    fb = next((f for f in (f"{a}/caw.csv", f"{q}/direct.csv") if os.path.exists(f)), None)
    DF = f" --direct-from {fb}" if fb else ""  # no fallback file yet: the step finds one itself or uses none
    stage("geometry", split, f"python scripts/run_open_vlm.py --split {split} --task geometry --name {RUN_NAME} --out {q}{DF}{LIM}")
    stage("geometry", split, f"python scripts/run_open_vlm.py --split {split} --task geometry --name {RUN_NAME} --out {c} --specs-from {q}/specs{DF}{LIM}")
''')

md("""
## 14. Scores on validation
MRA of every method that produced a CSV (`scripts/score.py`), saved to `outputs/<RUN_NAME>/val/scores.csv`;
the best one is used for the test submission when `SUBMISSION_FROM = "auto"`. 159 questions: differences
under ~0.03 are noise.
""")
code('''
METHODS = {"qwen_direct": "qwen/direct.csv", "caw_direct": "caw/caw.csv", "qwen_geometry": "qwen/geometry.csv",
           "cv_geometry": "cv/geometry.csv", "cv_geometry_only": "cv/cv_geometry.csv"}
SCORE = r"""
import sys
import pandas as pd
from qp.data import load_validation
from qp.mra import score
gt, rows = load_validation(), []
for arg in sys.argv[2:]:
    name, path = arg.split("=", 1)
    pred = pd.read_csv(path)
    pred = pred.rename(columns={pred.columns[0]: "qid"})[["qid", "parsed_value"]]
    s = score(gt.merge(pred, on="qid", how="left"))
    rows.append({"method": name, "MRA": s["mra"], **s["per_category"], "path": path,
                 "missing": int((~gt.qid.isin(pred.dropna().qid)).sum())})
df = pd.DataFrame(rows).sort_values("MRA", ascending=False)
df.to_csv(sys.argv[1], index=False)
print(df.round(4).to_string(index=False))
"""
VAL = f"outputs/{RUN_NAME}/val"
if "val" in SPLITS and STAGES.get("score", True):
    have = {m: f"{VAL}/{p}" for m, p in METHODS.items() if os.path.exists(f"{VAL}/{p}")}
    if have:
        sh("python scripts/score.py " + " ".join(have.values()), check=False)
        pyrun(SCORE, f"{VAL}/scores.csv", *[f"{m}={p}" for m, p in have.items()])
    else:
        print("no validation predictions yet")
''')

md("""
## 15. Test submission
With `POSTPROCESS`, the chosen method's `test` CSV first goes through `scripts/postprocess.py`: model-free
rules from the test inputs only (a `*_segmented` twin takes its pixel-aligned original's answer; lab s/x
renders take the base render's motion answers; a size / speed / acceleration that another clip of the
same scene family states as its prior is used as stated). The decision log is written next to it
(`test/postprocessed/`); frame checks are cached in `runs/_postprocess_cache` (on Drive). If the step
fails, the raw answers are submitted. Then `scripts/make_submission.py` fills the official template
(checks ids, order, numeric non-zero values and the 2 MB limit) -> `outputs/<RUN_NAME>/submissions/`.
Upload it on the portal (3 scored uploads per day).
""")
code('''
if "test" in SPLITS and STAGES.get("submission", True):
    TEST = f"outputs/{RUN_NAME}/test"
    order = ["qwen_geometry", "cv_geometry", "caw_direct", "qwen_direct"]
    if SUBMISSION_FROM == "auto" and os.path.exists(f"{VAL}/scores.csv"):
        _, out = pyrun("import sys, pandas as pd\\nprint('BEST', ' '.join(pd.read_csv(sys.argv[1]).method))",
                       f"{VAL}/scores.csv")
        ranked = next((ln.split()[1:] for ln in out.splitlines() if ln.startswith("BEST")), [])
        order = ranked + [m for m in order if m not in ranked]
    elif SUBMISSION_FROM != "auto":
        order = [SUBMISSION_FROM]
    method = next((m for m in order if os.path.exists(f"{TEST}/{METHODS[m]}")), None)
    if method is None:
        print("no test predictions found for", order)
    else:
        src, tag = f"{TEST}/{METHODS[method]}", ""
        if POSTPROCESS:
            post, plog = f"{TEST}/postprocessed/{method}.csv", f"{TEST}/postprocessed/{method}_log.csv"
            if os.path.exists(post):
                os.remove(post)   # never submit a stale file from an earlier run
            if (stage("postprocess", "test", f"python scripts/postprocess.py {src} {post} --log {plog}") == 0
                    and os.path.exists(post)):
                src, tag = post, "_post"
            else:
                print("postprocess failed: submitting the raw answers")
        sub = f"outputs/{RUN_NAME}/submissions/{RUN_NAME}_{method}{tag}.csv"
        if stage("submission", "test", f"python scripts/make_submission.py {src} {sub}") == 0:
            print("submission file on Drive:", f"{DRIVE_ROOT}/{sub}")
else:
    print("skipped (needs the test split)")
''')

md("""
## 16. Push outputs to GitHub (branch `colab-outputs`)
Copies the small outputs of this run (CSV / JSON / TXT under `outputs/<RUN_NAME>/`, no caches, files
< 20 MB; per-video records only for `PUSH_RECORDS_FOR` splits) plus the redacted log into
`outputs/<RUN_NAME>/` of the `colab-outputs` branch, commits and pushes.
""")
code('''
if PUSH_OUTPUTS:
    import shutil

    PUSH_DIR, MAX_BYTES = "/content/outputs_push", 20 * 2**20
    RECORD_DIRS = {"specs", "annotate", "direct", "caw"}
    shutil.rmtree(PUSH_DIR, ignore_errors=True)
    if sh(f"git clone -q --depth 1 --branch colab-outputs {REPO_URL} {PUSH_DIR}", check=False):
        os.makedirs(PUSH_DIR, exist_ok=True)  # first push: new orphan branch
        sh(f"git -C {PUSH_DIR} init -q && git -C {PUSH_DIR} checkout -q --orphan colab-outputs "
           f"&& git -C {PUSH_DIR} remote add origin {REPO_URL}")
    src = f"{DRIVE_ROOT}/outputs/{RUN_NAME}"
    n = skipped = 0
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        parts = [] if rel == "." else rel.split(os.sep)   # <split>/<method>/<record dir>: only the third
        dirs[:] = [d for d in dirs if d not in ("cv_cache", "cache")   # level holds records (test/caw/ is kept)
                   and (len(parts) < 2 or parts[0] in PUSH_RECORDS_FOR or d not in RECORD_DIRS)]
        for f in files:
            p = os.path.join(root, f)
            if not f.endswith((".csv", ".json", ".jsonl", ".txt")):
                continue
            if os.path.getsize(p) > MAX_BYTES:
                skipped += 1
                continue
            dst = os.path.join(PUSH_DIR, "outputs", RUN_NAME, rel, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(p, dst)
            n += 1
    if os.path.exists(LOG) and os.path.getsize(LOG) <= MAX_BYTES:
        os.makedirs(os.path.join(PUSH_DIR, "outputs", RUN_NAME), exist_ok=True)
        shutil.copy2(LOG, os.path.join(PUSH_DIR, "outputs", RUN_NAME, "colab.log"))
    print(f"{n} files staged ({skipped} skipped as > 20 MB)")
    g = f"git -C {PUSH_DIR}"
    sh(f'{g} config user.name "{GIT_NAME}" && {g} config user.email "{GIT_EMAIL}" && {g} add -A')
    if sh(f"{g} diff --cached --quiet", check=False):
        sh(f'{g} commit -q -m "outputs: {RUN_NAME} ({SPLIT}, {GPU_NAME}) {time.strftime("%Y-%m-%d %H:%M")}"')
        if sh(f"{g} push -q origin colab-outputs", check=False):
            sh(f"{g} pull -q --rebase origin colab-outputs && {g} push -q origin colab-outputs")
        print(f"pushed to branch colab-outputs: outputs/{RUN_NAME}/")
    else:
        print("nothing new to push")
''')

md("## 17. Summary")
code('''
print("failed stages:", *FAILED, sep="\\n  ") if FAILED else print("all stages ok")
print(f"outputs on Drive: {DRIVE_ROOT}/outputs/{RUN_NAME}")
print(f"on GitHub: branch colab-outputs, folder outputs/{RUN_NAME}/" if PUSH_OUTPUTS else "outputs not pushed")
''')


def build() -> dict:
    cells = []
    for i, (kind, src) in enumerate(CELLS):
        cell = {"cell_type": kind, "id": f"cell-{i:02d}", "metadata": {}, "source": src.splitlines(keepends=True)}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)
    meta = {"accelerator": "GPU",
            "colab": {"provenance": [], "gpuType": "A100", "machine_shape": "hm", "toc_visible": True},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"}}
    return {"cells": cells, "metadata": meta, "nbformat": 4, "nbformat_minor": 5}


def main() -> None:
    nb = build()
    OUT.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
    try:
        import nbformat
    except ImportError:
        print(f"wrote {OUT} ({len(nb['cells'])} cells; nbformat not installed, not validated)")
        return
    nbformat.validate(nbformat.read(str(OUT), as_version=4))
    print(f"wrote {OUT} ({len(nb['cells'])} cells, nbformat-valid)")


if __name__ == "__main__":
    main()
