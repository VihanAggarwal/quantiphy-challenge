# simulation_0158 (A2MS, 2D, 24 fps, 48 frames, 1920x1080)
Scene: static underwater camera; shark (top) and leatherback turtle (middle) both swim leftward, starting from rest at t=0
with constant acceleration (velocity fits give v0 ~ 0 px/s, quadratic position residual ~1 px).

Method
- Background = frame 0 (x<1700) / frame 47 (x>=1700) composite; diff-threshold masks (verified with overlays).
- Pixel accelerations from rigid features, rest-constrained quadratic fits x = c - 0.5 a t^2:
  - turtle: carapace rear-tip rows y540-560 -> 527-533; head-tip long baseline f0->f47 ~528; carapace patch TM 529-543;
    chained whole-band TM 550 (TM biased high ~4% on both animals, same for shark head). Adopted a_T = 532 px/s^2.
  - shark: dorsal-fin edges (rows 15-35) -> 1401-1413; nose rows rest-constrained 1413-1420; head TM 1468. Adopted a_S = 1413 px/s^2.
- Scale (2D planar, same depth plane): s = 2.639 / 532 = 0.00496 m/px. Ratio a_S/a_T = 2.656.
- Sizes: shark x-extent 906-918 px (frames 26-38, fully visible) -> 912 px; turtle head-tip to rear-flipper 297-350 px
  (pose varies) -> 338 px.
- Speeds: backward difference at frame 24 / 36 of constant accel from rest: v = a*(n-0.5)/24 (verified against measured
  per-frame fin/shell displacement: shark 57.7 px/f at f24, 88 px/f at f36).

Answers
- 364 turtle length 1.68 m (medium confidence; pose-dependent extent, +-5%)
- 365 turtle speed 1 s 2.58 m/s (high; analytic a*t would be 2.64)
- 366 turtle speed 1.5 s 3.90 m/s (high)
- 367/368 shark length 4.52 m (medium-high)
- 369 shark accel 7.01 m/s^2 (medium-high, depends on turtle px accel +-3%)
- 370 shark speed 1 s 6.86 m/s; 371 shark speed 1.5 s 10.37 m/s (medium-high)
Plausibility: shark 4.5 m (great white), leatherback 1.7 m -> consistent with same depth plane.
