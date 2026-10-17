# Audit simulation_0308 family (whale: clips 0304 V3SX / 0306 V3SS / 0308 V3SC)

## Family structure
- All three clips are one render with different backgrounds: 0304 is plain blue water, 0306 is a grey studio floor with a shadow, and 0308 is a caustic sea floor with a shadow.
  The head template sits at the same pixel in all three clips (within 2 px) at frames 1, 36 and 71 (frames_cmp.py).
  The prior (speed 1.67 m/s) and depth_info (33.7307 m at 1 s, 35.1624 m at 2 s) are the same in all three clips.
  The fps is 24 and each clip has 72 frames. Video frame 0 duplicates frame 1 (mean abs diff 0.03).
- So the whale has one true length, and the 0.5-1.0 s displacement is one value for the whole family.

| qid | clip | quantity | current | provenance | agent method |
|---|---|---|---|---|---|
| 1474 | 0304 | length | 19.5 | agent | projective axial ruler from V, head depth from SIFT scale; rostrum-notch 19.1-19.9 plus fluke sweep |
| 1479 | 0306 | length | 20.5 | agent | projective ruler u = u_VP + K/Z; notch 19.2, extreme tip 22.2 |
| 1484 | 0308 | length | 20.3 | agent | 3D reconstruction, f solved per V; snout to fluke tips 20.1-20.8 |
| 1475 / 1480 / 1485 | all | displacement 0.5-1.0 s | 0.835 | pre-agent | 1.67 x 0.5 |

The lengths are 19.5 / 20.5 / 20.3, a spread of +/-2.5% around 20.1. Nothing in the family is inconsistent:
no clip is scaled off, measures a different object or uses a different convention.

## My re-measurement (0304, cleanest background; scripts track.py, fitV.py, length.py, constvel.py)
- Mask: cubic-polynomial background with a colour-distance threshold (masks.py). The mask includes the grey rostrum.
- KLT tracks (forward-backward check < 0.3 px) on the head and fore-body. Pectoral-fin tracks curve (the fins flap) and were rejected by residual.
- Pure-translation fit x(t) = V + (A - V) n/(n + t). Using head tracks only, the best V is (-269, -362) with track rms 0.76 px.
  The cost is shallow along the track direction.
- Length from the f-independent axial ruler: lambda = |v| tau_snout r_snout / r. tau_snout comes from head tracks collinear with V.
  Rearmost silhouette point at frames 1 and 48, where the whole tail is in view:
  - V (-269,-362): 19.4 / 20.4 m
  - V (-500,-536): 20.8 / 21.5 m
  - V (-653,-624): 21.7 / 22.0 m
  - V (-755,-680): 22.1 / 22.4 m
  The rearmost single fluke tip overstates the axial extent by about 0.5 m.
  Range: 19-22 m. Every current answer sits inside it, and none is 15% from any value in it.
- Constant velocity: the mean head image speed falls smoothly, 3.35 -> 3.21 -> 3.09 -> 2.95 -> 2.83 -> 2.75 px/frame in 12-frame blocks.
  That is the projective decay of a receding body. There is no start-up acceleration in frames 1-24, and the signed model residual is under 0.5 px.
  So the 0.5-1.0 s displacement is 1.67 x 0.5 = 0.835 m. The 0308 agent's 3D reconstruction independently gave 0.836-0.841.
- Caveat: the deceleration-based V is closer to the image than the depth_info geometry allows (the 0308 agent saw the same).
  So V is the main uncertainty. It moves the length by about +/-7%, which is not enough to support any >=15% change.

## Decision
- No fixes. The three length rows agree with each other (+/-2.5%) and with my own re-measurement (19-22 m).
  The displacement rows equal the exact prior times 0.5 s, and the image motion confirms constant velocity.
- Possible later refinement, below the fix threshold: give all three length rows one common value of about 20.1 m, since it is one render.
