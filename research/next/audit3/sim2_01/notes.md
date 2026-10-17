# Audit sim2_01: family simulation_0210 / 0213 / 0214 / 0215 / 0216 / 0216_segmented / 0217

Every clip has the same prior: black cat speed = 0.94 m/s, 24 fps, 50 frames, 1920x1080. All 76 rows are scored.
None of them has 'stated fact' or 'earlier audit fix' provenance. No labels or validation data were opened.

## Scene and scale (my own measurements)
- **Front cameras (0210, 0213, 0216, 0216_seg).** The camera is level, so the horizon is at y=540. The cat follows the same path
  in every front clip: its left edge is at x 227, 330, 444, 547, 649, 760, 867, 969, 1075 at frames 0, 6, ..., 48.
  That is 17.67 px/frame, so s_cat = 0.94/24/17.67 = 0.002217 m/px at the cat's depth.
  The cat's ground contact is at y about 1017 (0213, 0216) or 1032 (0210), which puts the camera at h_c = 1.06 m or 1.09 m.
  At other depths the scale is s = (h_c - h_support)/(y_contact - 540). This is the same model the agents used, and it is sound.
- **Top-down cameras (0214, 0215, 0217).** The cat moves 10.97 px/frame, so s = 0.003570 m/px at the cat's back (h about 0.27).
  The leaning floor mirror is 199 px wide at its top edge and about 170 px at its bottom edge. With the mirror top at about 1.45 m
  (from the front views), that gives a camera height H of about 10 m and s(h) = 0.00357*(10-h)/9.73.
- **Systematic gap between views.** At the same object, front views read about 3-7% larger than top views:
  bench 1.06-1.09 vs 1.00, lampshade 0.53 vs 0.505, TV 0.99 vs 0.94-0.96, vase 0.27 vs 0.25. The mirror width agrees
  (0.62 vs 0.62). I could not tell which view is right. The gap is too small to justify any fix.

## Family table (current answers)
| object / quantity | 0210 | 0213 | 0214 | 0215 | 0216 (=seg) | 0217 | my quick check |
|---|---|---|---|---|---|---|---|
| cat length | .673 | .672 | .686 | .70 | .68 | .70 | 0.68 (front 305px, top 191px) |
| cat height | .488 | .48 | | | .49 | | 0.49 |
| bench length | 1.153 | 1.08 | .999 | .99 | 1.10 | 1.0 | front 1.06-1.09 (front edge), top 1.00 |
| bench height / width | .464 | .45 | w .40 | w .395 | .453 | w .40 | h 0.44-0.455, w 0.40 |
| lampshade height | .253 | .238 | | | .263 | | 0.25-0.264 |
| lampshade diameter | .521 | .512 | .506 | .50 | .529 | .51 | front 0.514-0.53, top 0.505 |
| lamp height | .695 | .68 | | | .71 | | 0.70-0.717 |
| vase height / diameter | .514 | .507 | | d .247 | .532 | d .26 | h 0.52-0.53; d top 0.246-0.255, front 0.27 |
| mirror height | 1.441 | 1.43 | | | 1.453 | | 1.45-1.466 |
| mirror width | .628 | .612 | .594 | .575 | .62 | .60 | 0.62-0.635 |
| TV length / height | | | | | .988/.65 | .94 | 0.984/0.64 front; 0.957 top |
| TV stand length | | | **1.68** | **1.52** | 1.823 | | **1.82 front; 1.78 top** |
| TV stand width / height | | | .381 | .424 | h .445 | .39 | w 0.39-0.42, h 0.443 |
| dog speed t=1s | | 1.04 | 1.056 | | | 1.08 | 1.10 (0213), 1.054 (0214/0217) |
| dog speed t=1.5s | | .935 | .881 | | | .95 | 0.936 (0213), 0.94 (0214/0217) |
| dog length | | 1.0 | 1.121 | | | 1.08 | 0.86-1.19, depends on tail pose |
| dog height | | .57 | | | | | 0.56 (back top) to 0.68 (tail up) |
| carpet diameter | | | 1.738 | 1.71 | | 1.72 | 1.735 (473 px, h about 0) |
| sofa length / width | | | 3.081/1.656 | 3.03/1.63 | | 3.03/1.68 | 3.05 / 1.65 (884 x 474 px) |

Every scored row was quick-checked. Rows 0216 and 0216_segmented are the same footage, so they share answers.
Dog speeds come from template tracking of the dog's torso, linking each frame to the previous one.
In both views the dog accelerates from rest, peaks around frame 31, then slows down.

| clip | t=1s (px/frame) | t=1.5s (px/frame) |
|---|---|---|
| 0214 | 12.6 | 11.25 |
| 0217 | 12.6 | 11.2 |
| 0213 | 22.4 | 19.0 |

## Rows looked at in depth
- **qid 601 (0215, TV stand length, 1.52): FIX to 1.80.** The agent measured 442 px, from x=710 to about 1152. At x=1152 the
  lampshade (x 1117-1265, centre 1191) starts to hide the stand. But the lamp stands *on* the stand, so the stand has to run on
  under the shade at least as far as the lamp base. That alone makes the length at least 1.70 m.
  - **Route A:** 0216 front view, where the stand is fully visible (segmented clip). The front face spans x 651-1423, which is
    773 px. Its depth comes from the top-surface back edge (y 777), which sits flush with the wall line (y 948), and the front
    edge (y 800). That gives s = 0.002354, so the length is **1.82 m**. Using the leg floor contact (y 988) instead gives 1.83.
  - **Route B:** 0215's own top-view scale. The left end is at x=710. The lamp axis is at the stand-top height, x=1180.
    In the front view the stand runs 0.135 m past the lamp axis (+38.5 px). That gives 509 px x 0.003506 = **1.78 m**
    (1.77-1.80 for H between 8.3 and 12). A second estimate puts the stand centre 0.05 m right of the TV centre, as the front
    view shows. That gives 514 px, which is 1.80 m.
  - The two routes agree within 2.5%. The current 1.52 is 15.6% below 1.80.
- **qid 588 (0214, TV stand length, 1.68):** the same error in a milder form. The agent assumed the stand is centred on the TV
  legs and got 485 px. It is only 6.7% below 1.80, so there is no fix under the 15% rule.
- **qid 563 (0210, bench length, 1.153):** the right end is cut off by the frame edge. The agent's 478 px mixes the far-left
  corner with an extrapolated end, and used an average-feet scale. The front edge at the front-feet depth gives
  460 px x 0.00237 = 1.09. In 0216, the bench top's front edge is x 24-477, which is 453 px, giving 1.06; the agents' 468 px
  there was the image bounding box, which mixes the front-left and back-right corners. The top views give 1.00.
  1.153 is 5.8% above its own clip's route and 15% above the top view. The routes disagree with each other by 8.5%,
  so there is no fix.
- **qid 584 (0213, dog height, 0.57) and the dog lengths (583/594/633):** these depend on the pose. The height runs from
  0.56 at the back top to 0.68 with the tail raised. The length runs from 0.86 to 1.19 depending on the tail. Nothing
  independent pins down which pose the label uses, so there is no fix. Confidence is low.
- Smaller gaps, with no fix: qid 575 (shade height 0.238 vs 0.264, 10%) and qid 605 (mirror width 0.575 vs 0.62, 7%).
  The agents' top-view mirror bottom edges (160-165 px) are low; I measure about 170 px.

## Fixes
| qid | clip | question | current | new | routes |
|---|---|---|---|---|---|
| 601 | simulation_0215 | TV stand length | 1.52 | 1.80 | front 0216 full extent 1.82; 0215 top-view scale with the hidden end placed from the lamp 1.78 |
