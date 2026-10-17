# Audit simulation_0309 family (dragon: clips 0302 V3S? sky / 0309 S3SC terrain)

## Family structure
- 0302 and 0309 are one scene and one motion. 0309 is 2880x1440 with 160 px black bars; its 2560x1440 content
  shows the dragon at the same pixels as 0302 (masked template match: dx/dy within 7 px, scale 0.99-1.01, frames 1-71; scripts/align.py).
  The glide-phase vanishing point is (-445,-482) in 0302 and (-454,-485) in 0309.
  The depth_info differs by 0.9% (5.1661/6.2783 vs 5.2108/6.3261). The prior is the same (1.29 m/s).
- Siblings outside the input that share the same asset and speed:
  - 0282 (2D top view): prior 1.29 m/s.
  - 0283 (2D side view, the same snowy terrain as 0309): **stated prior "length of the dragon = 0.75 m"**.
  These are the same wyvern with the flat grey head patch, flying at the same 1.29 m/s, so the scale is the same.

| qid | clip | quantity | current | provenance | agent's own value |
|---|---|---|---|---|---|
| 1469 | 0302 | body length | 0.75 | pre-agent (= 0283 stated length) | 0.74 (3D recon, back of head to tail 0.62-0.65 + head 0.11) |
| 1486 | 0309 | body length | 0.75 | pre-agent (= 0283 stated length) | 0.96 (sagittal-plane recon in flapping frames 1-17) |
| 1470 | 0302 | displacement 0.5-1.0 s | 0.645 | agent | 0.645 |
| 1487 | 0309 | displacement 0.5-1.0 s | 0.645 | pre-agent | 0.645 |

The current answers are consistent within the family. The only discordant number is the 0309 agent's 0.96, and it is not in use.

## Re-measurement (0302, sky background; scripts seg.py, klt.py, jointfit.py, recon*.py, tailtip.py, headtrack.py, cv_check.py)
- Frames 51-71 are a frozen glide pose, so I modelled them as rigid translation: x_j(t) = vp + K_j/(t - t*_j).
  - Fit: 216 KLT tracks with a forward-backward check, median rms 0.38 px, vp (-445,-482).
  - Each track's t*_j gives Z_j = Vz (t - t*_j).
- Depth convention: under the Z convention, Vz = 6.2783 - 5.1661 = 1.112. That gives f = |vp - c|/tan(acos(Vz/1.29)) = 3579,
  close to Blender's 50 mm default of 3556. The origin's t* is -3.645, which equals the head/shoulder tracks' t* (-3.63 to -3.66).
  The range convention would put the origin beyond the head, so Z is the self-consistent reading.
- Along-flight coordinate a = X·V̂ (frame 51, f = 3556). The extent is f-independent: it is 0.694-0.695 m for f = 3300-3700.
  - head patch / neck: -0.11 to -0.17
  - hips/legs: about -0.30
  - mid-tail: -0.58 to -0.66
  - silhouette tail tip: -0.69 (t*_tip = -3.264, 1/r fit residual < 1.7 px)
  So back of head to tail tip is about 0.56 m. The snout is hidden behind the head.
  The head's extent is about 0.06-0.15 m (top view 0282; 0302 agent's side-on frame 14).
  That makes the glide-pose snout-to-tail extent about **0.62-0.71 m**.
- 2D sibling check (0282 top view, scale from 1.29 m/s at 33.6-35 px/frame):
  the snout-to-tail extent is 0.6-0.84 m over the flap cycle, with the most extended frames at 0.81-0.84.
  The 0283 agent measured 505 px at 36.8 px/frame, so 0.74 m, which is consistent with the stated 0.75 and the 1.29 m/s speed.
- Constant velocity: the head-patch track over frames 11-71 lies on the glide-phase projective constant-velocity curve.
  Its radius deviation is under 2% (flap bob), and its glide t* is -3.656, matching the depth-info origin t* of -3.645.
  So the origin moves at constant velocity through t = 1-2 s and earlier. Displacement 0.5-1.0 s = 1.29 x 0.5 = 0.645 m.
  The 2D siblings give the same value (0282 0.645, 0283 0.65).

## Why the 0309 agent's 0.96 is wrong (not in use)
- It intersected head and tail rays with an assumed level, unbanked sagittal plane in the flapping and rolling frames 1-17.
- That put the tail tip 0.55-0.63 m behind the hip. The f-independent glide reconstruction above gives about 0.39 m.
- It put the head front 0.21-0.35 m ahead of the hip. The glide reconstruction gives about 0.17 m to the back of the head plus a short head.
- The roll in those frames inflates both offsets.

## Decision
- Body length (1469, 1486): route A is the sibling stated fact, 0.75 m (0283, same asset and speed).
  Route B is my frame re-measurement: 0.62-0.71 glide pose, and up to about 0.8 at maximum extension in 2D siblings.
  The current 0.75 agrees with both routes. No route supports 0.96. **No change.**
- Displacement (1470, 1487): 0.645, with constant velocity verified. **No change.**
- Fixes: none.
