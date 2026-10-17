# Audit internet_13 (clips 0003, 0011, 0016, 0023, 0031, 0051)

Scope: 27 scored rows. Every row is S2 except 0051, which is D2. Each "family" holds a single clip, so there is no cross-clip
comparison to make. For step (1) I checked each clip's scale against other markings in the same scene instead
(court, pitch and key dimensions). I read every clip's agent notes. I quick-checked every scored row with my own
pixel reads or tracks on full-resolution crops; the crops (jpg) are in this folder and the scripts are in `scripts/`.
Frame times use the stated fps.

## Scale checks
| clip | prior | scale used by agent | independent check |
|---|---|---|---|
| 0003 | monopoly bill width 7.5 cm | short side about 165-177 px | Bill short sides read: 150 px (top 500 bill, vertical, foreshortened), 160 px (100 bill), 172 px ("1" bill). The 100 bill sits at the pizza-centre row; its long side is 340 px, and with aspect 1.92 that gives 177 px per 7.5 cm. The convention (short vs long side) is the dominant risk and cannot be resolved from the frames, so I kept the agent's 70/30 call for the short side. |
| 0011 | court (key) width 4.88 m | 1077 px, 220.7 px/m | Volleyball court overlay: 1997 px = 9.05 m (9.00 m true). Outer sidelines: 3333 px = 15.1 m. Scale confirmed to under 1%. |
| 0016 | inner court (key) width 4.88 m | 640 px | Key length 5.80 m and court width / key = 3.07 (agent). My read of the bottom key is 634 px. Confirmed. |
| 0023 | swimmer height 1.8 m | 217 px | My toe-to-crown read at frame 0 is 206 px (578 to 784); toe to fingertip is about 250 px. The agent's 217 is 5% off head-to-toe, so all 0023 answers would be about 5% higher with 206 px. That is under the threshold. |
| 0031 | goal frame 7.32 m | 98.5 px | Post-centre peaks are at y=415 and y=512.5 (97.5 px). Penalty box: 525 px = 39.0 m (40.3 m true), 220 px deep = 16.3 m (16.5 m true). Goal area: 5.4 m / 17.7 m. Confirmed. |
| 0051 | rider average speed 2.07 m/s | 17.56 px/frame | ORB background pan is +15 px over 49 frames. Rear wheel: x 1490 to 640 at f49, plus pan, gives 865 px / 49 frames = 17.65 px/frame. That gives 0.00391 m/px at rider depth (agent: 0.00393). |

## Rows checked
| qid | clip | quantity | current | quick-check value (route) | diff | action |
|---|---|---|---|---|---|---|
| 2022 | 0003 | pizza diameter (cm) | 46.0 | 42.8-44.5 (1010 px / 170-177 px per 7.5 cm at pizza row) | -3 to -7% | keep |
| 2023 | 0003 | wine glass diameter (cm) | 12.0 | 11.1-12.6 (rim 245 px, bowl about 276 px, 164 px per 7.5 cm at glass row) | within 8% | keep |
| 2024 | 0003 | cutter speed at 0.2 s (cm/s) | 42.0 | 40-41 (cap read f2 to f8: 36.8 px/frame image; table-relative 38 px/frame = 912 px/s) | -3% | keep |
| 2025 | 0003 | pepperoni diameter (cm) | 5.9 | 5.3-5.5 (125-127 px) | -8% | keep |
| 2052 | 0011 | initial distance between the players (m) | 2.1 | 2.07 (head to head 457 px at f0) | -1% | keep |
| 2053 | 0011 | displacement, player in white (m) | 6.55 | 6.52-6.59 (bg-subtracted blob track f0 to f102, extrapolated to f106; overview read 1440 px) | 0% | keep |
| 2054 | 0011 | average speed, player in white (m/s) | 1.53 | 1.53-1.55 (6.52-6.59 m / 4.24-4.28 s; the player moves steadily through the whole clip) | 0% | keep |
| 2055 | 0011 | displacement, player in black (m) | 3.35 | 3.2-3.3 (705-726 px) | -2 to -4% | keep |
| 2080 | 0016 | distance between the players at t=0 (m) | 3.305 | 3.32 (435 px) | 0% | keep |
| 2081 | 0016 | ball velocity at 0 s (m/s) | 1.62 | 1.35-1.81 by interval (NCC template track: first step 6.3 px/frame gives 1.44; quadratic v0 5.8-6.9 px/frame gives 1.33-1.57; 0 to 0.1 s gives 1.60; 0 to 0.2 s gives 1.81) | about -10% vs the centre value of 1.45 | keep (under 15%; depends on the annotator's interval) |
| 2082 | 0016 | ball to player in black at 0.5 s (m) | 1.382 | 1.32 (ball (1140,3433) f15 by template, player torso (1060,3280)) | -5% | keep |
| 2083 | 0016 | basket to player in black at 0.5 s (m) | 2.234 | 2.21 (rim centre (1060,3570) to torso, 290 px) | -1% | keep |
| 2116 | 0023 | pool length (m) | 9.614 | 9.6-10.1 (1158 px; 206-217 px per 1.8 m) | 0 to +5% | keep |
| 2117 | 0023 | pool width (m) | 4.488 | 4.5-4.7 (540 px) | 0 to +5% | keep |
| 2118 | 0023 | deck chair length (m) | 2.053 | 2.03-2.14 (top-left lounger 245 px) | -1 to +4% | keep |
| 2119 | 0023 | swimmer average velocity (m/s) | 1.261 | 1.26-1.33 (head 773 to about 1418-1432 px in 4.3 s, which is the agent's 655 px) | 0 to +5% | keep |
| 2120 | 0023 | distance between the two left umbrellas (m) | 3.973 | 3.93-4.14 (centres (224,496) and (216,970), 474 px) | 0 to +4% | keep |
| 3008 | 0031 | distance travelled, player in white, 0.5 to 5.53 s (m) | 11.5 | 11.0-11.2 (path through f15, 45, 75, 105, 135, 166 = 151 px; displacement 148.5 px) | -3% | keep |
| 3009 | 0031 | distance travelled, player in black (m) | 2.65 | 2.53 (34 px, stationary until about f80) | -5% | keep |
| 3010 | 0031 | speed, player in white (m/s) | 2.28 | 2.20-2.23 | -3% | keep |
| 3011 | 0031 | speed, player in black (m/s) | 0.53 | 0.50 | -5% | keep |
| 3012 | 0031 | pitch width (m) | 62.2 | 62.2 (touchlines y=47 and 884) | 0% | keep |
| 3124 | 0051 | rider height (m) | 1.16 | 1.10-1.16 (282-296 px x 0.00391) | -2% | keep |
| 3125 | 0051 | green car (Fiat) width (m) | 1.31 | 1.37-1.40 (262 px x 0.00391 x depth ratio 1.33-1.37) | +5 to +7% | keep |
| 3126 | 0051 | green car height (m) | 1.01 | 1.05-1.08 (201 px) | +5 to +7% | keep |
| 3127 | 0051 | tree height (m) | 3.97 | 4.1-4.3 (702 px x ratio 1.50-1.55) | +4 to +8% | keep |
| 3128 | 0051 | brown-green car distance, gap (m) | 1.59 | 1.66-1.70 (318 px gap) | +5 to +7% | keep |

No row's quick check differs from the current answer by 15% or more, so no row needed the in-depth second-route
re-measurement, and I propose no fixes.

## Observations (no change proposed)
- 0051: the agent used y=855 as the rider's ground row, but that is the wheel-axle height. The wheels touch the
  ground at y of about 872-875. With the agent's horizon (about y=600), this understates the depth ratio from the
  car row and tree base to the rider: 1.36 instead of 1.275 for the cars, and 1.54 instead of 1.44 for the tree.
  The car and tree answers are therefore about 7% low. The horizon itself is uncertain (about 547 to 627, from the
  rider-vs-Fiat geometry with a rider 1.65-1.82 m tall including the deck), so the bias could be anywhere from about
  0% to +13%. That is under the threshold. Two larger, unresolvable ambiguities remain:
  - Did the annotator use one uniform 2D scale? If so, the car and tree answers would be about 0.73x the current values.
  - Do the real-world dimensions apply? The Fiat 500 implies about 1.4x the prior-based scale.
  The current depth-corrected values sit between these two cases. For 3128, gap vs centre-to-centre (3.06 m) is
  also a convention risk; keeping the gap is the better choice under the scoring asymmetry.
- 0003: the main risk is the "width" convention (short vs long side; the long side would give about 0.52x every
  answer). Pixel measurements agree with the agent. Under the scoring asymmetry, keeping the short-side reading is
  the better bet at p(short) of 0.6 or more.
- 0023: the scale comes from the swimmer's pixel length. Head-to-toe gives 206 px, so the answers would be 5% higher
  than the current ones. The fingertip reading (about 250 px) would make them 13% lower. The current 217 px is a mild hedge.
- 0016 2081: the image-plane ball speed at t=0 depends strongly on the interval (1.35-1.81). The current 1.62 is near
  the middle.
- 0011: the black player is jumping at the rim at f0. With the drone at about 14 m (the rim looks 1.29x magnified),
  the head positions are radially magnified about 15%. The 2D head-based convention is kept.
