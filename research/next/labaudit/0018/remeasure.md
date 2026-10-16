# 0018 independent remeasure: qid 2316 (captured_0018s, "width of the box in cm")

Current answer 11.0. Sibling renders of the same event currently say 8 (0018, qid 2297) and 9 (0018x, qid 2335).
The labels are shared across renders, so all three should carry one value.

**Best value: 7.9 cm** (range 7.4 to 8.5). Confidence: medium.

## Object
The box is the white printed carton (black square logo near its bottom) that the left (far) person holds upright, next to the
soccer ball, in frames 0 to 29. Its long axis is vertical. At frame 30 she releases it, it falls straight down, lands upright
(frames 39 to 41, orange end face on top), then tips over and slides (frames 46 to 48).
The video is 1280x720, 49 frames at 24 fps. Frames 35 to 36 have a time gap (both the ball and the box jump about 2.5x their step).

## Pixel measurement (frames 0 to 28, box held still)
- Sub-pixel half-level edges (remeasure_scripts/box_edges.py), with a 10x averaged crop and grid (remeasure_frames/box_avg10x_grid.png):
  - Front face: x 470.0 to 490.0 (median 19.4 to 19.7 px per row; 20.0 px at row 266) and y 239.2 to 291.1 (51.9 px).
    This is stable over all 29 frames.
  - The SAM mask in the x render (white background) also includes a dark 1.5 to 2 px strip at x 468 to 469 (the left side face
    in shadow; it is not the tripod, which sits at x 471 to 472 behind the box) and a 2 px dark bottom face at y 292 to 293.
    So the silhouette is about 22 px wide and 54 px tall.
- The front face aspect ratio is W/L = 20.0/51.9 = 0.385.

## Route A: back-projection at the box depth (held frames)
- The box is in front of the forearm whose hand holds the ball, about 2 to 3 hand-widths left of the ball.
  The ball's stated range is 2.80 m. Its centre pixel is (541.7, 263), giving Z = 2.75 m (if the range is to the centre) or 2.84 m (if it is to the front surface).
- Gravity check on the ball fall (frames 31 to 35, a = 4.47 to 4.55 px/frame^2 at 24 fps) gives Z = 9.8*711/(4.5*576) = 2.70 m
  just after release. The ball drifted about 4 px toward the image centre (toward the camera), so Z is about 2.8 m at hold.
  This confirms that f = 711 and the 24 fps time base are consistent.
- Arm geometry (shoulder about 3.0 m, hand about 2.78 m, box at about 60% along the arm, box in front of the forearm) puts the box front face at Z of about 2.72 to 2.80 m.
- W = 20.0 px * Z / 711 = **7.6 to 7.9 cm**. Including the dark side strip (about 21.5 px) it would be 8.2 to 8.5 cm.

## Route B: aspect ratio times length
- Own length: 51.9 px (front face) to 53.5 px (with the bottom face) at Z of about 2.75 m gives 20.1 to 20.7 cm. This agrees with the current length answer of 21.
- W = 0.385 * L gives 7.75 cm (own L) to 8.1 cm (L = 21).

## Route C: lying on the floor, frame 48 (weak)
- Floor depth comes from the left person's front shoe sole (y of about 576, Z of about 2.85 to 2.93 from the 3.13 m torso range) and a horizon at y 360 to 392.
  That horizon range comes from a level camera, or from the two people's feet and ranges, which give h of about 0.755 m and a horizon at 392.
- The box's lower edge at y of about 604 gives Z of about 2.47 to 2.59 m. The visible face is about 22 px tall, so 7.6 to 8.0 cm.
  This holds only if the whole 22 px is the front face. If the top 5 px strip is the box's top face, it would be about 6 cm.
- The box is motion-blurred and the face identity is unsure, so this is only a consistency check.

## Gravity on the box fall
I tried this and rejected it: the box blob is blurred and its leading edge is occluded by the arm.
A 4-point fit gave a = 6.3 px/frame^2, which is not credible.

## Conclusion
All the credible routes give 7.6 to 8.5 cm. 11 cm would need the box at Z of about 3.9 m (behind the person), or a 28 px face, and the image rules out both.
I recommend 7.9 cm for qid 2316, with the same value on its sibling renders (2297, 2335).

Files:
- remeasure_scripts/box_edges.py, track_fall.py, fit_fall.py, ball_circle.py
- remeasure_frames/*.png (crops, montages, segmentations)
