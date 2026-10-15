# simulation_0102 (A2MS, 2D side view, shark + boat), fps 24, 73 frames, 1920x1080
Prior: shark acceleration = 1 m/s^2. Static camera. Video frames 0 and 1 are identical (duplicated first render).

## Scale
- Shark tracked by template matching (front/body templates, sub-pixel) frames 1-58, quadratic fit x(t), t = frame/24:
  a = 86.9 px/s^2 (front 86.94, body 86.89; centroid 86.45; rms resid 0.06 px). Velocity vertex at t = -2.00 s.
- Scale s = 1/86.94 = 0.011502 m/px (planar 2D assumption: boat and shark in same plane).

## Answers
- 196 shark speed at 0.0 s: v(0) = 173.99 px/s -> 2.00 m/s (v0 = 2 m/s design; video frame 0 duplicate of frame 1). Conf: high.
- 197 boat speed at 1.0 s: constant velocity. Centreline features (mast, rudder, bow tip, stern antenna) 428-429 px/s,
  cabin front 440 px/s (parallax, Z~40 m), red-mask edges 428-431 -> 4.93-5.0 m/s -> 4.95. Conf: high.
- 198 boat length: x-extent 858-860 px (stern rub-rail 640 to bow 1500 at frame 24; masks 857-859) -> 9.88 m; if boat plane
  ~1% farther (5.0 m/s design) -> 10.0. Answer 9.9. Conf: medium-high.
- 199 shark length: nose tip (ghostly translucent snout) to upper tail-lobe tip 279-281 px -> 3.22 m. Conf: medium-high.
- 200 shark height: dorsal tip y 852 to pectoral tip y 956 -> 105 px -> 1.21 m. Conf: medium.
- 201 distance at 0.5 s (frame 12): shark bbox centre (721.7, 904); boat bbox x-centre 856 (dx = 134 px = 1.55 m).
  Boat origin height unknown (mast cut off by frame top): keel/bottom origin (y 638) -> 3.43 m; hull centre -> ~4.7 m;
  full bbox centre incl. mast (~y 300) -> ~7.1 m. Shark centre sits 3.06 m below the keel/water surface.
  Chose 3.9 m as expected-score hedge between hypotheses. Conf: low.
