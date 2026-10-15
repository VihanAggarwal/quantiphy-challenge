# internet_0023: drone top-down view of a pool, swimmer (prior: swimmer height 1.8 m)

Camera: near-nadir drone shot, 2560x1440, 130 frames at 30 fps. It drifts slowly: by frame 129 the
ORB+RANSAC similarity on the deck background gives scale 1.0035, rotation <0.07 deg and a shift of about -15 px.
Swimmer positions are mapped into frame-0 coordinates (work/cam.py -> work/cam.json).

Scale: in frames 0-2 the swimmer is stretched out and clearly visible. Toe tips to crown measure 207-214 px
(frame 0: 578 -> 785). Toe tips to fingertips, with the arms stretched forward, measure about 257 px.
I used S = 217 px per 1.8 m (0.00829 m/px). This is the head-to-toe reading, nudged slightly toward the
arms-included reading as a hedge.

Measurements (frame 0, px):
- Main pool water surface, inner coping edges (excluding the stair alcove): x 566 -> 1725 = 1159 px;
  y 477 -> 1018 = 541 px. The keystone effect is under 1%.
- Deck chair: the top two loungers (fully visible) measure 247.5 px along their axis. The bottom ones are
  hidden by plants; the bottom-left one is about 240 px.
- Left umbrellas: the hubs are 481 px apart and the white-region centroids 474 px apart; I used 479.
- Swimmer: the head (hair) is at x=773 in frame 0. From frame 17 on, a flat grey patch covers the head and
  shoulders; I tracked it automatically (work/blob2.py) and it reaches x=1418 by frame 129 in frame-0 coordinates.
  Head displacement is 645 px. The body or bounding-box centre gives about 665 px and the pelvis about 698 px.
  I used 655 px over 4.3 s, which is 152 px/s.

Answers (m, m/s): pool length 9.61, width 4.49, chair 2.05, velocity 1.26, umbrella distance 3.97.
If the annotator measured toe to fingertip (257 px), every answer would be about 16% lower.

Confidence: pool length and width medium-high (pixels are precise; the swimmer's pixel length is the main
risk); chair medium; umbrellas medium; velocity medium (which body point was used, and the stroke phase at
the endpoints).
