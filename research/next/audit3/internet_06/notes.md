# audit3 / internet_06 (internet_0043, internet_0048, internet_0055)

Each family has one clip only, so there is no cross-clip comparison. The audit is a per-clip re-measurement plus a check of the scale decision.
Scripts are in work/ (track43.py, track48.py, fit48.py, person48.py, motion55.py). The PNG crops were viewed and then deleted.

## Result: no fixes proposed (0 of 24 scored rows)
One family-level risk is flagged (internet_0043, 2x scale). It is NOT a fix (see below).

## internet_0043  (prior: white ball v(1.0 s) = 33.38 cm/s)
Own ball track (HSV-white & bg-diff): the ball enters at f19 at ~75 px/frame, skids and slows, then rolls at a constant 44-45 px/frame from f30 on.
v(1.0 s) = 45.2 px/f = 1356 px/s. Ball diameter is 79-80 px (vertical). The camera is static.
- Literal prior: 0.0246 cm/px at the ball -> ball 1.97 cm, wine bottle ~15 cm, 0.8 L T-fal kettle ~8.4 cm, bottle cap ~1.6 cm. Physically impossible.
- The agent's 2x scale (0.0492 cm/px at the ball, x1.17 at the objects' depth with horizon ~400) gives ball 3.9 cm (ping-pong 4.0), 750 ml wine bottle 29.8,
  500 ml US-label bottle 22.5, T-fal Aprecia 0.8 L kettle 16.6 (spec ~17-18), cap ~3.2 cm. Every known-size object agrees with 2x within ~3%.
  No time shift in the track gives 22 px/frame (the speed is never below 44 px/f while the ball is visible), so the gap cannot be a speed taken at the wrong time.
- Verdict: the 2x is a deliberate, well-founded choice. The velocity label is most likely an fps or resolution slip by the annotators, and the tape-measured
  sizes are physical. NOT proposed as a fix.
  RISK: if the GT follows the prior literally, all 8 rows should be halved (3066..3073 -> 1.99, 8.5, 5.9, 15.05, 11.4, 4.9, 30.0, 12.15).
- Distances are centre-to-centre (the agent's definition). Edge-to-edge would be ~38 cm (kettle-plate) and ~17 cm (cylinder-bottle). The definition is ambiguous, so they are not changed.

| qid | quantity | current | quick check (2x scale, persp 1.17) | diff |
|---|---|---|---|---|
| 3066 | ball diameter cm | 3.97 | 80 px*0.0492 = 3.94 | 1% |
| 3067 | kettle height | 17.0 | 287 px*0.0577 = 16.6 | 2% |
| 3068 | cylinder height | 11.8 | 194 px -> 11.2 | 5% |
| 3069 | green bottle | 30.1 | 517 px -> 29.8 | 1% |
| 3070 | plastic bottle | 22.8 | 390 px -> 22.5 | 1% |
| 3071 | plate (bowl) height | 9.8 | 172 px -> 9.9 | 1% |
| 3072 | kettle-plate dist | 60.0 | centres 1022 px -> 59.0 | 2% |
| 3073 | cylinder-bottle dist | 24.3 | centres 410 px -> 23.7 | 3% |

## internet_0048  (prior: g = 9.8)
Own drift (phase correlation): -0.2 px/f in x and -0.37 px/f in y, which is compensated. Own projectile fit on the colour-mask centroid, f36-59:
a_y = 3550-3700 px/s^2 depending on the window (rms 0.8-1.9 px) -> 2.65-2.76 mm/px (mid 2.69). vx = 1935-1952 px/s.
Pads: 8 pads, seam spacing 216 px, height ~635 px (top 172-180, bottom 812). Aspect 2.94 matches a standard 2'x6' pad.
Floor-wall line is row 858 (f0). Ball contact is row 875 at f61 (= 897 at f0). Horizon is row 608 (the agent's) -> wall/ball depth 1.12-1.16.
Person: cap top ~178 and sole ~893 at f90 -> 715 px. Feet depth is 0.915 of the ball's. Head/torso x moves ~560 px from f75 to f105 (+4.5 px drift).

| qid | quantity | current | quick check | diff |
|---|---|---|---|---|
| 3102 | ball diameter cm | 24.0 | 91.5 px*2.65-2.76 = 24.2-25.3 | 1-5% |
| 3103 | pad width cm | 62 | 216 px*3.0-3.1 = 64-67 (standard 61) | 3-8% |
| 3104 | pad height cm | 184 | 635 px*3.0-3.1 = 188-197 (standard 183) | 2-7% |
| 3105 | ball-floor gap at 1.5 s, m | 1.39 | (880-351) px*2.65-2.76 = 1.40-1.46 (centre would be ~1.53) | 1-5% |
| 3106 | displacement 1.2-1.8 s, m | 3.10 | 1179 px*2.65-2.76 = 3.12-3.25 | 1-5% |
| 3107 | v(1.5 s) apex, m/s | 5.16 | vx*scale = 5.15-5.34 | 0-3% |
| 3108 | person height, m | 1.72 | 715*2.69*0.915 = 1.76 incl cap | 2% |
| 3109 | walking speed 2.5-3.5 s | 1.36 | 565 px/s*2.46 mm = 1.39 | 2% |

## internet_0055  (prior: average speed of "person riding scooter" = 1.95 m/s)
- The only rider-like object is a tiny far figure (white top, arms forward, seen from f34 to f74 behind the hedge at x 390 -> 282, y ~440-460).
  It moves ~90 px/s -> 21.7 mm/px at its depth. Its ground contact is hidden, so that depth cannot be carried to the near objects.
  It also conflicts with the Tesla (27.3 mm/px), which is nearer. The walker as a 1.95 m/s object would be 2.1 m tall, which is implausible.
  So the prior cannot set the scale here. The agent's ground-plane plus standard-sign-size route is the only workable one.
- Ground plane: Tesla Model Y top 437 / tyre 496 (1.624 m -> 27.3 mm/px). Combined with the bus (3.1-3.4 m over 225 px), this gives horizon 435-446 and camera height 1.37-1.66 m.
- Walker at t0: cap 425, feet 685-686, 260-262 px -> H = 1.50-1.73 across that horizon/camera-height range (centre 1.62).
- Bike diamond: pole base y~660 -> 6.95 mm/px -> bbox 1.13-1.16 m (30" W11-1 diagonal 1.078) and diamond bottom ~2.6-2.7 m.
  The plaque bottom is at ~2.14 m, which is exactly the 7 ft MUTCD mounting height.
- DO NOT ENTER (151 px) and YIELD (122 px): their pole bases are hidden by the foreground bushes. The occlusion bound gives >0.81-0.89 m for the DNE.
  The YIELD/plaque ratio of 1.44 favours 36".
Every row checks within ~10% of the current answer under the same geometry. The remaining uncertainty is in definitions, not in measurement:
- bike sign size could be the 0.76 m side or the 1.08 m diagonal;
- the bike sign's height above ground could be measured to the diamond or to the plaque;
- DNE could be 30" or 36".
None can be settled by two independent routes, so nothing is proposed.

| qid | quantity | current | quick check | note |
|---|---|---|---|---|
| 3151 | walker height m | 1.63 | 1.50-1.73 (centre 1.62) | ok |
| 3152 | DNE height | 0.91 | >=0.81-0.89 from bound; 36" std | ok |
| 3153 | DNE width | 0.91 | same | ok |
| 3154 | DNE to ground | 2.35 | 2.3-2.5 (base hidden) | low conf, kept |
| 3155 | bike sign height | 1.08 | bbox 1.13-1.16 (30" diag 1.078) | side-vs-diagonal ambiguity |
| 3156 | bike sign width | 1.08 | 1.10-1.13 | same |
| 3157 | bike sign to ground | 2.55 | diamond bottom 2.6-2.7, plaque 2.14 | definition ambiguity |
| 3158 | YIELD width | 0.91 | plaque ratio -> 36" | ok |

## Fixes
None.
