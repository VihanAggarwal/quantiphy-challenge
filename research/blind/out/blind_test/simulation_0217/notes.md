# simulation_0217 - top-down living room, black cat walks right, brindle dog walks left (24 fps, 50 frames)

## Scale
- Cat front/centroid track (dark threshold): 10.95 px/frame, very steady -> 262.8 px/s for 0.94 m/s
  -> 0.003577 m/px at cat feature height (~0.2 m).
- Camera looks straight down (vertical room corners radial from image centre). Perspective height cues:
  TV-stand front face (top edge y=281.5, bottom y=292 -> ratio 1.042 -> h_stand = 0.041 H);
  leaning floor mirror bottom width 165 px vs top width 196.5 px (ratio 1.19 -> h_top = 0.16 H).
  Typical stand 0.5 m / mirror 1.9 m both give H ~ 12 m above floor (FOV ~32 deg).
- s(h) = 0.003637 * (12 - h)/12 m/px (floor scale 0.003637).

## Measurements (px, assumed height of outline -> m)
- Cat length incl tail: median x-extent 191-194 px (max 200), h~0.15 -> 0.70 (conf medium)
- TV length: 283 px (x 811-1094), top ~1.1 m -> 0.94 (medium)
- Bench: 286.5 x 115.5 px top at ~0.45 m -> 1.00 x 0.40 (high)
- TV stand: depth 112.5 px (y 169-281.5) at h 0.49 -> 0.39. "Width" interpreted as the short horizontal
  (same convention as bench/sofa width). Long side ~522 px (right end hidden under lamp) -> ~1.8 m if the
  other meaning was intended. (low-medium)
- Lampshade: 150 px, rim ~0.8 m -> 0.51 (medium)
- Vase: 75 px at ~0.6 m -> 0.26 (medium)
- Floor mirror width: bottom 165 px at floor -> 0.60; top edge 196.5 px at h~1.9 m gives the same 0.60 (medium-high)
- Dog speed: frame-to-frame template tracking of torso and rump (2 templates agree): ~12.85 px/frame at t=1 s,
  ~11.3 px/frame at t=1.5 s; feature height ~0.45 m (s=0.0035) -> 1.08, 0.95 m/s (medium)
- Dog length incl tail: 275 px (f0, tail curled up) .. 329 px (f48, tail out); body 259 px -> chose ~1.08 m (low)
- Fur carpet: ~470-480 px diameter -> 1.72 (medium)
- Sofa: outline x 566-1451, y 522-997, corrected for heights (arms 0.7, back 0.8, seat front 0.35)
  -> 3.03 x 1.68 m (medium)
