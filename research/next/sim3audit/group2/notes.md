# sim3audit group2: 0008, 0011, 0013, 0172 (+seg), 0188 (+seg)

Scripts are in `scripts/` and frames/crops in `frames/` (crops and half-res PNG/JPG; full-res frames deleted). No labels were read.
Siblings outside this group were used only as cross-checks (current answers from `submissions/trackA_cand_next_merge4.csv`, agent notes).

Real scene families (sim3_families.json lists these clips as singletons, but the test set has siblings):
- Boat/pier: 0007 (2D, stated boat length 3.62), **0008** (stated boat height 0.75), 0009/0009_seg (stated speed 1.5).
- Farm (bird, falling nest, house, cart): 0010/0010_seg (stated bird length 1.19), **0011**, 0012/0012_seg (stated bird speed 6), **0013**, 0014. 0011/0013/0014 have the gravity prior.
- Astronaut: 0169/0170 form one 2D/3D pair (drift), and 0171/**0172** form another (moon-hop).
  The 3D clip is the 2D animation plus a depth motion. The image tracks of 0171 and 0172 are nearly identical, but 0172's mask area grows 25k->36k px while 0171's stays flat (`scripts/astro_track.py`).
  So the 3D world motions differ, and accelerations cannot be transferred between them.
- Truck: 0187 (2D) and **0188**/seg, same acceleration prior 10.757.

## Frame timing
0013 (54 frames, 21.75 fps container), 0010 and 0008 have container fps below 24 with uniform timestamps.
- The wing-beat period, from bbox-height autocorrelation in `scripts/birdtrack.py`, is 17 mp4 frames in 0010, 0011 and 0013. 0011 is a true 24 fps clip.
- So mp4 frame index = original frame index. There are no spread-out drops, and the 24 fps time mapping the agents used is correct.

## Farm family table (current answers)
| quantity | 0010 (bird 1.19 used as world) | 0011 | 0012 | 0013 | 0014 |
|---|---|---|---|---|---|
| cart wheel diameter | 1.40 | 2.55 | - | 2.70 | 2.62 |
| door height | 2.87 | 5.30 | - | - | 6.00 |
| eaves width | 9.72 | 16.6 | 15.4 | - | 20.2 |
| cart max height | 1.75 | - | - | - | 3.27 |
| bird body length (agent's own, world) | (1.19 prior) | 2.4 | 2.11 | 2.85 | - |
| bird body length (current) | prior | 1.19 | 1.19 | 1.19 | - |
| wingspan (current) | - | **5.8** | 2.23 / seg 2.28 | - | - |

The gravity-calibrated clips (0011, 0013, 0014) agree on the cart (2.55-2.70) and on the house within about 15%. In world units, the bird is about 2.1-2.85 m long in all four clips that can measure it:
- 0011: VP f=2046 and gravity agree.
- 0012: from its 6 m/s speed prior.
- 0013: gravity.
- 0010: about 2.2 m if its house is the same house.

The stated 0010 bird length (1.19) is therefore about half of the world-space length.

**0010 cannot be a half-scale copy of the world.** With its own ranges, the cart-to-house origin distance is at least |55.083-30.374| = 24.7 m. In 0011 and 0014 that distance is about 31 m (ranges plus ray angles at their calibrated f). A world scaled by 0.53 would need about 16.5 m. The house, cart and barrels layout is identical.

So the bird-size labels use a unit that is about half of world. The most likely cause is that the bird's dimensions exclude a ×2 parent/rig scale. Bird speed priors are world (0012).

Consequences:
- **Group1 / 0010:** 0010's house and cart answers use the bird as a world anchor. They are about 1.6-1.9x too small against the rest of the family:
  - cart max height 1.75 × 1.87 = 3.27, the same as 0014's 3.27;
  - wheel 1.40 × 1.87 = 2.62;
  - door 2.87 × 1.87 = 5.4;
  - eaves 9.72 × 1.87 = 18.2.
  - The bird speed 4.29 is affected the same way.
  - This is not in this group's rows. It is flagged for the group1 auditor.
- 1062 / 1065, body length 1.19 (stated-fact transfer): **kept**. This is the family's bird-label convention. Risk: if the labels for those clips were world-space, the answer would be about 2.4 / 2.85.
- **1063, wingspan 5.8 -> 2.34.** The 5.8 is world-scaled, from the 0011 agent's heading-sensitive extrapolation. Within the same clip the body length is 1.19, which gives a span/length ratio of 4.9.
  - Top-down 0012_segmented (`scripts/bird12_ratio.py`): the x-extent along the flight direction is stable at 124-140 px (median 130). The max y-extent across the wings is 256 px (frames 17-18, 33). That gives span/length = 1.97 (range 1.83-2.06), so the span is 1.97 × 1.19 = **2.34**.
  - Crow proportions (span ≈ 2.0 × length) give 2.38.
  - The family's current 0012 wingspan answers are 2.23 and 2.28.
  - Even in world units, 5.8 is 23% above 2.4 × 1.97 = 4.7.
  - Risk: if wingspan labels are world-space while body length is not, about 4.7 would be right.
- 1059 door 5.3, 1060 wheel 2.55, 1061 eaves 16.6 and 1066 wheel 2.7 sit inside the world-unit family spread: wheel 2.55-2.70; door 5.3-6.0 (5.4 from 0010×1.87); eaves 15.4-20.2 (18.2 from 0010×1.87). Kept.
  - Door/eaves ratio: 0011 gives 0.319, while frontal 0010 gives 0.293 and 0014 gives 0.297. So 0011's door may be about 8% high or its eaves 8% low. That is under the threshold.
- 1058 bird speed 0.5-1.0 s = 6.1 and 1064 speed at 1 s = 9.7 are kept.
  - The flights differ between takes: 0011 accelerates through the whole clip, while 0012 and 0013 ease in and out. So there is no sibling value.
  - The tracks (`*_birdtrack.json`) agree with the agents' pixel velocities: 0013 shows about 18-19 px/frame at frame 24.

## Boat family (0008 vs 0007, 0009)
- Pier width: 1.60 vs 1.48 / 1.68. If 0007 is rescaled to the shared boat speed 1.5 (it measured 1.40 with the length prior), its width becomes 1.585.
- Pier length: 5.9 vs 5.8 (6.2 rescaled) / 5.4.
- Gap at 3 s: 2.05 vs 1.88 (2.01 rescaled) / 2.25.
- Stairs width: 1.78 vs 1.9. Deck height: 0.415 vs 0.44. Cabin floor: 1.15 vs 1.08.
- Speed 1.5 equals the stated 0009 prior.
- 0008's zero-draft scale is confirmed by its own ranges (h_w 1.274 vs 1.305) and by the speed.

All rows are within 10% of the siblings. Kept.

## Astronaut 0172 (+seg)
- Speeds 1.74 / 5.15 / 2.28 / 1.5 are calibrated from depth plus the default 50 mm lens (f=3200). This calibration is independent of the 2.2 m prior, and it agrees with the height-prior route (3180). Kept.
- Accelerations 0.45 / 0.5 / 0.15 / 0.9 are near stationary points of the speed curve and have low confidence.
  - 0171 is not the same 3D motion (see above), so its 0.20 / 0.36 / 0.05 / 0.15 is not a valid cross-check.
  - There is no second route, so they are kept.

## Truck 0188 (+seg)
- The calibration is careful: VP f=2682 matches depth f=2690, and the constant-acceleration fit has rms 0.2 px with start at t0=0.
- Against 0187: length 8.2 vs 8.78 (0187 never sees the whole truck), height 3.41 vs 3.36, tire 0.78 vs 0.773.
- Speeds 10.67 / 16.05 are within 1% of the backward-difference values 10.58 / 15.96 (a·(t-1/60) from rest).
- Width 2.55 is a hedge between the body width 2.27 and the mirror span of about 2.6 (AABB). Kept.

## Fixes proposed
| qid | clip | current | new | basis |
|---|---|---|---|---|
| 1063 | 0011 | 5.8 | 2.34 | family bird length 1.19 × top-down span/length 1.97; crow proportions give 2.38; 0012's answers are 2.23/2.28 |
