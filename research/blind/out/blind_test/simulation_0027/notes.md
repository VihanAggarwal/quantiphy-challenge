# simulation_0027 - notes

Q1116: speed of the person from 1.0 s to 2.0 s (m/s). Prior: person height 1.75 m. Depth labels: 100.5638 m at t=1 s, 100.5996 m at t=2 s.

## Scene
- The camera is static: phase correlation on the rock region drifts by less than 0.02 px over the clip.
- Oblique aerial view of a beach. Water is at the bottom of the frame, the sand plateau is in the middle and a rock is at the top. The visible side faces of the rock and of the sand slab show that the camera looks down from the image-bottom side.
- The person is upright in the image (axis tilt about 2 deg). The shadow attaches at the feet. The person walks down-right in the image, so on flat ground they are approaching the camera diagonally.
- Track: the shirt-centroid velocity is (11.1, 14.9) px/s, giving 18.6 px/s. The displacement from frame 24 to frame 48 is 18.4 px.
- Gait: the feet are planted with no sliding. The step period is about 17.3 frames (cadence 1.39 steps/s), and each step is about (6.7, 10.8) px in the image. Lateral foot-track offset is about (4.4, -1.8) px.
- Person extent: shirt top to sole 49.6 px; head top (faint) to sole about 60 px.

## Conflict
- On flat ground, the visible motion would reduce the range by about 0.85-0.9 m/s. The labels instead show +0.036 m.
- To keep the range constant, the person would have to descend about 0.4 m/s. That is impossible here because the feet stay planted and the shadow stays attached on visibly flat sand.
- Conclusion: the labelled depth change is not consistent with the rendered motion. I trusted the rendered motion (flat-ground walk) and used D of about 100.6 m only as the overall scale.
- Curiosity: |dD_label| = 0.0358 equals the predicted per-frame range change (1/24 s) for a depression angle of about 25.8 deg, but the sign is opposite.

## Scale and angle
- Scale: k = (1.45 cos d + 0.15 sin d) / 49.3 m/px. This uses a shoulder-top height of 1.45 m plus foreshortening extras, and agrees with the head-top extent of 60 px for 1.75 m.
- Depression angle d to the person is about 24-28 deg, from three cues:
  - a natural step length of 0.66-0.78 m at the observed cadence (consistent with a 30 fps walk cycle played at 24 fps);
  - the rock's aspect ratio (about 26 deg);
  - the water-texture anisotropy, which sets a lower bound of about 18 deg.
- The resulting camera has f of about 3600 px (horizontal FOV about 15 deg) and a pitch of about 27 deg.

## Result
- Back-projecting the image displacement onto the horizontal plane gives speed by angle d:

| d (deg) | speed (m/s) |
|---|---|
| 24 | 1.08 |
| 25 | 1.03 |
| 26 | 0.99 |
| 28 | 0.92 |

- Answer: **1.0 m/s**.

## Confidence
Low to medium. If the ground truth instead follows the depth labels (transverse motion only), it would be about 0.5 m/s. If the labelled origin is nearly static, it would be about 0.04 m/s.
