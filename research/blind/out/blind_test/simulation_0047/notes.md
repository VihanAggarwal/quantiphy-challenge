# simulation_0047 - notes

Scene: Blender street, camera looking straight down (nadir ~ image centre), perspective (booth/stair sides visible).
Prior: walking person (top sidewalk, walks -x) speed 1.236 m/s. fps 33, 99 frames, 1920x1072.

## Tracking (template matching, subpixel)
- Walker head: 110.1 px/s mean over whole gait cycles (frames 0-85; step period 17 fr).
  -> scale at head height (~1.65 m): s_wh = 1.236/110.1 = 0.011226 m/px.
- Moving bicycle (+rider), constant velocity: rear rack 420.5-421.9 px/s, rider head 432.5 px/s (y drift 5 px/s).
  Ratio rider-head/rack = 1.0285 (perspective: different heights).

## Camera height H (only enters as few-% height corrections)
- Booth: roof edge vs base edge radial ratio k = 1.10-1.126 -> h_b/H ~ 0.10.
- Walker head vs stance-foot offsets: h/(H-h) ~ 0.068.
- Rider head vs rack ratio 1.0285 -> dh/(H-h) consistent with dh ~0.7 m.
- Adopted H = 25.5 m, f = 2124 px (HFOV ~49 deg); s(h) = (H-h)/f; ground s_g = 0.01200 m/px.
- Cross-check: step length 54 px ground = 0.65 m x 1.94 steps/s = 1.26 m/s (prior 1.236).

## Answers
- Q15 booth width: roof 110.9 x 111.0 px at roof height; s_roof = s_g/k = 0.0108 -> 1.20 m (conf. medium-high).
- Q16 planter between staircases: hedge+fence span x 1128.6-1398.6 px; left end hidden by stair cheek wall
  (face at X~1.94 m), right end 5.08 (hedge top) / 5.18 (fence) / 5.32 (stair face) m -> 3.12-3.38; answer 3.28 m (conf. medium).
- Q17 bicycle length: rack-stabilised stack (frames 42-58, bike at image centre): front tire tip -130 px, rear reflector +20 px
  rel. rack -> 150 px; with heights 0.34/0.6 m -> 1.76 m (conf. medium-high).
- Q18 bicycle speed at 1.0 s: constant 12.75 px/frame; 420.5 px/s rack (h~0.87) / 432.5 px/s rider head (h~1.55) -> 4.88 m/s (conf. high).
