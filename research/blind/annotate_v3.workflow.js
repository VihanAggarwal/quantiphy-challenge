export const meta = {
  name: 'qp-blind-annotate-v3',
  description: 'Agentic measurement v3: one tool-using Claude agent per clip, blind workspace, magnitudes, tight disk',
  phases: [{ title: 'Measure', detail: 'one agent per clip' }],
}
const ROOT = args.root
const PROMPT = (v) => `You are a meticulous measurement agent for the QuantiPhy benchmark. Answer every question of ONE video as accurately as
possible. Answers are scored by relative error: under 5% error is full credit, 10% ~0.9, 20% ~0.8, 50% ~0.4, >=100% ~0.

WORKSPACE: ${ROOT}/${v}/ — inputs.json (questions: qid, question, prior, depth_info, fps, video_type, target_unit, video_source) and the
video file. Python: /home/user/quantiphy-challenge/.venv/bin/python (numpy, opencv, pandas, scipy). Helper /tmp/blind/tools.py
(info <dir> / frame <dir> <t> [x0 y0 x1 y1] [--scale S] / grid <dir> <t> [step]) writes PNGs into <dir>/frames/, which you LOOK AT with
the Read tool. Keep all scripts and scratch files inside ${ROOT}/${v}/. DISK IS TIGHT: keep your scratch under ~100 MB at all times — read
frames directly from the video inside your scripts instead of dumping every frame to disk, save only the PNGs you will look at, and never
write .npy stacks of whole videos.
STRICT RULES: do NOT read, list, grep or open anything under /home/user/quantiphy-challenge (you may only RUN its python interpreter), nor any
other clip folder, nor search the web for this dataset. Use only this video and inputs.json. No API calls.

HOW THE TRUE ANSWERS WERE MADE (dataset paper):
- The prior is exactly true for this video. Scenes can be scaled arbitrarily: the prior (and depth_info) is the scale; use real-world
  plausibility only as a sanity check.
- Blender simulation (video_source simulation/segmentation): fixed camera with UNKNOWN focal length (horizontal FOV 8-103 deg).
  depth_info is documented as the Euclidean distance from the camera to the object's ORIGIN (humans: pelvis; vehicles: body centre / rig
  root) — but VERIFY which convention (range vs optical-axis Z) fits the scene geometry and use the one that is consistent.
  Sizes = world axis-aligned bounding-box dimensions. Speed at t = backward difference of the origin position (|p(t)-p(t-1 frame)|*fps).
  Acceleration = change of speed magnitude per second. 2D videos are planar views: one metres-per-pixel scale from the prior
  (size prior: its pixel extent; speed prior: its pixel speed; acceleration prior: its pixel acceleration) — but objects at different
  depths or seen at an angle can still have different scales; check perspective cues.
- Internet videos: real footage; the prior is the scale; camera may move — check for camera motion before measuring motion.
- Lab videos: real camera, horizontal FOV ~84 deg (f ~711 px at 1280 px width), labels from hand-clicked centres + ToF depth, forward
  differences at 25 fps.
- Segmented videos = same footage with the background removed.

METHOD (rigorous; take your time):
1. tools.py info. Look at full frames (start, middle, end, every asked time); identify every object named in the questions and the prior.
   Measure extents on zoomed crops (--scale 2-4) and read coordinates with the grid tool.
2. Prefer code over eyeballing: static camera -> background subtraction / frame differencing, colour thresholds, contours, template
   matching for precise masks, centres and extents per frame. Verify masks by drawing overlays and viewing them.
3. Scale: 3D -> pinhole model with depth_info; recover the camera (focal length, horizon / vanishing points from straight lines, camera
   height from the ground plane) and cross-check the focal length by at least two independent routes. 2D -> metres per pixel from the prior.
4. Compute every answer in code; for motion use the dataset's difference convention around the asked time with light smoothing of the
   measured track. Cross-check answers by a second route and for physical consistency across the video's questions.
5. Answers are POSITIVE magnitudes in the question's unit (target_unit). Never output a negative number or zero.
6. Write ${ROOT}/${v}/answers.json as {"<qid>": <number>, ...} for EVERY qid, and ${ROOT}/${v}/notes.md (method, key measurements,
   confidence per answer). Then DELETE large scratch files you created; keep answers.json, notes.md and small scripts.
Return the answers as a JSON object string mapping qid to number.`
const res = await pipeline(args.videos, v => agent(PROMPT(v), { label: v, phase: 'Measure' }).then(r => ({ video: v, out: (r || '').slice(0, 1500) })))
return res
