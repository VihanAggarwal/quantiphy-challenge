# Claude research session (2026-10-12) on the 3D gap: key claims (condensed from the user's paste)

Claims it attributes to arXiv:2512.19526 App. D and to vendor docs (verify before relying on them):
- Sim depth_info = 3D Euclidean distance camera origin -> object world position (Blender origin; humans: pelvis
  bone; some vehicles / multi-part machines: an Empty parented to the rig root).
- Sim size labels = axis-aligned world bounding-box dimensions (birds/insects: min and max width over the flight;
  humans: rest / min / max height). Possibly Blender `dimensions` (local box x scale) in practice.
- Sim speed label: v_i = (p_i - p_{i-1}) / dt, s_i = |v_i|, frame i = round(f_start + fps t) (backward difference).
- Sim acceleration label: a_i = (s_i - s_{i-1}) / dt, i.e. the change of SPEED MAGNITUDE (tangential).
- Sim camera fixed during each clip; focal lengths wide / normal / telephoto; ~125 base models, 81 base scenes.
- Blender sensor fit AUTO with a 36 mm sensor: f_px = F_mm / 36 * max(W, H) (FOV on the larger image side).
  Portrait renders at 50 mm would show ~20 deg horizontal FOV.
- Segmented clips: SAM 2 + Grounding DINO 1.5 masks; original annotations reused unchanged (also lab/internet).
- Lab: four Orbbec Femto Mega, RGB up to 3840x2160 @ 25 fps; ToF depth reprojected to RGB; the Orbbec depth frame
  holds Z-coordinates in mm. Labels: centre clicked on >= 5 adjacent frames "(for smoothing purpose)";
  v_k = (x_{k+1} - x_k)/dt; a_k = (x_{k+1} - 2x_k + x_{k-1})/dt^2; occluded frames use the average of the other
  three cameras.
- Public references: kuotunyu/quantiphy-geo-vlm Track B 0.577 test; Code-as-World-VL-9B 55.4 on validation.

Hypotheses and ideas (ranked by the report):
1. Lab near-surface depth correction (size shortfall 0.94 = 1 - r/Z). -> REFUTED on our data (PROBES.md 2026-10-12).
2. Per-event lab label-noise calibration: sigma2_ev = v_prior_label^2 - v_prior_phys^2, predict
   sqrt(v_t_phys^2 + sigma2_ev) with shrinkage; do not also use the prior as a scale (double counting).
   E[v_hat^2] = v^2 + 2 fs^2 sum(sigma_i^2); E[a_hat^2] = a^2 + 6 fs^4 sum(sigma_i^2). Printed lab accelerations
   look too clean for raw second differences -> labels may be smoothed.
   Forward difference at k = round(25 t) estimates v at t + 1/50 s (free fall: +0.196 m/s).
3. Cross-clip asset/prior table. -> 4/10 right on validation; not adopted.
4. Blind-prior ratio correction: ask the LLM for target and prior with the prior withheld; y = y_t_blind *
   y_p_true / y_p_blind; adopt iff Var(e_t_blind - e_p_blind) < Var(e_cur) on facts + validation (API cost).
5. Sim convention audit + discrete lens prior (sent to the simfov agent).
6. Sigma-driven MRA shading (delta = -sigma^2). -> rejected on validation and facts (PROBES.md).
7. Lab physics-constrained trajectories (SAM 2 centroids, looming depth for balls, free fall / ramp fits), then
   label emulation at t + 1/50 s.
8. Metric point maps (MoGe-2 / MapAnything) anchored to depth_info + masks -> oriented 3D extents, gated fusion.
Arithmetic: reaching .8525 from .8045 needs +.096 on both S3 and D3; the list is worth ~+.02-.035 at best.
