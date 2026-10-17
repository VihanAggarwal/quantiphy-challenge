# Audit simulation_0217 family (simulation_0211, simulation_0212): living room with black cat, bench, lamp, vase, floor mirror, dog

Result: **no fixes**. All 28 rows were checked. The current answers agree with this family's 3D twin and its 2D siblings, and with my own re-measurement.

## Cross-clip table (3D rows, compared with the same room's 2D siblings 0210/0213/0216 and top views 0214/0215/0217/0221/0222)

| quantity | 0211 | 0212 | 2D / top-view siblings | verdict |
|---|---|---|---|---|
| cat length | 0.706 | 0.675 | 0.672-0.70 | ok |
| cat height | 0.49 | 0.49 | 0.48-0.49 | ok |
| bench length | 1.024 | 1.05 | 0.99-1.02 (top), 1.08-1.15 (side 2D) | ok |
| bench height | 0.457 | 0.455 | 0.45-0.464 | ok |
| shade height | 0.248 | 0.255 | 0.238-0.263 | ok |
| shade diameter | 0.508 | 0.516 | 0.494-0.529 | ok |
| lamp height | 0.697 | 0.70 | 0.68-0.71 | ok |
| vase height | 0.52 | 0.525 | 0.507-0.532 | ok |
| mirror height | 1.444 | 1.445 | 1.43-1.453 | ok |
| mirror length / width | 0.631 | 0.63 | 0.575-0.628 | ok. Both clips also ask height, so "length" means the horizontal side |
| cat range at 0.5 s | 4.317 | 4.317 | - | ok |
| cat range at 1.5 s | 4.687 | 4.685 | - | ok |
| dog speed at 1 s | - | 1.00 | 1.04 (0213), 1.056 (0214), 1.08 (0217) | ok |
| dog speed at 1.5 s | - | 0.92 | 0.935, 0.881, 0.95 | ok |
| dog length | - | 1.12 | 1.00, 1.121, 1.08 | ok (pose dependent) |
| dog height | - | 0.61 | 0.57 | ok (pose dependent: back 0.57, tail raised 0.675) |

## Camera check (scripts/cam.py, scripts/cattrack.py)

- Camera model: f=2130, principal point (960,538), level, camera height 0.784. Wall vanishing points are at u=4920 and u=-181, and the two directions are orthogonal (dot product 0.0017).
- Closest bench leg foot (1405,840) gives a range of 5.703, against 5.69 given.
- Cat track on 0211, with the background taken as the median frame: the centroid track on the plane c=4.0 is linear (residual 1 cm).
  - Fitted speed 0.945 m/s, against the 0.94 prior.
  - Ranges 4.18 and 4.49, against the labels 4.199 and 4.481.
- So the camera is validated, and the cat-distance answers (an r^2 = D^2 + a^2 fit) stand.

## Dog (scripts/dogmask.py, dogworld.py, dogspeed.py)

- Dog background comes from 0211, which uses the same camera and has no dog.
- The paws give the dog's midline at c0 ≈ 3.73 (near paw 3.64, far paw 3.83).
- Torso template track converted to the along-wall coordinate a:
  - The dog is nearly still for 0-0.25 s, peaks at about 1.13 m/s around 1.25 s, then slows to about 0.3 m/s at 2 s.
  - v(1.0) = 1.00-1.04 and v(1.5) = 0.96-0.98, using central or local-quadratic fits. The c0 uncertainty is ±1.3%.
- Depth-label anomaly, confirming the 0212 agent's note:
  - Label t=0 (5.094) gives origin a=3.43, which is the body centre (centroid 3.37).
  - Label t=0.5 (4.625) gives a=2.69, but the body is at 3.07-3.10 at 0.5 s. It only reaches 2.62-2.69 at about 1.0 s.
  - The labels imply 1.5 m/s average over 0-0.5 s, while the visible motion averages 0.55 m/s there.
  - This fits a label taken at the wrong time (0.5 s written for about frame 24) or a time-scale or offset slip for the dog only. The cat labels have no such slip.
  - The question timeline (speed at 1 s and 1.5 s inside a 2.04 s clip) matches the video timeline. The visible-body route also agrees across four independent clips (0212, 0213, 0214, 0217).
  - So no second route supports any other value, and the dog speeds are kept. This is a residual risk, not a fix.
