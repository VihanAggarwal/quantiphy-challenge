# Audit internet_02 (clips internet_0030, internet_0070, internet_0053, internet_0044)

Scripts are in `scripts/`. Frames were read with OpenCV inside the scripts. The PNG crops I viewed were kept
only in the session scratchpad and deleted at the end. Nothing large is stored here.

## Family facts

* **internet_0030 is exactly frames 44..85 of internet_0070.** Each 0030 frame i matches 0070 frame i+44, with
  mean abs diff 0.6 against at least 2.3 for any other frame (all 42 frames checked). So both clips show the same
  boat in the same frames.
* The two priors do not agree under pixel geometry. With L_px/v_px about 12.8 frames (measured at f30, f59, f85
  and f120 of 0070; it stays constant because the boat recedes at constant speed):
  * 0030's "length = 3.2 m" gives v of about 7.5 m/s.
  * 0070's "v(1.00 s) = 11 m/s" gives L of about 4.7 m (205 px x 0.0230 m/px; the agent got 5.0 m from 217 px).
  * So the size scale and the motion scale of this footage differ by about 1.47x.
  * The real boat is a bowrider with a bimini top, and at least 4.5 m long. That fits the 11 m/s prior better
    than the 3.2 m prior. But the dataset states 3.2 m for this boat.
* internet_0053 shows the same kind of gap. Its speed prior (4.46 m/s) gives a 2.5 m person and a 1.6 m e-scooter.
  The current answers are the agent's prior-scaled values x 0.6495 (scooter rows x 0.666): person 1.62 m,
  scooter 1.08 m. That rescale is not in the agent notes or in qp/ code. It is a clip-level scale choice, not a
  measurement error. **Flagged, not changed** (see the policy note below).
* internet_0044 (g prior) is consistent with itself. The gravity scale gives a 3.9-4.2 cm ping-pong ball, close to
  the real 4.0 cm.

## Camera / tracking

* 0070/0030: the camera pans right. Background shift from phase correlation on the tree band: x -8 at f30, -28 at
  f60, -49 at f90, -57 at f120 (pan about 0.85 px/f around f45-85, then slowing). The boat was template-matched
  (template from f60, sub-pixel) and compensated by subtracting the pan. Compensated px/frame: f30 15.95, f60 14.87,
  f85 14.21, f120 13.36. Boat length in px (bow tip to transom, ruler crops): f30 205, f59 ~197, f85 ~182, f120 ~170.
* 0053: static camera (shake under 2-4 px). Rider px speed: the agent's wheel track gives 1452 px / 80 f = 544 px/s.
  My scooter template gives f0-70 18.5 px/f; with extrapolation, 545-554 px/s over the clip (decelerating
  20 to 16 px/f). Prior scale at the rider: 0.0081 m/px. The fixed objects stand further back (ground y 680-703 vs
  716; horizon about 595), so they get a perspective factor of 1.12-1.42.
* 0044: static camera. Ball tracked with a median background and a white-blob mask, refined at full resolution.
  Parabola fits by segment give g = 20.1, 19.8, 19.5, 19.3, 19.3 px/f^2. 19.5 px/f^2 -> 0.05584 cm/px (same as
  the agent).

## Rows checked (all 30 scored rows)

| qid | clip | quantity | current | quick check (route) | verdict |
|---|---|---|---|---|---|
| 3003 | 0030 | dist 0.5-1.0 s | 3.77 | 222.3 px x 0.01684 = 3.74 (raw image 3.54) | ok |
| 3004 | 0030 | dist 0.5-1.37 s | 6.43 | 381.8 px -> 6.43 (raw 6.10) | ok |
| 3005 | 0030 | speed 0.5-1.0 | 7.54 | 7.49 (raw 7.08) | ok |
| 3006 | 0030 | speed 0.5-1.37 | 7.39 | 7.42 (raw 7.04) | ok |
| 3007 | 0030 | avg accel 0.5-1.37 | 0.30 | 2D deceleration magnitude 0.39 (pan-compensated; local fits and interval speeds agree) / 0.22-0.26 (raw image) | ok (magnitude convention; world speed is constant) |
| 3259 | 0070 | boat length | 5.0 | own prior: 205 px x 0.0230 = 4.71; **twin 0030 states 3.2 m** | **FIX -> 3.2** |
| 3260 | 0070 | boat height | 1.55 | 60-65 px x 0.0230-0.0237 = 1.38-1.54 | ok under own prior (would be 0.96-1.02 if length is 3.2; flagged) |
| 3261 | 0070 | disp 1-4 s | 31.8 | 1314 px x 0.02299 = 30.2 (single scale) / 33 (constant speed) | ok |
| 3262 | 0070 | disp 2-3 s | 10.6 | 437.6 px -> 10.06 / 11.0 | ok |
| 3263 | 0070 | v(2.00 s) | 10.8 | 14.87 px/f -> 10.26 / 11.0 | ok |
| 3074 | 0044 | ball diameter | 3.91 | vertical extent at apex 74-75 px (f76, f86, f95) -> 4.13-4.19 | ok (6%) |
| 3075 | 0044 | kettle height | 15.97 | 508..794 = 286 px -> 15.97 | ok |
| 3076 | 0044 | cylinder height | 11.0 | 588..785 = 197 px -> 11.0 | ok |
| 3077 | 0044 | green bottle | 28.6 | 287..800 = 513 px -> 28.6 | ok |
| 3078 | 0044 | plastic bottle | 21.6 | 410..795 = 385 px -> 21.5 | ok |
| 3079 | 0044 | plate (bowl) height | 9.16 | 628..798 = 170 px -> 9.5 | ok |
| 3080 | 0044 | kettle-plate distance | 56.7 | centres 1325 - 310 = 1015 px -> 56.7 (gap 658 px = 36.7) | ok (centre convention) |
| 3081 | 0044 | cylinder-bottle distance | 22.9 | centres 411-415 px -> 22.9-23.2 | ok |
| 3082 | 0044 | v(1.50 s) | 0.886 | instantaneous 0.985, central 0.979, backward 0.885, forward 1.10 | ok (11%, under the threshold) |
| 3083 | 0044 | v(2.50 s) | 0.611 | **instantaneous 0.446, central 0.426**, backward 0.56-0.59, forward 0.32 | **FIX -> 0.44** |
| 3135 | 0053 | person height | 1.624 | 301-313 px x 0.0081 = 2.47-2.54 (prior scale) | current = 0.65 x prior scale: policy flag |
| 3136 | 0053 | lamp | 3.345 | 565-578 px, ground 703 -> 5.1-5.24 | same flag |
| 3137 | 0053 | scooter wheel-to-wheel | 1.079 | 194-207 px -> 1.57-1.68 | same flag |
| 3138 | 0053 | scooter height | 1.091 | 198-211 px -> 1.60-1.71 | same flag |
| 3139 | 0053 | sign height | 0.779 | 105-110 px at ground ~680 -> 1.21-1.27 | same flag |
| 3140 | 0053 | sign width | 0.474 | 66 px -> 0.76 | same flag |
| 3141 | 0053 | hydrant | 0.864 | 127 px at ground 685 -> 1.38 | same flag |
| 3142 | 0053 | bench width | 1.884 | 315 px at ground 699 -> 2.96 | same flag |
| 3143 | 0053 | bench height | 0.896 | 149 px -> 1.40 | same flag |
| 3144 | 0053 | trash bin | 0.753 | 124 px at ground 699 -> 1.17 | same flag |

The 0053 rows agree with each other at the current effective scale: object ratios match my pixel extents within
5%. The only open question is the clip-wide scale.

## Fixes proposed

1. **3259: 5.0 -> 3.2 m.** The dataset states "length of the speedboat = 3.2 m" for internet_0030, which is
   frame-for-frame the same footage. The 0070 agent never saw that clip. It derived 5.0 m from the 0070 velocity
   prior through the size-motion pixel relation, and the two priors of this family show that relation is off by
   about 1.47x. Route 2: the 0070 prior-implied length of 4.7-5.0 x the 0.6495 speed-to-size factor used by the
   current 0053 answers = 3.05-3.25 m. This is the same transfer the facts rule makes for same-base twins, which
   has no size guard. It is also the lower, safer value when the two hypotheses are about even.
2. **3083: 0.611 -> 0.44 m/s.** The agent used a one-frame backward difference. That is the mean velocity over
   2.467-2.500 s, centred on 2.483 s. The ball is 1.15 frames before its apex (f76.15), so vy changes by 0.32 m/s
   per frame and a half-frame shift inflates the speed by about 35%. At 2.50 s the parabola derivative gives 0.446
   (vx -14.7, vy -22.2 px/f) and the central difference gives 0.426. The internet label convention is unknown
   (simulation labels use backward differences, lab labels use forward ones), so 0.44 is also the minimax value
   between backward (0.56-0.59) and forward (0.32).

## Flags for the orchestrator (no fix proposed)

* **Policy conflict, prior scale vs family / real-world scale.**
  * Under "prior sets the scale" (pixel-consistent labels per clip), 0053 should be the agent's prior-scale values
    (person 2.5 m and so on; current is 35% low, i.e. the prior-scale values are 1.54x the current). Under that
    view, 0070's length would be 4.7-5.0.
  * Under one shared annotation per footage, with dataset speeds about 1.5x the size scale, the current 0053
    values are right. Under that view, 3259 = 3.2, 3260 is about 1.0, and the 0030 motion rows are about 1.38x
    current (0.5-1.0 s: 5.2 m; 0.5-1.37 s: 8.8 m; 10.3 and 10.2 m/s).
  * I kept the lower, safer value in each case, so the proposed set is coherent with the second view for 3259 and
    leaves the rest as hedges. If you have evidence for which view the internet labels follow, apply it to both
    families together.
* 3260: if 3259 becomes 3.2, the height/length pixel ratio (0.29-0.33) gives 0.96-1.06 m. Current 1.55 holds only
  under the 0070 prior scale.
* 3082: the instantaneous value (0.98) is 11% above current. Leave it unless the convention for 3083 is settled.
