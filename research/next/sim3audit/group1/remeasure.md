# group1 independent re-measure (qids 1383, 1384, 1192, 1754, 1647)

Scripts and frames: research/next/sim3audit/group1/remeasure_work/ (scripts/, frames/). I did not read any other file under group1/.

## 1383 / 1384: simulation_0143, man speed at t=1 s and t=2 s
- 0143 and 0141 have pixel-identical backgrounds (median absdiff 1), so they share one camera. The horizon is at y=540 and the camera is level.
- World depth scale K = f*Hc, fixed from scene geometry and not from the walker's gait:
  - 0142 (same tunnel, side view, the man walks parallel to the image plane, prior 1.693 m/s at 24 fps) gives the along-corridor tile pitch 0.599 m and a man height of 1.815 m, which matches 0143's 1.8 m prior.
  - In 0141/0143 the transverse joints are spaced 2.5e-4 in 1/(y-540). That gives K = 2390.
  - 0141's speed prior gives K = 2421 independently.
  - K/Hc gives f = 1861, which is a 35 mm lens. 0142's across-corridor pitch implies a 50 mm lens there.
  - Adopted K = 2393 and Hc = 1.286 (Hc from the 1.8 m head-top ratio).
- In this world the 0143 walker's steps are 0.75 m in the lateral (profile) phase and 1.4-1.7 m in the away phase, at the same cadence (12.5 frames per step) and the same 6 cm head bob as 0141. The body is stretched along the corridor axis, probably a child of a scaled path. The steps would be isotropic only at K of about 1250 (f about 975), which is what the original agent assumed.
- The 0143 depth labels (7.21 / 7.91) contradict K=1250 by a factor of 1.7. They fit K=2393 if the origin is a rigid offset of about 1 m to the man's side that turns with him. The heading turns between frames 0 and 12, which explains the label range rate.
- Speed: mid-stance plants at frames 0, 12, 24.6, 36.8, 49.3, 61.8 (head-peak frames), back-projected to the floor.
  - Chord F2->F4 (centred at frame 24.4): 2.29 m/s. Local quadratic at frame 24: 2.24.
  - Chord F4->F6 (centred at 49.3): 3.16. Quadratic at frame 48: 3.07.
  - Heading is steady at both times (-24 deg and +6 deg), so the offset origin adds no rotation term.
- Answers: **1383 = 2.25 m/s, 1384 = 3.1 m/s**. Confidence medium-low. An isotropic-world answer would be about 1.45 / 1.6.

## 1192 = 1754: telephone-booth width (0048 and 0048_segmented, the same object)
- Front-face width / height ratio, measured from intensity edges in the median background:
  - 0049, head-on: 98 / 258 px = 0.380.
  - 0045, about 10 deg oblique: 105 / (285.7 * 0.98) = 0.375.
- Booth height from those clips' bike-calibrated cameras is 2.97-3.09. That gives a width of 1.12-1.17.
- 0048 cap geometry, w = 0.695 * (Hs - z_top) with z_top of about 3.03, gives 1.06-1.10.
- Answer: **1.14 m** for both. Confidence medium.

## 1647: simulation_0010_segmented, average flight speed of the bird
- The bird eases in. The tail and beak move about 11-12 px/frame over frames 0-10, then 21-24 px/frame.
- Displacement over the clip is about 1171 px. The tail goes from x=282 at frame 0 to about 1453 at frame 58, extrapolated because the bird is behind leaves at the end.
- Scale: the bird is 140-152 px long at Z of about 34 m (1.19 m prior), so f is about 4000-4200 (about 0.0081 m/px at the bird).
- The depth change is about -0.25 m/s.
- The container is 59 frames at 22.89 fps, about 62 frames at 24 fps, so about 3 frames were dropped.
- Average speed = 9.5 m / 2.54 s = 3.75 m/s. With no drop correction it is 3.93; flap bob adds 1-2%.
- Answer: **3.85 m/s**. Confidence medium-low. The 0.5-1.0 s window is faster, about 4.3.
