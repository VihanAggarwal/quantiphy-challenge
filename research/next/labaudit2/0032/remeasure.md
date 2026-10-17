# 0032 independent re-measure (second measurer) -- qid 2537

Scope: qid 2537, captured_0032, "velocity of the white ball at 1.6s in cm/s" (current 64.0).
I did not read research/next/labaudit*/0032 notes or the other measurer's files. No labels used.
Scripts and small outputs are in `remeasure/` (track.py, table.py, edges2.py, pnp2.py, wrad.py, wrow.py,
wtop.py, wshadow.py, vel*.py, final.py). Frames are PNGs in remeasure/frames (49 frames, about 38 MB).

## Timing
- 49 video frames at 24 fps, from a 25 fps capture.
- The tennis ball's x-step is 13.5, 14.0, 13.8, 14.3, **30.3**, 17.1, 17.4 px, and the white ball also takes
  a double step. So the dropped capture frame falls between video frames 35 and 36 (capture 37). With
  c = floor((25k+12)/24), the drops are at capture 12 and 37. Video k>=36 maps to capture k+2.
- t=1.6 s is capture 40, which is video 38. The label forward difference uses capture 40->41, which is
  video 38->39. These are consecutive capture frames, so no drop sits inside the step.

## What happens
- The tennis ball rolls left and hits the ping-pong ball around video 30-32. The white ball first slides
  to the right near the far edge at about 10 px/frame. From video 36 onward it rolls steadily, mostly
  TOWARD the camera, with a small rightward drift (path direction about 13 deg off the optical axis).
- Most of the 3D speed is depth motion. Image motion is only about 5.8 px/frame in x and 2 px/frame in y.

## Geometry
- Table-top edges: L-channel subpixel line fits on the mean of static frames 0-20. Corners:
  NL(463.7,482.6), NR(962.7,495.2), FR(849.2,427.2), FL(573.7,423.8).
  The image fits only a 60.3 (left-right) x 76.0 (depth) cm rectangle.
- PnP f-scan (pp = image centre): reprojection error is 4 px at f=711, about 1 px at f=770
  (camera 17.2 cm above the table, horizon y about 347.5 at x=735).
- f=770 is consistent with the other cues:
  * Side-edge vanishing point at (716, 347.6), the same horizon.
  * Ping-pong ToF anchor: plane-model centre range at capture 38 is 1.377 m. ToF gives 1.353+0.02 = 1.373 m (0.3%).
  * Tennis ToF anchor: plane model gives Z = 1.224 m. ToF gives 1.208 m (1.3%).
  * Two-ball ToF depth ratio with the measured contact-shadow rows gives horizon y about 348.6 (noisy, +-8).
  * Row-wise half-level ball width at video 36 is 22.8 px. With the ToF anchor and D=4.0 cm, that gives f of about 774.
- Note: f~711 from the earlier audits does not fit this clip as well (PnP residual 4 px, ToF off by 6%).
  The final speed hardly depends on f (see below).

## Measurements of the white ball (video 36-48 = capture 38-50)
- Centre x and diameter: row-wise 50% crossings on the left and right edges, then a circle fit
  (horizontal motion blur does not move the 50% points).
- Contact-shadow row: darkest row under the ball, parabolic subpixel, 9 columns (sd < 0.1 px).
  Values: 444.28, 446.08, 448.08, 450.10, 452.11, 454.64, ...
- A radial-edge circle fit gave about 1.8 px smaller diameters (biased inward). It was rejected
  after checking it visually against the overlay (remeasure/circ_overlay.png).

## Results (cm/s)
Route 1 (main): back-project the shadow row and centre x onto the PnP table plane (f=770), then lift by r=2 cm.
- Per-step speeds, capture 38->50: 63.5, 68.1, **65.9 (40->41)**, 63.2, 75.0, 64.8, 61.0, 70.4, 63.4, 59.2, 57.4, 64.7
- Local linear fit over capture 38-44, evaluated at 40.5: 66.9 (vx +15.6, vz -65.1)
- Quadratic fits 38-46 / 38-50: 66.5 / 67.5
- Label-style (clicked-centre ray x (ToF range - 2 cm)): 40->41 = 65.8, smoothed 66.7
- PnP-scaled shadow route at f=711/740/800: 66.0-67.6. With the ToF anchor instead:
  70.6 (f=711), 68.1 (740), 65.7 (770), 63.4 (800).

Route 2 (size, Z = f*D/d, D=4.0 cm): too noisy per frame (d jitter +-0.4 px, giving +-2.5% Z).
- Global linear fit over capture 38-50: 69.5. Local fits (40-50) are not reliable.

Route 3 (ball-centre-row plane, horizon 348-351, ToF anchored): 64-66 (38-44 linear), 65-67 (38-50 quadratic).

## Answer
- qid 2537: **66 cm/s** (label-style forward difference capture 40->41 = 65.8; smoothed physical = 66.7).
  Plausible range is 63-70. Confidence: medium. The real labels carry ToF depth noise on a one-frame
  difference, and the motion is mostly in depth, so a single label could land +-15-30% away.
- The current 64.0 is within 3% of this value. No change is needed.
