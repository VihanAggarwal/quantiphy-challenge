# simulation_0101 — boat + shark (A2MS), prior: shark acceleration = 1 m/s^2

## Method
- 1920x1080, 73 frames @24 fps, static perspective camera. Boat floats on water surface, shark swims underwater; both move left.
- Video frames 0 and 1 are identical (motion starts at frame 1); fits use frames >= 1 with t = k/24.
- Shark track: median-background subtraction mask + template matching. Centreline features (dorsal fin template, tail tip) give
  pixel acceleration 85.7-86.0 px/s^2 (side-surface body templates give ~86.8, slightly larger as they lie nearer the camera).
  Adopted 85.9 px/s^2  ->  scale 85.9 px/m (0.01164 m/px).
- Shark speed: parabola fit gives 172-173 px/s at t=0 -> 2.00 m/s (175.6 px/s at frame 1 = 2.04 m/s).
- Boat: template matching of parts. Centreline parts (bow, keel, rudder, stern pole) move 17.88 px/frame = 429.1 px/s;
  near-side hull text 18.75 px/frame (perspective: near side ~4.6% closer), confirming real perspective.
  Boat speed = 429.1/85.9 = 4.995 m/s (constant).
- Depth check: the water box front edge (y=672) is closer than the boat (keel at y~637, horizon 567), so the shark's depth
  is not geometrically pinned. Single-scale assumption confirmed by round numbers: boat 5.00 m/s, boat 10.0 m, shark v0 2.00 m/s.
- Boat length: mask x-extent 861-863 px over frames 30-72 (stern/bow effectively on centreline) -> 10.0 m.
- Shark length: snout tip (pale see-through head region included) to tail tip 280-282 px -> 3.27 m.
- Shark height: dorsal fin tip (851.5) to near pectoral fin tip (955.7) = 104 px raw = 1.21 m; near pectoral fin tip is
  pushed down by perspective (camera looks down ~345 px / f~2800) by ~4-6 px -> ~99 px -> ~1.15 m. Answer 1.16 (hedge).

## Answers / confidence
- 191 shark speed @0 s: 2.0 m/s (high; ~2.0-2.04 depending on convention)
- 192 boat speed @1 s: 5.0 m/s (high)
- 193 boat length: 10.0 m (high)
- 194 shark length: 3.27 m (medium-high)
- 195 shark height: 1.16 m (medium; 1.14-1.21 depending on perspective of pectoral fin)
