# sim3audit group4: simulation_0159, 0164, 0168, 0176, 0180 (30 scored test rows)

Result: **no fixes proposed.** Every row either agrees with its sibling clips or differs only by a matter
of definition or a scale hypothesis that I cannot settle with two independent routes.

## Family structure (the inputs said "singletons", but they are not)
`sim3_families.json` lists all five clips as singletons. A search of the test parquet (question, prior and
depth_info text only, no labels) found 2D sibling clips of the same Blender scenes:

| 3D clip | 2D siblings (same prior) | scene |
|---|---|---|
| 0159 | 0157, 0158 (turtle a=2.639); 0154/0155/0156 (shark v=7, another take) | shark + leatherback |
| 0164 | 0163 (ball D=0.21); 0162 is a different roll | bowling |
| 0168 | 0165, 0166, 0167 (bike v=5.52) | crossroads, bike + police VW T5 |
| 0176 | 0173, 0175 (plane v=153.582) | jet + rock stack |
| 0180 | 0179 (trolley a=1.507) | trolley hall |

## Cross-clip table (current answers in trackA_cand_next_merge4.csv)
| quantity | 3D clip (this group) | 2D siblings | verdict |
|---|---|---|---|
| shark length | 0159: 4.38 | 4.60, 4.60, 4.57, 4.52 | 3-5% low, ok |
| turtle length | 0159: **1.85** | 1.60 (0156), 1.52 (0157), 1.68 (0158) | 10-20% high, see below |
| turtle v(1), v(1.5) | 2.584, 3.903 | 2.51-2.61, 3.83-3.90 | ok (= a(t-1/48)) |
| shark a, v(1), v(1.5) | 6.82, 6.71, 10.12 | 0158: 7.01, 6.86, 10.37 | 2-3%, ok |
| shark-turtle depth diff | 2.13 | 0158 side view: body centres 410 px * 0.00496 = 2.03, bbox centres 2.38 | ok |
| ball v(0.5), v(1) | 0164: 3.37, 3.19 | 0163: 3.235, 3.049 | ok. Impact is at frame 38 in 0164 and frame 28 in 0163, so the takes are offset by about 0.4 s, which with k = 0.11/s accounts for the 4% |
| ball a(0.5), a(1) | 0.37, 0.355 | 0.371, 0.371 | ok. The evaluator takes abs(), so the sign does not matter |
| pin height | 0.328 | 0.328 | ok |
| bike wheel / length | 0.716 / 1.79 | 0.726 / 1.766-1.80 | ok |
| road crossed | 8.99 | 8.94, 8.96, 8.15 | ok |
| car road width | 6.7 | 6.15 (0167) | 9%, below threshold |
| van length | 4.4 | 4.59, 4.60 | 4%, ok |
| van tyre | 0.72 | 0.785 (0166) | 9%, below threshold |
| van speed | 6.87 | 6.88, 6.90 | ok |
| van width | **2.25** (mirrors included) | 1.87 (0167, top view, body) | 20%, depends on definition, see below |
| plane length / cliff / wheel | 47.8 / 42 / 1.23 | 47.2-47.9 / 43-44 / 1.20-1.25 | ok |
| trolley L / H / gate / tile / v1 / v2 | 1.11 / 1.17 / 3.99 / 0.48 / 1.49 / 3.00 | 1.12 / 1.21 / 4.0 / 0.5 / 1.5 / 3.01 | ok |

## Suspects examined

### 0164 bowling: prior scale vs depth scale (5 rows, kept)
- I confirmed the conflict (scripts/b164_ball.py). With the blue-mask ellipse the ball is 80-86 px at frame 12,
  so with the agent's VP focal length (f = 2395, orthocentre at the image centre) the range is 6.2-6.75 m.
  depth_info gives 9.391 m, a factor of about 1.4-1.5. Making the depth fit needs f of about 3400-3650.
- I tested two ways the depth could still be right while the clip is measured at ball scale. (a) The depth is at another
  time: no visible frame has the ball at 9.39 m in ball scale, because the pin deck is at about 8 m. (b) The ball origin is
  far from the ball: the ball rolls straight with a smooth exponential decay under rigid-body physics, so the origin must be
  at the centre.
- The leftover explanations are that the generator used another camera position (keep the answers), or that the prior is
  the local obj.dimensions under a parent scaled 1.5x (multiply the speeds by 1.505). The brief says the prior is exact.
  Ball scale is also the realistic world: ball 0.21 (real 0.218), pin 0.33 (real 0.38), lane 1.4 m, camera 1.2 m. Depth
  scale would give a 0.32 m ball and a 2.1 m lane. A gravity check could settle it, but pin toppling depends on the model
  (Bullet's inertia and centre of mass), and nothing in the clip falls freely where it can be seen.
- Kept. Risk: if the GT follows depth_info, rows 1386-1389 are x1.505 (and 1390 is too if the pins share the scale).
  0163, outside this group, would carry the same risk.

### 0159 turtle length 1.85 (row 1546, kept)
- The 2D siblings measured 1.52, 1.60 and 1.68 with the same acceleration prior. Their pose-dependent x-extent is 297-352 px,
  which is 1.47-1.75 m.
- A check inside 0159 that needs no f or depth: the head-blur front and the carapace rear tip move along the same 3D
  midline. The carapace tip reaches the image x that the head front had at frame 10 at about frame 29.2, so
  L = a/2 (t2^2 - t1^2) = 1.72 m from the head blur to the carapace tip. In the 0158 side view the same span is
  296-330 px (1.47-1.64 m), and the rear flippers add about 10 px.
- The face-blur ellipse changes size from frame to frame and may extend past the true head. In 0159 a lateral offset moves
  the image about 150 px/m, against about 106 px/m along the heading, so flipper tips cannot be placed on the midline.
  Neither route reaches 8% precision. The truth is probably 1.6-1.75, so 1.85 carries 6-15% error. That is not a clear
  error and is below the 15% bar, so no fix.

### 0168 van width 2.25 (row 1394, kept)
- 0167 (top view) gave 1.87, from a bright mask of the body. In the 0167 top view the dark mirror housings are almost
  invisible against the asphalt (frames/s0167_front_zoom.png shows a small dark bump at the A-pillar). In the 0168 front
  view the mirrors are clear (frames/simulation_0168_f048.png). The agent solved them in 3D: 2.30 m with mirrors and
  1.85-1.90 m for the body, the same proportions as a real T5 (1.904 / about 2.25).
- The answer depends on whether the GT AABB includes the mirrors. It is not a measurement error. Kept at 2.25,
  consistent with the AABB convention.

## Rules followed
No labels were used. Validation answers were not opened. No paid API was called. Only test inputs (question, prior and
depth_info text) and the videos were read. Scratch space is about 60 MB of PNGs and scripts, with no frame dumps.
