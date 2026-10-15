# simulation_0171 (S2SS, astronaut leap on Moon, 24 fps, 80 frames, 2304x1296)

## Method
- Static camera, side view. Median background -> foreground mask (excludes darker shadow pixels) -> bbox/centroid per frame (work/mask.py).
- Pelvis track: rotation+translation template matching of the rigid backpack/upper torso (always against black sky), sub-pixel,
  angle search +-10 deg (work/tmpl2.py). Four reference templates (frames 12, 24, 48, 72); each segment uses the template from inside it.
  Pelvis = torso centre + R(theta)*offset (hip joint ~ (32,112) px from backpack centre at frame 48; offsets 90-125 px tested).
- Motion has velocity discontinuities at frames 14/15, 29/30, 60/61 (stitched clips / root keyframes); fits never cross them.
- Speed = backward difference |p(t)-p(t-1)|*fps from local polynomial fits (half-window 5-8, deg 2-3); accel = (v(t)-v(t-1))*fps of fitted speed.

## Scale
- Height 2.2 m. Tight pixel heights: frame 0 = 335 px; standing-like frame 78 = ~356 px; legs-spread airborne frames ~360 px.
- Template scale search shows the astronaut appears ~3% smaller at frames 0-24 and ~2.5% larger at 72-78 than at frame 48 (slight approach to camera).
- Standing/rest height normalised to frame-48 scale ~342-350 px -> 346 px => 6.36 mm/px at frame 48; local factors 0.975 (f12), 0.978 (f24), 1.025 (f72).
- Gravity is not ballistic (keyframed/mocap animation), so it cannot be used for scale.

## Results (pelvis)
| qid | quantity | value | confidence |
|---|---|---|---|
| 427 | v(0.5s) | 1.80 m/s | medium (pelvis vs torso differ ~8%: 1.70-1.91) |
| 428 | a(0.5s) | 0.33 m/s^2 | low (sign ambiguous, -0.5..+0.4) |
| 429 | v(1s) | 5.53 m/s | medium |
| 430 | a(1s) | 0.55 m/s^2 | low (0.38-1.1) |
| 431 | v(2s) | 2.32 m/s | medium-high |
| 432 | a(2s) | 0.12 m/s^2 | very low (near zero) |
| 433 | v(3s) | 1.39 m/s | medium (1.20-1.50 across refs) |
| 434 | a(3s) | 0.30 m/s^2 | low (0.07-0.9) |

Main systematic risk: which pose defines the 2.2 m height (+-4%), and pelvis vs root origin.
