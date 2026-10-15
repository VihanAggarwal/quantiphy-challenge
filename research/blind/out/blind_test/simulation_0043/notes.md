# simulation_0043 - boat passing a rock on a sandbar (S3MC)

## What's in the scene
- 1080x1080 video, 24 fps, 72 frames. The camera is fixed and looks down at about 51 deg. Frame 0 is a duplicate of frame 1.
- A red and white fishing boat moves bow-first, left and slightly up in the image, along its own axis. A large boulder sits on a sandbar near the top of the frame.

## Tracking
- The boat was tracked with template matching (frame 24 template, sub-pixel peak). Its image motion is close to linear: about 3.70 px/frame in total (dx about -3.56 px/frame, dy about -1.03 px/frame).
- An aligned average of frames 8-40, upsampled 4x, gave a cleaner boat image for edge measurements.

## Scale
- The boat's length along the motion direction is about 214 +/- 2 px. This is measured from the bow tip at deck level to the aft-most point of the stern, corrected for about 0.65 m of sheer (the bow is higher than the stern).
- The speed comes from a ratio that needs neither f nor depth: speed = 10 m * (px speed) / (px length along the same 3D direction). This gives 10 * 88.85 / 214, about 4.15 m/s.
- Cross-check: the 3D solution gives |P(48)-P(24)| = 4.17 m over the 1 s interval. That matches.

## Camera, and which depth convention
- The depth convention was tested. Solving for focal length f and pitch with each convention:
  - Euclidean range: f about 3780 px, pitch about 56.4 deg.
  - Optical-axis Z: f about 3810-3830 px, pitch about 51.3 deg.
- Vertical cabin edges (window frames and cabin corner, 5 edges in 7 frame groups) separate the two:
  - How the tilt changes with image x is 2.08 +/- 0.1 deg per 100 px. Z predicts 2.11; range predicts 2.65.
  - The absolute tilts also fit Z with no roll.
- Hatch and roof edges along the beam direction are noisy (+/- 2-3 deg) and lean slightly toward the range convention.
- Conclusion: Z is preferred. Horizontal FOV is about 16 deg.

## Boat width
- Both gunwales were mapped onto the gunwale plane with the full pinhole model.
- The widest station is about 4.9 m aft of the bow:
  - Far gunwale (just aft of the cabin): +1.07 m
  - Near gunwale: -2.01 m to the top of the white sheer strip, -2.19 m to the edge where the red hull begins
- Width: 3.08-3.26 m with Z, 2.94-3.12 m with range.
- **Answer 3.12 m.** Confidence: medium (+/- 5%).

## Boat speed at t = 1 s
- Local linear fit of the image speed over frames 12-36 gives 3.702 px/frame. The speed is essentially constant.
- **Answer 4.15 m/s.** Confidence: high (+/- 3%). It depends only on the length ratio.

## Rock width
- Base contact points (left, bottom, lower right) were projected onto the ground plane. The camera is about 146 m above it.
- The near-vertical right side is a cliff about 8.3 m tall, read from its length in pixels. The far/top outline was placed at that height.
- Extents with Z:
  - Along the boat's beam axis (e2): about 26.1 m, possibly up to about 28 m if the far base reaches beyond the top edge
  - Along the camera's horizontal axis: about 25.9 m
  - Along the boat's length axis (e1): about 23.6 m
- With range, the e2 extent is about 24.0 m.
- "Width" is assumed to be the same world axis as the boat's width (e2), and the answer leans slightly toward e1.
- **Answer 25.5 m.** Confidence: medium-low (+/- 10%), because the axis is ambiguous and the far side is hidden.
