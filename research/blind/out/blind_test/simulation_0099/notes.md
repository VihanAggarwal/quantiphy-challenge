# simulation_0099 (S2MS): boat and shark, fixed camera, 24 fps, 73 frames (frames 0 and 1 are identical)

## Scene
- Red fishing boat "AH805" on the water surface, moving to the right at constant speed. A shark below the surface moves left at constant speed.
- Static perspective camera. The sea-sky line is at y=566.2, the boat's keel and rudder meet the water at y=637.6, and the water surface ends at y=671.8. Below that line is uniform blue (the underwater area).

## Scale (prior: boat length = 10 m)
- The boat's horizontal extent, from the stern hull to the bow tip, is 859.5 +- 1 px. It stays the same across frames 1-47. Both extreme points move at the centreline velocity, so they lie at the centreline depth.
- Scale: 85.95 px/m.

## Motion (template tracking, linear fit over frames 1-47 for the boat and 1-61 for the shark; no measurable acceleration)
- Boat centreline features (rudder, bow tip, stern pole, mast, bbox edges): 17.88 px/frame = 429.1 px/s, giving **4.99 m/s, answered as 5.0**.
- Shark centreline features (dorsal fin, caudal fin, mid-body): 10.750 px/frame = 258.0 px/s, giving **3.00 m/s**.
- Near-side features move faster, which confirms the camera is perspective: the cabin near face is +2.5%, railing A +2.0%, the shark's pectoral fin +1.1 to 1.7%.

## Shark size
- Length: snout tip (x=421 at frame 24) to upper caudal tip (701.5) is 280.5 +- 1.5 px, giving **3.27 m**.
- Height: dorsal fin tip (851.5) to pectoral fin tip (957) is 105.5 px. The pectoral tip is about 1.5-1.7% closer to the camera than the centreline (from its velocity ratio), so it appears about 6 px too low. After correcting for that, the height is about 99.5 px, giving **1.16 m** (1.23 m without the correction).

## Main risk: depth of the shark
- The method assumes the shark is in the same depth plane as the boat. Reasons:
  - This is a 2D video with no depth_info, so the question is only answerable if the two share a plane.
  - With one scale, both speeds come out as exact whole numbers (boat 4.99, shark 3.00).
- Alternative considered: the shark sits at the front face of the blue water region, about 0.68-0.74 of the boat's depth. This would multiply all shark answers by about 0.70. Two things pointed this way:
  - The shark is not tinted blue.
  - There is a soft dark halo above the shark.
  
  Both are equally consistent with a backdrop just behind a shark at the boat's depth, so they do not separate the two options. A pale patch on the snout looked like a cut by a plane, but the shark has no yaw and its closer pectoral fin is not cut, so I treat the patch as a flaw in the 3D model.

## Confidence
- 183 boat speed: high.
- 184 shark speed: medium-high. The answer depends on the same-depth assumption; if it is wrong, the shark speed would be about 2.0-2.2 m/s.
- 185 shark length: medium-high, same dependency.
- 186 shark height: medium. It also depends on the pectoral-fin depth correction (range 1.15-1.23 m).
