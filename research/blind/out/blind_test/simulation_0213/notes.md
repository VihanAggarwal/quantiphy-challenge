# simulation_0213 (V2MC, 24 fps, prior: cat speed 0.94 m/s)
Static camera, near-zero pitch (vertical edges vertical; lampshade bottom rim nearly edge-on). Horizon assumed y~540 (results robust for 540-580).
- Cat track (dark mask + bg diff): 17.9 px/frame = 429.6 px/s -> s_cat = 0.002188 m/px. Cat ground-contact y ~1015.
- Camera height h = s_cat*(1015-540) = 1.04 m. Per-object scale s = (h - support height)/(y_base - 540).
- Dog ground centre y ~1052 (near paws 1067, far 1037) -> s_dog = 0.00203 (0.928 x cat).
- Bench: front feet 990/back feet 965, top 782-797; height 0.45 (front and back routes agree). Length ~465 px (slat end right is at frame edge) at s~0.00233 -> 1.08.
- Lamp/vase on bench top (base y 788/790): s ~0.00238/0.00236. Lamp 286 px -> 0.68; shade h 100 px -> 0.238, dia 215 px -> 0.512; vase 215 px -> 0.507.
- Mirror (leaning): top width 241 px, bottom 252 px (ratio 1.046); width 0.612 by both ends; height = h + 151.5*s_top = 1.43.
- Dog speed: torso template matching + Farneback flow on back band; backward diff px/frame: t=1s ~21.3, t=1.5s ~19.2 -> 1.04, 0.935 m/s.
- Dog length varies with tail pose 455-578 px (median ~475) -> answered 1.0 (hedge). Height back top 780 to centre ground 1052 = 272 px -> 0.55; tail-up frames 0.65; answered 0.57.
Confidence: cat sizes, mirror, bench height high; lamp/vase medium; bench length medium (edge cut); dog speeds medium; dog sizes low-medium.
